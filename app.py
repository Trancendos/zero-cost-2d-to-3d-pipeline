#!/usr/bin/env python3
"""
Character Studio - Zero-Cost 2D to 3D + Talking Characters
Now with streaming chat via the official ollama Python library.
"""

import gradio as gr
import torch
from PIL import Image
from rembg import remove
from pathlib import Path
import tempfile
import sys
import datetime
import os

sys.path.append(str(Path(__file__).parent / "TripoSR"))

ROOT = Path(__file__).parent
CHARACTERS_DIR = ROOT / "characters"

# ---------- 3D Generation ----------
def get_triposr_model(local_dir: str = None, device: str = "cuda"):
    from tsr.system import TSR
    if local_dir and Path(local_dir).exists():
        model = TSR.from_pretrained(local_dir, config_name="config.yaml", weight_name="model.ckpt")
    else:
        model = TSR.from_pretrained("stabilityai/TripoSR", config_name="config.yaml", weight_name="model.ckpt")
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

        progress(0.3, desc="Loading TripoSR...")
        model = get_triposr_model(local_model_path.strip() if local_model_path else None, device)

        progress(0.55, desc="Generating mesh...")
        with torch.no_grad():
            scene_codes = model([img], device=device)
            meshes = model.extract_mesh(scene_codes, resolution=int(resolution))

        progress(0.9, desc="Exporting...")
        tmp = tempfile.NamedTemporaryFile(suffix=".glb", delete=False)
        meshes[0].export(tmp.name)
        status = f"✅ Success | Verts: {len(meshes[0].vertices):,} | Faces: {len(meshes[0].faces):,}"
        progress(1.0)
        return tmp.name, status
    except Exception as e:
        return None, f"Error: {e}"

# ---------- Character Creation ----------
def create_character(image, name, description):
    if image is None or not name or not name.strip():
        return "Please provide an image and a character name."
    try:
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name.lower()).strip("_")
        char_dir = CHARACTERS_DIR / safe_name
        char_dir.mkdir(parents=True, exist_ok=True)
        image.save(char_dir / "source.png")
        personality = f"You are {name}, {description or 'a unique character'}.\n\nSpeak in a way that matches your character. Keep responses engaging, in-character, and concise unless the user asks for more detail.\n\nNever break character.\n"
        (char_dir / "personality.txt").write_text(personality.strip() + "\n")
        (char_dir / "README.md").write_text(f"# {name}\n\nCreated: {datetime.date.today()}\n")
        return f"✅ Character '{name}' created at characters/{safe_name}/"
    except Exception as e:
        return f"Error: {e}"

def list_characters():
    if not CHARACTERS_DIR.exists():
        return []
    return sorted([d.name for d in CHARACTERS_DIR.iterdir() if d.is_dir() and not d.name.startswith("_") and (d / "personality.txt").exists()])

# ---------- Streaming Chat (using official ollama library) ----------
def chat_with_character_stream(character, message, history, model_name):
    """
    Streaming chat using the official ollama Python package.
    Install with: pip install ollama
    """
    if not character:
        history.append((message, "Please select a character first."))
        yield history, ""
        return
    if not message.strip():
        yield history, ""
        return

    personality_file = CHARACTERS_DIR / character / "personality.txt"
    if not personality_file.exists():
        history.append((message, f"No personality found for {character}."))
        yield history, ""
        return

    personality = personality_file.read_text().strip()

    # Build messages for better quality
    messages = [
        {"role": "system", "content": personality},
    ]
    # Add previous history for context (keep last few turns)
    for user_msg, bot_msg in history[-6:]:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})
    messages.append({"role": "user", "content": message})

    history.append((message, ""))
    yield history, ""

    try:
        import ollama
        stream = ollama.chat(
            model=model_name,
            messages=messages,
            stream=True,
        )
        full_reply = ""
        for chunk in stream:
            part = chunk.get("message", {}).get("content", "")
            if part:
                full_reply += part
                history[-1] = (message, full_reply)
                yield history, ""
    except ImportError:
        history[-1] = (message, "Please install the ollama package: pip install ollama")
        yield history, ""
    except Exception as e:
        history[-1] = (message, f"Error: {e}\n\nMake sure Ollama is running and the model is pulled.")
        yield history, ""

def prepare_for_vrm_message():
    return """### Prepare for VRM (Talking Avatar)

1. Take your best cleaned + rigged **GLB**
2. Open it in **Blender**
3. Make sure the free **VRM Add-on for Blender** is installed
4. Go to File → Export → **VRM**
5. Map humanoid bones if asked
6. Save the `.vrm` file

You can then load the VRM into:
- Amica
- AITuber Kit
- Three.js + `@pixiv/three-vrm`
- Unity (UniVRM)

Full guide: `docs/vrm_conversion_guide.md`
"""

# ---------- UI ----------
with gr.Blocks(title="Character Studio", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Character Studio\nZero-Cost 2D → 3D + Talking Characters\n*Local after initial model download*")

    with gr.Tab("Generate 3D"):
        with gr.Row():
            with gr.Column():
                input_image = gr.Image(type="pil", label="Upload Image", height=300)
                resolution = gr.Slider(128, 320, value=256, step=32, label="Resolution")
                local_model = gr.Textbox(label="Local TripoSR folder (optional)", placeholder="Leave empty for default cache")
                gen_btn = gr.Button("Generate 3D Model", variant="primary")
            with gr.Column():
                output_model = gr.Model3D(label="3D Preview", height=380)
                status = gr.Textbox(label="Status")
                download = gr.File(label="Download GLB")

        gen_btn.click(
            generate_3d,
            inputs=[input_image, resolution, local_model],
            outputs=[output_model, status]
        ).then(lambda p: p, inputs=output_model, outputs=download)

    with gr.Tab("Create Character"):
        with gr.Row():
            char_image = gr.Image(type="pil", label="Character Image", height=280)
            with gr.Column():
                char_name = gr.Textbox(label="Character Name", placeholder="Cornelius MacIntyre")
                char_desc = gr.Textbox(label="Description", lines=3, placeholder="a warm, eccentric elderly scientist with wild white hair")
                create_btn = gr.Button("Create Character", variant="primary")
        create_status = gr.Textbox(label="Result")
        create_btn.click(create_character, inputs=[char_image, char_name, char_desc], outputs=create_status)

    with gr.Tab("Talk"):
        gr.Markdown("Chat with streaming replies (requires `pip install ollama` and Ollama running).")
        with gr.Row():
            character_dropdown = gr.Dropdown(choices=list_characters(), label="Select Character", interactive=True)
            refresh_btn = gr.Button("Refresh List", size="sm")
            ollama_model = gr.Textbox(value="llama3.1", label="Ollama Model")

        chatbot = gr.Chatbot(label="Conversation", height=420)
        with gr.Row():
            msg = gr.Textbox(label="Your message", scale=5, placeholder="Say something...")
            send_btn = gr.Button("Send", variant="primary", scale=1)

        refresh_btn.click(lambda: gr.Dropdown(choices=list_characters()), outputs=character_dropdown)

        send_btn.click(
            chat_with_character_stream,
            inputs=[character_dropdown, msg, chatbot, ollama_model],
            outputs=[chatbot, msg]
        )
        msg.submit(
            chat_with_character_stream,
            inputs=[character_dropdown, msg, chatbot, ollama_model],
            outputs=[chatbot, msg]
        )

    with gr.Tab("Prepare for VRM"):
        gr.Markdown(prepare_for_vrm_message())

    gr.Markdown("---\n**Install for streaming chat:** `pip install ollama`")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", share=False)
