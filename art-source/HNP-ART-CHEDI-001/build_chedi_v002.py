"""HNP-ART-CHEDI-001 v002 reference-led Blender revision.

Loads the immutable v001 staging source, replaces only visible Core, Sanctuary
Shell and Interior geometry, refines exterior rails, then writes v002 assets.
Native axes: Z up, local approach/front -Y. FBX: -Z forward, Y up.
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
BASE_BLEND = SRC / "HNP_Chedi_Modular_ProductionStaging_v001.blend"
SOURCE_BLEND = SRC / "HNP_Chedi_Modular_ProductionStaging_v002.blend"
PHOTO_REF = ROOT / "ref" / "pra.jpg"
PHOTO_SRC = SRC / "textures" / "HNP_Chedi_PrayerPhoto_pra_v002.jpg"
PHOTO_OUT = OUT / "Textures" / "HNP_Chedi_PrayerPhoto_pra_v002.jpg"
for directory in (SRC, OUT, PHOTO_SRC.parent, PHOTO_OUT.parent):
    directory.mkdir(parents=True, exist_ok=True)
shutil.copyfile(PHOTO_REF, PHOTO_SRC)
shutil.copyfile(PHOTO_REF, PHOTO_OUT)

bpy.ops.wm.open_mainfile(filepath=str(BASE_BLEND))
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

COL = {
    "core": bpy.data.collections["HNP_Chedi_M01_CoreLandmark"],
    "exterior": bpy.data.collections["HNP_Chedi_M02_ExteriorWalk"],
    "shell": bpy.data.collections["HNP_Chedi_M03_SanctuaryShell"],
    "interior": bpy.data.collections["HNP_Chedi_M04_SanctuaryInterior"],
    "collision": bpy.data.collections["HNP_Chedi_M05_Collision"],
}

M = {material.name: material for material in bpy.data.materials}

# Update only the v002 photo material image; the reference bytes remain exact.
photo_image = bpy.data.images.load(str(PHOTO_SRC), check_existing=False)
photo_image.colorspace_settings.name = "sRGB"
photo_mat = M["HNP_Chedi_PrayerPhoto"]
for node in photo_mat.node_tree.nodes:
    if node.type == "TEX_IMAGE":
        node.image = photo_image


def clear_collection(target):
    for obj in list(target.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


clear_collection(COL["core"])
clear_collection(COL["shell"])
clear_collection(COL["interior"])
# Preserve v001 walk surfaces/stairs, replace only the blocky rail batch.
for obj in list(COL["exterior"].objects):
    if obj.name.endswith("__HNP_Chedi_White"):
        bpy.data.objects.remove(obj, do_unlink=True)


def own(obj, name, mat_name, target):
    obj.name = name
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    target.objects.link(obj)
    if mat_name:
        obj.data.materials.append(M[mat_name])
    return obj


def mesh_object(name, vertices, faces, mat_name, target, smooth=False):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    target.objects.link(obj)
    mesh.materials.append(M[mat_name])
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    for polygon in mesh.polygons:
        polygon.use_smooth = smooth
    return obj


def box(name, location, dimensions, mat_name, target, rotation=0.0, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=(0, 0, rotation))
    obj = own(bpy.context.object, name, mat_name, target)
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        modifier = obj.modifiers.new("SoftEdge", "BEVEL")
        modifier.width = bevel
        modifier.segments = 1
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    return obj


def cylinder(name, location, radius, depth, mat_name, target, vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    return own(bpy.context.object, name, mat_name, target)


def lathe(name, profile, mat_name, target, segments=64):
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
    faces.append(tuple(reversed(range(segments))))
    top = (len(profile) - 1) * segments
    faces.append(tuple(top + i for i in range(segments)))
    return mesh_object(name, vertices, faces, mat_name, target, smooth=True)


def annulus(name, inner, outer, bottom, top, mat_name, target, segments=64):
    vertices = []
    for z in (bottom, top):
        for radius in (inner, outer):
            for i in range(segments):
                angle = math.tau * i / segments
                vertices.append((radius * math.cos(angle), radius * math.sin(angle), z))
    row = segments
    faces = []
    bi, bo, ti, to = 0, row, row * 2, row * 3
    for i in range(segments):
        j = (i + 1) % segments
        faces.extend([
            (ti+i, ti+j, to+j, to+i), (bo+i, bo+j, bi+j, bi+i),
            (bi+i, bi+j, ti+j, ti+i), (to+i, to+j, bo+j, bo+i),
        ])
    return mesh_object(name, vertices, faces, mat_name, target)


def beam(name, a, b, width, depth, mat_name, target):
    a, b = Vector(a), Vector(b)
    delta = b - a
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(a+b)/2)
    obj = own(bpy.context.object, name, mat_name, target)
    obj.dimensions = (width, depth, delta.length)
    obj.rotation_euler = delta.to_track_quat("Z", "Y").to_euler()
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def gable_prism(name, half_width, front_y, rear_y, eave_z, ridge_z, mat_name, target):
    vertices = [
        (-half_width,front_y,eave_z), (half_width,front_y,eave_z), (0,front_y,ridge_z),
        (-half_width,rear_y,eave_z), (half_width,rear_y,eave_z), (0,rear_y,ridge_z),
    ]
    faces = [(0,1,2), (5,4,3), (0,3,4,1), (1,4,5,2), (2,5,3,0)]
    return mesh_object(name, vertices, faces, mat_name, target)


def arch_prism(name, center, tangent, normal, width, bottom, shoulder, top, depth, mat_name, target, steps=7):
    """Extruded arched plaque/opening on any vertical façade plane."""
    center, tangent, normal = Vector(center), Vector(tangent).normalized(), Vector(normal).normalized()
    outline = [(-width/2, bottom), (width/2, bottom), (width/2, shoulder)]
    radius = width / 2
    for i in range(1, steps):
        theta = i * math.pi / steps
        outline.append((math.cos(theta) * radius, shoulder + math.sin(theta) * (top-shoulder)))
    outline.extend([(-width/2, shoulder)])
    vertices = []
    for side in (-depth/2, depth/2):
        for u, z in outline:
            point = center + tangent*u + normal*side
            vertices.append((point.x, point.y, z))
    count = len(outline)
    faces = [tuple(reversed(range(count))), tuple(count+i for i in range(count))]
    for i in range(count):
        j = (i+1) % count
        faces.append((i,j,count+j,count+i))
    return mesh_object(name, vertices, faces, mat_name, target)


def ensure_uv(obj):
    if obj.type != "MESH" or obj.get("manual_uv"):
        return
    uv = obj.data.uv_layers.active or obj.data.uv_layers.new(name="UVMap")
    for polygon in obj.data.polygons:
        dominant = max(range(3), key=lambda axis: abs(polygon.normal[axis]))
        for loop_index in polygon.loop_indices:
            co = obj.data.vertices[obj.data.loops[loop_index].vertex_index].co
            if dominant == 2:
                value = (co.x*.08, co.y*.08)
            elif dominant == 1:
                value = (co.x*.08, co.z*.08)
            else:
                value = (co.y*.08, co.z*.08)
            uv.data[loop_index].uv = value


# --- M01: elongated ogive bell, deep collar and slender characteristic spire.
bell_profile = [
    (23.0,0.0), (23.0,.42), (23.35,.62), (23.35,.92),
    (22.72,1.15), (22.98,1.48), (22.35,1.72), (22.62,2.08),
    (21.95,2.34), (22.20,2.72), (21.47,3.00), (21.72,3.42),
    (20.92,3.74), (21.16,4.18), (20.30,4.53), (20.52,5.02),
    (19.62,5.40), (19.82,5.92), (18.95,6.30), (18.72,7.15),
    (18.48,8.25), (18.12,10.1), (17.60,12.4), (16.82,15.0),
    (15.70,17.7), (14.30,20.3), (12.55,22.8), (10.55,25.0),
    (8.55,26.75), (7.45,27.65),
]
lathe("V002_M01_ElongatedBell", bell_profile, "HNP_Chedi_GoldTile", COL["core"], 64)
for index, (radius, z, height) in enumerate(((23.36,.68,.20),(22.98,1.50,.18),(22.20,2.75,.20),
                                              (21.72,3.45,.18),(21.16,4.20,.18),(20.52,5.04,.20),
                                              (19.82,5.94,.22),(19.28,6.68,.32))):
    annulus(f"V002_M01_LowerCourse_{index}", radius-.45, radius, z, z+height,
            "HNP_Chedi_Terracotta", COL["core"], 64)

annulus("V002_M01_CollarDark", 6.55, 7.55, 27.55, 30.25,
        "HNP_Chedi_DarkInset", COL["core"], 48)
annulus("V002_M01_CollarLowerCap", 6.72, 7.78, 27.45, 27.78,
        "HNP_Chedi_Terracotta", COL["core"], 48)
annulus("V002_M01_CollarUpperCap", 6.35, 7.45, 30.05, 30.38,
        "HNP_Chedi_GoldTrim", COL["core"], 48)
for i in range(24):
    angle = math.tau*i/24
    radius = 7.62
    box(f"V002_M01_CollarPier_{i:02d}", (radius*math.cos(angle),radius*math.sin(angle),28.86),
        (.26,.44,2.55), "HNP_Chedi_Terracotta", COL["core"], rotation=angle)

spire_profile = [(6.70,30.25),(6.35,30.55)]
for i in range(20):
    z = 30.55 + i*.82
    radius = max(.25, 6.32*(1-i/21.2))
    spire_profile.extend([(radius,z),(radius*.91,z+.20),(radius*.97,z+.38)])
spire_profile.extend([(.24,47.25),(.12,47.70),(.035,48.0)])
lathe("V002_M01_SlenderRibbedSpire", spire_profile, "HNP_Chedi_GoldTile", COL["core"], 48)

# Layered white lower architecture with recognisable arched/grille bays.
annulus("V002_M01_WhitePlinthLower", 21.85,23.05,.35,.95,
        "HNP_Chedi_White", COL["core"],64)
annulus("V002_M01_WhitePlinthUpper", 21.55,22.85,5.15,5.75,
        "HNP_Chedi_White", COL["core"],64)
for i in range(20):
    angle = math.tau*i/20
    delta_front = abs((angle+math.pi/2+math.pi)%math.tau-math.pi)
    if delta_front < math.radians(20):
        continue
    radial = Vector((math.cos(angle),math.sin(angle),0))
    tangent = Vector((-math.sin(angle),math.cos(angle),0))
    center = radial*22.52
    arch_prism(f"V002_M01_ArchSurround_{i:02d}", center, tangent, radial, 3.70,.90,3.60,5.15,.50,
               "HNP_Chedi_Ivory", COL["core"])
    center_dark = radial*22.80
    arch_prism(f"V002_M01_Grille_{i:02d}", center_dark, tangent, radial, 2.45,1.32,3.28,4.25,.12,
               "HNP_Chedi_DarkInset", COL["core"])
    for offset in (-1.72,1.72):
        point = center + tangent*offset
        box(f"V002_M01_Pilaster_{i:02d}_{offset:+.0f}", (point.x,point.y,2.88),(.32,.72,4.35),
            "HNP_Chedi_White", COL["core"], rotation=angle+math.pi/2, bevel=.035)

# Sparse pointed plaques echo the observed frieze without the v001 sawtooth.
for i in range(24):
    angle = math.tau*i/24
    radius = 20.15
    x,y = radius*math.cos(angle),radius*math.sin(angle)
    radial = Vector((math.cos(angle),math.sin(angle),0))
    tangent = Vector((-math.sin(angle),math.cos(angle),0))
    arch_prism(f"V002_M01_FriezePlaque_{i:02d}", radial*radius, tangent, radial, 1.05,6.15,6.58,7.25,.22,
               "HNP_Chedi_Terracotta", COL["core"], steps=4)

# Carve the actual room volume through all intersecting core layers.
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,-22.35,5.55))
void = bpy.context.object
void.dimensions = (8.45,14.5,11.3)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
void_min, void_max = Vector((-4.225,-29.60,-.10)), Vector((4.225,-15.10,11.20))
for candidate in list(COL["core"].objects):
    points = [candidate.matrix_world@Vector(corner) for corner in candidate.bound_box]
    low = Vector((min(p.x for p in points),min(p.y for p in points),min(p.z for p in points)))
    high = Vector((max(p.x for p in points),max(p.y for p in points),max(p.z for p in points)))
    if not all(low[a] <= void_max[a] and high[a] >= void_min[a] for a in range(3)):
        continue
    bpy.context.view_layer.objects.active = candidate
    candidate.select_set(True)
    mod = candidate.modifiers.new("V002_SanctuaryVoid","BOOLEAN")
    mod.operation, mod.solver, mod.object = "DIFFERENCE","EXACT",void
    bpy.ops.object.modifier_apply(modifier=mod.name)
    candidate.select_set(False)
    if not candidate.data.vertices:
        bpy.data.objects.remove(candidate,do_unlink=True)
    else:
        for slot_index in reversed(range(len(candidate.data.materials))):
            if candidate.data.materials[slot_index] is None:
                candidate.data.materials.pop(index=slot_index)
bpy.data.objects.remove(void,do_unlink=True)

# --- M02: actual open stair balustrade language instead of solid box rails.
for cardinal, angle in enumerate((-math.pi/2,0,math.pi/2,math.pi)):
    radial = Vector((math.cos(angle),math.sin(angle),0))
    tangent = Vector((-math.sin(angle),math.cos(angle),0))
    for side in (-1,1):
        offset = tangent*(3.45*side)
        rail_points = []
        for j, radius in enumerate((29.4,31.0,32.6,34.2,35.8)):
            base_z = -.10 - (radius-29.4)*(.30/.82)
            point = radial*radius + offset
            box(f"V002_M02_RailPost_{cardinal}_{side}_{j}",(point.x,point.y,base_z+.58),
                (.18,.18,1.18),"HNP_Chedi_White",COL["exterior"],rotation=angle)
            cylinder(f"V002_M02_PostCap_{cardinal}_{side}_{j}",(point.x,point.y,base_z+1.22),
                     .16,.16,"HNP_Chedi_GoldTrim",COL["exterior"],12)
            rail_points.append((point.x,point.y,base_z+1.10))
        for j in range(len(rail_points)-1):
            beam(f"V002_M02_SlopedRail_{cardinal}_{side}_{j}",rail_points[j],rail_points[j+1],
                 .15,.15,"HNP_Chedi_White",COL["exterior"])

# --- M03: layered, attached sanctuary with detailed gable and side arches.
box("V002_M03_LeftWall",(-4.55,-22.55,5.10),(.72,11.6,10.2),
    "HNP_Chedi_Ivory",COL["shell"],bevel=.06)
box("V002_M03_RightWall",(4.55,-22.55,5.10),(.72,11.6,10.2),
    "HNP_Chedi_Ivory",COL["shell"],bevel=.06)
for x in (-4.98,4.98):
    outward = Vector((-1,0,0)) if x < 0 else Vector((1,0,0))
    tangent = Vector((0,-1,0)) if x < 0 else Vector((0,1,0))
    for j,y in enumerate((-25.3,-22.2,-19.1)):
        center = Vector((x,y,0))
        arch_prism(f"V002_M03_SideArch_{x:+.0f}_{j}",center,tangent,outward,1.55,1.25,3.25,4.15,.16,
                   "HNP_Chedi_DarkInset",COL["shell"],steps=6)
    for y in (-26.7,-23.7,-20.7,-17.7):
        box(f"V002_M03_SidePilaster_{x:+.0f}_{y}",(x,y,4.8),(.18,.34,7.7),
            "HNP_Chedi_White",COL["shell"],bevel=.025)
box("V002_M03_FrontLintel",(0,-28.28,9.75),(10.0,.82,1.25),
    "HNP_Chedi_White",COL["shell"],bevel=.06)
for x in (-4.10,4.10):
    box(f"V002_M03_FrontColumn_{x:+.0f}",(x,-28.28,4.85),(.95,.88,9.7),
        "HNP_Chedi_White",COL["shell"],bevel=.055)
    box(f"V002_M03_ColumnBase_{x:+.0f}",(x,-28.40,.55),(1.35,1.15,1.10),
        "HNP_Chedi_Ivory",COL["shell"],bevel=.04)
gable_prism("V002_M03_RoofMain",5.45,-29.05,-12.8,10.20,15.55,
            "HNP_Chedi_Terracotta",COL["shell"])
gable_prism("V002_M03_GableFace",5.12,-29.18,-28.72,10.12,15.35,
            "HNP_Chedi_Ivory",COL["shell"])
# Double pointed trim and small apex finial establish the front hierarchy.
for depth_offset,mat_name,width in ((-29.43,"HNP_Chedi_White",.30),(-29.48,"HNP_Chedi_GoldTrim",.14)):
    beam(f"V002_M03_GableTrimL_{mat_name}",(-5.2,depth_offset,10.18),(0,depth_offset,15.55),width,width,mat_name,COL["shell"])
    beam(f"V002_M03_GableTrimR_{mat_name}",(0,depth_offset,15.55),(5.2,depth_offset,10.18),width,width,mat_name,COL["shell"])
beam("V002_M03_DoorPointL",(-3.35,-29.53,8.8),(0,-29.53,12.15),.20,.20,
     "HNP_Chedi_GoldTrim",COL["shell"])
beam("V002_M03_DoorPointR",(0,-29.53,12.15),(3.35,-29.53,8.8),.20,.20,
     "HNP_Chedi_GoldTrim",COL["shell"])
for x in (-3.35,3.35):
    box(f"V002_M03_DoorTrim_{x:+.0f}",(x,-29.53,4.7),(.20,.20,8.2),
        "HNP_Chedi_GoldTrim",COL["shell"])
cylinder("V002_M03_ApexFinial",(0,-29.44,16.0),.18,1.0,
         "HNP_Chedi_GoldTrim",COL["shell"],12)
for step,(y,z,width) in enumerate(((-29.10,-.03,7.8),(-29.55,-.24,8.5),(-30.0,-.45,9.2))):
    box(f"V002_M03_ThresholdStep_{step}",(0,y,z),(width,.92,.24),
        "HNP_Chedi_Ivory",COL["shell"],bevel=.025)

# --- M04: calm material-separated hall; image stays full-frame and unobstructed.
box("V002_M04_Floor",(0,-22.35,.10),(8.35,11.5,.20),"HNP_Chedi_Stone",COL["interior"])
box("V002_M04_LeftLiner",(-4.16,-22.35,4.95),(.16,11.2,9.9),"HNP_Chedi_White",COL["interior"])
box("V002_M04_RightLiner",(4.16,-22.35,4.95),(.16,11.2,9.9),"HNP_Chedi_White",COL["interior"])
box("V002_M04_Ceiling",(0,-22.35,9.82),(8.25,11.2,.20),"HNP_Chedi_RedInterior",COL["interior"])
box("V002_M04_BackWall",(0,-16.70,5.10),(8.25,.34,10.2),"HNP_Chedi_Ivory",COL["interior"])
box("V002_M04_PhotoRecess",(0,-16.91,5.10),(5.05,.18,9.15),"HNP_Chedi_RedInterior",COL["interior"],bevel=.05)

photo_height = 8.0
photo_width = photo_height*387.0/792.0
photo_z0 = 1.28
verts = [(-photo_width/2,-17.03,photo_z0),(photo_width/2,-17.03,photo_z0),
         (photo_width/2,-17.03,photo_z0+photo_height),(-photo_width/2,-17.03,photo_z0+photo_height)]
photo = mesh_object("V002_M04_PrayerPhoto",verts,[(0,1,2,3)],"HNP_Chedi_PrayerPhoto",COL["interior"])
uv = photo.data.uv_layers.new(name="UVMap")
for loop_index,coord in enumerate(((0,0),(1,0),(1,1),(0,1))):
    uv.data[loop_index].uv = coord
photo["manual_uv"] = True
# Slim rectangular frame stays outside the image; no oversized overlay.
frame_x = photo_width/2+.18
for x in (-frame_x,frame_x):
    box(f"V002_M04_PhotoFrameV_{x:+.2f}",(x,-17.10,photo_z0+photo_height/2),(.14,.12,photo_height+.28),
        "HNP_Chedi_GoldTrim",COL["interior"],bevel=.025)
for z in (photo_z0-.12,photo_z0+photo_height+.12):
    box(f"V002_M04_PhotoFrameH_{z:.2f}",(0,-17.10,z),(photo_width+.48,.12,.14),
        "HNP_Chedi_GoldTrim",COL["interior"],bevel=.025)
box("V002_M04_Altar",(0,-18.20,.48),(3.9,1.05,.74),"HNP_Chedi_GoldTrim",COL["interior"],bevel=.06)
# Ceiling beams and side pilasters give photographed-hall scale cues.
for y in (-26.6,-24.2,-21.8,-19.4,-17.2):
    box(f"V002_M04_CeilingBeam_{y}",(0,y,9.63),(8.1,.16,.22),"HNP_Chedi_GoldTrim",COL["interior"])
for side in (-1,1):
    x = side*4.04
    for y in (-26.2,-23.2,-20.2,-17.5):
        box(f"V002_M04_WallPier_{side}_{y}",(x,y,4.6),(.20,.34,7.4),"HNP_Chedi_Ivory",COL["interior"],bevel=.02)
for x in (-2.75,2.75):
    cylinder(f"V002_M04_OfferingLamp_{x:+.0f}",(x,-18.55,1.05),.16,1.55,
             "HNP_Chedi_GoldTrim",COL["interior"],12)


for module in COL.values():
    for obj in module.objects:
        ensure_uv(obj)


def join_by_material(target,prefix):
    groups = {}
    for obj in list(target.objects):
        if obj.type != "MESH":
            continue
        mat_name = next((mat.name for mat in obj.data.materials if mat),"NoMaterial")
        groups.setdefault(mat_name,[]).append(obj)
    for mat_name,objects in groups.items():
        bpy.ops.object.select_all(action="DESELECT")
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        if len(objects)>1:
            bpy.ops.object.join()
        objects[0].name = f"{prefix}__{mat_name}"


for key,prefix in (("core","HNP_Chedi_v002_M01_Core"),("exterior","HNP_Chedi_v002_M02_Exterior"),
                   ("shell","HNP_Chedi_v002_M03_Shell"),("interior","HNP_Chedi_v002_M04_Interior"),
                   ("collision","COLL_HNP_Chedi_v002_M05")):
    join_by_material(COL[key],prefix)


def mesh_objects(target):
    return [obj for obj in target.objects if obj.type=="MESH"]


def metrics(objects):
    objects = list(objects)
    points = [obj.matrix_world@vertex.co for obj in objects for vertex in obj.data.vertices]
    low = Vector((min(p.x for p in points),min(p.y for p in points),min(p.z for p in points)))
    high = Vector((max(p.x for p in points),max(p.y for p in points),max(p.z for p in points)))
    triangles=vertices=degenerate=loose=0
    mats=set(); uv_missing=[]; negative=[]
    for obj in objects:
        obj.data.calc_loop_triangles(); triangles += len(obj.data.loop_triangles); vertices += len(obj.data.vertices)
        mats.update(mat.name for mat in obj.data.materials if mat)
        if not obj.data.uv_layers: uv_missing.append(obj.name)
        if any(v<0 for v in obj.scale): negative.append(obj.name)
        bm=bmesh.new(); bm.from_mesh(obj.data)
        degenerate += sum(1 for face in bm.faces if face.calc_area()<1e-10)
        loose += sum(1 for vertex in bm.verts if not vertex.link_edges)
        bm.free()
    return {"min_m":[round(v,6) for v in low],"max_m":[round(v,6) for v in high],
            "dimensions_m":[round(v,6) for v in high-low],"triangles":triangles,"vertices":vertices,
            "mesh_count":len(objects),"materials":sorted(mats),"material_count":len(mats),
            "uv0_missing":uv_missing,"negative_scale":negative,"degenerate_faces":degenerate,"loose_vertices":loose}


module_metrics={key:metrics(mesh_objects(value)) for key,value in COL.items()}
visible=sum((mesh_objects(COL[key]) for key in ("core","exterior","shell","interior")),[])
visible_metrics=metrics(visible)
collision_metrics=metrics(mesh_objects(COL["collision"]))
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE_BLEND))


def export(objects,path):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects: obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={"MESH"},
        axis_forward="-Z",axis_up="Y",add_leaf_bones=False,bake_anim=False,
        apply_unit_scale=True,apply_scale_options="FBX_SCALE_UNITS",path_mode="COPY",embed_textures=False)


module_files={
    "core":"HNP_Chedi_M01_Core_v002.fbx","exterior":"HNP_Chedi_M02_ExteriorWalk_v002.fbx",
    "shell":"HNP_Chedi_M03_SanctuaryShell_v002.fbx","interior":"HNP_Chedi_M04_SanctuaryInterior_v002.fbx",
    "collision":"HNP_Chedi_M05_Collision_v002.fbx"}
exports={}
for key,filename in module_files.items():
    path=OUT/filename; export(mesh_objects(COL[key]),path); exports[key]=path
combined=OUT/"HNP_Chedi_Modular_ProductionStaging_v002.fbx"; export(visible,combined); exports["combined_visible"]=combined


def render_preview(filename,location,target,lens,resolution,interior=False):
    for obj in COL["collision"].objects: obj.hide_render=True
    bpy.ops.object.camera_add(location=location); camera=bpy.context.object; camera.data.lens=lens
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler(); scene.camera=camera
    bpy.ops.object.light_add(type="SUN",location=(30,-40,55)); sun=bpy.context.object
    sun.rotation_euler=(math.radians(28),math.radians(-18),math.radians(-35)); sun.data.energy=2.15
    sun.data.color=(1.0,.82,.62); sun.data.angle=math.radians(9)
    bpy.ops.object.light_add(type="AREA",location=(-24,-35,28)); area=bpy.context.object
    area.data.energy=1300; area.data.shape="DISK"; area.data.size=16; area.data.color=(.58,.70,1.0)
    area.rotation_euler=(Vector(target)-area.location).to_track_quat("-Z","Y").to_euler()
    lights=[camera,sun,area]
    if interior:
        for x in (-2.4,2.4):
            bpy.ops.object.light_add(type="POINT",location=(x,-21.0,5.8)); point=bpy.context.object
            point.data.energy=420; point.data.color=(1.0,.55,.22); point.data.shadow_soft_size=2.0; lights.append(point)
    scene.world.use_nodes=True; background=scene.world.node_tree.nodes.get("Background")
    background.inputs[0].default_value=(.20,.27,.34,1); background.inputs[1].default_value=.55
    scene.render.resolution_x,scene.render.resolution_y=resolution; scene.render.filepath=str(OUT/filename)
    bpy.ops.render.render(write_still=True)
    for obj in lights: bpy.data.objects.remove(obj,do_unlink=True)


previews=[
    ("HNP_Chedi_v002_preview_approach.png",(0,-91,2.3),(0,0,16.5),28,(1280,720),False),
    ("HNP_Chedi_v002_preview_three-quarter.png",(58,-76,8.0),(0,0,16.0),30,(1280,720),False),
    ("HNP_Chedi_v002_preview_walkway.png",(15,-41,2.1),(0,-19,3.6),32,(1280,720),False),
    ("HNP_Chedi_v002_preview_interior.png",(0,-28.1,1.75),(0,-17.2,4.8),34,(1280,720),True),
]
for item in previews: render_preview(*item)


def roundtrip(path,expected):
    before=set(bpy.data.objects); bpy.ops.import_scene.fbx(filepath=str(path),automatic_bone_orientation=False)
    imported=[obj for obj in bpy.data.objects if obj not in before and obj.type=="MESH"]
    observed=metrics(imported); delta=max(abs(a-b) for a,b in zip(expected["dimensions_m"],observed["dimensions_m"]))
    result={"status":"PASS" if observed["triangles"]==expected["triangles"] and delta<.001 else "FAIL",
            "expected_triangles":expected["triangles"],"observed_triangles":observed["triangles"],
            "max_dimension_delta_m":round(delta,8),"observed_dimensions_m":observed["dimensions_m"],
            "mesh_count":observed["mesh_count"]}
    for obj in imported: bpy.data.objects.remove(obj,do_unlink=True)
    return result


roundtrips={}
for key,path in exports.items():
    roundtrips[path.name]=roundtrip(path,visible_metrics if key=="combined_visible" else module_metrics[key])
roundtrip_path=OUT/"roundtrip-v002.json"
roundtrip_path.write_text(json.dumps({"blender_version":bpy.app.version_string,"exports":roundtrips},indent=2),encoding="utf-8")

source_pass=(visible_metrics["triangles"]<=30000 and visible_metrics["degenerate_faces"]==0 and
             visible_metrics["loose_vertices"]==0 and not visible_metrics["uv0_missing"] and
             not visible_metrics["negative_scale"])
roundtrip_pass=all(item["status"]=="PASS" for item in roundtrips.values())
manifest={
    "task_id":"HNP-ART-CHEDI-001","revision":"v002",
    "supersedes_art_revision":"v001 (independent reference-led visual review FAIL; files preserved)",
    "classification":"reference-led production-staging revision; pending independent visual review",
    "status":{"blender_cli":"PASS","source_geometry":"PASS" if source_pass else "FAIL",
              "visible_triangle_budget_le_30000":"PASS" if visible_metrics["triangles"]<=30000 else "FAIL",
              "fbx_roundtrip":"PASS" if roundtrip_pass else "FAIL","designer_visual_review":"NOT RUN",
              "unity_import_prefab_collision":"NOT RUN","mobile_web_performance":"NOT RUN"},
    "review_corrections":{
        "silhouette":"Elongated ogive bell, eight readable lower courses, 2.7 m open collar and 20-tier slender spire; total top 48 m.",
        "facade":"Layered white plinth, 18 visible arched surrounds/dark grilles, pilasters, open stair balustrades, side arches and double-trim front gable.",
        "interior":"Unchanged full-frame pra.jpg in a quieter ivory/red recess with slim perimeter trim, smaller altar, ceiling beams and warm preview lighting."
    },
    "units":"metres","axis":{"blender_up":"+Z","local_front":"-Y","fbx_forward":"-Z","fbx_up":"Y"},
    "pivot":"origin at Chedi centre on upper circumambulation surface z=0",
    "dimensions":{"combined_visible_bounds":visible_metrics,"collision_bounds":collision_metrics,
                  "body_nominal_diameter_m":46.7,"complex_outer_diameter_m":74.0,"total_height_m":48.0,
                  "upper_walk_surface_z_m":0.0,"lower_court_surface_z_m":-2.4},
    "modules":{key:{"file":module_files[key],"metrics":module_metrics[key]} for key in module_files},
    "combined_visible_export":{"file":combined.name,"metrics":visible_metrics},
    "materials":{"count_combined_visible":visible_metrics["material_count"],"names":visible_metrics["materials"],
        "photo_texture":{"source_reference":"ref/pra.jpg","source_copy":str(PHOTO_SRC.relative_to(ROOT)).replace("\\","/"),
            "export_copy":str(PHOTO_OUT.relative_to(ROOT)).replace("\\","/"),"dimensions_px":[387,792],
            "color_space":"sRGB","uv":"UV0 full frame; upright; no crop or mirror",
            "sha256":hashlib.sha256(PHOTO_REF.read_bytes()).hexdigest(),
            "copies_hash_match":hashlib.sha256(PHOTO_REF.read_bytes()).digest()==hashlib.sha256(PHOTO_SRC.read_bytes()).digest()==hashlib.sha256(PHOTO_OUT.read_bytes()).digest()},
        "unity_consolidation_plan":"Nine visible materials in staging. Reuse one opaque shader; bake the eight flat architectural colors into one exterior/interior atlas or palette LUT, keep pra.jpg as the only dedicated photo material. Target 3 runtime material groups: architecture opaque, interior opaque/emissive accents, prayer photo. Verify draw calls in Unity before approval."},
    "walkability_contract":{"player_clearance_assumption":"capsule <=0.8 m diameter and <=2.2 m high, provisional",
        "front_chamber_clear_width_m":6.7,"front_chamber_walkable_depth_m":11.1,"four_cardinal_stair_clear_width_m":5.8,
        "upper_circumambulation_width_m":6.05,"lower_court_width_m":8.0,"collision_export":module_files["collision"],
        "note":"Collision source is carried from v001 because traversal dimensions are unchanged; Unity conversion and route probes remain NOT RUN."},
    "references":{"macro_silhouette":["ref/jd.jpg"],"front_interior":["ref/pra.jpg"],
        "bell_lower_courses":["ref/IMG_20211023_161058.jpg","ref/IMG_20211023_161311.jpg"],
        "spire_collar":["ref/IMG_20211023_161037.jpg","ref/IMG_20211023_161317.jpg"],
        "white_arch_facade":["ref/IMG_20211023_160913.jpg","ref/IMG_20211023_161123.jpg"],
        "stairs_railings":["ref/IMG_20211023_161403.jpg","ref/IMG_20211023_162159.jpg"]},
    "provisional_invented_details":["All metre dimensions remain unsurveyed gameplay-scale estimates.",
        "Unseen side/rear elevations, exact bay count, grille pattern and collar support count.",
        "Sanctuary room depth, side-arch spacing, ceiling beams, altar and lighting are gameplay adaptations.",
        "Four symmetric stair flights and collider conversion require Unity route validation."],
    "roundtrip":{"report":roundtrip_path.name,"exports":roundtrips},
    "source":{"blend":str(SOURCE_BLEND.relative_to(ROOT)).replace("\\","/"),
              "generator":str(Path(__file__).relative_to(ROOT)).replace("\\","/"),
              "baseline_read_only":str(BASE_BLEND.relative_to(ROOT)).replace("\\","/")},
    "previews":[item[0] for item in previews]
}
hash_targets=[SOURCE_BLEND,Path(__file__),roundtrip_path,PHOTO_SRC,PHOTO_OUT,*exports.values(),*(OUT/item[0] for item in previews)]
manifest["sha256"]={str(path.relative_to(ROOT)).replace("\\","/"):hashlib.sha256(path.read_bytes()).hexdigest() for path in hash_targets}
manifest_path=OUT/"manifest-v002.json"; manifest_path.write_text(json.dumps(manifest,indent=2),encoding="utf-8")
if any(value=="FAIL" for value in manifest["status"].values()):
    raise RuntimeError(json.dumps(manifest["status"]))
print("HNP_ART_CHEDI_001_V002_PASS",json.dumps(manifest["status"]))
