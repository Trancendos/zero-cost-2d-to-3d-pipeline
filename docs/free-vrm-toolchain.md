# Free VRM Toolchain (AAF Phase 3 notes)

Date: 2026-10-20. Zero-marginal-cost options for the interactive avatar path.

## Creation

| Tool | Type | Licence / cost | Notes |
|------|------|----------------|-------|
| VRoid Studio | Desktop app (pixiv) | Free | Most popular stylised humanoid VRM creator; exports VRM 0.x / 1.0 |
| CharacterStudio | Browser, open-source (MIT) | Free | Modular drag-and-drop VRM builder; export GLB/VRM |
| Free ready-made packs | Download | CC0 / public domain | Useful for runtime testing without generating anything |

## Conversion (after reconstruction + rigging)

| Tool | Type | Notes |
|------|------|-------|
| gltf2vrm | Browser, no install | Converts already-rigged GLB/glTF to VRM 0.x or 1.0 with bone + blend-shape mapping. Ideal post-SkinTokens or manual rig step |
| SoulFlame VRM Exporter | Free (VCC) | Converts VRChat avatars (Modular Avatar, PhysBones) to VRM |
| Browser FBX/GLB/Unity-package converters | Web tools | Some purely client-side; others credit-based |
| VMD to VRMA | Browser | Converts MMD motions to VRM animation files client-side |

## Runtime / interactive

| Tool | Type | Notes |
|------|------|-------|
| @pixiv/three-vrm | JS library | De-facto browser runtime; bones, blend-shapes, spring bones. Used by Amica-style chat demos |
| UniVRM | Unity | Reference implementation |
| godot-vrm | Godot | Free import/export |
| VRM4U | Unreal | Runtime loader |
| Blender VRM add-on | Blender | Import/export/edit |

## Recommended AAF Phase 3 path (zero marginal cost)

1. Reconstruction GLB (Phase 1, CPU TripoSR or experimental remote).
2. Rigging: SkinTokens on Kaggle P100 (only free >=14 GB route) or manual (VRoid / AccuRIG / Mixamo as fallback).
3. Deformation QA must pass before any `avatar` stage label.
4. Convert with gltf2vrm (browser).
5. Preview / interact with @pixiv/three-vrm inside AAF Studio or a minimal local page.

## Honest status

Guidance and research only. No claim that any of these tools have been executed or integrated in this repository. Live runs must be evidenced before updating Implementation Status.
