# AAF Phase 1 Advancement - Adaptive Core, Toolset and Roadmap

Date: 2026-10-19 (updated 2026-10-20 with TRELLIS.2 / VRM / low-VRAM research).
Package: AAF Adaptive Core v0.4.0.
Status: core logic implemented and 34/34 tests passed locally (sandboxed run, 2026-10-19); Windows helper scripts drafted, not yet executed on the target machine.

## Locked configuration

- Hardware: Windows PC without NVIDIA GPU - CPU-first local inference (expected profile: cpu-local).
- End-use: interactive AI 3D avatar characters. Phase 1 output is labelled "3D Reconstruction", never "Avatar", until rigging plus deformation-test evidence exists.
- Cost policy: $0.00 cloud spend. The correct wording is "zero-marginal-cost", never "free" - local hardware, electricity and maintenance are not free.
- Licence: Hunyuan3D 2.x is blocked for UK/EU territory (standing register item), enforced by the router.

## What this change adds

- aaf/adaptive-core/ - the Adaptive Core package (profiler, router, recovery, gates, provenance passport) with its 34-test suite.
- scripts/aaf_detect_hardware.ps1 - hardware detection writing the execution profile the router consumes.
- scripts/aaf_validate_gates.py - dual validation gate: official Khronos glTF Validator plus Trimesh mesh metrics, pass/review/fail verdicts.
- scripts/aaf_watchdog.ps1 - scheduled-task maintenance: temp cleanup and weights-snapshot integrity logging.
- docs/trellis2-low-vram-comfyui.md - practical low-VRAM guide for TRELLIS.2 in ComfyUI.
- docs/free-vrm-toolchain.md - free VRM creation, conversion and runtime options.

## Research basis (checked 2026-10-19 / 2026-10-20)

- Official Khronos glTF Validator is published as the npm package gltf-validator - no Docker needed for Gate 1.
- Kaggle Notebooks provide a weekly GPU quota of about 30 hours (P100 or 2x T4) - the best zero-cost rigging compute for Phase 3 (SkinTokens needs 14 GB+ VRAM).
- Google Colab free tier offers T4 GPUs with no published fixed allowance and idle termination - a dev accelerator only, never a Phase 1 dependency.
- SageMaker Studio Lab is closed to new signups (from 30 July 2026) - excluded.
- TripoSR runs on CPU, but slowly; the router uses a deliberately conservative 240 s planning estimate at 512 px until the smoke test measures the real duration.
- TRELLIS.2 (Microsoft, MIT) is the strongest open quality step-up. Official baseline is >=24 GB VRAM; community low-VRAM paths (ComfyUI --lowvram, sequential loading, 512 resolution, GGUF quantisation) can reach 6-12 GB with speed/quality trade-offs. No clean CPU fallback. Treat as experimental-remote only under the existing policy flag.
- Mixamo is free but stalled - manual Phase 3 fallback, never automated, never load-bearing.
- Free VRM path: VRoid Studio (creation), gltf2vrm (browser conversion), CharacterStudio (open modular builder), @pixiv/three-vrm (browser runtime).

## Roadmap

1. Phase 1 (this change plus machine work): run hardware detection, wire the core into aaf_api, run the end-to-end smoke test (real CPU inference, dual gates, provenance manifest, download hash check), record the real CPU duration and feed it back as the measured estimate.
2. Phase 2: duration telemetry (the router self-calibrates after 10 measured jobs); Kaggle GPU worker contract for speed; per-executor health memory; optional TRELLIS.2 experimental-remote executor behind policy flag.
3. Phase 3: SkinTokens auto-rig on Kaggle P100 (the only zero-cost 14 GB+ VRAM route), deformation QA suite, GLB-to-VRM conversion via gltf2vrm, interactive VRM preview with three-vrm.
4. Explicitly gated on new decisions: benchmark lab across approved models, adaptive provider ranking, voice/viseme extension.

## Honest status - what is and is not claimed

Claimed: the Adaptive Core logic and its 34/34 local test result; the research findings above with their sources; the drafting of the Windows toolset against the verified core contract; the low-VRAM and free VRM guidance documents.

Not claimed: any live inference, GPU run, cloud deployment, provider account connection, or that the Windows scripts have been executed anywhere. The scripts receive "implemented" status only after a successful run on the target machine, recorded verbatim. No step may report as passed if it was blocked or skipped.
