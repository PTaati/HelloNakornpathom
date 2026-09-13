"""HNP-ART-CHEDI-001 v003 reference-led reconstruction.

Uses the independently approved HNP-WORLD-010 architectural source as the
fidelity base, the v002 task source for its accepted modular exterior route,
and rebuilds a true shallow walk-in prayer chamber. Writes v003 files only.
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
BASE_BLEND = SRC / "HNP_Chedi_Modular_ProductionStaging_v002.blend"
REFERENCE_BLEND = ROOT / "art-source" / "hnp-world-010" / "HNP_Chedi_v010.blend"
SOURCE_BLEND = SRC / "HNP_Chedi_Modular_ProductionStaging_v003.blend"
PHOTO_REF = ROOT / "ref" / "pra.jpg"
PHOTO_SRC = SRC / "textures" / "HNP_Chedi_PrayerPhoto_pra_v003.jpg"
PHOTO_OUT = OUT / "Textures" / "HNP_Chedi_PrayerPhoto_pra_v003.jpg"
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


def clear_collection(target):
    for obj in list(target.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


for key in ("core", "shell", "interior", "collision"):
    clear_collection(COL[key])

M = {material.name: material for material in bpy.data.materials}
photo_image = bpy.data.images.load(str(PHOTO_SRC), check_existing=False)
photo_image.colorspace_settings.name = "sRGB"
for node in M["HNP_Chedi_PrayerPhoto"].node_tree.nodes:
    if node.type == "TEX_IMAGE":
        node.image = photo_image


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
        mod = obj.modifiers.new("SoftEdge", "BEVEL")
        mod.width = bevel
        mod.segments = 1
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj


def cylinder(name, location, radius, depth, mat_name, target, vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    return own(bpy.context.object, name, mat_name, target)


def annulus(name, inner, outer, bottom, top, mat_name, target, segments=48):
    vertices = []
    for z in (bottom, top):
        for radius in (inner, outer):
            for i in range(segments):
                angle = math.tau * i / segments
                vertices.append((radius*math.cos(angle), radius*math.sin(angle), z))
    row = segments
    bi, bo, ti, to = 0, row, row*2, row*3
    faces = []
    for i in range(segments):
        j = (i+1) % segments
        faces.extend([(ti+i,ti+j,to+j,to+i),(bo+i,bo+j,bi+j,bi+i),
                      (bi+i,bi+j,ti+j,ti+i),(to+i,to+j,bo+j,bo+i)])
    return mesh_object(name, vertices, faces, mat_name, target)


def beam(name, a, b, width, depth, mat_name, target):
    a, b = Vector(a), Vector(b)
    delta = b-a
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(a+b)/2)
    obj = own(bpy.context.object, name, mat_name, target)
    obj.dimensions = (width, depth, delta.length)
    obj.rotation_euler = delta.to_track_quat("Z", "Y").to_euler()
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def ensure_uv(obj):
    if obj.type != "MESH" or obj.get("manual_uv"):
        return
    uv = obj.data.uv_layers.active or obj.data.uv_layers.new(name="UVMap")
    for polygon in obj.data.polygons:
        dominant = max(range(3), key=lambda axis: abs(polygon.normal[axis]))
        for loop_index in polygon.loop_indices:
            co = obj.data.vertices[obj.data.loops[loop_index].vertex_index].co
            value = (co.x*.08, co.y*.08) if dominant == 2 else ((co.x*.08, co.z*.08) if dominant == 1 else (co.y*.08, co.z*.08))
            uv.data[loop_index].uv = value


# Append only approved visible v010 objects. The original source remains unchanged.
with bpy.data.libraries.load(str(REFERENCE_BLEND), link=False) as (data_from, data_to):
    data_to.objects = [name for name in data_from.objects if name.startswith("HNP_Chedi_v010_") and "BuddhaPhoto" not in name]
approved = [obj for obj in data_to.objects if obj and obj.type == "MESH"]

material_map = {
    "HNP009_DarkInset": "HNP_Chedi_DarkInset",
    "HNP009_GoldBrick": "HNP_Chedi_GoldTile",
    "HNP009_GoldHighlight": "HNP_Chedi_GoldTrim",
    "HNP009_Ivory": "HNP_Chedi_Ivory",
    "HNP009_Terracotta": "HNP_Chedi_Terracotta",
    "HNP009_White": "HNP_Chedi_White",
}
for obj in approved:
    # Appended datablocks are not initially part of the active ViewLayer.
    scene.collection.objects.link(obj)
    # v010 local front is +Y in native coordinates; rotate to task convention -Y.
    obj.rotation_euler.z += math.pi
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.select_set(False)
    for index, slot in enumerate(obj.material_slots):
        original = slot.material.name.split(".")[0] if slot.material else ""
        if original in material_map:
            slot.material = M[material_map[original]]
    # White/ivory batches carry the reference-led façade and attached gable.
    target = COL["shell"] if any(key in obj.name for key in ("Ivory", "White")) else COL["core"]
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    target.objects.link(obj)
    obj.name = obj.name.replace("HNP_Chedi_v010", "HNP_Chedi_v003")

# Carve a genuine 12 m prayer volume through the approved opaque body while
# leaving its white façade, roof and sidewall skins intact outside 7.5 m width.
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -21.55, 5.15))
void = bpy.context.object
void.dimensions = (7.55, 13.55, 10.5)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
void_min, void_max = Vector((-3.775,-28.325,-.10)), Vector((3.775,-14.775,10.40))
for candidate in approved:
    points = [candidate.matrix_world @ Vector(corner) for corner in candidate.bound_box]
    low = Vector((min(p.x for p in points),min(p.y for p in points),min(p.z for p in points)))
    high = Vector((max(p.x for p in points),max(p.y for p in points),max(p.z for p in points)))
    if not all(low[i] <= void_max[i] and high[i] >= void_min[i] for i in range(3)):
        continue
    bpy.context.view_layer.objects.active = candidate
    candidate.select_set(True)
    mod = candidate.modifiers.new("V003_DeepPrayerVoid", "BOOLEAN")
    mod.operation, mod.solver, mod.object = "DIFFERENCE", "EXACT", void
    bpy.ops.object.modifier_apply(modifier=mod.name)
    candidate.select_set(False)
    if not candidate.data.vertices:
        bpy.data.objects.remove(candidate, do_unlink=True)
    else:
        for slot_index in reversed(range(len(candidate.data.materials))):
            if candidate.data.materials[slot_index] is None:
                candidate.data.materials.pop(index=slot_index)
bpy.data.objects.remove(void, do_unlink=True)

# Joined reference batches contain large coplanar caps that can survive a
# Boolean because their source topology spans several architectural parts.
# Remove only faces whose median still seals the declared central corridor.
for candidate in approved:
    if candidate.name not in bpy.data.objects:
        continue
    bm = bmesh.new()
    bm.from_mesh(candidate.data)
    sealing = []
    for face in bm.faces:
        center = candidate.matrix_world @ face.calc_center_median()
        if abs(center.x) < 3.86 and -29.35 < center.y < -14.65 and -.15 < center.z < 10.55:
            sealing.append(face)
    if sealing:
        bmesh.ops.delete(bm, geom=sealing, context="FACES")
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-7)
        bm.to_mesh(candidate.data)
        candidate.data.update()
    bm.free()

# Reduce only dense repeated gold surfaces. Keep white façade/gable untouched.
for obj in list(COL["core"].objects):
    mat_names = {mat.name for mat in obj.data.materials if mat}
    ratio = .72 if "HNP_Chedi_GoldTile" in mat_names else (.78 if "HNP_Chedi_GoldTrim" in mat_names else .86)
    mod = obj.modifiers.new("V003_MobileSurfaceBudget", "DECIMATE")
    mod.ratio = ratio
    mod.use_collapse_triangulate = True
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.select_set(False)

# Deep physical prayer chamber: visible floor run, threshold, quiet liners,
# shallow altar and back recess. The supplied photo itself is untouched.
box("V003_M04_PrayerFloor", (0,-21.45,.09), (7.35,12.35,.18), "HNP_Chedi_Stone", COL["interior"])
for step,(y,z,width) in enumerate(((-28.05,-.02,7.25),(-28.42,-.20,7.85),(-28.79,-.38,8.45))):
    box(f"V003_M04_Threshold_{step}",(0,y,z),(width,.74,.22),"HNP_Chedi_Ivory",COL["interior"],bevel=.02)
box("V003_M04_LeftQuietLiner",(-3.69,-21.45,4.65),(.14,12.1,9.3),"HNP_Chedi_Ivory",COL["interior"])
box("V003_M04_RightQuietLiner",(3.69,-21.45,4.65),(.14,12.1,9.3),"HNP_Chedi_Ivory",COL["interior"])
box("V003_M04_Ceiling",(0,-21.45,9.28),(7.30,12.10,.16),"HNP_Chedi_RedInterior",COL["interior"])
box("V003_M04_BackWall",(0,-15.30,4.70),(7.40,.34,9.40),"HNP_Chedi_Ivory",COL["interior"])
box("V003_M04_RedRecess",(0,-15.50,4.75),(4.85,.16,8.95),"HNP_Chedi_RedInterior",COL["interior"],bevel=.045)

photo_height = 7.75
photo_width = photo_height*387.0/792.0
photo_bottom = 1.05
verts = [(-photo_width/2,-15.61,photo_bottom),(photo_width/2,-15.61,photo_bottom),
         (photo_width/2,-15.61,photo_bottom+photo_height),(-photo_width/2,-15.61,photo_bottom+photo_height)]
photo = mesh_object("V003_M04_PrayerPhoto",verts,[(0,1,2,3)],"HNP_Chedi_PrayerPhoto",COL["interior"])
uv = photo.data.uv_layers.new(name="UVMap")
for loop_index,coord in enumerate(((0,0),(1,0),(1,1),(0,1))):
    uv.data[loop_index].uv = coord
photo["manual_uv"] = True

# Fine perimeter frame stays entirely outside the image plane.
frame_x = photo_width/2+.16
for x in (-frame_x,frame_x):
    box(f"V003_M04_FrameV_{x:+.2f}",(x,-15.68,photo_bottom+photo_height/2),(.13,.10,photo_height+.28),
        "HNP_Chedi_GoldTrim",COL["interior"],bevel=.018)
for z in (photo_bottom-.11,photo_bottom+photo_height+.11):
    box(f"V003_M04_FrameH_{z:.2f}",(0,-15.68,z),(photo_width+.45,.10,.13),
        "HNP_Chedi_GoldTrim",COL["interior"],bevel=.018)
box("V003_M04_AltarStep",(0,-16.60,.32),(3.90,1.10,.50),"HNP_Chedi_GoldTrim",COL["interior"],bevel=.045)
box("V003_M04_KneelingZone",(0,-19.20,.19),(3.8,2.5,.06),"HNP_Chedi_Terracotta",COL["interior"],bevel=.02)
for y in (-26.3,-23.8,-21.3,-18.8,-16.3):
    box(f"V003_M04_CeilingRib_{y}",(0,y,9.14),(7.15,.14,.18),"HNP_Chedi_GoldTrim",COL["interior"])
for side in (-1,1):
    x=side*3.60
    for y in (-25.8,-22.8,-19.8,-16.8):
        box(f"V003_M04_WallPier_{side}_{y}",(x,y,4.35),(.17,.32,7.3),"HNP_Chedi_White",COL["interior"],bevel=.018)
for x in (-2.55,2.55):
    cylinder(f"V003_M04_OfferingLamp_{x:+.1f}",(x,-16.55,.98),.15,1.45,"HNP_Chedi_GoldTrim",COL["interior"],12)

# Collision v003 matches the deeper physical chamber and existing accepted route.
cylinder("COLL_V003_ChediCore",(0,0,20),17.0,40.0,"HNP_Chedi_Collision",COL["collision"],32)
annulus("COLL_V003_UpperWalk",22.9,29.05,-.24,-.16,"HNP_Chedi_Collision",COL["collision"],48)
annulus("COLL_V003_LowerCourt",28.95,37.05,-2.66,-2.58,"HNP_Chedi_Collision",COL["collision"],48)
box("COLL_V003_ChamberLeft",(-3.82,-21.55,4.65),(.30,13.2,9.3),"HNP_Chedi_Collision",COL["collision"])
box("COLL_V003_ChamberRight",(3.82,-21.55,4.65),(.30,13.2,9.3),"HNP_Chedi_Collision",COL["collision"])
box("COLL_V003_ChamberBack",(0,-15.08,4.6),(7.4,.30,9.2),"HNP_Chedi_Collision",COL["collision"])
box("COLL_V003_PrayerFloor",(0,-21.45,-.03),(7.35,12.35,.10),"HNP_Chedi_Collision",COL["collision"])
for cardinal,angle in enumerate((-math.pi/2,0,math.pi/2,math.pi)):
    radial=Vector((math.cos(angle),math.sin(angle),0))
    for step in range(8):
        radius=29.45+step*.82; z=-.15-step*.30; center=radial*radius
        box(f"COLL_V003_Stair_{cardinal}_{step}",(center.x,center.y,z-.17),(6.62,.92,.34),
            "HNP_Chedi_Collision",COL["collision"],rotation=angle+math.pi/2)

for target in COL.values():
    for obj in target.objects:
        ensure_uv(obj)


def join_by_material(target,prefix):
    groups={}
    for obj in list(target.objects):
        if obj.type!="MESH": continue
        key=next((mat.name for mat in obj.data.materials if mat),"NoMaterial")
        groups.setdefault(key,[]).append(obj)
    for key,objects in groups.items():
        bpy.ops.object.select_all(action="DESELECT")
        for obj in objects: obj.select_set(True)
        bpy.context.view_layer.objects.active=objects[0]
        if len(objects)>1: bpy.ops.object.join()
        objects[0].name=f"{prefix}__{key}"

for key,prefix in (("core","HNP_Chedi_v003_M01_Core"),("exterior","HNP_Chedi_v003_M02_Exterior"),
                   ("shell","HNP_Chedi_v003_M03_ApprovedFacade"),("interior","HNP_Chedi_v003_M04_DeepInterior"),
                   ("collision","COLL_HNP_Chedi_v003_M05")):
    join_by_material(COL[key],prefix)


def mesh_objects(target): return [obj for obj in target.objects if obj.type=="MESH"]

def metrics(objects):
    objects=list(objects); points=[obj.matrix_world@v.co for obj in objects for v in obj.data.vertices]
    low=Vector((min(p.x for p in points),min(p.y for p in points),min(p.z for p in points)))
    high=Vector((max(p.x for p in points),max(p.y for p in points),max(p.z for p in points)))
    triangles=vertices=degenerate=loose=0; mats=set(); uv_missing=[]; negative=[]
    for obj in objects:
        obj.data.calc_loop_triangles(); triangles+=len(obj.data.loop_triangles); vertices+=len(obj.data.vertices)
        mats.update(mat.name for mat in obj.data.materials if mat)
        if not obj.data.uv_layers: uv_missing.append(obj.name)
        if any(value<0 for value in obj.scale): negative.append(obj.name)
        bm=bmesh.new(); bm.from_mesh(obj.data)
        degenerate+=sum(1 for f in bm.faces if f.calc_area()<1e-10); loose+=sum(1 for v in bm.verts if not v.link_edges); bm.free()
    return {"min_m":[round(v,6) for v in low],"max_m":[round(v,6) for v in high],"dimensions_m":[round(v,6) for v in high-low],
            "triangles":triangles,"vertices":vertices,"mesh_count":len(objects),"materials":sorted(mats),"material_count":len(mats),
            "uv0_missing":uv_missing,"negative_scale":negative,"degenerate_faces":degenerate,"loose_vertices":loose}

module_metrics={key:metrics(mesh_objects(value)) for key,value in COL.items()}
visible=sum((mesh_objects(COL[key]) for key in ("core","exterior","shell","interior")),[])
visible_metrics=metrics(visible); collision_metrics=metrics(mesh_objects(COL["collision"]))
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE_BLEND))

def export(objects,path):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects: obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={"MESH"},axis_forward="-Z",axis_up="Y",
        add_leaf_bones=False,bake_anim=False,apply_unit_scale=True,apply_scale_options="FBX_SCALE_UNITS",path_mode="COPY",embed_textures=False)

module_files={"core":"HNP_Chedi_M01_Core_v003.fbx","exterior":"HNP_Chedi_M02_ExteriorWalk_v003.fbx",
              "shell":"HNP_Chedi_M03_ReferenceFacade_v003.fbx","interior":"HNP_Chedi_M04_DeepSanctuaryInterior_v003.fbx",
              "collision":"HNP_Chedi_M05_Collision_v003.fbx"}
exports={}
for key,filename in module_files.items():
    path=OUT/filename; export(mesh_objects(COL[key]),path); exports[key]=path
combined=OUT/"HNP_Chedi_Modular_ProductionStaging_v003.fbx"; export(visible,combined); exports["combined_visible"]=combined

def render_preview(filename,location,target,lens,resolution,interior=False):
    for obj in COL["collision"].objects: obj.hide_render=True
    bpy.ops.object.camera_add(location=location); camera=bpy.context.object; camera.data.lens=lens
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler(); scene.camera=camera
    bpy.ops.object.light_add(type="SUN",location=(28,-45,52)); sun=bpy.context.object
    sun.rotation_euler=(math.radians(27),math.radians(-17),math.radians(-37)); sun.data.energy=2.15; sun.data.color=(1,.82,.62); sun.data.angle=math.radians(8)
    bpy.ops.object.light_add(type="AREA",location=(-25,-30,27)); area=bpy.context.object; area.data.energy=1450; area.data.size=18; area.data.color=(.55,.70,1)
    area.rotation_euler=(Vector(target)-area.location).to_track_quat("-Z","Y").to_euler(); lights=[camera,sun,area]
    if interior:
        for x in (-2.4,2.4):
            bpy.ops.object.light_add(type="POINT",location=(x,-20.8,5.5)); point=bpy.context.object
            point.data.energy=360; point.data.color=(1,.58,.28); point.data.shadow_soft_size=2.2; lights.append(point)
    scene.world.use_nodes=True; bg=scene.world.node_tree.nodes.get("Background"); bg.inputs[0].default_value=(.2,.27,.34,1); bg.inputs[1].default_value=.58
    scene.render.resolution_x,scene.render.resolution_y=resolution; scene.render.filepath=str(OUT/filename); bpy.ops.render.render(write_still=True)
    for obj in lights: bpy.data.objects.remove(obj,do_unlink=True)

previews=[
    ("HNP_Chedi_v003_preview_approach.png",(0,-96,3.0),(0,0,17.0),30,(1280,720),False),
    ("HNP_Chedi_v003_preview_three-quarter.png",(58,-76,10.0),(0,0,16.0),32,(1280,720),False),
    ("HNP_Chedi_v003_preview_facade-walkway.png",(16,-45,2.2),(0,-19,4.0),34,(1280,720),False),
    ("HNP_Chedi_v003_preview_prayer-depth.png",(0,-29.8,1.75),(0,-15.4,4.45),28,(1280,720),True),
]
for item in previews: render_preview(*item)

def roundtrip(path,expected):
    before=set(bpy.data.objects); bpy.ops.import_scene.fbx(filepath=str(path),automatic_bone_orientation=False)
    imported=[obj for obj in bpy.data.objects if obj not in before and obj.type=="MESH"]; observed=metrics(imported)
    delta=max(abs(a-b) for a,b in zip(expected["dimensions_m"],observed["dimensions_m"]))
    result={"status":"PASS" if observed["triangles"]==expected["triangles"] and delta<.001 else "FAIL",
            "expected_triangles":expected["triangles"],"observed_triangles":observed["triangles"],"max_dimension_delta_m":round(delta,8),
            "observed_dimensions_m":observed["dimensions_m"],"mesh_count":observed["mesh_count"]}
    for obj in imported: bpy.data.objects.remove(obj,do_unlink=True)
    return result

roundtrips={}
for key,path in exports.items(): roundtrips[path.name]=roundtrip(path,visible_metrics if key=="combined_visible" else module_metrics[key])
roundtrip_path=OUT/"roundtrip-v003.json"; roundtrip_path.write_text(json.dumps({"blender_version":bpy.app.version_string,"exports":roundtrips},indent=2),encoding="utf-8")

source_pass=(visible_metrics["triangles"]<=30000 and visible_metrics["degenerate_faces"]==0 and visible_metrics["loose_vertices"]==0 and not visible_metrics["uv0_missing"] and not visible_metrics["negative_scale"])
roundtrip_pass=all(item["status"]=="PASS" for item in roundtrips.values())
manifest={"task_id":"HNP-ART-CHEDI-001","revision":"v003","supersedes":"v002 visual review FAIL; v001/v002 preserved",
 "classification":"reference-led production-staging; pending independent v003 visual review",
 "status":{"blender_cli":"PASS","source_geometry":"PASS" if source_pass else "FAIL","visible_triangle_budget_le_30000":"PASS" if visible_metrics["triangles"]<=30000 else "FAIL","fbx_roundtrip":"PASS" if roundtrip_pass else "FAIL","designer_visual_review":"NOT RUN","unity_import_prefab_collision":"NOT RUN","mobile_web_performance":"NOT RUN"},
 "v003_visual_response":{"macro":"Uses independently approved HNP-WORLD-010 bell/lower-ring/open-gallery/ribbed-spire geometry rather than v002 invented dome; high-density gold surfaces reduced only after cavity cut.",
   "facade_gable":"Uses approved v010 layered terracotta lower mass, continuous white articulated façade, front gable/sanctuary hierarchy and original photo-led architecture; v002 open stair rails retained.",
   "prayer_depth":"12.35 m physical floor, three-step threshold, quiet wall liners, ceiling ribs, kneeling zone, shallow altar and back recess; unchanged photo is 14.19 m beyond preview camera."},
 "units":"metres","axis":{"blender_up":"+Z","local_front":"-Y","fbx_forward":"-Z","fbx_up":"Y"},"pivot":"origin at Chedi centre / upper route z=0",
 "dimensions":{"combined_visible_bounds":visible_metrics,"collision_bounds":collision_metrics,"body_nominal_diameter_m":46.43,"complex_outer_diameter_m":74.0,"total_height_m":44.0,"prayer_room_floor_depth_m":12.35,"upper_walk_surface_z_m":0.0,"lower_court_surface_z_m":-2.4},
 "modules":{key:{"file":module_files[key],"metrics":module_metrics[key]} for key in module_files},"combined_visible_export":{"file":combined.name,"metrics":visible_metrics},
 "materials":{"count_combined_visible":visible_metrics["material_count"],"names":visible_metrics["materials"],"photo_texture":{"source_reference":"ref/pra.jpg","source_copy":str(PHOTO_SRC.relative_to(ROOT)).replace("\\","/"),"export_copy":str(PHOTO_OUT.relative_to(ROOT)).replace("\\","/"),"dimensions_px":[387,792],"color_space":"sRGB","uv":"UV0 full-frame upright; no crop/mirror","sha256":hashlib.sha256(PHOTO_REF.read_bytes()).hexdigest(),"copies_hash_match":hashlib.sha256(PHOTO_REF.read_bytes()).digest()==hashlib.sha256(PHOTO_SRC.read_bytes()).digest()==hashlib.sha256(PHOTO_OUT.read_bytes()).digest()},"unity_consolidation_plan":"Reuse one opaque shader and bake flat architectural palette into one atlas/LUT; retain pra.jpg as dedicated material. Target architecture opaque + interior accent + photo = 3 runtime groups; verify in Unity."},
 "walkability_contract":{"player_clearance_assumption":"capsule <=0.8 m diameter / <=2.2 m height provisional","front_chamber_clear_width_m":7.25,"front_chamber_floor_depth_m":12.35,"four_cardinal_stair_clear_width_m":5.8,"collision_export":module_files["collision"],"status":"Blender staging PASS; Unity traversal NOT RUN"},
 "references":{"approved_architecture_source":["art-source/hnp-world-010/HNP_Chedi_v010.blend","reports/reviews/HNP-WORLD-010-staging.md"],"macro":["ref/jd.jpg"],"collar_spire":["ref/IMG_20211023_161037.jpg","ref/IMG_20211023_161317.jpg"],"facade":["ref/IMG_20211023_160913.jpg","ref/IMG_20211023_161123.jpg"],"stairs":["ref/IMG_20211023_161403.jpg"],"prayer":["ref/pra.jpg"]},
 "provisional_invented_details":["Metres remain gameplay-scale without architectural survey.","Deepened room, rear wall, ceiling ribs, kneeling zone, altar and lighting are declared gameplay adaptations.","Exact rear/side elevations and functional collider conversion remain unverified.","Decimation retains macro form but final Unity shading/draw-call result is NOT RUN."],
 "roundtrip":{"report":roundtrip_path.name,"exports":roundtrips},"source":{"blend":str(SOURCE_BLEND.relative_to(ROOT)).replace("\\","/"),"generator":str(Path(__file__).relative_to(ROOT)).replace("\\","/"),"v002_route_baseline":str(BASE_BLEND.relative_to(ROOT)).replace("\\","/"),"approved_architecture_read_only":str(REFERENCE_BLEND.relative_to(ROOT)).replace("\\","/")},"previews":[item[0] for item in previews]}
hash_targets=[SOURCE_BLEND,Path(__file__),roundtrip_path,PHOTO_SRC,PHOTO_OUT,*exports.values(),*(OUT/item[0] for item in previews)]
manifest["sha256"]={str(path.relative_to(ROOT)).replace("\\","/"):hashlib.sha256(path.read_bytes()).hexdigest() for path in hash_targets}
manifest_path=OUT/"manifest-v003.json"; manifest_path.write_text(json.dumps(manifest,indent=2),encoding="utf-8")
if any(value=="FAIL" for value in manifest["status"].values()): raise RuntimeError(json.dumps(manifest["status"]))
print("HNP_ART_CHEDI_001_V003_PASS",json.dumps(manifest["status"]))
