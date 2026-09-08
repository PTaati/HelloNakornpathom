"""Remove the canopy post in the station exit/spawn, preserving all other geometry."""
import bpy,bmesh,json
from pathlib import Path
r=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(r/'art-source/world/Nakornpathom.blend'))
o=bpy.data.objects['Town_HNPW_Teal'];bm=bmesh.new();bm.from_mesh(o.data)
verts=[v for v in bm.verts if abs((o.matrix_world@v.co).x+101)<.13 and abs((o.matrix_world@v.co).y)<.13]
assert len(verts)==8,len(verts)
bmesh.ops.delete(bm,geom=verts,context='VERTS');bm.to_mesh(o.data);bm.free()
bpy.ops.object.select_all(action='DESELECT')
objects=[o for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith('Town_') or o.name=='COLL_Town')]
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.export_scene.fbx(filepath=str(r/'art-export/world/HNP_Town.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=False)
tris=0
for o in objects:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
p=r/'art-export/world/world-manifest.json';data=json.loads(p.read_text());data['assets'][0]['triangles_including_collision']=tris;p.write_text(json.dumps(data,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(r/'art-source/world/Nakornpathom.blend'))
bpy.ops.render.render(write_still=True)
print('STATION_EXIT_CLEAR',tris)
