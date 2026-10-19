# Optional SkinTokens / TokenRig auto-rigging

This stage runs after mesh generation and cleanup. It does not replace or alter the default TripoSR path.

## Requirements
- Python 3.11+, compatible NVIDIA/CUDA/PyTorch/flash-attn setup as specified upstream.
- NVIDIA GPU with at least 14 GB total memory; this wrapper additionally requires 12 GB free by default.
- SkinTokens cloned at external/SkinTokens and dependencies installed according to the upstream README.
- Checkpoint experiments/articulation_xl_quantization_256_token_4/grpo_1400.ckpt; weights are not bundled.

## Usage
```bash
git submodule add https://github.com/VAST-AI-Research/SkinTokens.git external/SkinTokens
python scripts/hardware_gate.py
python scripts/rig_with_skintokens.py --input output/cleaned.glb --output output/cleaned_rigged.glb
```

Optional local LLM assistance (no cloud API):
```bash
ollama pull qwen2.5:3b
python scripts/rig_with_skintokens.py --input output/cleaned.glb --output output/cleaned_rigged.glb --llm-assist
```

Only loopback Ollama or LM Studio endpoints are accepted. The model can recommend bounded sampling values only; it cannot control paths, shell commands, checkpoint selection, post-processing, overwrite policy or the hardware gate. If it is unavailable, safe defaults are used.

The upstream demo supports input/output, model_ckpt, top_k, top_p, temperature, repetition_penalty, num_beams, use_transfer and use_postprocess. It exposes no seed argument, so seed handling is best-effort and does not guarantee deterministic GPU output.

The wrapper checks GLB 2.0 structure, skins, joint references, node-to-skin references and JOINTS_0/WEIGHTS_0 attributes. These structural checks do not prove deformation quality or non-zero accessor values. Inspect the result in Blender and run a deformation test.

The upstream repository declares MIT for its code. Checkpoint and dependency licensing must be verified separately; provenance records checkpoint licensing as pending.
