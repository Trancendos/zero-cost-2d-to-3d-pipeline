import bpy
import sys
import os

# Get arguments after --
argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []

input_path = argv[0] if len(argv) > 0 else "input.glb"
output_path = argv[1] if len(argv) > 1 else "cleaned.glb"
do_rig = "--rig" in argv

print(f"Processing: {input_path} → {output_path}")

# Fresh scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Import
ext = os.path.splitext(input_path)[1].lower()
if ext in [".glb", ".gltf"]:
    bpy.ops.import_scene.gltf(filepath=input_path)
elif ext == ".obj":
    bpy.ops.wm.obj_import(filepath=input_path)
else:
    raise ValueError("Unsupported format")

obj = bpy.context.selected_objects[0]
bpy.context.view_layer.objects.active = obj
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Cleanup
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles(threshold=0.0001)
bpy.ops.mesh.dissolve_degenerate()
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

# Auto UV
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')

# Very basic armature
if do_rig:
    bpy.ops.object.armature_add(enter_editmode=False, location=obj.location)
    arm = bpy.context.active_object
    arm.name = "Armature"
    
    obj.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

# Export clean GLB
bpy.ops.export_scene.gltf(
    filepath=output_path,
    export_format='GLB',
    use_selection=False,
    export_apply=True
)

print(f"✅ Cleaned & exported: {output_path}")
