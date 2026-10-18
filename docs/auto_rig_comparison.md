# Auto-Rig Options Comparison (Honest 2026 Assessment)

| Option | Type | Quality | Ease of Use | Dependencies | Best For | Honest Limitations |
|--------|------|---------|-------------|--------------|----------|--------------------|
| **SkinTokens / TokenRig** | Open research | High (reported big gains over prior SOTA) | Medium | PyTorch + specific setup | Best open quality | Still research-grade; setup can be fiddly |
| **UniRig** | Open (SIGGRAPH 2025) | Good | Medium-Hard | Heavy (CUDA, flash-attn, spconv, etc.) | Diverse skeletons | Installation friction is real |
| **AssetFurnace** | Full local app | High for characters | High | Bundled | End-to-end characters + animation | Currently strongest practical local package |
| **Rigify** (Blender built-in) | Free native | Good / controllable | Medium | None extra | Reliable production baseline | Requires manual metarig placement |
| **BlenRig 6** | Free Blender add-on | High (film pedigree) | Medium | Blender | Body + face quality | Steeper learning curve |
| **Auto-Rig Pro** | Paid Blender add-on | Very High | High | Paid | One-click professional | Costs money |
| **Basic armature in this repo** | Simple script | Low-Basic | Very High | Blender only | Quick tests | Not production-ready |

**Honest recommendation for this project:**
- Start with the basic `--rig` option we already have for testing.
- For real characters, use **AssetFurnace** or **SkinTokens** if you can set them up.
- Stay with **Rigify** if you want zero extra dependencies and full control.
