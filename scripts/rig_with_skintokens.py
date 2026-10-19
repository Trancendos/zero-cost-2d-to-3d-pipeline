#!/usr/bin/env python3
"""Optional SkinTokens/TokenRig stage; leaves default TripoSR generation unchanged."""
import argparse, hashlib, json, os, random, struct, subprocess, sys, time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from hardware_gate import require_vram
from local_llm_rig_assist import DEFAULT,recommend
DEFAULT_CKPT="experiments/articulation_xl_quantization_256_token_4/grpo_1400.ckpt"

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def validate_glb(path):
    path=Path(path)
    with path.open("rb") as f:
        header=f.read(12)
        if len(header)!=12 or header[:4]!=b"glTF" or int.from_bytes(header[4:8],"little")!=2: raise ValueError("Output is not GLB 2.0.")
        if int.from_bytes(header[8:12],"little")!=path.stat().st_size: raise ValueError("GLB declared length mismatch.")
        doc=None
        while f.tell()<path.stat().st_size:
            chunk=f.read(8)
            if len(chunk)!=8: raise ValueError("Truncated GLB chunk header.")
            size,kind=struct.unpack("<II",chunk)
            if size<1 or size>path.stat().st_size-f.tell(): raise ValueError("Invalid GLB chunk length.")
            raw=f.read(size)
            if kind==0x4E4F534A:
                if doc is not None: raise ValueError("Multiple GLB JSON chunks.")
                doc=json.loads(raw.decode("utf-8").rstrip("\x00 \t\r\n"))
    if not isinstance(doc,dict): raise ValueError("Missing GLB JSON document.")
    skins=doc.get("skins",[]); nodes=doc.get("nodes",[])
    if not skins: raise ValueError("Output contains no skin definitions.")
    joints=sum(len(s.get("joints",[])) for s in skins if isinstance(s,dict))
    if joints<1: raise ValueError("Output skins contain no joints.")
    for skin in skins:
        for joint in skin.get("joints",[]):
            if type(joint) is not int or not 0<=joint<len(nodes): raise ValueError("Skin has invalid joint node index.")
    if not any(isinstance(n,dict) and isinstance(n.get("skin"),int) for n in nodes): raise ValueError("No node references a skin.")
    attrs=[p.get("attributes",{}) for m in doc.get("meshes",[]) if isinstance(m,dict) for p in m.get("primitives",[]) if isinstance(p,dict)]
    if not any("JOINTS_0" in a and "WEIGHTS_0" in a for a in attrs): raise ValueError("Mesh has no JOINTS_0/WEIGHTS_0 attributes.")
    return {"skin_count":len(skins),"joint_count":joints,"validation_level":"structural only; deformation/weight values need further QA"}

def run_rig(input_path,output_path,skintokens_dir,seed=42,use_transfer=True,use_postprocess=False,llm_assist=False,llm_provider="ollama",llm_model="qwen2.5:3b",overwrite=False,timeout=900):
    src=Path(input_path).resolve(); out=Path(output_path).resolve(); engine=Path(skintokens_dir).resolve()
    if src.suffix.lower() not in {".glb",".obj",".fbx"} or not src.is_file(): return {"success":False,"error":"Input must be an existing GLB, OBJ, or FBX file."}
    if not (engine/"demo.py").is_file(): return {"success":False,"error":f"SkinTokens demo.py not found: {engine}"}
    if out.exists() and not overwrite: return {"success":False,"error":"Output exists; pass --overwrite to replace it."}
    sidecar=out.with_suffix(".rig.json"); manifest=out.with_name(out.stem+".asset-manifest.json")
    if not overwrite and (sidecar.exists() or manifest.exists()): return {"success":False,"error":"Sidecar/manifest already exists; choose another output or use --overwrite."}
    ok,msg,hardware=require_vram()
    if not ok: return {"success":False,"error":msg,"hardware":hardware}
    ckpt=engine/DEFAULT_CKPT
    if not ckpt.is_file(): return {"success":False,"error":f"Checkpoint missing: {ckpt}. Follow upstream instructions; weights are not bundled."}
    params,llm_status=recommend(llm_provider,llm_model) if llm_assist else (dict(DEFAULT),"LLM disabled; defaults selected.")
    random.seed(seed) # upstream demo.py exposes no seed argument: not deterministic GPU seeding.
    env=os.environ.copy(); env.setdefault("PYTHONHASHSEED",str(seed)); env.setdefault("CUBLAS_WORKSPACE_CONFIG",":4096:8")
    selected=hardware.get("selected_gpu") or {}
    if "CUDA_VISIBLE_DEVICES" not in env and selected.get("index") is not None: env["CUDA_VISIBLE_DEVICES"]=str(selected["index"])
    out.parent.mkdir(parents=True,exist_ok=True)
    cmd=[sys.executable,str(engine/"demo.py"),"--input",str(src),"--output",str(out),"--model_ckpt",str(ckpt),
         "--top_k",str(params["top_k"]),"--top_p",str(params["top_p"]),"--temperature",str(params["temperature"]),
         "--repetition_penalty",str(params["repetition_penalty"]),"--num_beams",str(params["num_beams"])]
    if use_transfer: cmd.append("--use_transfer")
    if use_postprocess: cmd.append("--use_postprocess")
    started=time.monotonic()
    try:
        proc=subprocess.run(cmd,cwd=engine,env=env,capture_output=True,text=True,timeout=max(30,min(int(timeout),3600)))
        elapsed=round(time.monotonic()-started,2)
        if proc.returncode: return {"success":False,"error":(proc.stderr or proc.stdout)[-4000:],"duration_s":elapsed}
        if not out.is_file() or out.stat().st_size<20: return {"success":False,"error":"Engine returned success but no output GLB exists."}
        qa=validate_glb(out); run_id=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"-"+str(seed)
        sidecar=out.with_suffix(".rig.json"); manifest=out.with_name(out.stem+".asset-manifest.json")
        if not overwrite and (sidecar.exists() or manifest.exists()): return {"success":False,"error":"Sidecar/manifest exists; choose another output or use --overwrite."}
        input_hash=sha256(src); output_hash=sha256(out)
        record={"schema":"aaf.rig-sidecar.v1","run_id":run_id,"generated_utc":datetime.now(timezone.utc).isoformat(),
          "input":{"filename":src.name,"sha256":input_hash},"output":{"filename":out.name,"sha256":output_hash,"bytes":out.stat().st_size},
          "tool":"SkinTokens/TokenRig","code_license":"MIT per upstream LICENSE; checkpoint license pending separate verification",
          "checkpoint":str(ckpt.relative_to(engine)),"checkpoint_license_status":"pending_verification","seed":seed,
          "seed_note":"Upstream demo has no seed CLI; GPU-level determinism is not guaranteed.","use_transfer":use_transfer,
          "use_postprocess":use_postprocess,"llm_assist":llm_status,"sampling":params,"hardware":hardware,"validation":qa,"duration_s":elapsed}
        asset={"schema":"aaf.asset-manifest.v1","asset_id":"aaf-rig-"+run_id,"created_utc":datetime.now(timezone.utc).isoformat(),
          "source":{"sha256":input_hash,"filename":src.name,"consent_record_id":None},
          "rig":{"tool":"SkinTokens/TokenRig","checkpoint_licence_status":"pending_verification","bones_detected":qa["joint_count"],"sidecar":sidecar.name},
          "outputs":[{"path":out.name,"sha256":output_hash,"bytes":out.stat().st_size,"format":"glb"}],
          "licensing":{"status":"pending_verification","evidence":["Verify checkpoint and dependency licences independently."]},
          "qa":{"l1_structural":"pass","bones_ok":True,"notes":qa["validation_level"]}}
        sidecar.write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8"); manifest.write_text(json.dumps(asset,indent=2)+"\n",encoding="utf-8")
        return {"success":True,"output":str(out),"sidecar":str(sidecar),"manifest":str(manifest),"validation":qa,"llm_assist":llm_status,"duration_s":elapsed}
    except subprocess.TimeoutExpired: return {"success":False,"error":f"Timed out after {timeout}s; check for a surviving upstream bpy_server process."}

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--input",required=True,type=Path); p.add_argument("--output",required=True,type=Path)
    p.add_argument("--skintokens-dir",type=Path,default=ROOT/"external"/"SkinTokens"); p.add_argument("--seed",type=int,default=42)
    p.add_argument("--no-transfer",action="store_true"); p.add_argument("--use-postprocess",action="store_true"); p.add_argument("--llm-assist",action="store_true")
    p.add_argument("--llm-provider",choices=["ollama","lmstudio"],default="ollama"); p.add_argument("--llm-model",default="qwen2.5:3b")
    p.add_argument("--overwrite",action="store_true"); p.add_argument("--timeout",type=int,default=900); a=p.parse_args()
    result=run_rig(a.input,a.output,a.skintokens_dir,a.seed,not a.no_transfer,a.use_postprocess,a.llm_assist,a.llm_provider,a.llm_model,a.overwrite,a.timeout)
    print(json.dumps(result,indent=2)); return 0 if result.get("success") else 1
if __name__=="__main__": raise SystemExit(main())
