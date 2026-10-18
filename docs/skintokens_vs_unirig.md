# SkinTokens vs UniRig – Detailed Honest Comparison (2026)

## Overview

**UniRig** (SIGGRAPH 2025, VAST-AI) was a strong unified auto-rigging model that could produce skeletons for diverse characters.

**SkinTokens / TokenRig** is the successor work from the same research line. It introduces a learned discrete representation for skinning weights (SkinTokens) and generates the entire rig (skeleton + skinning) as one autoregressive sequence.

## Key Differences

| Aspect | UniRig | SkinTokens / TokenRig |
|--------|--------|-----------------------|
| **Approach** | Separate stages for skeleton prediction and skinning | Unified sequence: skeleton + SkinTokens together |
| **Skinning Representation** | Traditional continuous weights | Learned compact discrete tokens (FSQ-CVAE) |
| **Reported Gains** | Strong baseline | 98–133% better skinning accuracy, 17–22% better bone prediction over prior SOTA |
| **Diversity** | Good across humans, animals, objects | Explicitly strong on stylized, anime, quadrupeds, fantasy |
| **Maturity** | Public code + partial checkpoints | Newer, with improving ecosystem (ComfyUI nodes, some no-Blender ports) |
| **Installation Difficulty** | High (CUDA, flash-attn, spconv, specific versions) | Still non-trivial, but community wrappers are appearing |
| **Best Current Use** | Research / diverse skeletons | Highest open-source quality target for characters |

## Practical Recommendation for Cornelius-style Characters

For a stylized humanoid cartoon character like **Cornelius MacIntyre**:

1. Generate the mesh with TripoSR or TRELLIS.2
2. Clean topology in Blender
3. Prefer **SkinTokens / TokenRig** (or AssetFurnace which already integrates similar technology) for the auto-rig
4. Fall back to Rigify if you want maximum control and zero extra heavy dependencies

## Links
- UniRig: https://github.com/VAST-AI-Research/UniRig
- SkinTokens: https://github.com/VAST-AI-Research/SkinTokens
- AssetFurnace (practical package using related tech): https://github.com/Bingeljell/image-to-3dlab
