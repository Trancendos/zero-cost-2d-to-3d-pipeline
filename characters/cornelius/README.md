# Cornelius MacIntyre – Complete Workflow

## Quick Commands

```bash
# 1. Generate base mesh
python multi_image_to_3d.py examples/cornelius_macintyre.png --out output/cornelius --res 320

# 2. Clean + UV
blender --background --python blender_cleanup_rig.py -- \
  output/cornelius/cornelius_macintyre.glb \
  output/cornelius/cornelius_cleaned.glb

# 3. Clean + basic armature
blender --background --python blender_cleanup_rig.py -- \
  output/cornelius/cornelius_macintyre.glb \
  output/cornelius/cornelius_rigged.glb --rig
```

## Personality
See `personality.txt`. Use it with Ollama:

```bash
ollama run llama3.1 "$(cat characters/cornelius/personality.txt)\n\nUser: Hello Cornelius!"
```

Or use the talking character launcher:
```bash
python talking_character_launcher.py
```

## Recommended Next Steps
1. Improve topology if needed
2. Auto-rig with SkinTokens / AssetFurnace (preferred) or Rigify
3. Convert to VRM with the official Blender VRM add-on
4. Connect to a talking frontend (Amica, AITuber Kit, or Three.js + VRM)
