"""Optional SkinTokens tab. Call add_skintokens_rig_tab(gr) inside gr.Blocks."""
from pathlib import Path
import json

def add_skintokens_rig_tab(gr):
    with gr.Tab("Auto-rig (SkinTokens)"):
        gr.Markdown("Optional local rigging stage. Requires SkinTokens dependencies and an NVIDIA GPU. The existing Generate 3D path is unchanged.")
        source=gr.File(label="Generated mesh",file_types=[".glb",".obj",".fbx"])
        output=gr.File(label="Rigged GLB",interactive=False)
        transfer=gr.Checkbox(value=True,label="Preserve/transfer materials")
        post=gr.Checkbox(value=False,label="Voxel post-processing (additional compute)")
        llm=gr.Checkbox(value=False,label="Use local LLM for bounded sampler settings")
        provider=gr.Radio(choices=["ollama","lmstudio"],value="ollama",label="Local LLM")
        model=gr.Textbox(value="qwen2.5:3b",label="Local model")
        status=gr.Textbox(label="Status",lines=8)
        button=gr.Button("Rig selected mesh",variant="primary")
        def execute(file_obj,use_transfer,use_post,use_llm,llm_provider,llm_model):
            if not file_obj: return None,"Choose a mesh first."
            from scripts.rig_with_skintokens import run_rig
            src=Path(getattr(file_obj,"name",file_obj))
            target=src.with_name(src.stem+"_rigged.glb")
            result=run_rig(src,target,Path(__file__).resolve().parents[1]/"external"/"SkinTokens",
                           use_transfer=bool(use_transfer),use_postprocess=bool(use_post),
                           llm_assist=bool(use_llm),llm_provider=llm_provider,llm_model=llm_model)
            return (result.get("output") if result.get("success") else None),json.dumps(result,indent=2)
        button.click(execute,inputs=[source,transfer,post,llm,provider,model],outputs=[output,status])
