# VRM vs GLB – Clear Difference

| Feature | GLB | VRM |
|---------|-----|-----|
| **What it is** | Standard 3D model format (binary glTF) | Specialised avatar format built on top of glTF/GLB |
| **Main purpose** | General 3D assets (objects, scenes, props) | Humanoid characters / avatars for real-time use |
| **Skeleton & Skinning** | Supported | Required and standardised |
| **Blendshapes / Morphs** | Supported | Standardised for facial expressions and lip-sync |
| **First-person / VR features** | No | Yes (view, spring bones, etc.) |
| **Common use** | Games, web, Blender, general pipelines | VTubing, talking characters, VRChat, Amica, Three.js avatars |
| **Best for Cornelius** | Good intermediate format | **Final format** for talking AI character |

**Simple rule:**
- Use **GLB** while you are generating, cleaning and rigging.
- Convert the finished character to **VRM** when you want it to talk, lip-sync, and act as an interactive avatar.
