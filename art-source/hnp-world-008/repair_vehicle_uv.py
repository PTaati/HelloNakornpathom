"""Repair only mismatched joined UV layer names; geometry/material budgets unchanged."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];OUT=R/'art-export/hnp-world-008';OUT.mkdir(parents=True,exist_ok=True);rows=[]
for kind in ('Sedan','Hatchback','Pickup','Minibus'):
 name='HNP_'+kind+'_v003';bpy.ops.wm.open_mainfile(filepath=str(R/'art-source/hnp-world-003'/(name+'.blend')))
 collection=bpy.data.collections['HNP_WORLD_003'];objects=[o for o in collection.objects if o.type=='MESH'];fixed=0
 for o in objects:
  uv=o.data.uv_layers.get('UVMap');palette=o.data.uv_layers.get('Palette')
  if uv and palette:
   for i in range(len(uv.data)):
    if uv.data[i].uv.x<.00001 and palette.data[i].uv.x>.00001:uv.data[i].uv=palette.data[i].uv;fixed+=1
   o.data.uv_layers.remove(palette);o.data.uv_layers.active=uv;uv.active_render=True
 assert fixed>=24,(kind,fixed)
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 path=OUT/(name+'.fbx');bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=False)
 bpy.ops.wm.save_as_mainfile(filepath=str(Path(__file__).parent/(name+'.blend')))
 points=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box];dims=[max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)]
 tris=0
 for o in objects:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
 # Actual reimport, verify glass palette coordinate survives as UV0.
 before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(path));imported=[o for o in bpy.data.objects if o not in before and o.type=='MESH'];glass=sum(1 for o in imported for v in o.data.uv_layers[0].data if abs(v.uv.x-.34375)<.00001)
 assert glass>=24,(kind,glass)
 for o in imported:o.hide_render=True
 scene=bpy.context.scene;target=Vector((0,0,1));extent=max(dims)
 bpy.ops.object.camera_add(location=(extent*.8,-extent*1.25,extent*.65));cam=bpy.context.object;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=extent*1.3;scene.camera=cam
 bpy.ops.object.light_add(type='AREA',location=(2,-5,7));key=bpy.context.object;key.data.energy=1200;key.data.size=5;key.rotation_euler=(target-key.location).to_track_quat('-Z','Y').to_euler()
 scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.5;scene.render.engine='CYCLES';scene.cycles.samples=8;scene.render.resolution_x=600;scene.render.resolution_y=600;scene.render.resolution_percentage=100;scene.render.filepath=str(OUT/(name+'-preview.png'));bpy.ops.render.render(write_still=True)
 rows.append({'asset':name,'fixed_loops':fixed,'roundtrip_glass_loops':glass,'dimensions_blender_xyz':dims,'triangles':tris,'materials':sorted({m.name for o in objects for m in o.data.materials}),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'status':'PASS','source':'v003 reviewed geometry, UV layer repair only','unit':'metres','forward':'-Z export / Y up'})
(OUT/'vehicle-uv-manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print(json.dumps(rows))
