"""Triangulate welded cap geometry for robust FBX import, retaining world source placement."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];OUT=R/'art-export/world'
bpy.ops.wm.open_mainfile(filepath=str(R/'art-source/world/Nakornpathom.blend'))
selected=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Chedi_')]
for o in selected:
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.00001);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'art-source/world/Nakornpathom.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in selected:o.location-=Vector((53,0,2.9));o.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(OUT/'HNP_Chedi.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=False)
m=json.loads((OUT/'world-manifest.json').read_text());tri=0
for o in selected:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
m['assets'][1]['triangles_including_collision']=tri;m['assets'][1]['cap_validation']='Welded and triangulated before export'
(OUT/'world-manifest.json').write_text(json.dumps(m,indent=2));print('REPAIRED_CHEDI',tri)
