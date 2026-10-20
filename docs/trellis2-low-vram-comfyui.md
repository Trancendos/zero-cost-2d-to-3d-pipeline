# TRELLIS.2 Low-VRAM Guide for ComfyUI (AAF notes)

Date: 2026-10-20. Calibrated to AAF zero-marginal-cost / experimental-remote policy.

## VRAM reality

| Path | Typical VRAM | Notes |
|------|--------------|-------|
| Official Microsoft baseline | >= 24 GB | Full quality, high resolution (up to 1536), verified on A100/H100 |
| ComfyUI `--lowvram` + sequential loading | 8-12 GB (sometimes 6-8 GB) | Models loaded/unloaded stage-by-stage; 2-3x slower |
| Resolution 512 + low steps + colour-only texture | ~6-8 GB | Noticeable quality drop |
| GGUF quantised weights (Q4/Q8 community) | ~6-9 GB | Further quality/speed trade-off; not official weights |
| CPU fallback | None | TRELLIS.2 is CUDA-only; no clean CPU path |

For AAF locked hardware (Windows, no NVIDIA): TRELLIS.2 remains an **experimental-remote** candidate only. Use under the Adaptive Core policy flag `allowExperimentalRemoteGpu`.

## How to enable Low VRAM Mode

### 1. Launch flag (required)

```bash
python main.py --lowvram
```

Stronger variant (almost everything stays in system RAM until needed):

```bash
python main.py --novram
```

### 2. Node settings (in the web UI)

1. Click the main TRELLIS generation node.
2. Set **batch_size** = `1`.
3. Turn **Low VRAM Mode** / `low_vram` checkbox **ON**.
4. Set **Resolution** = `512` (or use an Image Scale node before the TRELLIS input).
5. Optionally lower texture resolution to 512 and sampling steps to 16-25.

### 3. Recommended settings by VRAM

**16 GB card**
- Launch: `--lowvram`
- Batch size: 1
- Resolution: 512 (try 768 only after confirming stability)
- Low VRAM Mode: On
- Texture resolution: 512
- Steps: 16-25

**8 GB or less**
- Launch: `--lowvram` or `--novram`
- Batch size: 1
- Resolution: 512 (or 384/256 if still OOM)
- Low VRAM Mode: On
- Texture resolution: 512 or lower
- Steps: 12-20
- Close all other GPU programs

## What batch size means

Batch size = how many items the model processes at once.  
Batch size 1 = one image/generation at a time (lowest memory).  
Higher values multiply VRAM use almost linearly. Always use 1 on cards under ~24 GB.

## What gradient checkpointing means

Normal mode stores every intermediate activation in VRAM (fast, memory-heavy).  
Gradient checkpointing discards most intermediates and recalculates them when needed (uses far less memory, a bit slower).  
It is turned on automatically by `--lowvram` and the node Low VRAM Mode checkbox.

## How to make the 2D input image smaller

**Option A (inside TRELLIS node):** set Resolution / Image Size to 512.  
**Option B (recommended):** add an `Image Scale` or `Image Resize` node, set Width/Height to 512, and connect it before the TRELLIS image input.

## Useful ComfyUI shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl + Enter | Queue prompt |
| Ctrl + Shift + Enter | Queue at front |
| Ctrl + S | Save workflow |
| Ctrl + O | Load workflow |
| Ctrl + A | Select all nodes |
| Delete / Backspace | Delete selected |
| Ctrl + C / V | Copy / paste |
| Ctrl + Z | Undo |
| Ctrl + M | Mute/unmute |
| Ctrl + B | Bypass |
| F | Fit view |
| Space (hold) | Pan |
| Ctrl + Mouse wheel | Zoom |
| Double-click empty canvas | Node search |

## Honest status

This document is guidance only. No claim is made that TRELLIS.2 has been run, measured, or integrated into the AAF control plane. Any live use must be recorded with evidence (duration, VRAM peak, output hashes) before the Adaptive Core planning estimates are updated.
