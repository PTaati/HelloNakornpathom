"""Remove only disconnected old parked-car/train geometry from the existing world.
Retains terrain, road/canal geometry and previous station-exit repairs.
"""
import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'art-export/hnp-world-003'
bpy.ops.wm.open_mainfile(filepath=str(R/'art-source/world/Nakornpathom.blend'))
cars=[(-83,28,1.1,2.1),(-13,-26,1.1,2.1),(-43,2.7,2.1,1.1),(-27,-2.7,2.1,1.1),(104,24,1.1,2.1),(-13,40,1.1,2.1)]
obs=[o for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith('Town_') or o.name=='COLL_Town')]
removed={}
for o in obs:
 bm=bmesh.new();bm.from_mesh(o.data);seen=set();kill=[]
 for start in bm.verts:
  if start in seen:continue
  stack=[start];seen.add(start);comp=[]
  while stack:
   v=stack.pop();comp.append(v)
   for e in v.link_edges:
    n=e.other_vert(v)
    if n not in seen:seen.add(n);stack.append(n)
  pts=[o.matrix_world@v.co for v in comp]
  if max(p.z for p in pts)<.35:continue
  car=any(all(abs(p.x-x)<dx and abs(-p.y-z)<dz and -.05<p.z<2.1 for p in pts) for x,z,dx,dz in cars)
  train=all(-116.6<p.x<-113.4 and -20<-p.y<28 and .25<p.z<3.3 for p in pts)
  if car or train:kill.extend(comp)
 removed[o.name]=len(kill)
 bmesh.ops.delete(bm,geom=kill,context='VERTS');bm.to_mesh(o.data);bm.free()
bpy.ops.object.select_all(action='DESELECT')
for o in obs:o.select_set(True)
bpy.context.view_layer.objects.active=obs[0]
bpy.ops.export_scene.fbx(filepath=str(O/'HNP_Town_v003.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=False)
bpy.ops.wm.save_as_mainfile(filepath=str(Path(__file__).parent/'HNP_Town_v003.blend'))
(O/'town-cleanup.json').write_text(json.dumps({'removed_vertices':removed,'purpose':'old parked traffic and station train replaced by mobile actors; roads retained','source':'art-source/world/Nakornpathom.blend'},indent=2))
print('TOWN_CLEANED',sum(removed.values()))
