#!/usr/bin/env python3
"""
Gradio Web UI for Zero-Cost 2D-to-3D Pipeline
Upload an image → generate 3D model with TripoSR → download GLB
"""

import gradio as gr
import torch
from PIL import Image
from rembg import remove
from pathlib import Path
import tempfile
import sys
import os

# Add TripoSR
sys.path.append(str(Path(__file__).parent / "TripoSR"))

def generate_3d(image, resolution=256):
    if image is None:
        return None, "Please upload an image."
    
    try:
        from tsr.system import TSR
        from tsr.utils import resize_foreground
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Clean background
        img = image.convert("RGB")
        img = remove(img)
        img = resize_foreground(img, 0.85)
        
        # Load model (cached after first run)
        model = TSR.from_pretrained(
            "stabilityai/TripoSR",
            config_name="config.yaml",
            weight_name="model.ckpt"
        )
        model.renderer.chunk_size = 8192
        model.to(device)
        
        with torch.no_grad():
            scene_codes = model([img], device=device)
            meshes = model.extract_mesh(scene_codes, resolution=int(resolution))
        
        # Save to temp file
        tmp = tempfile.NamedTemporaryFile(suffix=".glb", delete=False)
        meshes[0].export(tmp.name)
        
        return tmp.name, f"Success! Vertices: {len(meshes[0].vertices):,} | Faces: {len(meshes[0].faces):,}"
    
    except Exception as e:
        return None, f"Error: {str(e)}"

with gr.Blocks(title="Zero-Cost 2D → 3D") as demo:
    gr.Markdown("# Zero-Cost 2D-to-3D Pipeline\nUpload a photo and get a 3D model (GLB). Runs locally with TripoSR.")
    
    with gr.Row():
        with gr.Column():
            input_image = gr.Image(type="pil", label="Input Image")
            resolution = gr.Slider(128, 320, value=256, step=32, label="Resolution (higher = more detail, slower)")
            btn = gr.Button("Generate 3D Model", variant="primary")
        
        with gr.Column():
            output_model = gr.Model3D(label="3D Preview")
            status = gr.Textbox(label="Status")
            download = gr.File(label="Download GLB")
    
    btn.click(
        fn=generate_3d,
        inputs=[input_image, resolution],
        outputs=[output_model, status]
    ).then(
        fn=lambda path: path if path else None,
        inputs=output_model,
        outputs=download
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", share=False)
