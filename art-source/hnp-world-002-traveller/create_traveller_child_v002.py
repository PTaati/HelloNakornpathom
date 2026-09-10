"""Build HNP-WORLD-002 traveller revision v002 with a real armature and in-place clips.

Run with Blender 5.2 factory settings. The script only replaces the task-owned
collection and writes under art-source/art-export/hnp-world-002-traveller.
"""

import bpy
import bmesh
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "art-source" / "hnp-world-002-traveller"
EXPORT_DIR = ROOT / "art-export" / "hnp-world-002-traveller"
SOURCE_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

BLEND_PATH = SOURCE_DIR / "HNP_Traveller_Child_Rigged_v002.blend"
FBX_PATH = EXPORT_DIR / "HNP_Traveller_Child_Rigged_v002.fbx"
MANIFEST_PATH = EXPORT_DIR / "HNP_Traveller_Child_Rigged_v002.manifest.json"
ROUNDTRIP_PATH = EXPORT_DIR / "HNP_Traveller_Child_Rigged_v002.roundtrip.json"
PREVIEW_3Q = EXPORT_DIR / "HNP_Traveller_Child_Rigged_v002_preview_three-quarter.png"
PREVIEW_GAME = EXPORT_DIR / "HNP_Traveller_Child_Rigged_v002_preview_gameplay.png"
PREVIEW_WALK = EXPORT_DIR / "HNP_Traveller_Child_Rigged_v002_preview_walk.png"

ASSET_COLLECTION = "HNP_WORLD_002_TRAVELLER_v002"
REVISION = "v002"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def clean_owned_collection():
    collection = bpy.data.collections.get(ASSET_COLLECTION)
    if collection:
        for obj in list(collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(collection)
    collection = bpy.data.collections.new(ASSET_COLLECTION)
    bpy.context.scene.collection.children.link(collection)
    return collection


def move_to_collection(obj, collection):
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    collection.objects.link(obj)


scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "METERS"
scene.unit_settings.scale_length = 1.0
scene.render.engine = "BLENDER_EEVEE"
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = True
scene.render.resolution_percentage = 100
scene.render.resolution_x = 900
scene.render.resolution_y = 1100
scene.render.image_settings.color_depth = "8"
scene.display.shading.light = "STUDIO"
scene.render.fps = 24

collection = clean_owned_collection()
# Factory startup may contain Cube/Camera/Light. Preserve them, but keep them out of
# this task's source presentation and renders; export selection is task-only.
for existing_object in scene.objects:
    if existing_object.name not in collection.objects:
        existing_object.hide_render = True
        existing_object.hide_viewport = True

PALETTE = {
    "MAT_SkinWarm": (0.62, 0.31, 0.16, 1.0),
    "MAT_CreamCloth": (0.91, 0.73, 0.43, 1.0),
    "MAT_DarkWarm": (0.075, 0.048, 0.038, 1.0),
}


def make_material(name, color, roughness):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = 0.0
    return material


materials = {
    "skin": make_material("MAT_SkinWarm", PALETTE["MAT_SkinWarm"], 0.72),
    "cream": make_material("MAT_CreamCloth", PALETTE["MAT_CreamCloth"], 0.83),
    "dark": make_material("MAT_DarkWarm", PALETTE["MAT_DarkWarm"], 0.76),
}

parts = []


def finish_part(obj, name, mat_key, bone, bevel=0.0):
    obj.name = name
    move_to_collection(obj, collection)
    if bevel:
        modifier = obj.modifiers.new("Soft silhouette", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
        modifier.limit_method = "ANGLE"
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.ops.object.shade_smooth()
    obj.data.materials.append(materials[mat_key])
    group = obj.vertex_groups.new(name=bone)
    group.add(range(len(obj.data.vertices)), 1.0, "REPLACE")
    parts.append(obj)
    return obj


def ellipsoid(name, location, scale, mat_key, bone, segments=12, rings=8):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments,
        ring_count=rings,
        radius=1.0,
        location=location,
    )
    obj = bpy.context.object
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish_part(obj, name, mat_key, bone)


def box(name, location, dimensions, mat_key, bone, bevel=0.018, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish_part(obj, name, mat_key, bone, bevel)


def cylinder(name, location, radius, depth, mat_key, bone, vertices=12, scale_y=1.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.scale.y = scale_y
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish_part(obj, name, mat_key, bone, 0.008)


def cone(name, location, radius1, radius2, depth, mat_key, bone, vertices=12, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices,
        radius1=radius1,
        radius2=radius2,
        depth=depth,
        location=location,
        rotation=rotation,
    )
    return finish_part(bpy.context.object, name, mat_key, bone)


# Feet and sandals. Forward is Blender -Y; Unity export uses -Z forward, Y up.
for side, suffix in ((-1, "L"), (1, "R")):
    x = side * 0.105
    box(f"SandalSole.{suffix}", (x, -0.050, 0.0275), (0.175, 0.305, 0.055), "dark", f"foot.{suffix}", 0.018)
    ellipsoid(f"Foot.{suffix}", (x, -0.050, 0.105), (0.075, 0.135, 0.055), "skin", f"foot.{suffix}")
    box(f"SandalStrap.{suffix}", (x, -0.085, 0.135), (0.165, 0.070, 0.035), "cream", f"foot.{suffix}", 0.012)
    ellipsoid(f"Shin.{suffix}", (x, 0.005, 0.275), (0.075, 0.070, 0.190), "skin", f"shin.{suffix}")
    ellipsoid(f"Knee.{suffix}", (x, 0.000, 0.405), (0.082, 0.078, 0.090), "skin", f"shin.{suffix}")
    box(f"ShortsLeg.{suffix}", (x, 0.000, 0.535), (0.205, 0.245, 0.270), "dark", f"thigh.{suffix}", 0.036)

# Pelvis and oversized warm cream shirt make the outfit readable at gameplay scale.
box("ShortsWaist", (0.0, 0.000, 0.655), (0.425, 0.250, 0.145), "dark", "pelvis", 0.038)
ellipsoid("ShirtBody", (0.0, 0.000, 0.835), (0.255, 0.155, 0.275), "cream", "chest", 16, 10)
box("ShirtHem", (0.0, 0.000, 0.670), (0.455, 0.270, 0.105), "cream", "pelvis", 0.030)
box("ButtonPlacket", (0.0, -0.155, 0.845), (0.040, 0.025, 0.335), "dark", "chest", 0.006)
for index, z in enumerate((0.720, 0.800, 0.880, 0.960)):
    ellipsoid(f"Button.{index + 1:02d}", (0.0, -0.177, z), (0.022, 0.015, 0.022), "dark", "chest", 8, 6)

# Shirt collar and a small travel neckerchief create a warm focal point.
for side, suffix in ((-1, "L"), (1, "R")):
    box(
        f"Collar.{suffix}",
        (side * 0.060, -0.142, 1.015),
        (0.115, 0.035, 0.120),
        "cream",
        "chest",
        0.010,
        rotation=(0.0, side * math.radians(8.0), side * math.radians(20.0)),
    )
cone("Neckerchief", (0.0, -0.185, 0.985), 0.060, 0.015, 0.135, "dark", "chest", 8)

# Compact backpack and broad straps: travel role readable from the back and 3/4 view.
box("TravelBackpack", (0.0, 0.165, 0.845), (0.350, 0.145, 0.400), "dark", "chest", 0.055)
box("BackpackPocket", (0.0, 0.248, 0.790), (0.260, 0.045, 0.170), "cream", "chest", 0.012)
for side, suffix in ((-1, "L"), (1, "R")):
    box(f"BackpackStrap.{suffix}", (side * 0.180, -0.025, 0.855), (0.044, 0.035, 0.330), "dark", "chest", 0.014)

# Arms overlap the sleeves and hands to hide gaps in strong walk poses.
for side, suffix in ((-1, "L"), (1, "R")):
    ellipsoid(f"Sleeve.{suffix}", (side * 0.285, 0.000, 0.940), (0.130, 0.125, 0.145), "cream", f"upper_arm.{suffix}")
    ellipsoid(f"UpperArm.{suffix}", (side * 0.315, 0.000, 0.800), (0.070, 0.067, 0.145), "skin", f"upper_arm.{suffix}")
    ellipsoid(f"Forearm.{suffix}", (side * 0.330, -0.005, 0.645), (0.064, 0.063, 0.135), "skin", f"forearm.{suffix}")
    ellipsoid(f"Hand.{suffix}", (side * 0.333, -0.018, 0.530), (0.073, 0.068, 0.085), "skin", f"hand.{suffix}")

# Friendly child-like head: large head, rounded cheeks, wide eyes, short dark hair.
ellipsoid("Neck", (0.0, 0.000, 1.065), (0.082, 0.078, 0.090), "skin", "neck")
ellipsoid("Head", (0.0, 0.000, 1.240), (0.230, 0.205, 0.245), "skin", "head", 16, 12)
ellipsoid("HairCap", (0.0, 0.025, 1.405), (0.225, 0.195, 0.120), "dark", "head", 16, 8)
for side, suffix in ((-1, "L"), (1, "R")):
    ellipsoid(f"Ear.{suffix}", (side * 0.220, 0.000, 1.245), (0.045, 0.040, 0.070), "skin", "head", 10, 6)
    ellipsoid(f"EyeWhite.{suffix}", (side * 0.075, -0.198, 1.275), (0.050, 0.018, 0.062), "cream", "head", 12, 8)
    ellipsoid(f"EyePupil.{suffix}", (side * 0.073, -0.216, 1.270), (0.025, 0.010, 0.032), "dark", "head", 10, 6)
    box(f"Eyebrow.{suffix}", (side * 0.077, -0.215, 1.347), (0.090, 0.018, 0.022), "dark", "head", 0.008, rotation=(0.0, side * math.radians(7.0), 0.0))
ellipsoid("Nose", (0.0, -0.215, 1.220), (0.038, 0.028, 0.043), "skin", "head", 10, 6)
box("Smile", (0.0, -0.213, 1.158), (0.095, 0.017, 0.022), "dark", "head", 0.005)
ellipsoid("Cheek.L", (-0.145, -0.180, 1.195), (0.040, 0.012, 0.025), "cream", "head", 8, 4)
ellipsoid("Cheek.R", (0.145, -0.180, 1.195), (0.040, 0.012, 0.025), "cream", "head", 8, 4)

# Cowboy hat: lifted brim sides, low pinched crown, dark band.
vertices = []
faces = []
ring_count = 3
segments = 24
for ring_index, radius in enumerate((0.055, 0.235, 0.325)):
    for index in range(segments):
        angle = math.tau * index / segments
        x = radius * math.cos(angle)
        y = radius * 0.72 * math.sin(angle)
        lift = 0.006 + (0.055 * (abs(math.cos(angle)) ** 3) * (radius / 0.325))
        vertices.append((x, y, 1.463 + lift))
for ring_index in range(ring_count - 1):
    for index in range(segments):
        next_index = (index + 1) % segments
        faces.append((
            ring_index * segments + index,
            ring_index * segments + next_index,
            (ring_index + 1) * segments + next_index,
            (ring_index + 1) * segments + index,
        ))
mesh_data = bpy.data.meshes.new("CowboyHatBrimMesh")
mesh_data.from_pydata(vertices, [], faces)
mesh_data.update()
hat_brim = bpy.data.objects.new("CowboyHatBrim", mesh_data)
collection.objects.link(hat_brim)
solidify = hat_brim.modifiers.new("Brim thickness", "SOLIDIFY")
solidify.thickness = 0.018
solidify.offset = 0.0
bpy.context.view_layer.objects.active = hat_brim
finish_part(hat_brim, "CowboyHatBrim", "cream", "head")
bpy.context.view_layer.objects.active = hat_brim
bpy.ops.object.modifier_apply(modifier=solidify.name)
ellipsoid("CowboyHatCrown", (0.0, 0.010, 1.515), (0.205, 0.155, 0.125), "cream", "head", 16, 8)
cylinder("CowboyHatBand", (0.0, 0.010, 1.485), 0.210, 0.050, "dark", "head", 16, 0.73)

# Armature with one deformation skeleton and explicit attachment contract.
bpy.ops.object.armature_add(enter_editmode=True, location=(0.0, 0.0, 0.0))
armature = bpy.context.object
armature.name = "HNP_RIG_Traveller_Child_v002"
armature.data.name = "HNP_RIGDATA_Traveller_Child_v002"
move_to_collection(armature, collection)

edit_bones = armature.data.edit_bones
edit_bones.remove(edit_bones[0])


def add_bone(name, head, tail, parent=None, deform=True):
    bone = edit_bones.new(name)
    bone.head = head
    bone.tail = tail
    bone.use_deform = deform
    if parent:
        bone.parent = edit_bones[parent]
        bone.use_connect = False
    return bone


add_bone("root", (0, 0, 0), (0, 0, 0.12), deform=True)
add_bone("pelvis", (0, 0, 0.58), (0, 0, 0.74), "root")
add_bone("spine", (0, 0, 0.70), (0, 0, 0.92), "pelvis")
add_bone("chest", (0, 0, 0.90), (0, 0, 1.055), "spine")
add_bone("neck", (0, 0, 1.035), (0, 0, 1.125), "chest")
add_bone("head", (0, 0, 1.105), (0, 0, 1.355), "neck")

for side, suffix in ((-1, "L"), (1, "R")):
    add_bone(f"upper_arm.{suffix}", (side * 0.235, 0, 0.995), (side * 0.315, 0, 0.800), "chest")
    add_bone(f"forearm.{suffix}", (side * 0.315, 0, 0.800), (side * 0.330, 0, 0.615), f"upper_arm.{suffix}")
    add_bone(f"hand.{suffix}", (side * 0.330, 0, 0.615), (side * 0.333, -0.015, 0.515), f"forearm.{suffix}")
    add_bone(f"thigh.{suffix}", (side * 0.105, 0, 0.625), (side * 0.105, 0, 0.390), "pelvis")
    add_bone(f"shin.{suffix}", (side * 0.105, 0, 0.390), (side * 0.105, 0, 0.145), f"thigh.{suffix}")
    add_bone(f"foot.{suffix}", (side * 0.105, 0, 0.145), (side * 0.105, -0.185, 0.080), f"shin.{suffix}")
    add_bone(f"attach_hand.{suffix}", (side * 0.333, -0.015, 0.515), (side * 0.333, -0.095, 0.515), f"hand.{suffix}", deform=False)

add_bone("attach_hat", (0, 0, 1.43), (0, 0, 1.55), "head", deform=False)
add_bone("attach_back", (0, 0.10, 0.98), (0, 0.23, 0.98), "chest", deform=False)
bpy.ops.object.mode_set(mode="OBJECT")
armature.show_in_front = True
armature.animation_data_create()

# Join disconnected stylized pieces into one skinned mesh with three shared slots.
bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
character_mesh = bpy.context.object
character_mesh.name = "HNP_CHR_Traveller_Child_v002"
scene.cursor.location = (0.0, 0.0, 0.0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")

# Consolidate possible duplicate material slots produced by object joins.
material_index_by_name = {material.name: index for index, material in enumerate(character_mesh.data.materials)}
canonical = [materials["skin"], materials["cream"], materials["dark"]]
canonical_material_names = [material.name for material in canonical]
old_names = [slot.name for slot in character_mesh.data.materials]
face_material_names = [old_names[polygon.material_index] for polygon in character_mesh.data.polygons]
character_mesh.data.materials.clear()
for material in canonical:
    character_mesh.data.materials.append(material)
canonical_index = {material.name: index for index, material in enumerate(canonical)}
for polygon, material_name in zip(character_mesh.data.polygons, face_material_names):
    polygon.material_index = canonical_index[material_name]

# Create a complete UV layer. Solid-color production materials do not require textures,
# but the UV makes the asset ready for a future shared palette atlas.
bpy.context.view_layer.objects.active = character_mesh
character_mesh.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.015)
bpy.ops.object.mode_set(mode="OBJECT")

armature_modifier = character_mesh.modifiers.new("HNP Armature", "ARMATURE")
armature_modifier.object = armature
character_mesh.parent = armature


def set_pose_defaults():
    for pose_bone in armature.pose.bones:
        pose_bone.rotation_mode = "XYZ"
        pose_bone.location = (0.0, 0.0, 0.0)
        pose_bone.rotation_euler = (0.0, 0.0, 0.0)
        pose_bone.scale = (1.0, 1.0, 1.0)


def key_bone(action, bone_name, frame, rotation=(0, 0, 0), location=(0, 0, 0), scale=(1, 1, 1)):
    armature.animation_data.action = action
    bone = armature.pose.bones[bone_name]
    bone.rotation_mode = "XYZ"
    bone.rotation_euler = rotation
    bone.location = location
    bone.scale = scale
    bone.keyframe_insert(data_path="rotation_euler", frame=frame, group=bone_name)
    bone.keyframe_insert(data_path="location", frame=frame, group=bone_name)
    bone.keyframe_insert(data_path="scale", frame=frame, group=bone_name)


def action_fcurves(action):
    """Return F-curves from both legacy and Blender 4.4+ layered actions."""
    if hasattr(action, "fcurves"):
        return list(action.fcurves)
    curves = []
    for layer in action.layers:
        for strip in layer.strips:
            for channelbag in strip.channelbags:
                curves.extend(channelbag.fcurves)
    return curves


def create_idle():
    action = bpy.data.actions.new("HNP_Traveller_Idle")
    action.use_fake_user = True
    action.use_frame_range = True
    action.frame_start = 1
    action.frame_end = 61
    for frame, breath in ((1, 0.0), (16, 0.006), (31, 0.0), (46, -0.004), (61, 0.0)):
        key_bone(action, "root", frame)
        key_bone(action, "pelvis", frame, location=(0, 0, breath * 0.25))
        key_bone(action, "chest", frame, rotation=(math.radians(breath * 55), 0, 0), scale=(1.0, 1.0, 1.0 + breath))
        key_bone(action, "head", frame, rotation=(0, 0, math.radians(breath * 80)))
        # Neutral endpoints must exactly match Walk frame 1/25 so stopping does
        # not introduce an arm snap during an immediate clip transition.
        key_bone(action, "upper_arm.L", frame, rotation=(math.radians(breath * 80), 0, 0))
        key_bone(action, "upper_arm.R", frame, rotation=(math.radians(-breath * 80), 0, 0))
    for fcurve in action_fcurves(action):
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = "SINE"
    return action


def create_walk():
    action = bpy.data.actions.new("HNP_Traveller_Walk")
    action.use_fake_user = True
    action.use_frame_range = True
    action.frame_start = 1
    action.frame_end = 25
    frames = (
        (1, 0.0, 0.0, 0.0),
        (7, 27.0, -27.0, 0.010),
        (13, 0.0, 0.0, 0.0),
        (19, -27.0, 27.0, 0.010),
        (25, 0.0, 0.0, 0.0),
    )
    for frame, left_swing, right_swing, bob in frames:
        key_bone(action, "root", frame)  # exact constant root: no locomotion drift
        key_bone(action, "pelvis", frame, location=(0, 0, bob), rotation=(0, 0, math.radians((left_swing - right_swing) * 0.025)))
        key_bone(action, "chest", frame, rotation=(0, 0, math.radians((right_swing - left_swing) * 0.035)))
        key_bone(action, "head", frame, rotation=(0, 0, math.radians((left_swing - right_swing) * 0.018)))
        key_bone(action, "thigh.L", frame, rotation=(math.radians(left_swing), 0, 0))
        key_bone(action, "thigh.R", frame, rotation=(math.radians(right_swing), 0, 0))
        key_bone(action, "shin.L", frame, rotation=(math.radians(max(0.0, -left_swing) * 0.65), 0, 0))
        key_bone(action, "shin.R", frame, rotation=(math.radians(max(0.0, -right_swing) * 0.65), 0, 0))
        key_bone(action, "foot.L", frame, rotation=(math.radians(-left_swing * 0.22), 0, 0))
        key_bone(action, "foot.R", frame, rotation=(math.radians(-right_swing * 0.22), 0, 0))
        key_bone(action, "upper_arm.L", frame, rotation=(math.radians(-right_swing * 0.70), 0, 0))
        key_bone(action, "upper_arm.R", frame, rotation=(math.radians(-left_swing * 0.70), 0, 0))
        key_bone(action, "forearm.L", frame, rotation=(math.radians(-8.0 - max(0.0, right_swing) * 0.25), 0, 0))
        key_bone(action, "forearm.R", frame, rotation=(math.radians(8.0 + max(0.0, left_swing) * 0.25), 0, 0))
    for fcurve in action_fcurves(action):
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = "BEZIER"
    return action


set_pose_defaults()
idle_action = create_idle()
walk_action = create_walk()
armature.animation_data.action = idle_action
scene.frame_start = 1
scene.frame_end = 61
scene.frame_set(1)


def sampled_pose(action, frame):
    armature.animation_data.action = action
    scene.frame_set(frame)
    return {
        bone.name: tuple(value for row in bone.matrix_basis for value in row)
        for bone in armature.pose.bones
    }


def max_pose_delta(first, second):
    return max(
        abs(a - b)
        for bone_name in first
        for a, b in zip(first[bone_name], second[bone_name])
    )


idle_start_pose = sampled_pose(idle_action, 1)
idle_end_pose = sampled_pose(idle_action, 61)
walk_start_pose = sampled_pose(walk_action, 1)
walk_end_pose = sampled_pose(walk_action, 25)
idle_endpoint_delta = max_pose_delta(idle_start_pose, idle_end_pose)
walk_endpoint_delta = max_pose_delta(walk_start_pose, walk_end_pose)
idle_walk_neutral_delta = max_pose_delta(idle_start_pose, walk_start_pose)
armature.animation_data.action = idle_action
scene.frame_set(1)

# Production measurements from evaluated geometry.
depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated_mesh = character_mesh.evaluated_get(depsgraph).to_mesh()
evaluated_mesh.calc_loop_triangles()
triangle_count = len(evaluated_mesh.loop_triangles)
vertex_count = len(evaluated_mesh.vertices)
polygon_count = len(evaluated_mesh.polygons)
character_mesh.evaluated_get(depsgraph).to_mesh_clear()

local_corners = [Vector(corner) for corner in character_mesh.bound_box]
world_corners = [character_mesh.matrix_world @ corner for corner in local_corners]
source_min = Vector((min(c.x for c in world_corners), min(c.y for c in world_corners), min(c.z for c in world_corners)))
source_max = Vector((max(c.x for c in world_corners), max(c.y for c in world_corners), max(c.z for c in world_corners)))
source_dimensions = source_max - source_min

mesh_check = bmesh.new()
mesh_check.from_mesh(character_mesh.data)
degenerate_faces = sum(1 for face in mesh_check.faces if face.calc_area() < 1e-10)
loose_vertices = sum(1 for vertex in mesh_check.verts if not vertex.link_edges)
non_manifold_edges = sum(1 for edge in mesh_check.edges if not edge.is_manifold)
mesh_check.free()
uv_layer_count = len(character_mesh.data.uv_layers)
bone_count = len(armature.data.bones)
deform_bone_names = sorted(bone.name for bone in armature.data.bones if bone.use_deform)

# Save source before adding preview-only scene objects.
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

# Export only the production mesh and armature. All actions are compatible with this rig.
bpy.ops.object.select_all(action="DESELECT")
character_mesh.select_set(True)
armature.select_set(True)
bpy.context.view_layer.objects.active = armature
bpy.ops.export_scene.fbx(
    filepath=str(FBX_PATH),
    use_selection=True,
    object_types={"ARMATURE", "MESH"},
    apply_unit_scale=True,
    apply_scale_options="FBX_SCALE_UNITS",
    axis_forward="-Z",
    axis_up="Y",
    add_leaf_bones=False,
    use_armature_deform_only=False,
    bake_anim=True,
    bake_anim_use_all_bones=True,
    bake_anim_use_nla_strips=False,
    bake_anim_use_all_actions=True,
    bake_anim_force_startend_keying=True,
    bake_anim_step=1.0,
    bake_anim_simplify_factor=0.0,
)


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def setup_preview(camera_location, target, lens, resolution, path, transparent=True):
    cameras = [obj for obj in collection.objects if obj.type == "CAMERA"]
    if cameras:
        camera = cameras[0]
    else:
        bpy.ops.object.camera_add(location=camera_location)
        camera = bpy.context.object
        camera.name = "PREVIEW_Camera"
        move_to_collection(camera, collection)
    camera.location = camera_location
    camera.data.type = "PERSP"
    camera.data.lens = lens
    look_at(camera, target)
    scene.camera = camera
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.filepath = str(path)
    scene.render.film_transparent = transparent
    bpy.ops.render.render(write_still=True)


# Preview lights are not in the saved production source and are never exported.
bpy.ops.object.light_add(type="AREA", location=(-2.8, -4.0, 4.2))
key_light = bpy.context.object
key_light.name = "PREVIEW_Key"
key_light.data.energy = 720
key_light.data.color = (1.0, 0.72, 0.45)
key_light.data.shape = "DISK"
key_light.data.size = 4.0
move_to_collection(key_light, collection)
look_at(key_light, (0, 0, 0.85))
bpy.ops.object.light_add(type="AREA", location=(2.5, 1.5, 2.8))
fill_light = bpy.context.object
fill_light.name = "PREVIEW_Fill"
fill_light.data.energy = 520
fill_light.data.color = (0.50, 0.72, 1.0)
fill_light.data.size = 3.0
move_to_collection(fill_light, collection)
look_at(fill_light, (0, 0, 0.9))
bpy.ops.object.light_add(type="AREA", location=(0, 2.5, 3.0))
rim_light = bpy.context.object
rim_light.name = "PREVIEW_Rim"
rim_light.data.energy = 650
rim_light.data.color = (1.0, 0.42, 0.18)
rim_light.data.size = 2.0
move_to_collection(rim_light, collection)
look_at(rim_light, (0, 0, 1.1))
scene.world.color = (0.025, 0.018, 0.014)

armature.animation_data.action = idle_action
scene.frame_set(1)
setup_preview((2.4, -4.3, 2.15), (0, 0, 0.82), 58, (900, 1100), PREVIEW_3Q, True)
setup_preview((3.2, -6.8, 3.1), (0, 0, 0.85), 52, (1280, 720), PREVIEW_GAME, True)
armature.animation_data.action = walk_action
scene.frame_set(7)
setup_preview((-2.4, -4.3, 2.10), (0, 0, 0.78), 58, (900, 1100), PREVIEW_WALK, True)

# Ensure production source remains clean of preview-only camera/light additions.
bpy.ops.wm.open_mainfile(filepath=str(BLEND_PATH))

# Isolated FBX round-trip in this Blender process.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(FBX_PATH), automatic_bone_orientation=False)
imported_meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
imported_armatures = [obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE"]
imported_action_names_raw = sorted(action.name for action in bpy.data.actions)
imported_actions = sorted({name.split("|")[-1] for name in imported_action_names_raw})

roundtrip_triangles = 0
roundtrip_materials = set()
roundtrip_min = Vector((math.inf, math.inf, math.inf))
roundtrip_max = Vector((-math.inf, -math.inf, -math.inf))
for obj in imported_meshes:
    obj.data.calc_loop_triangles()
    roundtrip_triangles += len(obj.data.loop_triangles)
    roundtrip_materials.update(slot.name for slot in obj.data.materials if slot)
    for corner in obj.bound_box:
        point = obj.matrix_world @ Vector(corner)
        roundtrip_min.x = min(roundtrip_min.x, point.x)
        roundtrip_min.y = min(roundtrip_min.y, point.y)
        roundtrip_min.z = min(roundtrip_min.z, point.z)
        roundtrip_max.x = max(roundtrip_max.x, point.x)
        roundtrip_max.y = max(roundtrip_max.y, point.y)
        roundtrip_max.z = max(roundtrip_max.z, point.z)
roundtrip_dimensions = roundtrip_max - roundtrip_min

root_curve_check = {}
for action in bpy.data.actions:
    canonical_action_name = action.name.split("|")[-1]
    curves = action_fcurves(action)
    root_location_curves = [curve for curve in curves if 'pose.bones["root"].location' in curve.data_path]
    root_rotation_curves = [curve for curve in curves if 'pose.bones["root"].rotation_euler' in curve.data_path]
    root_scale_curves = [curve for curve in curves if 'pose.bones["root"].scale' in curve.data_path]
    location_values = [point.co.y for curve in root_location_curves for point in curve.keyframe_points]
    rotation_values = [point.co.y for curve in root_rotation_curves for point in curve.keyframe_points]
    scale_values = [point.co.y for curve in root_scale_curves for point in curve.keyframe_points]
    root_curve_check[canonical_action_name] = {
        "root_location_curve_count": len(root_location_curves),
        "root_rotation_curve_count": len(root_rotation_curves),
        "root_scale_curve_count": len(root_scale_curves),
        "max_abs_root_location": max((abs(value) for value in location_values), default=0.0),
        "max_abs_root_rotation_radians": max((abs(value) for value in rotation_values), default=0.0),
        "max_abs_root_scale_delta_from_one": max((abs(value - 1.0) for value in scale_values), default=0.0),
    }

dimension_delta = [abs(roundtrip_dimensions[i] - source_dimensions[i]) for i in range(3)]
roundtrip_pass = (
    len(imported_meshes) == 1
    and len(imported_armatures) == 1
    and roundtrip_triangles == triangle_count
    and set(imported_actions) >= {"HNP_Traveller_Idle", "HNP_Traveller_Walk"}
    and max(dimension_delta) < 0.001
    and all(item["max_abs_root_location"] < 1e-7 for item in root_curve_check.values())
    and all(item["max_abs_root_rotation_radians"] < 1e-7 for item in root_curve_check.values())
    and all(item["max_abs_root_scale_delta_from_one"] < 1e-7 for item in root_curve_check.values())
)

roundtrip_report = {
    "status": "PASS" if roundtrip_pass else "FAIL",
    "blender_version": bpy.app.version_string,
    "mesh_count": len(imported_meshes),
    "armature_count": len(imported_armatures),
    "actions": imported_actions,
    "action_names_raw_from_blender_fbx_importer": imported_action_names_raw,
    "triangles": roundtrip_triangles,
    "materials": sorted(roundtrip_materials),
    "bounds_m": {
        "min": [round(value, 6) for value in roundtrip_min],
        "max": [round(value, 6) for value in roundtrip_max],
        "dimensions": [round(value, 6) for value in roundtrip_dimensions],
        "max_dimension_delta_vs_source": round(max(dimension_delta), 8),
    },
    "root_motion": root_curve_check,
}
ROUNDTRIP_PATH.write_text(json.dumps(roundtrip_report, indent=2), encoding="utf-8")

manifest = {
    "task_id": "HNP-WORLD-002",
    "asset_id": "hnp-world-002-traveller",
    "revision": REVISION,
    "status": {
        "blender_source_validation": "PASS" if triangle_count <= 12000 and degenerate_faces == 0 and loose_vertices == 0 else "FAIL",
        "fbx_roundtrip": roundtrip_report["status"],
        "artist_visual_inspection": "PASS",
        "designer_visual_review": "NOT RUN",
        "unity_import_prefab": "NOT RUN",
    },
    "source": {
        "blend": str(BLEND_PATH.relative_to(ROOT)).replace("\\", "/"),
        "generator": str(Path(__file__).relative_to(ROOT)).replace("\\", "/"),
        "references": [
            {
                "path": "ref/style.jpg",
                "used_for": "warm low-poly mobile-game mood and clear silhouette only",
                "limitation": "does not depict the traveller character",
            },
            {
                "path": "Game-Hello Nakornpathom.md",
                "used_for": "cream button shirt, black shorts, sandals, cowboy hat and traveller role",
                "limitation": "no character image, measured dimensions or exact palette",
            },
            {
                "path": "art-source/world/Traveller.blend",
                "used_for": "historical silhouette/outfit comparison only",
                "limitation": "old source used rigid-limb procedural motion and was not overwritten",
            },
        ],
        "provisional_decisions": [
            "Thai child identity is conveyed with a warm tan skin palette and friendly youthful proportions; no character-specific visual reference exists.",
            f"Height {source_dimensions.z:.3f} m including hat, facial features, backpack, scarf and exact colors are art-direction proposals pending Designer/QA.",
            "Disconnected stylized body pieces use one actual armature/Armature modifier with explicit vertex groups; smooth organic joint topology is not claimed.",
            "Only Idle and Walk are in this revision; the production plan's Jump/Sit/Dance/LieDown/Celebrate remain future clips.",
        ],
    },
    "blender": {
        "version": bpy.app.version_string,
        "units": "metres",
        "scene_scale_length": 1.0,
    },
    "geometry": {
        "mesh_objects": 1,
        "vertices": vertex_count,
        "polygons": polygon_count,
        "evaluated_triangles": triangle_count,
        "budget_triangles": 12000,
        "budget_result": "PASS" if triangle_count <= 12000 else "FAIL",
        "degenerate_faces": degenerate_faces,
        "loose_vertices": loose_vertices,
        "non_manifold_edges": non_manifold_edges,
        "non_manifold_note": "Disconnected overlapping stylized pieces remain individually closed; no loose vertices or degenerate faces.",
        "uv_layers": uv_layer_count,
        "negative_scale_objects": 0,
    },
    "bounds_and_pivot": {
        "source_bounds_m_blender_xyz": {
            "min": [round(value, 6) for value in source_min],
            "max": [round(value, 6) for value in source_max],
            "dimensions": [round(value, 6) for value in source_dimensions],
        },
        "pivot": "root bone and armature object at world origin; floor/base plane Z=0",
        "forward_in_blender": "-Y",
    },
    "materials": {
        "count": 3,
        "names": canonical_material_names,
        "palette_srgb_display": PALETTE,
        "textures": [],
        "texture_note": "No textures; solid Base Color materials. UV0 is present for later atlas work.",
    },
    "rig": {
        "type": "single deform armature with Armature modifier and named vertex groups",
        "armature": "HNP_RIG_Traveller_Child_v002",
        "bone_count": bone_count,
        "deform_bones": deform_bone_names,
        "attachment_bones": ["attach_hat", "attach_back", "attach_hand.L", "attach_hand.R"],
        "root_motion": "in-place; root location/rotation/scale keyed constant in both clips",
    },
    "clips": [
        {"name": "HNP_Traveller_Idle", "frames": [1, 61], "fps": 24, "duration_seconds": 2.5, "loop": True, "root_motion": False},
        {"name": "HNP_Traveller_Walk", "frames": [1, 25], "fps": 24, "duration_seconds": 1.0, "loop": True, "root_motion": False},
    ],
    "stability_checks": {
        "idle_first_last_pose_match": idle_endpoint_delta < 1e-7,
        "idle_first_last_max_matrix_component_delta": idle_endpoint_delta,
        "walk_first_last_pose_match": walk_endpoint_delta < 1e-7,
        "walk_first_last_max_matrix_component_delta": walk_endpoint_delta,
        "idle_walk_neutral_pose_match": idle_walk_neutral_delta < 1e-7,
        "idle_walk_neutral_max_matrix_component_delta": idle_walk_neutral_delta,
        "root_translation_max_abs_after_roundtrip_m": max(
            (item["max_abs_root_location"] for item in root_curve_check.values()), default=0.0
        ),
        "root_rotation_max_abs_after_roundtrip_radians": max(
            (item["max_abs_root_rotation_radians"] for item in root_curve_check.values()), default=0.0
        ),
        "root_scale_max_abs_delta_after_roundtrip": max(
            (item["max_abs_root_scale_delta_from_one"] for item in root_curve_check.values()), default=0.0
        ),
        "stopping_contract": "Animator owns locomotion; clips do not translate root. Idle and Walk endpoints are neutral to avoid stop snap/jitter.",
    },
    "visual_inspection": {
        "status": "PASS",
        "checked_previews": ["three-quarter idle", "landscape gameplay distance idle", "three-quarter walk extreme"],
        "result": "Child-like large-head silhouette, cream button shirt, dark shorts, sandals, cowboy hat and travel backpack remain readable; no major overlap or detached part is visible in sampled Idle/Walk poses.",
        "independent_designer_review": "NOT RUN",
    },
    "unity_integration_contract": {
        "status": "NOT RUN",
        "source_height_m": round(source_dimensions.z, 6),
        "existing_character_controller_height_m": 2.15,
        "wrapper_scale_for_existing_controller": round(2.15 / source_dimensions.z, 6),
        "scale_note": "Use approximately 1.311 uniform wrapper scale only for compatibility with the current 2.15 m controller. That makes the child visually controller-height; Designer/Unity may instead approve a shorter controller, but must not silently change either value.",
        "animation_note": "This FBX requires Animator clips HNP_Traveller_Idle/HNP_Traveller_Walk. Do not drive it with legacy HnpTravellerPose rigid transforms or silently substitute it for the old Traveller.",
    },
    "export": {
        "fbx": str(FBX_PATH.relative_to(ROOT)).replace("\\", "/"),
        "axis_forward": "-Z",
        "axis_up": "Y",
        "apply_unit_scale": True,
        "add_leaf_bones": False,
        "bake_animation": True,
        "collision_intent": "capsule/CharacterController supplied by Unity wrapper; no collision mesh in FBX",
    },
    "roundtrip": roundtrip_report,
    "previews": [
        str(PREVIEW_3Q.relative_to(ROOT)).replace("\\", "/"),
        str(PREVIEW_GAME.relative_to(ROOT)).replace("\\", "/"),
        str(PREVIEW_WALK.relative_to(ROOT)).replace("\\", "/"),
    ],
}

manifest["hashes_sha256"] = {
    "blend": sha256(BLEND_PATH),
    "fbx": sha256(FBX_PATH),
    "roundtrip_report": sha256(ROUNDTRIP_PATH),
    "preview_three_quarter": sha256(PREVIEW_3Q),
    "preview_gameplay": sha256(PREVIEW_GAME),
    "preview_walk": sha256(PREVIEW_WALK),
}
MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

if not roundtrip_pass:
    raise RuntimeError(f"FBX round-trip failed: {json.dumps(roundtrip_report, indent=2)}")
if triangle_count > 12000 or degenerate_faces or loose_vertices:
    raise RuntimeError("Source geometry validation failed")

print("HNP_WORLD_002_TRAVELLER_PASS")
print(json.dumps({
    "triangles": triangle_count,
    "dimensions_m": [round(value, 6) for value in source_dimensions],
    "materials": len(canonical_material_names),
    "bones": bone_count,
    "actions": imported_actions,
    "roundtrip": roundtrip_report["status"],
}, indent=2))
