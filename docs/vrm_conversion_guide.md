# VRM Conversion Guide (Blender)

## Prerequisites
1. Install the official **VRM Add-on for Blender** (free):
   - https://vrm-addon-for-blender.info/en/
   - Or search "VRM" in Blender Preferences → Get Extensions / Add-ons

2. Enable the add-on in Blender Preferences.

## Step-by-Step Export to VRM

1. Open Blender.
2. Import your cleaned + rigged GLB:
   - File → Import → glTF 2.0 (.glb/.gltf)
3. Make sure the armature is selected and in a good rest pose (T-pose or A-pose preferred for most VRM tools).
4. Go to the **VRM** tab in the sidebar (press N if the sidebar is hidden).
5. Click **"Export VRM"** or use File → Export → VRM.
6. Important settings:
   - Choose humanoid bone mapping if prompted (the add-on can auto-detect many bones).
   - Enable spring bones if you want hair/coat physics later.
   - Export with materials and textures.
7. Save as `cornelius.vrm`.

## After Export
- Test the VRM in a viewer (e.g. https://vrm.dev/en/vrm-viewer or UniVRM in Unity).
- For talking characters, the VRM can now be loaded into Amica, AITuber Kit, Three.js + @pixiv/three-vrm, etc.
