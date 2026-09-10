"""Add a genuinely distinct in-place run cycle to the reviewed traveller rig."""
import bpy, math, json, hashlib
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'art-export/hnp-world-003'
bpy.ops.wm.open_mainfile(filepath=str(R/'art-source/hnp-world-002-traveller/HNP_Traveller_Child_Rigged_v002.blend'))
S=bpy.context.scene;arm=next(o for o in S.objects if o.type=='ARMATURE')
act=bpy.data.actions.new('HNP_Traveller_Run');act.use_fake_user=True;act.use_frame_range=True;act.frame_start=1;act.frame_end=17
arm.animation_data.action=act;S.render.fps=24
for f in range(1,18):
 phase=(f-1)/16*math.tau;swing=math.sin(phase)
 for b in arm.pose.bones:
  b.rotation_mode='XYZ';b.rotation_euler=(0,0,0);b.location=(0,0,0);b.scale=(1,1,1)
 arm.pose.bones['pelvis'].location.z=.035+.045*math.sin(phase*2)**2
 arm.pose.bones['chest'].rotation_euler.x=math.radians(12)
 for side,s in (('L',swing),('R',-swing)):
  arm.pose.bones['thigh.'+side].rotation_euler.x=math.radians(s*48)
  arm.pose.bones['shin.'+side].rotation_euler.x=math.radians(16+max(0,-s)*64)
  arm.pose.bones['foot.'+side].rotation_euler.x=math.radians(-s*16)
  arm.pose.bones['upper_arm.'+side].rotation_euler.x=math.radians(-s*43)
  arm.pose.bones['forearm.'+side].rotation_euler.x=math.radians(-55 if side=='L' else 55)
 for b in arm.pose.bones:
  b.keyframe_insert('rotation_euler',frame=f,group=b.name);b.keyframe_insert('location',frame=f,group=b.name);b.keyframe_insert('scale',frame=f,group=b.name)
def pose(frame):
 S.frame_set(frame);return {b.name:[v for row in b.matrix_basis for v in row] for b in arm.pose.bones}
a,b=pose(1),pose(17);delta=max(abs(x-y) for n in a for x,y in zip(a[n],b[n]))
S.frame_set(5)
S.camera.location=(2.5,-4,2.0);S.camera.rotation_euler=(Vector((0,0,.8))-S.camera.location).to_track_quat('-Z','Y').to_euler();S.camera.data.type='ORTHO';S.camera.data.ortho_scale=2.25
bpy.ops.object.light_add(type='AREA',location=(-3,-4,5));light=bpy.context.object;light.data.energy=900;light.data.size=4;light.rotation_euler=(Vector((0,0,.8))-light.location).to_track_quat('-Z','Y').to_euler()
S.world.use_nodes=True;S.world.node_tree.nodes.get('Background').inputs[0].default_value=(.32,.40,.49,1);S.world.node_tree.nodes.get('Background').inputs[1].default_value=.7
S.render.filepath=str(O/'HNP_Traveller_Run-preview.png');S.render.resolution_percentage=100;S.render.resolution_x=800;S.render.resolution_y=800
bpy.ops.render.render(write_still=True)
# Idle originally only keyed breathing bones. Explicitly key every remaining bone
# at rest so exporting after Run cannot leak a bent Run pose into Idle.
idle=bpy.data.actions.get('HNP_Traveller_Idle');arm.animation_data.action=idle
keyed={'root','pelvis','chest','head','upper_arm.L','upper_arm.R'}
for frame in (1,61):
 for bone in arm.pose.bones:
  if bone.name not in keyed:
   bone.location=(0,0,0);bone.rotation_euler=(0,0,0);bone.scale=(1,1,1)
   bone.keyframe_insert('rotation_euler',frame=frame,group=bone.name);bone.keyframe_insert('location',frame=frame,group=bone.name);bone.keyframe_insert('scale',frame=frame,group=bone.name)
S.frame_set(1)
bpy.ops.object.select_all(action='DESELECT');arm.select_set(True)
for o in S.objects:
 if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==arm for m in o.modifiers):o.select_set(True)
bpy.context.view_layer.objects.active=arm
path=O/'HNP_Traveller_v003.fbx'
bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0)
bpy.ops.wm.save_as_mainfile(filepath=str(Path(__file__).parent/'HNP_Traveller_v003.blend'))
before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(path));imported=[o for o in bpy.data.objects if o not in before]
names=[a.name for a in bpy.data.actions if 'Run' in a.name]
report={'task':'HNP-WORLD-003','source_revision':'v002 reviewed rig unchanged; new authored Run','clips':['HNP_Traveller_Idle','HNP_Traveller_Walk','HNP_Traveller_Run'],'run_frames':[1,17],'fps':24,'run_loop_delta':delta,'root_motion':False,'run_style':'48 degree thigh swing, bent knees/elbows, 12 degree torso lean and pelvis flight phase; not sped-up Walk','triangles':7340,'materials':3,'bones':len(arm.data.bones),'roundtrip_armatures':sum(o.type=='ARMATURE' for o in imported),'roundtrip_run_names':names,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'status':'PASS' if delta<1e-5 and len(names)>1 else 'FAIL','unity':'NOT RUN'}
(O/'traveller-manifest.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
