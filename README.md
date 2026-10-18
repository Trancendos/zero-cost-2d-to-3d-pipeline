# Zero-Cost 2D-to-3D Pipeline

Fully local, open-source pipeline that turns a 2D image into a textured 3D model, cleans it in Blender, optionally rigs it, and can bring it to life as an interactive talking character.

**Created for practical, zero-subscription use.**

## Features
- Multi-model support: TripoSR (low VRAM) + TRELLIS.2 fallback path
- Automatic background removal
- **New: Gradio Web UI** – use it in the browser
- Headless Blender cleanup, auto-UV, and basic rigging
- Path to interactive talking AI character (VRM + local LLM + TTS)
- Designed for future extension (better auto-rig, full TRELLIS.2, web deployment)

## Quick Start

### 1. Install dependencies
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install rembg pillow opencv-python trimesh numpy gradio

git clone https://github.com/VAST-AI-Research/TripoSR.git
cd TripoSR && pip install -r requirements.txt && cd ..
```

### 2. Run the Gradio Web UI (recommended)
```bash
python app.py
```
Then open http://127.0.0.1:7860 in your browser.

### 3. Or use the command-line script
```bash
python multi_image_to_3d.py your_image.jpg --model auto --res 320
```

### 4. Clean & UV in Blender (headless)
```bash
blender --background --python blender_cleanup_rig.py -- output/your_image.glb output/cleaned.glb
```

Add `--rig` for a basic armature.

## Better Auto-Rig Options (2026)
- **UniRig** (VAST-AI, SIGGRAPH 2025) – strong open model for diverse skeletons
- **AssetFurnace** – full local pipeline including SkinTokens auto-rig + 21 animations
- **Make-It-Animatable** (CVPR 2025)
- Blender add-ons + ComfyUI-UniRig nodes

These can be integrated as the next major upgrade.

## Talking Character Path
See `docs/talking_character.md`.

## Research & Future-Proof Notes
Latest open models (TRELLIS.2, UniRig, AssetFurnace) + commercial leaders (Meshy, Tripo, Rodin, Hunyuan) show the field is moving toward:
- Better single-image topology and PBR
- Native auto-rig + animation
- Multi-view / agentic scene reconstruction
- Fully local high-quality pipelines

This repo stays focused on zero-cost, local-first solutions while remaining easy to extend.

## License
Code in this repo: MIT  
Underlying models have their own licences. Always check.
