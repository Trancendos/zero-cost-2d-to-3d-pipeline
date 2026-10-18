#!/usr/bin/env python3
"""
Zero-Cost 2D-to-3D + Character Studio (Gradio)
- Generate 3D models (TripoSR)
- Create characters
- Talk to characters via Ollama
- Supports local model folder (offline after first download)
"""

import gradio as gr
import torch
from PIL import Image
from rembg import remove
from pathlib import Path
import tempfile
import sys
import subprocess
import datetime
import os

sys.path.append(str(Path(__file__).parent / "TripoSR"))

ROOT = Path(__file__).parent
CHARACTERS_DIR = ROOT / "characters"

# ---------- 3D Generation ----------
def get_triposr_model(local_dir: str = None, device: str = "cuda"):
    from tsr.system import TSR
    if local_dir and Path(local_dir).exists():
        # Try loading from local folder
        model = TSR.from_pretrained(
            local_dir,
            config_name="config.yaml",
            weight_name="model.ckpt"
        )
    else:
        # Default: Hugging Face (caches locally after first download)
        model = TSR.from_pretrained(
            "stabilityai/TripoSR",
            config_name="config.yaml",
            weight_name="model.ckpt"
        )
    model.renderer.chunk_size = 8192
    model.to(device)
    return model

def generate_3d(image, resolution, local_model_path, progress=gr.Progress(track_tqdm=True)):
    if image is None:
        return None, "Please upload an image."
    try:
        progress(0.1, desc="Removing background...")
        from tsr.utils import resize_foreground

        device = "cuda" if torch.cuda.is_available() else "cpu"
        img = image.convert("RGB")
        img = remove(img)
        img = resize_foreground(img, 0.85)

        progress(0.3, desc="Loading TripoSR model...")
        model = get_triposr_model(local_model_path if local_model_path.strip() else None, device)

        progress(0.55, desc="Generating 3D mesh...")
        with torch.no_grad():
            scene_codes = model([img], device=device)
            meshes = model.extract_mesh(scene_codes, resolution=int(resolution))

        progress(0.9, desc="Exporting GLB...")
        tmp = tempfile.NamedTemporaryFile(suffix=".glb", delete=False)
        meshes[0].export(tmp.name)

        status = f"✅ Success | Verts: {len(meshes[0].vertices):,} | Faces: {len(meshes[0].faces):,} | Device: {device}"
        progress(1.0)
        return tmp.name, status
    except Exception as e:
        return None, f"Error: {str(e)}"

# ---------- Character Creation ----------
def create_character(image, name, description):
    if image is None or not name or not name.strip():
        return "Please provide an image and a character name."
    try:
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name.lower()).strip("_")
        char_dir = CHARACTERS_DIR / safe_name
        char_dir.mkdir(parents=True, exist_ok=True)

        image.save(char_dir / "source.png")

        personality = f"""You are {name}, {description or 'a unique character'}.

Speak in a way that matches your character. Keep responses engaging, in-character, and concise unless the user asks for more detail.

Never break character.
"""
        (char_dir / "personality.txt").write_text(personality.strip() + "\n")

        readme = f"# {name}\n\nCreated: {datetime.date.today()}\n\nTalk with:\n```bash\npython scripts/talk_with_character.py {safe_name}\n```\n"
        (char_dir / "README.md").write_text(readme)

        return f"✅ Character '{name}' created successfully!\nFolder: characters/{safe_name}/\n\nYou can now talk to them in the 'Talk' tab or via terminal."
    except Exception as e:
        return f"Error: {e}"

def list_characters():
    if not CHARACTERS_DIR.exists():
        return []
    return sorted([
        d.name for d in CHARACTERS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith("_") and (d / "personality.txt").exists()
    ])

# ---------- Chat ----------
def chat_with_character(character, message, history, model_name):
    if not character:
        history.append((message, "Please select a character first."))
        return history, ""
    if not message.strip():
        return history, ""

    personality_file = CHARACTERS_DIR / character / "personality.txt"
    if not personality_file.exists():
        history.append((message, f"Personality file not found for {character}."))
        return history, ""

    personality = personality_file.read_text().strip()
    prompt = f"{personality}\n\nUser: {message}\n{character}:"

    try:
        result = subprocess.run(
            ["ollama", "run", model_name, prompt],
            capture_output=True, text=True, timeout=90
        )
        reply = result.stdout.strip() or "(No response)"
    except FileNotFoundError:
        reply = "Ollama not found. Please install Ollama and pull a model (e.g. ollama pull llama3.1)."
    except subprocess.TimeoutExpired:
        reply = "Response timed out."
    except Exception as e:
        reply = f"Error: {e}"

    history.append((message, reply))
    return history, ""

# ---------- UI ----------
with gr.Blocks(title="Character Studio – Zero-Cost 2D to 3D", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Character Studio\n**Zero-Cost 2D → 3D + Talking Characters**\nFully local after initial model download.")

    with gr.Tab("Generate 3D"):
        with gr.Row():
            with gr.Column(scale=1):
                input_image = gr.Image(type="pil", label="Upload Image", height=300)
                resolution = gr.Slider(128, 320, value=256, step=32, label="Resolution")
                local_model = gr.Textbox(
                    label="Local TripoSR folder (optional)",
                    placeholder="Leave empty to use Hugging Face cache / download",
                    info="Path to a folder containing config.yaml and model.ckpt for fully offline use"
                )
                gen_btn = gr.Button("Generate 3D Model", variant="primary")
            with gr.Column(scale=1):
                output_model = gr.Model3D(label="3D Preview", height=380)
                status = gr.Textbox(label="Status")
                download = gr.File(label="Download GLB")

        gen_btn.click(
            generate_3d,
            inputs=[input_image, resolution, local_model],
            outputs=[output_model, status]
        ).then(lambda p: p, inputs=output_model, outputs=download)

    with gr.Tab("Create Character"):
        gr.Markdown("Create a new character (saves image + personality for the talking system).")
        with gr.Row():
            char_image = gr.Image(type="pil", label="Character Image", height=280)
            with gr.Column():
                char_name = gr.Textbox(label="Character Name", placeholder="Cornelius MacIntyre")
                char_desc = gr.Textbox(label="Short Description", lines=3, placeholder="a warm, eccentric elderly scientist...")
                create_btn = gr.Button("Create Character", variant="primary")
        create_status = gr.Textbox(label="Result", lines=4)
        create_btn.click(create_character, inputs=[char_image, char_name, char_desc], outputs=create_status)

    with gr.Tab("Talk"):
        gr.Markdown("Chat with any character that has a personality file. Requires Ollama running locally.")
        with gr.Row():
            character_dropdown = gr.Dropdown(choices=list_characters(), label="Select Character", interactive=True)
            refresh_btn = gr.Button("Refresh List", size="sm")
            ollama_model = gr.Textbox(value="llama3.1", label="Ollama Model")

        chatbot = gr.Chatbot(label="Conversation", height=400)
        with gr.Row():
            msg = gr.Textbox(label="Your message", scale=4, placeholder="Say something...")
            send_btn = gr.Button("Send", variant="primary", scale=1)

        def refresh_chars():
            return gr.Dropdown(choices=list_characters())

        refresh_btn.click(refresh_chars, outputs=character_dropdown)

        send_btn.click(
            chat_with_character,
            inputs=[character_dropdown, msg, chatbot, ollama_model],
            outputs=[chatbot, msg]
        )
        msg.submit(
            chat_with_character,
            inputs=[character_dropdown, msg, chatbot, ollama_model],
            outputs=[chatbot, msg]
        )

    gr.Markdown("""
---
**Notes**
- TripoSR will download from Hugging Face the first time. After that it uses the local cache.
- To force a fully local folder, download the model once and paste the folder path in the "Local TripoSR folder" field.
- Talking requires [Ollama](https://ollama.com) installed and a model pulled (`ollama pull llama3.1`).
""")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", share=False)
