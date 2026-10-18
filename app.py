#!/usr/bin/env python3
"""
Improved Gradio UI for Zero-Cost 2D-to-3D + Character Creation
- Generate 3D from image
- Create new character folders
- Cornelius example built-in
"""

import gradio as gr
import torch
from PIL import Image
from rembg import remove
from pathlib import Path
import tempfile
import sys
import shutil
import datetime

sys.path.append(str(Path(__file__).parent / "TripoSR"))

ROOT = Path(__file__).parent

def generate_3d(image, resolution, progress=gr.Progress(track_tqdm=True)):
    if image is None:
        return None, "Please upload an image."
    try:
        progress(0.1, desc="Removing background...")
        from tsr.system import TSR
        from tsr.utils import resize_foreground

        device = "cuda" if torch.cuda.is_available() else "cpu"
        img = image.convert("RGB")
        img = remove(img)
        img = resize_foreground(img, 0.85)

        progress(0.35, desc="Loading TripoSR...")
        model = TSR.from_pretrained(
            "stabilityai/TripoSR",
            config_name="config.yaml",
            weight_name="model.ckpt"
        )
        model.renderer.chunk_size = 8192
        model.to(device)

        progress(0.6, desc="Generating mesh...")
        with torch.no_grad():
            scene_codes = model([img], device=device)
            meshes = model.extract_mesh(scene_codes, resolution=int(resolution))

        progress(0.9, desc="Exporting...")
        tmp = tempfile.NamedTemporaryFile(suffix=".glb", delete=False)
        meshes[0].export(tmp.name)

        status = f"✅ Success | Vertices: {len(meshes[0].vertices):,} | Faces: {len(meshes[0].faces):,} | Device: {device}"
        progress(1.0)
        return tmp.name, status
    except Exception as e:
        return None, f"Error: {str(e)}"

def create_character_ui(image, name, description):
    if image is None or not name.strip():
        return "Please provide both an image and a character name."
    try:
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name.lower()).strip("_")
        char_dir = ROOT / "characters" / safe_name
        char_dir.mkdir(parents=True, exist_ok=True)

        # Save image
        img_path = char_dir / "source.png"
        image.save(img_path)

        # Personality
        personality = f"You are {name}, {description or 'a unique character'}.\n\nSpeak in a way that matches your character. Keep responses engaging, in-character, and concise unless the user asks for more detail.\n\nNever break character.\n"
        (char_dir / "personality.txt").write_text(personality)

        # README
        readme = f"# {name}\n\nCreated via Gradio UI on {datetime.date.today()}\n\n## Talk to this character\n```bash\npython scripts/talk_with_character.py {safe_name}\n```\n"
        (char_dir / "README.md").write_text(readme)

        return f"✅ Character '{name}' created at characters/{safe_name}/\nYou can now talk to them with:\npython scripts/talk_with_character.py {safe_name}"
    except Exception as e:
        return f"Error creating character: {e}"

with gr.Blocks(title="Zero-Cost 2D → 3D + Characters", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Zero-Cost 2D-to-3D Pipeline + Character Creator\nFully local. No accounts required.")

    with gr.Tab("Generate 3D Model"):
        with gr.Row():
            with gr.Column():
                input_image = gr.Image(type="pil", label="Upload Image", height=320)
                resolution = gr.Slider(128, 320, value=256, step=32, label="Resolution")
                gen_btn = gr.Button("Generate 3D Model", variant="primary")
            with gr.Column():
                output_model = gr.Model3D(label="3D Preview", height=400)
                status = gr.Textbox(label="Status")
                download = gr.File(label="Download GLB")

        gen_btn.click(generate_3d, inputs=[input_image, resolution], outputs=[output_model, status]).then(
            lambda p: p, inputs=output_model, outputs=download
        )

    with gr.Tab("Create Character"):
        gr.Markdown("Create a new character folder (image + personality) that works with the talking launcher.")
        with gr.Row():
            char_image = gr.Image(type="pil", label="Character Image")
            with gr.Column():
                char_name = gr.Textbox(label="Character Name", placeholder="e.g. Cornelius MacIntyre")
                char_desc = gr.Textbox(label="Short Description", placeholder="a warm eccentric scientist...")
                create_btn = gr.Button("Create Character Folder", variant="primary")
        create_status = gr.Textbox(label="Result")
        create_btn.click(create_character_ui, inputs=[char_image, char_name, char_desc], outputs=create_status)

    with gr.Tab("Talk to Character"):
        gr.Markdown("""
        After creating a character, open a terminal and run:
        ```bash
        python scripts/talk_with_character.py cornelius
        ```
        Replace `cornelius` with the folder name of your character.
        """)

    gr.Markdown("---\n**Note:** TripoSR weights are currently loaded via Hugging Face Hub (`from_pretrained`). Once downloaded they are cached locally. Fully offline GGUF-style 3D models are not yet common for this task.")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", share=False)
