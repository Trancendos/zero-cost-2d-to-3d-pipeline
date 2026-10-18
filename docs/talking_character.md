# Interactive Talking Character Design

## Goal
Take the cleaned + rigged 3D model and turn it into a character you can talk to (voice in → intelligent reply + lip-sync + basic body language).

## Recommended Free / Local Stack (2026)

1. **Mesh Preparation**
   - Cleaned GLB from the pipeline
   - Convert to VRM using the free Blender VRM add-on (recommended for easiest avatar support)

2. **Runtime Engine**
   - Three.js + `@pixiv/three-vrm` (browser) or Godot / Unity

3. **Speech-to-Text**
   - `faster-whisper` (local) or Transformers.js in the browser

4. **Brain (LLM)**
   - Ollama (Llama 3.1, Qwen2.5, Mistral, etc.) — fully local and free

5. **Text-to-Speech + Lip Sync**
   - Piper TTS, Kokoro, or Style-Bert-VITS2 (local)
   - Map phonemes/visemes to VRM blendshapes

6. **Ready-made Frameworks**
   - Amica
   - AITuber Kit
   - DLP3D-style pipelines
   - Custom React + Three.js + VRM starter

## Simple Architecture
```
User voice → Whisper → Ollama (character personality prompt) → TTS → Viseme stream → VRM avatar (lip-sync + idle animation)
```

## Next Steps in this Repo
- Add a simple Gradio or Streamlit launcher
- Provide a minimal Three.js + VRM example
- Integrate better auto-rigging (UniRig / AssetFurnace)
