# Auto-rig integration catalogue

This is a capability catalogue, not a claim that every optional integration is installed or verified.

| Integration | Role | Default | Gate / caveat |
|---|---|---|---|
| SkinTokens / TokenRig | Primary optional mesh-to-skeleton-and-skin stage | Off until explicitly run | NVIDIA GPU, upstream dependencies and checkpoint required; check checkpoint licence separately |
| Ollama | Local LLM for conservative sampling suggestions | Off | Loopback endpoint only; output is schema-bounded; unavailable model falls back to fixed defaults |
| LM Studio | Alternative local OpenAI-compatible LLM endpoint | Off | Loopback endpoint only; no cloud API or secrets |
| Blender | Visual deformation, cleanup and manual repair | Manual QA | A structurally valid GLB can still deform badly |
| Khronos glTF Validator | Independent glTF conformance check | Optional external tool | Install/pin separately; not downloaded or executed automatically |
| UniRig | Alternative research auto-rig backend | Documented fallback only | Separate installation and CLI adapter required; not silently invoked |
| ComfyUI integrations | Optional graph-based workflow integration | Not embedded | Treat node packs as third-party dependencies; pin versions and review licences |
| AssetFurnace | External full character/animation workflow candidate | External evaluation only | Do not embed or depend on it until interface, licence and runtime are verified |

## Integration policy
1. Keep TripoSR generation and current Gradio tabs unchanged unless a separate reviewed change is approved.
2. Every backend must implement a narrow adapter contract: readiness check, supported formats, execution timeout, cancellation/cleanup, output path, provenance, and structured failure.
3. Never let an LLM produce shell commands, choose arbitrary paths, disable validation, change licence policy, or override the VRAM gate.
4. Hosted APIs remain disabled by default and require explicit cost, privacy, quota and licence controls.
5. Record model/checkpoint identifiers and their licence evidence separately from the wrapper's source-code licence.
6. Treat GLB parsing as an initial gate only; verify actual skin weights and test deformation in Blender before acceptance.
7. Use GPU-free mocked contract tests in pull requests; run real inference only in a separately labelled hardware acceptance job.
