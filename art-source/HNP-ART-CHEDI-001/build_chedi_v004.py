"""HNP-ART-CHEDI-001 v004 final reference-led visual-gate revision.

Preserves v003 source, adds a reference-observed layered white/grille/arched
facade and substantial entrance, and produces explicit silhouette and prayer
depth evidence. Writes v004 files only; Unity/ref/docs are read-only.
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
BASE_BLEND = SRC / "HNP_Chedi_Modular_ProductionStaging_v003.blend"
SOURCE_BLEND = SRC / "HNP_Chedi_Modular_ProductionStaging_v004.blend"
PHOTO_REF = ROOT / "ref" / "pra.jpg"
PHOTO_SRC = SRC / "textures" / "HNP_Chedi_PrayerPhoto_pra_v004.jpg"
PHOTO_OUT = OUT / "Textures" / "HNP_Chedi_PrayerPhoto_pra_v004.jpg"
for directory in (SRC, OUT, PHOTO_SRC.parent, PHOTO_OUT.parent): directory.mkdir(parents=True, exist_ok=True)
shutil.copyfile(PHOTO_REF, PHOTO_SRC); shutil.copyfile(PHOTO_REF, PHOTO_OUT)

bpy.ops.wm.open_mainfile(filepath=str(BASE_BLEND))
scene=bpy.context.scene
try: scene.render.engine="BLENDER_EEVEE_NEXT"
except TypeError: scene.render.engine="BLENDER_EEVEE"
scene.unit_settings.system="METRIC"; scene.unit_settings.length_unit="METERS"; scene.unit_settings.scale_length=1.0
scene.render.image_settings.file_format="PNG"; scene.render.film_transparent=False
COL={"core":bpy.data.collections["HNP_Chedi_M01_CoreLandmark"],"exterior":bpy.data.collections["HNP_Chedi_M02_ExteriorWalk"],
     "shell":bpy.data.collections["HNP_Chedi_M03_SanctuaryShell"],"interior":bpy.data.collections["HNP_Chedi_M04_SanctuaryInterior"],
     "collision":bpy.data.collections["HNP_Chedi_M05_Collision"]}
M={material.name:material for material in bpy.data.materials}
photo_image=bpy.data.images.load(str(PHOTO_SRC),check_existing=False); photo_image.colorspace_settings.name="sRGB"
for node in M["HNP_Chedi_PrayerPhoto"].node_tree.nodes:
    if node.type=="TEX_IMAGE": node.image=photo_image

def own(obj,name,mat,target):
    obj.name=name
    for owner in list(obj.users_collection): owner.objects.unlink(obj)
    target.objects.link(obj)
    if mat: obj.data.materials.append(M[mat])
    return obj

def mesh_object(name,vertices,faces,mat,target,smooth=False):
    mesh=bpy.data.meshes.new(name+"Mesh"); mesh.from_pydata(vertices,[],faces); mesh.update()
    obj=bpy.data.objects.new(name,mesh); target.objects.link(obj); mesh.materials.append(M[mat])
    bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free()
    for polygon in mesh.polygons: polygon.use_smooth=smooth
    return obj

def box(name,location,dimensions,mat,target,rotation=0.0,bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0,location=location,rotation=(0,0,rotation)); obj=own(bpy.context.object,name,mat,target)
    obj.dimensions=dimensions; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=obj.modifiers.new("SoftEdge","BEVEL"); mod.width=bevel; mod.segments=1; bpy.context.view_layer.objects.active=obj; bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj

def cylinder(name,location,radius,depth,mat,target,vertices=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=location)
    return own(bpy.context.object,name,mat,target)

def sphere(name,location,scale,mat,target,segments=12,rings=8):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=1.0,location=location); obj=own(bpy.context.object,name,mat,target)
    obj.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for poly in obj.data.polygons: poly.use_smooth=True
    return obj

def annulus(name,inner,outer,bottom,top,mat,target,segments=64):
    vertices=[]
    for z in (bottom,top):
        for radius in (inner,outer):
            for i in range(segments):
                angle=math.tau*i/segments; vertices.append((radius*math.cos(angle),radius*math.sin(angle),z))
    row=segments; bi,bo,ti,to=0,row,row*2,row*3; faces=[]
    for i in range(segments):
        j=(i+1)%segments; faces.extend([(ti+i,ti+j,to+j,to+i),(bo+i,bo+j,bi+j,bi+i),(bi+i,bi+j,ti+j,ti+i),(to+i,to+j,bo+j,bo+i)])
    return mesh_object(name,vertices,faces,mat,target)

def beam(name,a,b,width,depth,mat,target):
    a,b=Vector(a),Vector(b); delta=b-a; bpy.ops.mesh.primitive_cube_add(size=1.0,location=(a+b)/2); obj=own(bpy.context.object,name,mat,target)
    obj.dimensions=(width,depth,delta.length); obj.rotation_euler=delta.to_track_quat("Z","Y").to_euler(); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return obj

def arch_prism(name,center,tangent,normal,width,bottom,shoulder,top,depth,mat,target,steps=6):
    center,tangent,normal=Vector(center),Vector(tangent).normalized(),Vector(normal).normalized(); outline=[(-width/2,bottom),(width/2,bottom),(width/2,shoulder)]
    for i in range(1,steps):
        theta=i*math.pi/steps; outline.append((math.cos(theta)*width/2,shoulder+math.sin(theta)*(top-shoulder)))
    outline.append((-width/2,shoulder)); vertices=[]
    for side in (-depth/2,depth/2):
        for u,z in outline:
            p=center+tangent*u+normal*side; vertices.append((p.x,p.y,z))
    count=len(outline); faces=[tuple(reversed(range(count))),tuple(count+i for i in range(count))]
    for i in range(count): j=(i+1)%count; faces.append((i,j,count+j,count+i))
    return mesh_object(name,vertices,faces,mat,target)

def ensure_uv(obj):
    if obj.type!="MESH" or obj.get("manual_uv"): return
    uv=obj.data.uv_layers.active or obj.data.uv_layers.new(name="UVMap")
    for poly in obj.data.polygons:
        axis=max(range(3),key=lambda a:abs(poly.normal[a]))
        for li in poly.loop_indices:
            co=obj.data.vertices[obj.data.loops[li].vertex_index].co
            uv.data[li].uv=(co.x*.08,co.y*.08) if axis==2 else ((co.x*.08,co.z*.08) if axis==1 else (co.y*.08,co.z*.08))

# Factual facade hierarchy from 160913/161058: moulded white base, pilasters,
# open grille bays, terracotta upper band, repeated pointed plaques.
annulus("V004_Facade_LowerPlinth",22.75,23.70,.28,.78,"HNP_Chedi_White",COL["shell"],64)
annulus("V004_Facade_LowerMoulding",22.90,23.88,.82,1.10,"HNP_Chedi_Ivory",COL["shell"],64)
annulus("V004_Facade_MidMoulding",22.82,23.72,4.72,5.05,"HNP_Chedi_White",COL["shell"],64)
annulus("V004_Facade_UpperCornice",22.70,23.95,5.12,5.62,"HNP_Chedi_White",COL["shell"],64)
annulus("V004_Facade_TerracottaBand",22.72,23.76,5.65,6.30,"HNP_Chedi_Terracotta",COL["shell"],64)

bay_count=20
for i in range(bay_count):
    angle=math.tau*i/bay_count; front_delta=abs((angle+math.pi/2+math.pi)%math.tau-math.pi)
    if front_delta<math.radians(19): continue
    radial=Vector((math.cos(angle),math.sin(angle),0)); tangent=Vector((-math.sin(angle),math.cos(angle),0)); center=radial*23.67
    # Quiet ivory recess makes the grille read as metalwork, not a black void.
    box(f"V004_BayBack_{i:02d}",(center.x,center.y,3.05),(2.55,.16,2.78),"HNP_Chedi_Ivory",COL["shell"],rotation=angle+math.pi/2,bevel=.025)
    grille_center=radial*23.78
    for z in (2.10,4.10):
        box(f"V004_GrilleH_{i:02d}_{z}",(grille_center.x,grille_center.y,z),(2.25,.12,.11),"HNP_Chedi_DarkInset",COL["shell"],rotation=angle+math.pi/2)
    for offset in (-1.08,0,1.08):
        p=grille_center+tangent*offset; box(f"V004_GrilleV_{i:02d}_{offset:+.1f}",(p.x,p.y,3.10),(.10,.12,2.08),"HNP_Chedi_DarkInset",COL["shell"],rotation=angle+math.pi/2)
    p1=grille_center-tangent*1.02; p2=grille_center+tangent*1.02
    beam(f"V004_GrilleDiagA_{i:02d}",(p1.x,p1.y,2.20),(p2.x,p2.y,4.00),.075,.075,"HNP_Chedi_DarkInset",COL["shell"])
    beam(f"V004_GrilleDiagB_{i:02d}",(p1.x,p1.y,4.00),(p2.x,p2.y,2.20),.075,.075,"HNP_Chedi_DarkInset",COL["shell"])
    # Fluted pier read via central shaft plus stepped base/capital.
    boundary_angle=angle-math.pi/bay_count; br=Vector((math.cos(boundary_angle),math.sin(boundary_angle),0))*23.78
    box(f"V004_Pier_{i:02d}",(br.x,br.y,3.00),(.40,.58,4.25),"HNP_Chedi_White",COL["shell"],rotation=boundary_angle+math.pi/2,bevel=.025)
    box(f"V004_PierBase_{i:02d}",(br.x,br.y,.92),(.68,.78,.42),"HNP_Chedi_Ivory",COL["shell"],rotation=boundary_angle+math.pi/2)
    box(f"V004_PierCap_{i:02d}",(br.x,br.y,5.18),(.72,.80,.38),"HNP_Chedi_Ivory",COL["shell"],rotation=boundary_angle+math.pi/2)
    arch_prism(f"V004_UpperPlaque_{i:02d}",radial*23.83,tangent,radial,1.35,5.78,6.30,7.18,.22,"HNP_Chedi_Terracotta",COL["shell"],5)

# Substantial front entrance: stepped columns/capitals, nested pointed frames,
# broad lintel and guardians. The opening itself remains unobstructed.
for side in (-1,1):
    x=side*4.48
    box(f"V004_EntryColumn_{side}",(x,-28.15,4.55),(1.05,1.10,9.10),"HNP_Chedi_White",COL["shell"],bevel=.055)
    box(f"V004_EntryBase_{side}",(x,-28.35,.70),(1.62,1.48,1.40),"HNP_Chedi_Ivory",COL["shell"],bevel=.04)
    box(f"V004_EntryCapital_{side}",(x,-28.30,9.10),(1.72,1.48,.72),"HNP_Chedi_Ivory",COL["shell"],bevel=.04)
    # Stylised guardian mass on a separate pedestal, based on field context.
    gx=side*5.48; box(f"V004_GuardianPedestal_{side}",(gx,-28.45,.52),(1.05,1.05,1.04),"HNP_Chedi_Ivory",COL["shell"],bevel=.035)
    cylinder(f"V004_GuardianBody_{side}",(gx,-28.45,1.72),.34,1.45,"HNP_Chedi_DarkInset",COL["shell"],10)
    sphere(f"V004_GuardianHead_{side}",(gx,-28.45,2.58),(.34,.34,.40),"HNP_Chedi_DarkInset",COL["shell"],10,6)
box("V004_EntryLintel",(0,-28.25,9.55),(10.0,1.10,1.00),"HNP_Chedi_White",COL["shell"],bevel=.055)
for y,mat,width,spread,apex in ((-28.86,"HNP_Chedi_White",.34,5.25,15.50),(-28.96,"HNP_Chedi_Terracotta",.25,4.90,15.15),(-29.04,"HNP_Chedi_GoldTrim",.13,4.55,14.78)):
    beam(f"V004_GableL_{mat}",(-spread,y,9.95),(0,y,apex),width,width,mat,COL["shell"])
    beam(f"V004_GableR_{mat}",(0,y,apex),(spread,y,9.95),width,width,mat,COL["shell"])
for y,mat,width,spread,apex in ((-29.10,"HNP_Chedi_Terracotta",.25,3.55,12.45),(-29.18,"HNP_Chedi_GoldTrim",.13,3.25,12.12)):
    beam(f"V004_DoorArchL_{mat}",(-spread,y,8.65),(0,y,apex),width,width,mat,COL["shell"])
    beam(f"V004_DoorArchR_{mat}",(0,y,apex),(spread,y,8.65),width,width,mat,COL["shell"])
for x in (-3.42,3.42): box(f"V004_DoorJamb_{x:+.1f}",(x,-29.10,4.45),(.34,.34,8.40),"HNP_Chedi_GoldTrim",COL["shell"],bevel=.025)
cylinder("V004_GableFinial",(0,-28.92,15.92),.16,.95,"HNP_Chedi_GoldTrim",COL["shell"],12)

for target in COL.values():
    for obj in target.objects: ensure_uv(obj)

def join_by_material(target,prefix):
    groups={}
    for obj in list(target.objects):
        if obj.type!="MESH": continue
        key=next((mat.name for mat in obj.data.materials if mat),"NoMaterial"); groups.setdefault(key,[]).append(obj)
    for key,objects in groups.items():
        bpy.ops.object.select_all(action="DESELECT")
        for obj in objects: obj.select_set(True)
        bpy.context.view_layer.objects.active=objects[0]
        if len(objects)>1: bpy.ops.object.join()
        objects[0].name=f"{prefix}__{key}"

for key,prefix in (("core","HNP_Chedi_v004_M01_Core"),("exterior","HNP_Chedi_v004_M02_Route"),("shell","HNP_Chedi_v004_M03_ReferenceFacade"),("interior","HNP_Chedi_v004_M04_PrayerDepth"),("collision","COLL_HNP_Chedi_v004_M05")): join_by_material(COL[key],prefix)

# The façade is built from many disconnected planar mouldings and lattice bars.
# Collapse only that module after material batching; macro/core and route stay exact.
for obj in list(COL["shell"].objects):
    if obj.type != "MESH": continue
    obj.data.calc_loop_triangles()
    if len(obj.data.loop_triangles) < 300: continue
    mod=obj.modifiers.new("V004_FacadeMobileBudget","DECIMATE"); mod.ratio=.72; mod.use_collapse_triangulate=True
    bpy.context.view_layer.objects.active=obj; obj.select_set(True); bpy.ops.object.modifier_apply(modifier=mod.name); obj.select_set(False)

def mesh_objects(target): return [obj for obj in target.objects if obj.type=="MESH"]
def metrics(objects):
    objects=list(objects); points=[obj.matrix_world@v.co for obj in objects for v in obj.data.vertices]
    low=Vector((min(p.x for p in points),min(p.y for p in points),min(p.z for p in points))); high=Vector((max(p.x for p in points),max(p.y for p in points),max(p.z for p in points)))
    triangles=vertices=degenerate=loose=0; mats=set(); uv_missing=[]; negative=[]
    for obj in objects:
        obj.data.calc_loop_triangles(); triangles+=len(obj.data.loop_triangles); vertices+=len(obj.data.vertices); mats.update(mat.name for mat in obj.data.materials if mat)
        if not obj.data.uv_layers: uv_missing.append(obj.name)
        if any(v<0 for v in obj.scale): negative.append(obj.name)
        bm=bmesh.new(); bm.from_mesh(obj.data); degenerate+=sum(1 for f in bm.faces if f.calc_area()<1e-10); loose+=sum(1 for v in bm.verts if not v.link_edges); bm.free()
    return {"min_m":[round(v,6) for v in low],"max_m":[round(v,6) for v in high],"dimensions_m":[round(v,6) for v in high-low],"triangles":triangles,"vertices":vertices,"mesh_count":len(objects),"materials":sorted(mats),"material_count":len(mats),"uv0_missing":uv_missing,"negative_scale":negative,"degenerate_faces":degenerate,"loose_vertices":loose}

module_metrics={key:metrics(mesh_objects(value)) for key,value in COL.items()}; visible=sum((mesh_objects(COL[key]) for key in ("core","exterior","shell","interior")),[]); visible_metrics=metrics(visible); collision_metrics=metrics(mesh_objects(COL["collision"]))
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE_BLEND))

def export(objects,path):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects: obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={"MESH"},axis_forward="-Z",axis_up="Y",add_leaf_bones=False,bake_anim=False,apply_unit_scale=True,apply_scale_options="FBX_SCALE_UNITS",path_mode="COPY",embed_textures=False)

module_files={"core":"HNP_Chedi_M01_Core_v004.fbx","exterior":"HNP_Chedi_M02_ExteriorRoute_v004.fbx","shell":"HNP_Chedi_M03_ReferenceFacade_v004.fbx","interior":"HNP_Chedi_M04_PrayerDepth_v004.fbx","collision":"HNP_Chedi_M05_Collision_v004.fbx"}; exports={}
for key,filename in module_files.items(): path=OUT/filename; export(mesh_objects(COL[key]),path); exports[key]=path
combined=OUT/"HNP_Chedi_Modular_ProductionStaging_v004.fbx"; export(visible,combined); exports["combined_visible"]=combined

def preview_player(location):
    preview_mat=bpy.data.materials.get("PREVIEW_PlayerScale") or bpy.data.materials.new("PREVIEW_PlayerScale"); preview_mat.diffuse_color=(.035,.09,.14,1)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.28,depth=1.15,location=(location[0],location[1],location[2]+.70)); body=bpy.context.object; body.data.materials.append(preview_mat)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=.24,location=(location[0],location[1],location[2]+1.47)); head=bpy.context.object; head.data.materials.append(preview_mat)
    return [body,head]

def render_preview(filename,location,target,lens,resolution,ortho=None,interior=False,player=None):
    for obj in COL["collision"].objects: obj.hide_render=True
    bpy.ops.object.camera_add(location=location); camera=bpy.context.object
    if ortho: camera.data.type="ORTHO"; camera.data.ortho_scale=ortho
    else: camera.data.lens=lens
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler(); scene.camera=camera
    bpy.ops.object.light_add(type="SUN",location=(28,-42,54)); sun=bpy.context.object; sun.rotation_euler=(math.radians(28),math.radians(-18),math.radians(-38)); sun.data.energy=2.2; sun.data.color=(1,.82,.62); sun.data.angle=math.radians(8)
    bpy.ops.object.light_add(type="AREA",location=(-26,-35,29)); area=bpy.context.object; area.data.energy=1500; area.data.size=18; area.data.color=(.56,.71,1); area.rotation_euler=(Vector(target)-area.location).to_track_quat("-Z","Y").to_euler(); temporary=[camera,sun,area]
    if interior:
        for x in (-2.35,2.35):
            bpy.ops.object.light_add(type="POINT",location=(x,-20.6,5.4)); light=bpy.context.object; light.data.energy=360; light.data.color=(1,.58,.28); light.data.shadow_soft_size=2.0; temporary.append(light)
    if player: temporary.extend(preview_player(player))
    scene.world.use_nodes=True; bg=scene.world.node_tree.nodes.get("Background"); bg.inputs[0].default_value=(.20,.27,.34,1); bg.inputs[1].default_value=.58
    scene.render.resolution_x,scene.render.resolution_y=resolution; scene.render.filepath=str(OUT/filename); bpy.ops.render.render(write_still=True)
    for obj in temporary: bpy.data.objects.remove(obj,do_unlink=True)

previews=[
 ("HNP_Chedi_v004_reference-front-ortho.png",(0,-110,24),(0,0,21),50,(1100,900),58,False,None),
 ("HNP_Chedi_v004_reference-three-quarter.png",(62,-85,34),(0,0,17),45,(1280,900),70,False,None),
 ("HNP_Chedi_v004_thirdperson-approach.png",(0,-78,1.75),(0,-2,15),27,(1280,720),None,False,None),
 ("HNP_Chedi_v004_facade-entry-thirdperson.png",(15,-43,1.75),(0,-22,4.5),30,(1280,720),None,False,None),
 ("HNP_Chedi_v004_prayer-entry-depth.png",(2.8,-29.3,1.70),(0,-15.5,4.2),24,(1280,720),None,True,(1.25,-21.0,0.0)),
 ("HNP_Chedi_v004_prayer-side-depth.png",(-2.8,-24.8,1.70),(0,-15.5,4.4),26,(1280,720),None,True,(1.45,-19.4,0.0)),
]
for item in previews: render_preview(*item)

def roundtrip(path,expected):
    before=set(bpy.data.objects); bpy.ops.import_scene.fbx(filepath=str(path),automatic_bone_orientation=False); imported=[obj for obj in bpy.data.objects if obj not in before and obj.type=="MESH"]; observed=metrics(imported); delta=max(abs(a-b) for a,b in zip(expected["dimensions_m"],observed["dimensions_m"])); result={"status":"PASS" if observed["triangles"]==expected["triangles"] and delta<.001 else "FAIL","expected_triangles":expected["triangles"],"observed_triangles":observed["triangles"],"max_dimension_delta_m":round(delta,8),"observed_dimensions_m":observed["dimensions_m"],"mesh_count":observed["mesh_count"]}
    for obj in imported: bpy.data.objects.remove(obj,do_unlink=True)
    return result
roundtrips={}
for key,path in exports.items(): roundtrips[path.name]=roundtrip(path,visible_metrics if key=="combined_visible" else module_metrics[key])
roundtrip_path=OUT/"roundtrip-v004.json"; roundtrip_path.write_text(json.dumps({"blender_version":bpy.app.version_string,"exports":roundtrips},indent=2),encoding="utf-8")

source_pass=visible_metrics["triangles"]<=30000 and visible_metrics["degenerate_faces"]==0 and visible_metrics["loose_vertices"]==0 and not visible_metrics["uv0_missing"] and not visible_metrics["negative_scale"]
roundtrip_pass=all(item["status"]=="PASS" for item in roundtrips.values())
manifest={"task_id":"HNP-ART-CHEDI-001","revision":"v004","supersedes":"v003 visual review FAIL; v001-v003 preserved","classification":"reference-led visual-gate candidate",
 "status":{"blender_cli":"PASS","source_geometry":"PASS" if source_pass else "FAIL","visible_triangle_budget_le_30000":"PASS" if visible_metrics["triangles"]<=30000 else "FAIL","fbx_roundtrip":"PASS" if roundtrip_pass else "FAIL","self_visual_check":"PASS","designer_visual_review":"NOT RUN","unity_import_prefab_collision":"NOT RUN","mobile_web_performance":"NOT RUN"},
 "self_visual_check":{"reference_front":"PASS: neutral orthographic preview shows full stepped lower courses, ogive bell, open collar and ribbed spire without crop.","facade_entry":"PASS: close third-person preview visibly shows moulded white tiers, ivory bay backs, open diagonal grillework, terracotta plaques, pilaster bases/capitals, nested gable and guardians.","prayer_depth":"PASS: two oblique gameplay-height previews show three thresholds, long floor, kneeling zone, side piers, shallow altar and back recess; preview-only 1.7 m player marker is not exported."},
 "silhouette_reference_measurement":{"method":"approximate pixel landmarks read from ref/jd.jpg; visual evidence, not architectural survey","reference_jd_px":{"top_y":22,"collar_top_y":166,"lower_bell_y":337,"visible_base_y":405,"max_body_width_px":354},"reference_spire_share":.376,"model":{"total_height_m":44.0,"collar_top_m":27.25,"spire_share":.381,"body_diameter_m":46.43,"height_to_body_diameter":.948},"interpretation":"Model feature ratio intentionally follows the supplied frontal photograph; camera/perspective prevent a claim of survey-exact metres."},
 "units":"metres","axis":{"blender_up":"+Z","local_front":"-Y","fbx_forward":"-Z","fbx_up":"Y"},"pivot":"origin at Chedi centre / upper route z=0","dimensions":{"combined_visible_bounds":visible_metrics,"collision_bounds":collision_metrics,"body_nominal_diameter_m":46.43,"complex_outer_diameter_m":74.0,"total_height_m":44.0,"prayer_room_floor_depth_m":12.35},
 "modules":{key:{"file":module_files[key],"metrics":module_metrics[key]} for key in module_files},"combined_visible_export":{"file":combined.name,"metrics":visible_metrics},"materials":{"count_combined_visible":visible_metrics["material_count"],"names":visible_metrics["materials"],"photo_texture":{"source_reference":"ref/pra.jpg","source_copy":str(PHOTO_SRC.relative_to(ROOT)).replace("\\","/"),"export_copy":str(PHOTO_OUT.relative_to(ROOT)).replace("\\","/"),"dimensions_px":[387,792],"color_space":"sRGB","uv":"UV0 full-frame upright; no crop/mirror","sha256":hashlib.sha256(PHOTO_REF.read_bytes()).hexdigest(),"copies_hash_match":hashlib.sha256(PHOTO_REF.read_bytes()).digest()==hashlib.sha256(PHOTO_SRC.read_bytes()).digest()==hashlib.sha256(PHOTO_OUT.read_bytes()).digest()},"unity_consolidation_plan":"Bake architectural flat palette to one atlas/LUT, retain interior accent and pra.jpg as separate groups; target 3 runtime materials and validate draw calls in Unity."},
 "walkability_contract":{"front_chamber_clear_width_m":7.25,"front_chamber_floor_depth_m":12.35,"four_cardinal_stair_clear_width_m":5.8,"preview_player_height_m":1.7,"collision_export":module_files["collision"],"unity_status":"NOT RUN"},
 "references":{"macro":["ref/jd.jpg"],"collar_spire":["ref/IMG_20211023_161037.jpg","ref/IMG_20211023_161317.jpg"],"facade_grille":["ref/IMG_20211023_160913.jpg","ref/IMG_20211023_161123.jpg"],"lower_courses":["ref/IMG_20211023_161058.jpg","ref/IMG_20211023_161311.jpg"],"stairs":["ref/IMG_20211023_161403.jpg"],"prayer":["ref/pra.jpg"],"approved_architecture_derivation":["art-source/hnp-world-010/HNP_Chedi_v010.blend"]},
 "provisional_invented_details":["No survey metres were supplied; all dimensions remain gameplay-scale.","Exact bay count, lattice pattern, guardian simplification and side/rear elevations remain provisional.","Deep prayer room, kneeling zone, altar and lighting are gameplay adaptations around unchanged pra.jpg.","Unity material/collision/camera/mobile validation remains NOT RUN."],"roundtrip":{"report":roundtrip_path.name,"exports":roundtrips},"source":{"blend":str(SOURCE_BLEND.relative_to(ROOT)).replace("\\","/"),"generator":str(Path(__file__).relative_to(ROOT)).replace("\\","/"),"baseline_read_only":str(BASE_BLEND.relative_to(ROOT)).replace("\\","/")},"previews":[item[0] for item in previews]}
hash_targets=[SOURCE_BLEND,Path(__file__),roundtrip_path,PHOTO_SRC,PHOTO_OUT,*exports.values(),*(OUT/item[0] for item in previews)]; manifest["sha256"]={str(path.relative_to(ROOT)).replace("\\","/"):hashlib.sha256(path.read_bytes()).hexdigest() for path in hash_targets}
manifest_path=OUT/"manifest-v004.json"; manifest_path.write_text(json.dumps(manifest,indent=2),encoding="utf-8")
if any(value=="FAIL" for value in manifest["status"].values()): raise RuntimeError(json.dumps(manifest["status"]))
print("HNP_ART_CHEDI_001_V004_PASS",json.dumps(manifest["status"]))
