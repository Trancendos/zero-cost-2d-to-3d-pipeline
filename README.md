# Zero-Cost 2D-to-3D Pipeline

Fully local, open-source pipeline that turns a 2D image into a textured 3D model, cleans it in Blender, optionally rigs it, and can bring it to life as an interactive talking character.

**Created for practical, zero-subscription use.**

## Features
- Multi-model support: TripoSR (low VRAM) + TRELLIS.2 fallback
- Automatic background removal
- Headless Blender cleanup, auto-UV, and basic rigging
- Path to interactive talking AI character (VRM + local LLM + TTS)
- Designed to be extended into a web app (Gradio / FastAPI)

## Quick Start

### 1. Install dependencies
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install rembg pillow opencv-python trimesh numpy
git clone https://github.com/VAST-AI-Research/TripoSR.git
cd TripoSR && pip install -r requirements.txt && cd ..
```

### 2. Run the multi-model script
```bash
python multi_image_to_3d.py your_image.jpg --model auto --res 320
```

### 3. Clean & UV in Blender (headless)
```bash
blender --background --python blender_cleanup_rig.py -- output/your_image.glb output/cleaned.glb
```

Add `--rig` for a basic armature.

## Talking Character Path
See `docs/talking_character.md` for the recommended local stack (VRM + Ollama + Piper/Kokoro + Amica / AITuber Kit style).

## License
Code in this repo: MIT  
Underlying models have their own licences (TripoSR = MIT, TRELLIS.2 = MIT, etc.). Always check.

## Roadmap
- [ ] Full TRELLIS.2 integration
- [ ] Gradio web UI
- [ ] Better auto-rig (UniRig / AssetFurnace integration)
- [ ] One-click talking character launcher
