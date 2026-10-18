#!/usr/bin/env python3
"""
Improved Gradio Web UI for Zero-Cost 2D-to-3D Pipeline
- Model selection (TripoSR primary)
- Progress feedback
- Example images
- Cleaner layout
"""

import gradio as gr
import torch
from PIL import Image
from rembg import remove
from pathlib import Path
import tempfile
import sys
import os
import time

sys.path.append(str(Path(__file__).parent / "TripoSR"))

def generate_3d(image, resolution, progress=gr.Progress(track_tqdm=True)):
    if image is None:
        return None, "Please upload an image first."
    
    try:
        progress(0.1, desc="Removing background...")
        from tsr.system import TSR
        from tsr.utils import resize_foreground
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        img = image.convert("RGB")
        img = remove(img)
        img = resize_foreground(img, 0.85)
        
        progress(0.3, desc="Loading TripoSR model...")
        model = TSR.from_pretrained(
            "stabilityai/TripoSR",
            config_name="config.yaml",
            weight_name="model.ckpt"
        )
        model.renderer.chunk_size = 8192
        model.to(device)
        
        progress(0.5, desc="Generating 3D mesh...")
        with torch.no_grad():
            scene_codes = model([img], device=device)
            meshes = model.extract_mesh(scene_codes, resolution=int(resolution))
        
        progress(0.9, desc="Exporting GLB...")
        tmp = tempfile.NamedTemporaryFile(suffix=".glb", delete=False)
        meshes[0].export(tmp.name)
        
        verts = len(meshes[0].vertices)
        faces = len(meshes[0].faces)
        status = f"✅ Success! Vertices: {verts:,} | Faces: {faces:,} | Device: {device}"
        
        progress(1.0, desc="Done")
        return tmp.name, status
    
    except Exception as e:
        return None, f"Error: {str(e)}"

with gr.Blocks(title="Zero-Cost 2D → 3D", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # Zero-Cost 2D-to-3D Pipeline
    Upload a single image → get a textured 3D model (GLB).  
    Runs fully locally using **TripoSR**. No account or credits required.
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            input_image = gr.Image(type="pil", label="Upload Image", height=300)
            
            with gr.Accordion("Settings", open=True):
                model_choice = gr.Dropdown(
                    choices=["TripoSR (fast, low VRAM)"],
                    value="TripoSR (fast, low VRAM)",
                    label="Model",
                    info="More models (TRELLIS.2 etc.) can be added later"
                )
                resolution = gr.Slider(128, 320, value=256, step=32, label="Mesh Resolution")
            
            btn = gr.Button("Generate 3D Model", variant="primary", size="lg")
            
            gr.Examples(
                examples=[],  # Users can add their own example images later
                inputs=input_image,
                label="Example Images (add your own)"
            )
        
        with gr.Column(scale=1):
            output_model = gr.Model3D(label="3D Preview", height=400)
            status = gr.Textbox(label="Status", interactive=False)
            download = gr.File(label="Download GLB")
    
    btn.click(
        fn=generate_3d,
        inputs=[input_image, resolution],
        outputs=[output_model, status]
    ).then(
        fn=lambda path: path,
        inputs=[output_model],
        outputs=[download]
    )
    
    gr.Markdown("""
    ---
    **Tips:** Use a clear photo of a single object on a simple background for best results.  
    After generation you can run the Blender cleanup script for better topology and UVs.  
    For auto-rigging see the README (UniRig / SkinTokens / AssetFurnace).
    """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", share=False)
