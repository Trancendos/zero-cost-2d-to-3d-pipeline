#!/usr/bin/env python3
"""Fail-closed NVIDIA VRAM gate; respects the actual CUDA_VISIBLE_DEVICES selection."""
import json, os, subprocess

def get_gpu_info():
    try:
        out = subprocess.check_output(["nvidia-smi","--query-gpu=index,uuid,name,memory.total,memory.free","--format=csv,noheader,nounits"], text=True, stderr=subprocess.PIPE, timeout=10)
        gpus=[]
        for line in out.splitlines():
            p=[x.strip() for x in line.split(",",4)]
            if len(p)==5:
                gpus.append({"index":int(p[0]),"uuid":p[1],"name":p[2],"total_mb":int(float(p[3])),"free_mb":int(float(p[4]))})
        return {"available":bool(gpus),"gpus":gpus,"reason":None if gpus else "nvidia-smi returned no GPU rows"}
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        return {"available":False,"gpus":[],"reason":str(e)[:800]}

def select_gpu(info, min_total_mb=14000, min_free_mb=12000, visible=None):
    if min_total_mb < 1 or min_free_mb < 1: return False,"VRAM thresholds must be positive.",None
    if not info.get("available"): return False,info.get("reason") or "No NVIDIA GPU available",None
    gpus=info.get("gpus",[])
    if visible is None and "CUDA_VISIBLE_DEVICES" in os.environ: visible=os.environ["CUDA_VISIBLE_DEVICES"]
    if visible is not None:
        first=str(visible).split(",",1)[0].strip()
        if not first or first=="-1": return False,"CUDA_VISIBLE_DEVICES masks all GPUs.",None
        selected=next((g for g in gpus if str(g["index"])==first or g["uuid"].lower()==first.lower()),None)
        if selected is None: return False,"Cannot map CUDA_VISIBLE_DEVICES to nvidia-smi GPU.",None
    else:
        selected=max(gpus,key=lambda g:(g["free_mb"],g["total_mb"]))
    if selected["total_mb"] < min_total_mb or selected["free_mb"] < min_free_mb:
        return False,f"GPU {selected['index']} fails gate: {selected['total_mb']} MB total / {selected['free_mb']} MB free; need {min_total_mb}/{min_free_mb} MB.",selected
    return True,f"GPU {selected['index']} {selected['name']} passes VRAM gate.",selected

def require_vram(min_total_mb=14000,min_free_mb=12000):
    info=get_gpu_info(); ok,msg,gpu=select_gpu(info,min_total_mb,min_free_mb)
    return ok,msg,{"gpu_info":info,"selected_gpu":gpu,"min_total_mb":min_total_mb,"min_free_mb":min_free_mb}

if __name__=="__main__":
    ok,msg,details=require_vram()
    print(json.dumps({"ok":ok,"message":msg,**details},indent=2))
    raise SystemExit(0 if ok else 2)
