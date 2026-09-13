"""Repair only v004 decorative mouldings crossing its authored prayer corridor.

The source stays at its historical size; Unity applies the measured 120.45 m
uniform scale. The opening is a gameplay adaptation, not a surveyed interior.
"""
import bpy, bmesh, json, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'art-source/HNP-ART-CHEDI-001'
OUT=ROOT/'art-export/HNP-ART-CHEDI-001'
bpy.ops.wm.open_mainfile(filepath=str(SRC/'HNP_Chedi_Modular_ProductionStaging_v004.blend'))
shell=bpy.data.collections['HNP_Chedi_M03_SanctuaryShell']
objects=[o for o in shell.objects if o.type=='MESH']
# The source has disconnected/open decorative surfaces. Clip only existing
# triangles: a solid Boolean invents cutter-box caps on these open surfaces.
planes=[(0,-3.55,1),(0,3.55,-1),(1,-32.5,1),(1,-14.5,-1),(2,-.15,1),(2,9.25,-1)]
def split(poly,axis,bound,sign):
    inside=[];outside=[]
    for i,a in enumerate(poly):
        b=poly[(i+1)%len(poly)]
        da=(a[0][axis]-bound)*sign;db=(b[0][axis]-bound)*sign
        (inside if da>=0 else outside).append(a)
        if (da>=0)!=(db>=0):
            t=da/(da-db);cross=(a[0].lerp(b[0],t),a[1].lerp(b[1],t))
            inside.append(cross);outside.append(cross)
    return inside,outside
changed=[]
for obj in objects:
    old=obj.data;before=len(old.polygons);old.calc_loop_triangles()
    verts=[];faces=[];uvs=[];materials=[]
    for tri in old.loop_triangles:
        poly=[(obj.matrix_world@old.vertices[old.loops[li].vertex_index].co,old.uv_layers.active.data[li].uv.copy()) for li in tri.loops]
        keep=[]
        for axis,bound,sign in planes:
            if len(poly)<3:break
            poly,outside=split(poly,axis,bound,sign)
            if len(outside)>=3:keep.append(outside)
        for piece in keep:
            for i in range(1,len(piece)-1):
                triangle=[piece[0],piece[i],piece[i+1]]
                if (triangle[1][0]-triangle[0][0]).cross(triangle[2][0]-triangle[0][0]).length<1e-9:continue
                start=len(verts);verts.extend(v[0] for v in triangle);uvs.extend(v[1] for v in triangle)
                faces.append((start,start+1,start+2));materials.append(tri.material_index)
    mesh=bpy.data.meshes.new(obj.name+'_v005_Aperture');mesh.from_pydata(verts,[],faces);mesh.update()
    for mat in old.materials:mesh.materials.append(mat)
    uv=mesh.uv_layers.new(name='UVMap')
    for p,mat in zip(mesh.polygons,materials):
        p.material_index=mat
        for li in p.loop_indices:uv.data[li].uv=uvs[mesh.loops[li].vertex_index]
    obj.data=mesh;obj.matrix_world=Matrix.Identity(4)
    bm=bmesh.new();bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
    bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges))
    loose=[v for v in bm.verts if not v.link_faces]
    if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data);bm.free();obj.data.update()
    changed.append({'object':obj.name,'polygonsBefore':before,'polygonsAfter':len(obj.data.polygons)})
objects=[o for o in objects if len(o.data.vertices)]
def metrics(items):
    pts=[o.matrix_world@v.co for o in items for v in o.data.vertices]
    tris=deg=0
    for o in items:
        o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
        deg+=sum(p.area<1e-10 for p in o.data.polygons)
    return {'triangles':tris,'degenerateFaces':deg,'meshes':len(items),'uvMissing':[o.name for o in items if not o.data.uv_layers],
      'boundsMin':[min(p[i] for p in pts) for i in range(3)],'boundsMax':[max(p[i] for p in pts) for i in range(3)]}
result=metrics(objects)
assert result['degenerateFaces']==0 and not result['uvMissing'],result
trees=[(o.name,BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])) for o in objects]
hits=[]
for x in (-2,0,2):
    for z in (.3,.7,1.65,3):
        for name,t in trees:
            p,n,idx,d=t.ray_cast(Vector((x,-32,z)),Vector((0,1,0)),16.8)
            if p is not None:hits.append({'origin':[x,-32,z],'object':name,'point':list(p)})
assert not hits,hits
blend=SRC/'HNP_Chedi_Modular_ProductionStaging_v005.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
fbx=OUT/'HNP_Chedi_M03_ReferenceFacade_v005.fbx'
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',path_mode='COPY',embed_textures=False)
# Render actual retained source plus repaired aperture from player-height scale.
for c in bpy.data.collections:
    if c.name.startswith('HNP_Chedi_M05'):
        for o in c.objects:o.hide_render=True
bpy.ops.object.camera_add(location=(0,-31,.8));cam=bpy.context.object
cam.rotation_euler=(Vector((0,-15.61,3.5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=22
scene=bpy.context.scene;scene.camera=cam
try:scene.render.engine='BLENDER_EEVEE_NEXT'
except TypeError:scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=960;scene.render.resolution_y=540;scene.render.resolution_percentage=100
bpy.ops.object.light_add(type='AREA',location=(0,-25,6));light=bpy.context.object;light.data.energy=1200;light.data.shape='DISK';light.data.size=8
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
scene.render.filepath=str(OUT/'HNP_Chedi_v005_open-prayer-corridor.png');bpy.ops.render.render(write_still=True)
cam.location=(42,-62,28);cam.rotation_euler=(Vector((0,0,18))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=30
bpy.ops.object.light_add(type='SUN',location=(20,-30,50));sun=bpy.context.object;sun.rotation_euler=(.35,-.3,-.5);sun.data.energy=2
scene.render.filepath=str(OUT/'HNP_Chedi_v005_three-quarter.png');bpy.ops.render.render(write_still=True)
# A separate round-trip scene validates export bounds and triangle count.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(fbx))
actual=metrics([o for o in bpy.context.scene.objects if o.type=='MESH'])
assert actual['triangles']==result['triangles'],(result,actual)
assert all(abs(actual[k][i]-result[k][i])<.002 for k in ('boundsMin','boundsMax') for i in range(3)),(result,actual)
bpy.ops.wm.save_as_mainfile(filepath=str(SRC/'HNP_Chedi_M03_v005_roundtrip.blend'))
report={'revision':'v005-aperture','status':'PASS','scope':'M03 only; retain v004 M01 M02 M04. Unity integration NOT RUN.',
 'reason':'v004 added full annular mouldings crossing previously authored interior corridor',
 'source':str(blend.relative_to(ROOT)),'export':str(fbx.relative_to(ROOT)), 'units':'meters','axis':{'up':'Y','forward':'-Z'},
 'provisional':'Opening is adapted to the authored room, not a surveyed historical interior.',
 'changes':changed,'sourceMetrics':result,'roundtripMetrics':actual,'centerlineObstructions':hits,
 'sha256':hashlib.sha256(fbx.read_bytes()).hexdigest()}
(OUT/'manifest-v005-aperture.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('HNP_V005_APERTURE_PASS',json.dumps(report))
