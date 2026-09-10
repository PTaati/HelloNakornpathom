"""Root-owned, narrowly scoped removal of v003 cloister roofs/pillars only."""
import bpy, bmesh, hashlib, json, math, struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'art-source/hnp-world-003/HNP_Town_v003.blend'
OUT=ROOT/'art-export/hnp-world-009';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
objects=[o for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith('Town_') or o.name=='COLL_Town')]
collider=next(o for o in objects if o.name=='COLL_Town')
def geometry_hash(obj):
 h=hashlib.sha256()
 for v in obj.data.vertices:h.update(struct.pack('<3f',*v.co))
 for p in obj.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
 return h.hexdigest()
original_collision=geometry_hash(collider)
expected=[(53+32*math.cos(math.radians(a)),32*math.sin(math.radians(a))) for a in range(0,360,8) if min(a%90,90-a%90)>=12]
rows=[];removed={'roof':0,'pillar':0}
for obj in objects:
 if obj==collider:continue
 bm=bmesh.new();bm.from_mesh(obj.data);seen=set();kill=[]
 for start in bm.verts:
  if start in seen:continue
  stack=[start];seen.add(start);component=[]
  while stack:
   v=stack.pop();component.append(v)
   for edge in v.link_edges:
    other=edge.other_vert(v)
    if other not in seen:seen.add(other);stack.append(other)
  points=[obj.matrix_world@v.co for v in component]
  lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
  x=(lo[0]+hi[0])/2;z=-(lo[1]+hi[1])/2
  if not any(abs(x-ex)<.015 and abs(z-ez)<.015 for ex,ez in expected):continue
  kind=None
  if abs(lo[2]-3.39)<.015 and abs(hi[2]-3.61)<.015 and 'Roof' in obj.name:kind='roof'
  if abs(lo[2])<.015 and abs(hi[2]-3.3)<.015 and 'Ivory' in obj.name and hi[0]-lo[0]<.38 and hi[1]-lo[1]<.38:kind='pillar'
  if kind:
   rows.append(dict(kind=kind,object=obj.name,center=[x,z],vertices=len(component)));removed[kind]+=1;kill.extend(component)
 bmesh.ops.delete(bm,geom=kill,context='VERTS');bm.to_mesh(obj.data);bm.free()
assert removed['roof']==len(expected) and removed['pillar']==len(expected),(removed,len(expected))
assert geometry_hash(collider)==original_collision,'Existing traversal collider was modified'
bpy.ops.object.select_all(action='DESELECT')
for obj in objects:obj.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
fbx=OUT/'HNP_Town_v009.fbx'
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=False)
bpy.ops.wm.save_as_mainfile(filepath=str(Path(__file__).parent/'HNP_Town_v009.blend'))
def stats(obs):
 for o in obs:o.data.calc_loop_triangles()
 return {'meshes':len(obs),'triangles':sum(len(o.data.loop_triangles) for o in obs)}
source_stats=stats(objects)
before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(fbx))
imported=[o for o in bpy.data.objects if o not in before and o.type=='MESH']
roundtrip=stats(imported);assert source_stats==roundtrip,(source_stats,roundtrip)
report=dict(status='PASS',source=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),fbx_sha256=hashlib.sha256(fbx.read_bytes()).hexdigest(),removed=removed,details=rows,collision_sha256_before=original_collision,collision_sha256_after=geometry_hash(collider),source_metrics=source_stats,roundtrip=roundtrip,units='metres',axis='-Z forward, Y up, preserve existing Unity negative-X Town transform',purpose='Remove only exact old radius32 cloister roofs/pillars; preserve all other Town mesh islands and COLL_Town')
(OUT/'town-cleanup-manifest.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('HNP009_TOWN_CLEANUP_PASS',json.dumps(removed))
