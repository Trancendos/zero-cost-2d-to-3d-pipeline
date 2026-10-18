# Research & Future-Proof Notes (Citation-Ready)

## Key Open Models
- TRELLIS.2 (Microsoft) – strong open single-image to textured mesh (MIT)
- TripoSR (Stability AI + Tripo) – fast low-VRAM baseline (MIT)
- UniRig (VAST-AI) – SIGGRAPH 2025 auto-rigging
- SkinTokens / TokenRig – successor work with improved skinning representation

## Useful Repositories to Watch / Learn From
- https://github.com/VAST-AI-Research/UniRig
- https://github.com/VAST-AI-Research/SkinTokens
- https://github.com/Bingeljell/image-to-3dlab (AssetFurnace)
- https://github.com/VAST-AI-Research/TripoSR
- Microsoft TRELLIS.2 official repo
- ComfyUI wrappers for the above (many community nodes exist)

## Commercial Leaders (for comparison)
- Meshy, Tripo, Rodin (Hyper3D), Hunyuan 3D

## Strategic Observations (Honest)
- The biggest remaining gap for local pipelines is **reliable, high-quality auto-rigging + animation** on arbitrary (especially non-humanoid) meshes.
- Fully local high-quality image-to-3D is now practical.
- Fully local high-quality talking characters are possible but still require stitching several tools (mesh → VRM → LLM → TTS → lip-sync frontend).
- Agentic / multi-view / scene-level generation is the clear research frontier.
