import bpy,math,json,bmesh
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];OUT=R/'art-export/world';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S=bpy.context.scene;S.unit_settings.system='METRIC'
palette={'Skin':(.70,.43,.25),'Cream':(.90,.82,.64),'Seam':(.62,.49,.29),'Pants':(.075,.14,.15),'Hair':(.10,.045,.025),'Hat':(.67,.42,.17),'Band':(.26,.12,.04),'White':(.95,.94,.83),'Bag':(.29,.38,.25)}
mats={}; groups={}
def w(p):return Vector((p[0],-p[2],p[1]))
for n,c in palette.items():
 m=bpy.data.materials.new('HNPT_'+n);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);mats[n]=m
def ell(name,p,s,mat,g='Body',segments=12,rings=8):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=1,location=w(p));o=bpy.context.object;o.name=name;o.scale=(s[0],s[2],s[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats[mat]);groups.setdefault(g,[]).append(o);return o
def box(name,p,s,mat,g='Body',bevel=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=w(p));o=bpy.context.object;o.name=name;o.dimensions=(s[0],s[2],s[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats[mat]);groups.setdefault(g,[]).append(o)
 if bevel:
  mod=o.modifiers.new('Soft tailored edges','BEVEL');mod.width=bevel;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
ell('Tailored shirt',(0,1.17,0),(.29,.34,.19),'Cream')
box('Shirt hem',(0,.94,0),(.50,.14,.33),'Cream')
box('Button placket',(0,1.20,.182),(.035,.43,.025),'Seam',bevel=.004)
for y in [1.05,1.16,1.27,1.38]:ell('Button',(0,y,.205),(.018,.018,.012),'Band',segments=8,rings=4)
for side in [-1,1]:
 c=box('Collar',(side*.065,1.43,.14),(.11,.12,.04),'White',bevel=.009);c.rotation_euler[1]=side*.3
box('Belt',(0,.90,0),(.47,.075,.32),'Band')
box('Buckle',(0,.90,.174),(.08,.055,.018),'Hat',bevel=.005)
ell('Neck',(0,1.51,0),(.09,.11,.09),'Skin')
ell('Face',(0,1.75,.015),(.225,.27,.20),'Skin','Head',16,12)
ell('Hair cap',(0,1.91,-.025),(.23,.13,.19),'Hair','Head')
for side in [-1,1]:
 ell('Ear',(side*.22,1.74,.015),(.045,.075,.045),'Skin','Head')
 ell('Eye white',(side*.079,1.79,.196),(.045,.054,.017),'White','Head')
 ell('Eye',(side*.078,1.786,.212),(.025,.036,.009),'Hair','Head')
 ell('Eye glint',(side*.075-.007,1.799,.220),(.007,.010,.004),'White','Head',8,4)
 box('Eyebrow',(side*.08,1.862,.190),(.085,.021,.019),'Hair','Head',.008)
ell('Nose',(0,1.724,.207),(.04,.043,.034),'Skin','Head')
ell('Smile',(0,1.639,.193),(.062,.021,.009),'Band','Head')
ell('Smile teeth',(0,1.647,.202),(.043,.007,.005),'White','Head')
# Curved cowboy brim and pinched crown, keeping the clothing requested in the game document.
verts=[];faces=[];N=32
for r in [0,.26,.37]:
 for i in range(N):
  a=i*math.tau/N;verts.append(w((r*math.cos(a),2.01+.05*(abs(math.cos(a))**3)*(r/.37),r*.82*math.sin(a))))
for j in range(2):
 for i in range(N):faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
me=bpy.data.meshes.new('Hat brim');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Cowboy brim',me);S.collection.objects.link(o);o.data.materials.append(mats['Hat']);groups['Head'].append(o)
solid=o.modifiers.new('Brim thickness','SOLIDIFY');solid.thickness=.018;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=solid.name)
ell('Hat crown',(0,2.085,0),(.225,.16,.17),'Hat','Head',16,8)
ell('Hat ribbon',(0,2.025,0),(.23,.045,.18),'Band','Head',16,6)
box('Travel backpack',(0,1.18,-.235),(.35,.42,.18),'Bag',bevel=.07)
box('Backpack pocket',(0,1.12,-.34),(.26,.19,.07),'Hat',bevel=.035)
for side in [-1,1]:
 box('Backpack strap',(side*.18,1.24,.14),(.05,.37,.05),'Bag',bevel=.018)
 g='ArmL' if side<0 else 'ArmR'
 ell('Short sleeve',(side*.31,1.35,0),(.12,.17,.13),'Cream',g)
 ell('Forearm',(side*.35,1.11,.005),(.075,.20,.08),'Skin',g)
 ell('Hand',(side*.35,.91,.015),(.080,.095,.067),'Skin',g)
 g='LegL' if side<0 else 'LegR'
 box('Short trouser',(side*.14,.74,0),(.235,.30,.32),'Pants',g,.04)
 ell('Knee',(side*.14,.55,0),(.087,.11,.095),'Skin',g)
 ell('Calf',(side*.14,.33,-.012),(.073,.19,.076),'Skin',g)
 ell('Foot',(side*.14,.12,.065),(.09,.065,.16),'Skin',g)
 box('Sandal sole',(side*.14,.065,.06),(.19,.045,.32),'Band',g,.018)
 box('Sandal strap',(side*.14,.158,.09),(.19,.035,.07),'Pants',g,.01)
pivots={'Body':(0,0,0),'Head':(0,1.5,0),'ArmL':(-.29,1.44,0),'ArmR':(.29,1.44,0),'LegL':(-.14,.9,0),'LegR':(.14,.9,0)}
objects=[]
for name,parts in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name='HNP_'+name
 S.cursor.location=w(pivots[name]);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');objects.append(o)
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(OUT/'HNP_Traveller.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=False)
triangles=0
for o in objects:o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
bpy.ops.object.camera_add(location=w((2.6,2.1,4)));cam=bpy.context.object;cam.rotation_euler=(w((0,1.1,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.9;S.camera=cam
bpy.ops.object.light_add(type='AREA',location=w((1,4,3)));bpy.context.object.data.energy=450;bpy.context.object.data.size=4
S.world.color=(.3,.3,.3);S.render.engine='CYCLES';S.cycles.samples=24;S.render.resolution_x=800;S.render.resolution_y=900;S.render.resolution_percentage=100;S.render.film_transparent=True;S.render.filepath=str(OUT/'traveller-preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'art-source/world/Traveller.blend'));bpy.ops.render.render(write_still=True)
(OUT/'traveller-manifest.json').write_text(json.dumps(dict(triangles=triangles,palette=palette,height=2.25,animation='Procedural rigid-limb walking at named pivots; not a skinned rig',file='HNP_Traveller.fbx'),indent=2))
print('HNP_TRAVELLER_PASS',triangles)
