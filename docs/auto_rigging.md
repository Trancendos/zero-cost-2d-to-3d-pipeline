# Better Auto-Rigging Guide (2026)

## Recommended Open Solutions

### 1. SkinTokens / TokenRig (Strongest current open direction)
- Successor to UniRig
- Unified skeleton + skinning via discrete tokens
- Significant accuracy gains reported
- GitHub: https://github.com/VAST-AI-Research/SkinTokens
- Also available via ComfyUI nodes and some no-Blender ports

### 2. UniRig (VAST-AI, SIGGRAPH 2025)
- Diverse skeleton support
- Good research baseline
- Installation is non-trivial (specific CUDA / flash-attn / spconv requirements)
- Repo: https://github.com/VAST-AI-Research/UniRig

### 3. AssetFurnace
- Full local pipeline that already includes SkinTokens-style auto-rig + 21 animation presets
- Excellent for end-to-end character work
- https://github.com/Bingeljell/image-to-3dlab / https://assetfurnace.com

### 4. Blender Native / Free Add-ons
- **Rigify** (built-in) – still the most reliable free starting point
- **BlenRig 6** – free, film-quality body + face
- **CloudRig** (Blender Studio) – extends Rigify
- Voxel Heat Diffuse Skinning (paid but excellent weights)

## Practical Recommendation for this Pipeline
1. Generate mesh with TripoSR / TRELLIS.2
2. Clean with the provided Blender script
3. For characters: try AssetFurnace or SkinTokens for auto-rig
4. Fall back to Rigify metarig for maximum control and zero extra dependencies

## Integration Status in this Repo
- Basic armature is already available via `blender_cleanup_rig.py --rig`
- Full UniRig / SkinTokens integration is planned as a future module (requires careful dependency management)
