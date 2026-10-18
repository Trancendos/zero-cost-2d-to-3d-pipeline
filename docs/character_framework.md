# Smart Character Framework (Inspired by Cornelius MacIntyre)

This framework turns the Cornelius workflow into a reusable, intelligent template system for any new character image.

## Core Principles
- **One folder per character**
- **Standardised files**: source image, personality, generation settings, notes
- **Automated pipeline script** that can be copied and adapted
- **Clear next-action guidance** after each stage
- **Humanoid-first** with graceful fallback for non-humanoids

## Recommended Folder Structure
```
characters/
  cornelius/
    source.png              # Original image
    personality.txt         # LLM system prompt
    run_pipeline.sh         # One-click generation
    README.md               # Character-specific notes
    output/                 # Generated meshes (git-ignored if large)
  _template/
    personality.txt.example
    run_pipeline.sh.example
    README.md.example
```

## Smart / Adaptive Behaviour Goals
When generating a new character the system should eventually:
1. Detect if the subject is humanoid / stylized / object
2. Choose appropriate resolution and post-processing
3. Suggest the best auto-rig path (SkinTokens vs Rigify vs basic)
4. Pre-fill a sensible personality if none is provided
5. Output both GLB (working) and guidance for VRM (final talking format)

## Current Status
- Cornelius is the first fully templated character
- The one-click script and personality file already follow this pattern
- Future work: auto-generate the character folder from a new image + short description
