"""Build HNP-ART-CHEDI-001 modular Phra Pathom Chedi production staging.

Factory-startup safe.  Native Blender axes are X/Y horizontal and Z up; the
local front/approach is -Y.  Exports use FBX -Z forward, Y up for Unity.
Only task-local art-source/art-export directories are written.
"""

import bpy
import bmesh
import hashlib
import json
import math
import shutil
from pathlib import Path
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "art-source" / "HNP-ART-CHEDI-001"
OUT = ROOT / "art-export" / "HNP-ART-CHEDI-001"
SRC_TEX = SRC / "textures"
OUT_TEX = OUT / "Textures"
for directory in (SRC, OUT, SRC_TEX, OUT_TEX):
    directory.mkdir(parents=True, exist_ok=True)

VERSION = "v001"
PHOTO_REF = ROOT / "ref" / "pra.jpg"
PHOTO_SRC = SRC_TEX / "HNP_Chedi_PrayerPhoto_pra.jpg"
PHOTO_OUT = OUT_TEX / PHOTO_SRC.name
shutil.copyfile(PHOTO_REF, PHOTO_SRC)
shutil.copyfile(PHOTO_REF, PHOTO_OUT)

scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "METERS"
scene.unit_settings.scale_length = 1.0
try:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
except TypeError:
    scene.render.engine = "BLENDER_EEVEE"
scene.render.image_settings.file_format = "PNG"
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.render.fps = 24

# The process is launched with --factory-startup; still scope cleanup explicitly.
for obj in list(scene.objects):
    bpy.data.objects.remove(obj, do_unlink=True)


def collection(name):
    result = bpy.data.collections.new(name)
    scene.collection.children.link(result)
    return result


MODULES = {
    "core": collection("HNP_Chedi_M01_CoreLandmark"),
    "exterior": collection("HNP_Chedi_M02_ExteriorWalk"),
    "shell": collection("HNP_Chedi_M03_SanctuaryShell"),
    "interior": collection("HNP_Chedi_M04_SanctuaryInterior"),
    "collision": collection("HNP_Chedi_M05_Collision"),
}


PALETTE = {
    "HNP_Chedi_GoldTile": (0.72, 0.31, 0.055, 1.0),
    "HNP_Chedi_GoldTrim": (1.0, 0.62, 0.10, 1.0),
    "HNP_Chedi_Terracotta": (0.42, 0.105, 0.035, 1.0),
    "HNP_Chedi_Ivory": (0.89, 0.84, 0.70, 1.0),
    "HNP_Chedi_White": (0.96, 0.94, 0.86, 1.0),
    "HNP_Chedi_DarkInset": (0.035, 0.020, 0.016, 1.0),
    "HNP_Chedi_RedInterior": (0.24, 0.025, 0.018, 1.0),
    "HNP_Chedi_Stone": (0.30, 0.24, 0.20, 1.0),
    "HNP_Chedi_Bronze": (0.07, 0.085, 0.07, 1.0),
    "HNP_Chedi_PrayerPhoto": (1.0, 1.0, 1.0, 1.0),
    "HNP_Chedi_Collision": (0.08, 0.32, 0.55, 0.25),
}


def material(name, rgba, metallic=0.0, roughness=0.72):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


MATS = {
    name: material(name, rgba, 0.28 if "GoldTrim" in name else 0.02 if "GoldTile" in name else 0.0,
                   0.48 if "Gold" in name else 0.75)
    for name, rgba in PALETTE.items()
}
MATS["HNP_Chedi_Collision"].surface_render_method = "DITHERED"

photo_image = bpy.data.images.load(str(PHOTO_SRC), check_existing=False)
photo_image.colorspace_settings.name = "sRGB"
photo_nodes = MATS["HNP_Chedi_PrayerPhoto"].node_tree.nodes
photo_tex = photo_nodes.new("ShaderNodeTexImage")
photo_tex.name = "Exact unmodified pra.jpg"
photo_tex.image = photo_image
MATS["HNP_Chedi_PrayerPhoto"].node_tree.links.new(
    photo_tex.outputs["Color"], photo_nodes["Principled BSDF"].inputs["Base Color"]
)


def link_object(obj, name, mat_name, target):
    obj.name = name
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    target.objects.link(obj)
    if mat_name:
        obj.data.materials.append(MATS[mat_name])
    return obj


def mesh_object(name, vertices, faces, mat_name, target, smooth=False):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    target.objects.link(obj)
    mesh.materials.append(MATS[mat_name])
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    for polygon in mesh.polygons:
        polygon.use_smooth = smooth
    return obj


def box(name, location, dimensions, mat_name, target, rotation=0.0, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=(0.0, 0.0, rotation))
    obj = link_object(bpy.context.object, name, mat_name, target)
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        modifier = obj.modifiers.new("EdgeSoftening", "BEVEL")
        modifier.width = bevel
        modifier.segments = 1
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    return obj


def cylinder(name, location, radius, depth, mat_name, target, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    return link_object(bpy.context.object, name, mat_name, target)


def lathe(name, profile, mat_name, target, segments=64, cap=True):
    vertices = []
    for radius, z in profile:
        for index in range(segments):
            angle = math.tau * index / segments
            vertices.append((radius * math.cos(angle), radius * math.sin(angle), z))
    faces = []
    for row in range(len(profile) - 1):
        for index in range(segments):
            a = row * segments + index
            b = row * segments + (index + 1) % segments
            faces.append((a, b, b + segments, a + segments))
    if cap:
        faces.append(tuple(reversed(range(segments))))
        top = (len(profile) - 1) * segments
        faces.append(tuple(top + i for i in range(segments)))
    return mesh_object(name, vertices, faces, mat_name, target, smooth=True)


def annulus(name, inner, outer, bottom, top, mat_name, target, segments=64, start=0.0, end=math.tau):
    full = abs((end - start) - math.tau) < 1e-6
    count = segments if full else segments + 1
    vertices = []
    for z in (bottom, top):
        for radius in (inner, outer):
            for i in range(count):
                angle = start + (end - start) * i / segments
                vertices.append((radius * math.cos(angle), radius * math.sin(angle), z))
    row = count
    bi, bo, ti, to = 0, row, row * 2, row * 3
    faces = []
    limit = segments
    for i in range(limit):
        j = (i + 1) % count
        faces.extend([
            (ti + i, ti + j, to + j, to + i),
            (bo + i, bo + j, bi + j, bi + i),
            (bi + i, bi + j, ti + j, ti + i),
            (to + i, to + j, bo + j, bo + i),
        ])
    if not full:
        faces.extend([(bi, ti, to, bo), (bi + segments, bo + segments, to + segments, ti + segments)])
    return mesh_object(name, vertices, faces, mat_name, target)


def beam(name, a, b, width, depth, mat_name, target):
    a, b = Vector(a), Vector(b)
    center = (a + b) / 2
    delta = b - a
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj = link_object(bpy.context.object, name, mat_name, target)
    obj.dimensions = (width, depth, delta.length)
    obj.rotation_euler = delta.to_track_quat("Z", "Y").to_euler()
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def gable_prism(name, x_half, y_front, y_back, eave_z, ridge_z, mat_name, target):
    vertices = [
        (-x_half, y_front, eave_z), (x_half, y_front, eave_z), (0, y_front, ridge_z),
        (-x_half, y_back, eave_z), (x_half, y_back, eave_z), (0, y_back, ridge_z),
    ]
    faces = [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
    return mesh_object(name, vertices, faces, mat_name, target)


def point_finial(name, center, tangential_width, radial_depth, height, mat_name, target, rotation):
    # Low-poly pointed plaque, factual rhythm but simplified geometry.
    x, y, z = center
    verts = [(-tangential_width/2, -radial_depth/2, 0), (tangential_width/2, -radial_depth/2, 0),
             (tangential_width/2, radial_depth/2, 0), (-tangential_width/2, radial_depth/2, 0),
             (0, -radial_depth/2, height), (0, radial_depth/2, height)]
    c, s = math.cos(rotation), math.sin(rotation)
    verts = [(x + vx*c - vy*s, y + vx*s + vy*c, z + vz) for vx, vy, vz in verts]
    faces = [(0,1,2,3), (0,4,1), (3,2,5), (0,3,5,4), (1,4,5,2)]
    return mesh_object(name, verts, faces, mat_name, target)


def ensure_uv(obj):
    if obj.type != "MESH" or obj.get("manual_uv"):
        return
    uv = obj.data.uv_layers.active or obj.data.uv_layers.new(name="UVMap")
    for poly in obj.data.polygons:
        normal = poly.normal
        dominant = max(range(3), key=lambda axis: abs(normal[axis]))
        for loop_index in poly.loop_indices:
            co = obj.data.vertices[obj.data.loops[loop_index].vertex_index].co
            if dominant == 2:
                coords = (co.x * 0.08, co.y * 0.08)
            elif dominant == 1:
                coords = (co.x * 0.08, co.z * 0.08)
            else:
                coords = (co.y * 0.08, co.z * 0.08)
            uv.data[loop_index].uv = coords


# M01: silhouette from jd.jpg and field photos. Dimensions remain provisional.
bell_profile = [
    (22.9, 0.0), (22.9, .45), (22.4, .65), (22.55, .92),
    (22.0, 1.12), (22.18, 1.42), (21.5, 1.65), (21.72, 1.98),
    (20.95, 2.24), (21.17, 2.60), (20.35, 2.90), (20.55, 3.30),
    (19.75, 3.64), (19.95, 4.06), (19.15, 4.45), (19.35, 4.90),
    (18.65, 5.35), (18.82, 5.82), (18.15, 6.25), (17.85, 7.10),
    (17.45, 8.20), (17.15, 10.0), (16.55, 12.1), (15.55, 15.0),
    (14.15, 18.0), (12.25, 21.0), (9.95, 23.6), (7.75, 25.2), (6.75, 26.0),
]
lathe("M01_BellAndMouldings", bell_profile, "HNP_Chedi_GoldTile", MODULES["core"], 64)
annulus("M01_DarkCollar", 6.1, 7.2, 25.9, 27.8, "HNP_Chedi_DarkInset", MODULES["core"], 48)
for i in range(24):
    angle = math.tau * i / 24
    radius = 7.22
    x, y = radius * math.cos(angle), radius * math.sin(angle)
    box(f"M01_CollarPier_{i:02d}", (x, y, 26.85), (.34, .52, 1.95),
        "HNP_Chedi_Terracotta", MODULES["core"], rotation=angle)

spire_profile = [(6.55, 27.75), (6.10, 28.15)]
for i in range(14):
    z = 28.15 + i * .82
    radius = 6.10 * (1.0 - i / 15.4) + .20
    spire_profile.extend([(radius, z), (radius * .94, z + .24), (radius * .98, z + .42)])
spire_profile.extend([(.32, 43.3), (.18, 43.7), (.035, 44.0)])
lathe("M01_RibbedSpire", spire_profile, "HNP_Chedi_GoldTile", MODULES["core"], 48)
annulus("M01_TerracottaFrieze", 20.75, 21.55, 5.55, 6.30,
        "HNP_Chedi_Terracotta", MODULES["core"], 64)
for i in range(40):
    angle = math.tau * i / 40
    radius = 21.65
    point_finial(f"M01_FriezeFinial_{i:02d}", (radius*math.cos(angle), radius*math.sin(angle), 6.28),
                  1.05, .34, .85, "HNP_Chedi_Terracotta", MODULES["core"], angle + math.pi/2)

# Articulated white base, with front sanctuary gap.
for i in range(24):
    angle = math.tau * i / 24
    # Reserve a 24-degree front opening around local -Y.
    front_delta = abs((angle + math.pi/2 + math.pi) % math.tau - math.pi)
    if front_delta < math.radians(15):
        continue
    radius = 22.20
    x, y = radius * math.cos(angle), radius * math.sin(angle)
    box(f"M01_BasePanel_{i:02d}", (x, y, 2.65), (4.2, .72, 4.35),
        "HNP_Chedi_Ivory", MODULES["core"], rotation=angle + math.pi/2, bevel=.04)
    box(f"M01_DarkGrille_{i:02d}", (x*1.014, y*1.014, 3.10), (2.25, .16, 1.10),
        "HNP_Chedi_DarkInset", MODULES["core"], rotation=angle + math.pi/2)
    for offset in (-1.65, 1.65):
        tangent = Vector((-math.sin(angle), math.cos(angle), 0)) * offset
        box(f"M01_Pilaster_{i:02d}_{'L' if offset < 0 else 'R'}",
            (x+tangent.x, y+tangent.y, 2.7), (.34, .82, 5.10),
            "HNP_Chedi_White", MODULES["core"], rotation=angle + math.pi/2, bevel=.035)

# Create the real walkable prayer-room void in the opaque bell/base.  This is
# deliberately done before material batching so the source remains modular.
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -22.80, 5.0))
sanctuary_void = bpy.context.object
sanctuary_void.name = "TEMP_SanctuaryWalkableVoid"
sanctuary_void.dimensions = (8.05, 12.8, 10.2)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
void_min = Vector((-4.025, -29.20, -.10))
void_max = Vector((4.025, -16.40, 10.10))
for candidate in list(MODULES["core"].objects):
    corners = [candidate.matrix_world @ Vector(corner) for corner in candidate.bound_box]
    obj_min = Vector((min(p.x for p in corners), min(p.y for p in corners), min(p.z for p in corners)))
    obj_max = Vector((max(p.x for p in corners), max(p.y for p in corners), max(p.z for p in corners)))
    overlaps = all(obj_min[i] <= void_max[i] and obj_max[i] >= void_min[i] for i in range(3))
    if not overlaps:
        continue
    bpy.context.view_layer.objects.active = candidate
    candidate.select_set(True)
    modifier = candidate.modifiers.new("SanctuaryWalkableVoid", "BOOLEAN")
    modifier.operation = "DIFFERENCE"
    modifier.solver = "EXACT"
    modifier.object = sanctuary_void
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    candidate.select_set(False)
    if len(candidate.data.vertices) == 0:
        bpy.data.objects.remove(candidate, do_unlink=True)
    else:
        for slot_index in reversed(range(len(candidate.data.materials))):
            if candidate.data.materials[slot_index] is None:
                candidate.data.materials.pop(index=slot_index)
bpy.data.objects.remove(sanctuary_void, do_unlink=True)

# M02: two walkable rings and four broad cardinal stair flights.
annulus("M02_UpperCircumambulation", 22.95, 29.0, -.18, 0.0,
        "HNP_Chedi_Stone", MODULES["exterior"], 64)
annulus("M02_LowerCourt", 29.0, 37.0, -2.58, -2.40,
        "HNP_Chedi_Stone", MODULES["exterior"], 64)
for cardinal, angle in enumerate((-math.pi/2, 0, math.pi/2, math.pi)):
    radial = Vector((math.cos(angle), math.sin(angle), 0))
    tangent = Vector((-math.sin(angle), math.cos(angle), 0))
    for step in range(8):
        radius = 29.45 + step * .82
        z = -.15 - step * .30
        center = radial * radius
        box(f"M02_Stair_{cardinal}_{step}", (center.x, center.y, z-.16),
            (6.6, .92, .32), "HNP_Chedi_Ivory", MODULES["exterior"],
            rotation=angle + math.pi/2, bevel=.025)
    # Simple low balustrades preserve a clear 5.8 m player path.
    for side in (-1, 1):
        offset = tangent * (3.45 * side)
        center = radial * 32.35 + offset
        box(f"M02_StairRail_{cardinal}_{side}", (center.x, center.y, -.75),
            (.34, 6.9, 1.25), "HNP_Chedi_White", MODULES["exterior"],
            rotation=angle + math.pi/2, bevel=.04)

# M03: attached front prayer chamber shell; no freestanding billboard.
CHAMBER = {
    "outer_width_m": 9.2, "front_y_m": -28.25, "rear_y_m": -17.45,
    "clear_width_m": 6.6, "door_height_m": 8.8, "eave_height_m": 9.9,
    "ridge_height_m": 14.4, "walkable_depth_m": 9.5,
}
box("M03_LeftWall", (-4.35, -22.85, 4.75), (.72, 10.8, 9.5),
    "HNP_Chedi_Ivory", MODULES["shell"], bevel=.08)
box("M03_RightWall", (4.35, -22.85, 4.75), (.72, 10.8, 9.5),
    "HNP_Chedi_Ivory", MODULES["shell"], bevel=.08)
box("M03_FrontLintel", (0, -28.15, 9.35), (9.2, .72, 1.15),
    "HNP_Chedi_White", MODULES["shell"], bevel=.08)
for x in (-3.72, 3.72):
    box(f"M03_FrontJamb_{'L' if x < 0 else 'R'}", (x, -28.15, 4.55), (.82, .72, 9.1),
        "HNP_Chedi_White", MODULES["shell"], bevel=.06)
gable_prism("M03_AttachedGableRoof", 5.05, -28.65, -13.3, 9.75, 14.4,
            "HNP_Chedi_Terracotta", MODULES["shell"])
beam("M03_GableTrim_L", (-4.85,-28.73,9.95), (0,-28.73,14.40), .20, .20,
     "HNP_Chedi_GoldTrim", MODULES["shell"])
beam("M03_GableTrim_R", (0,-28.73,14.40), (4.85,-28.73,9.95), .20, .20,
     "HNP_Chedi_GoldTrim", MODULES["shell"])
box("M03_Threshold", (0, -28.0, .22), (7.25, 1.0, .44),
    "HNP_Chedi_Ivory", MODULES["shell"], bevel=.04)

# M04: true walkable interior staging with complete, upright pra.jpg.
box("M04_PrayerFloor", (0, -22.80, .10), (7.70, 9.65, .20),
    "HNP_Chedi_Stone", MODULES["interior"])
box("M04_InteriorCeiling", (0, -22.70, 9.25), (7.85, 9.8, .22),
    "HNP_Chedi_RedInterior", MODULES["interior"])
box("M04_BackWall", (0, -17.72, 4.65), (8.0, .34, 9.3),
    "HNP_Chedi_RedInterior", MODULES["interior"])
photo_width = 7.2 * 387.0 / 792.0
verts = [(-photo_width/2,-17.92,1.35), (photo_width/2,-17.92,1.35),
         (photo_width/2,-17.92,8.55), (-photo_width/2,-17.92,8.55)]
photo = mesh_object("M04_PrayerPhoto", verts, [(0,1,2,3)],
                    "HNP_Chedi_PrayerPhoto", MODULES["interior"])
uv = photo.data.uv_layers.new(name="UVMap")
# Viewed from the approach (-Y), left remains image-left; preserve full frame.
for loop_index, coords in enumerate(((0,0),(1,0),(1,1),(0,1))):
    uv.data[loop_index].uv = coords
photo["manual_uv"] = True
for x in (-2.12, 2.12):
    cylinder(f"M04_GoldColumn_{'L' if x < 0 else 'R'}", (x,-17.90,4.75), .24, 7.6,
             "HNP_Chedi_GoldTrim", MODULES["interior"], 16)
beam("M04_PointFrame_L", (-2.28,-17.88,7.25), (0,-17.88,9.02), .16, .16,
     "HNP_Chedi_GoldTrim", MODULES["interior"])
beam("M04_PointFrame_R", (0,-17.88,9.02), (2.28,-17.88,7.25), .16, .16,
     "HNP_Chedi_GoldTrim", MODULES["interior"])
box("M04_Altar", (0,-19.05,.58), (4.65,1.55,1.05),
    "HNP_Chedi_GoldTrim", MODULES["interior"], bevel=.08)
for x in (-2.75, 2.75):
    cylinder(f"M04_Lamp_{'L' if x < 0 else 'R'}", (x,-19.3,1.65), .24, 1.65,
             "HNP_Chedi_Bronze", MODULES["interior"], 12)

# M05: primitive/compound collision staging. Render-hidden, exported separately.
cylinder("COLL_ChediCore", (0,0,20.0), 17.15, 40.0,
         "HNP_Chedi_Collision", MODULES["collision"], 32)
annulus("COLL_UpperWalk", 22.90, 29.05, -.24, -.16,
        "HNP_Chedi_Collision", MODULES["collision"], 48)
annulus("COLL_LowerCourt", 28.95, 37.05, -2.66, -2.58,
        "HNP_Chedi_Collision", MODULES["collision"], 48)
box("COLL_SanctuaryLeft", (-4.35,-22.85,4.75), (.74,10.8,9.5),
    "HNP_Chedi_Collision", MODULES["collision"])
box("COLL_SanctuaryRight", (4.35,-22.85,4.75), (.74,10.8,9.5),
    "HNP_Chedi_Collision", MODULES["collision"])
box("COLL_SanctuaryBack", (0,-17.55,4.6), (8.0,.34,9.2),
    "HNP_Chedi_Collision", MODULES["collision"])
box("COLL_PrayerFloor", (0,-22.80,-.02), (7.70,9.65,.10),
    "HNP_Chedi_Collision", MODULES["collision"])
for cardinal, angle in enumerate((-math.pi/2, 0, math.pi/2, math.pi)):
    radial = Vector((math.cos(angle), math.sin(angle), 0))
    for step in range(8):
        radius = 29.45 + step*.82
        z = -.15 - step*.30
        center = radial * radius
        box(f"COLL_Stair_{cardinal}_{step}", (center.x,center.y,z-.17), (6.62,.92,.34),
            "HNP_Chedi_Collision", MODULES["collision"], rotation=angle+math.pi/2)


for module in MODULES.values():
    for obj in module.objects:
        ensure_uv(obj)


def join_by_material(target, prefix):
    groups = {}
    for obj in list(target.objects):
        if obj.type != "MESH":
            continue
        key = obj.data.materials[0].name if obj.data.materials else "NoMaterial"
        groups.setdefault(key, []).append(obj)
    for mat_name, objects in groups.items():
        bpy.ops.object.select_all(action="DESELECT")
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        if len(objects) > 1:
            bpy.ops.object.join()
        objects[0].name = f"{prefix}__{mat_name}"


for key, prefix in (
    ("core", "HNP_Chedi_M01_Core"),
    ("exterior", "HNP_Chedi_M02_Exterior"),
    ("shell", "HNP_Chedi_M03_Shell"),
    ("interior", "HNP_Chedi_M04_Interior"),
    ("collision", "COLL_HNP_Chedi_M05"),
):
    join_by_material(MODULES[key], prefix)


def mesh_objects(target):
    return [obj for obj in target.objects if obj.type == "MESH"]


def metrics(objects):
    objects = list(objects)
    points = [obj.matrix_world @ vertex.co for obj in objects for vertex in obj.data.vertices]
    minimum = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maximum = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    triangles = vertices = degenerate = loose = 0
    materials = set()
    uv_missing = []
    negative_scale = []
    for obj in objects:
        obj.data.calc_loop_triangles()
        triangles += len(obj.data.loop_triangles)
        vertices += len(obj.data.vertices)
        materials.update(mat.name for mat in obj.data.materials if mat is not None)
        if not obj.data.uv_layers:
            uv_missing.append(obj.name)
        if obj.scale.x < 0 or obj.scale.y < 0 or obj.scale.z < 0:
            negative_scale.append(obj.name)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        degenerate += sum(1 for face in bm.faces if face.calc_area() < 1e-10)
        loose += sum(1 for vert in bm.verts if not vert.link_edges)
        bm.free()
    return {
        "min_m": [round(v, 6) for v in minimum],
        "max_m": [round(v, 6) for v in maximum],
        "dimensions_m": [round(v, 6) for v in maximum - minimum],
        "triangles": triangles,
        "vertices": vertices,
        "mesh_count": len(objects),
        "materials": sorted(materials),
        "material_count": len(materials),
        "uv0_missing": uv_missing,
        "negative_scale": negative_scale,
        "degenerate_faces": degenerate,
        "loose_vertices": loose,
    }


module_metrics = {key: metrics(mesh_objects(module)) for key, module in MODULES.items()}
visible_objects = sum((mesh_objects(MODULES[key]) for key in ("core", "exterior", "shell", "interior")), [])
visible_metrics = metrics(visible_objects)
collision_metrics = metrics(mesh_objects(MODULES["collision"]))

# Save the clean task source before adding preview-only objects or round-trip imports.
blend_path = SRC / "HNP_Chedi_Modular_ProductionStaging_v001.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))


def export_objects(objects, path):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.fbx(
        filepath=str(path), use_selection=True, object_types={"MESH"},
        axis_forward="-Z", axis_up="Y", add_leaf_bones=False, bake_anim=False,
        apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
        path_mode="COPY", embed_textures=False,
    )


exports = {}
module_files = {
    "core": "HNP_Chedi_M01_Core_v001.fbx",
    "exterior": "HNP_Chedi_M02_ExteriorWalk_v001.fbx",
    "shell": "HNP_Chedi_M03_SanctuaryShell_v001.fbx",
    "interior": "HNP_Chedi_M04_SanctuaryInterior_v001.fbx",
    "collision": "HNP_Chedi_M05_Collision_v001.fbx",
}
for key, filename in module_files.items():
    path = OUT / filename
    export_objects(mesh_objects(MODULES[key]), path)
    exports[key] = path
combined_path = OUT / "HNP_Chedi_Modular_ProductionStaging_v001.fbx"
export_objects(visible_objects, combined_path)
exports["combined_visible"] = combined_path


def render_preview(filename, camera_location, target, lens, resolution):
    for obj in MODULES["collision"].objects:
        obj.hide_render = True
    bpy.ops.object.camera_add(location=camera_location)
    camera = bpy.context.object
    camera.data.lens = lens
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    bpy.ops.object.light_add(type="SUN", location=(25,-40,55))
    sun = bpy.context.object
    sun.rotation_euler = (math.radians(25), math.radians(-20), math.radians(-35))
    sun.data.energy = 2.3
    sun.data.color = (1.0,.78,.56)
    sun.data.angle = math.radians(8)
    bpy.ops.object.light_add(type="AREA", location=(-28,-38,30))
    area = bpy.context.object
    area.data.energy = 1800
    area.data.shape = "DISK"
    area.data.size = 18
    area.data.color = (.55,.68,1.0)
    area.rotation_euler = (Vector(target) - area.location).to_track_quat("-Z", "Y").to_euler()
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs[0].default_value = (.18,.25,.34,1)
    background.inputs[1].default_value = .65
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(OUT / filename)
    bpy.ops.render.render(write_still=True)
    for obj in (camera, sun, area):
        bpy.data.objects.remove(obj, do_unlink=True)


previews = [
    ("HNP_Chedi_v001_preview_approach.png", (0,-118,24), (0,0,16), 44, (1280,720)),
    ("HNP_Chedi_v001_preview_three-quarter.png", (74,-98,36), (0,0,15), 46, (1280,720)),
    ("HNP_Chedi_v001_preview_interior.png", (0,-34.0,4.2), (0,-18.0,4.7), 35, (960,720)),
    ("HNP_Chedi_v001_preview_walkway.png", (44,-60,12.0), (0,-18,1.0), 42, (1280,720)),
]
for preview in previews:
    render_preview(*preview)


def roundtrip(path, expected):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(path), automatic_bone_orientation=False)
    imported = [obj for obj in bpy.data.objects if obj not in before and obj.type == "MESH"]
    observed = metrics(imported)
    dimension_delta = max(abs(a-b) for a,b in zip(expected["dimensions_m"], observed["dimensions_m"]))
    status = "PASS" if observed["triangles"] == expected["triangles"] and dimension_delta < .001 else "FAIL"
    result = {
        "status": status,
        "expected_triangles": expected["triangles"],
        "observed_triangles": observed["triangles"],
        "max_dimension_delta_m": round(dimension_delta, 8),
        "observed_dimensions_m": observed["dimensions_m"],
        "mesh_count": observed["mesh_count"],
    }
    for obj in imported:
        bpy.data.objects.remove(obj, do_unlink=True)
    return result


roundtrips = {}
for key, path in exports.items():
    expected = visible_metrics if key == "combined_visible" else module_metrics[key]
    roundtrips[path.name] = roundtrip(path, expected)

roundtrip_path = OUT / "roundtrip.json"
roundtrip_path.write_text(json.dumps({"blender_version": bpy.app.version_string, "exports": roundtrips}, indent=2), encoding="utf-8")

reference_ids = {
    "macro_silhouette": ["ref/jd.jpg"],
    "front_interior": ["ref/pra.jpg"],
    "bell_and_lower_courses": ["ref/IMG_20211023_161058.jpg", "ref/IMG_20211023_161311.jpg"],
    "spire_and_collar": ["ref/IMG_20211023_161037.jpg", "ref/IMG_20211023_161317.jpg"],
    "white_facade_and_grilles": ["ref/IMG_20211023_160913.jpg", "ref/IMG_20211023_161123.jpg"],
    "stairs_and_courtyard": ["ref/IMG_20211023_161403.jpg", "ref/IMG_20211023_162159.jpg"],
    "layout_context": ["ref/game-document/image2.png"],
}

all_source_pass = (
    visible_metrics["triangles"] <= 30000
    and visible_metrics["degenerate_faces"] == 0
    and visible_metrics["loose_vertices"] == 0
    and not visible_metrics["uv0_missing"]
    and not visible_metrics["negative_scale"]
)
all_roundtrip_pass = all(item["status"] == "PASS" for item in roundtrips.values())
manifest = {
    "task_id": "HNP-ART-CHEDI-001",
    "revision": VERSION,
    "asset_name": "HNP_Chedi_Modular_ProductionStaging",
    "classification": "production-staging; reference-led modular exterior/interior",
    "status": {
        "blender_cli": "PASS",
        "source_geometry": "PASS" if all_source_pass else "FAIL",
        "visible_triangle_budget_le_30000": "PASS" if visible_metrics["triangles"] <= 30000 else "FAIL",
        "fbx_roundtrip": "PASS" if all_roundtrip_pass else "FAIL",
        "designer_visual_review": "NOT RUN",
        "unity_import_prefab_collision": "NOT RUN",
        "mobile_web_performance": "NOT RUN",
    },
    "units": "metres",
    "axis": {"blender_up": "+Z", "local_front": "-Y", "fbx_forward": "-Z", "fbx_up": "Y"},
    "pivot": "world/local origin at Chedi centre on upper circumambulation surface z=0",
    "dimensions": {
        "combined_visible_bounds": visible_metrics,
        "collision_bounds": collision_metrics,
        "body_nominal_diameter_m": 45.8,
        "complex_outer_diameter_m": 74.0,
        "total_height_m": 44.0,
        "upper_walk_surface_z_m": 0.0,
        "lower_court_surface_z_m": -2.4,
    },
    "modules": {key: {"file": module_files[key], "metrics": module_metrics[key]} for key in module_files},
    "combined_visible_export": {"file": combined_path.name, "metrics": visible_metrics},
    "materials": {
        "count_combined_visible": visible_metrics["material_count"],
        "names": visible_metrics["materials"],
        "photo_texture": {
            "source_reference": "ref/pra.jpg",
            "source_copy": str(PHOTO_SRC.relative_to(ROOT)).replace("\\", "/"),
            "export_copy": str(PHOTO_OUT.relative_to(ROOT)).replace("\\", "/"),
            "dimensions_px": [387, 792],
            "color_space": "sRGB",
            "uv": "UV0 full frame; upright; not cropped or mirrored",
            "sha256": hashlib.sha256(PHOTO_REF.read_bytes()).hexdigest(),
            "copies_hash_match": hashlib.sha256(PHOTO_REF.read_bytes()).digest() == hashlib.sha256(PHOTO_SRC.read_bytes()).digest() == hashlib.sha256(PHOTO_OUT.read_bytes()).digest(),
        },
        "other_surfaces": "flat PBR palette in .blend/FBX; no external procedural dependency",
    },
    "walkability_contract": {
        "player_clearance_assumption": "capsule <= 0.8 m diameter, <= 2.2 m height (provisional until Unity owner confirms)",
        "front_chamber_clear_width_m": CHAMBER["clear_width_m"],
        "front_chamber_walkable_depth_m": CHAMBER["walkable_depth_m"],
        "four_cardinal_stair_clear_width_m": 5.8,
        "upper_circumambulation_width_m": 6.05,
        "lower_court_width_m": 8.0,
        "collision_export": module_files["collision"],
        "collision_intent": [
            "COLL_ChediCore keeps the opaque bell/body impassable.",
            "Side/back chamber colliders keep the central front doorway open and stop entry into the solid core.",
            "Dedicated upper/lower annular floors and compound stair boxes provide traversal staging.",
            "Unity must choose MeshCollider/primitive conversion and revalidate step height, slope and route probes."
        ],
    },
    "chamber": CHAMBER,
    "references": reference_ids,
    "provisional_invented_details": [
        "All metre dimensions: no measured architectural survey was supplied.",
        "Unseen rear/side construction and exact chamber depth/roof structure.",
        "Simplified 24-bay white facade, grille spacing, finial count and collar pier count.",
        "Interior ceiling, altar, lamps, columns and gold outline are gameplay-readable abstractions around the authoritative pra.jpg image.",
        "Four symmetric stair flights and continuous lower court are traversal adaptations; site placement must be checked against the Unity map.",
        "Collision volumes and assumed player capsule require Unity integration validation."
    ],
    "roundtrip": {"report": roundtrip_path.name, "exports": roundtrips},
    "source": {
        "blend": str(blend_path.relative_to(ROOT)).replace("\\", "/"),
        "generator": str(Path(__file__).relative_to(ROOT)).replace("\\", "/"),
    },
    "previews": [item[0] for item in previews],
}

hash_targets = [blend_path, Path(__file__), roundtrip_path, PHOTO_SRC, PHOTO_OUT, *exports.values(), *(OUT / p[0] for p in previews)]
manifest["sha256"] = {str(path.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest() for path in hash_targets}
manifest_path = OUT / "manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

if any(value == "FAIL" for value in manifest["status"].values()):
    raise RuntimeError(json.dumps(manifest["status"], ensure_ascii=False))
print("HNP_ART_CHEDI_001_PASS", json.dumps(manifest["status"]))
