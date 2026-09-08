"""Reference-driven original low-poly town, chedi and traveller. Run in factory-startup Blender."""
import bpy, math, json, random
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2]
OUT=R/'art-export/world'; OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
S=bpy.context.scene; S.unit_settings.system='METRIC'; S.unit_settings.scale_length=1
random.seed(42)
palette={
 'Ivory':(.86,.77,.57),'Plaster':(.93,.84,.67),'Gold':(.82,.40,.055),'GoldLight':(1,.65,.16),
 'Copper':(.48,.18,.035),'Roof':(.53,.115,.065),'RoofLight':(.72,.23,.10),
 'Teal':(.035,.26,.27),'Glass':(.035,.12,.16),'Wood':(.28,.12,.052),
 'Asphalt':(.19,.205,.205),'Paving':(.58,.49,.37),'Path':(.76,.65,.48),'White':(.94,.91,.78),
 'Water':(.06,.38,.42),'WaterLight':(.22,.59,.55),'Grass':(.29,.38,.15),
 'Leaf':(.28,.44,.095),'LeafLight':(.49,.59,.13),'LeafDark':(.14,.29,.12),
 'Red':(.76,.17,.12),'Blue':(.075,.35,.49),'Pink':(.72,.27,.36),'Yellow':(.95,.65,.12),
 'Skin':(.64,.36,.18),'Hair':(.105,.055,.03),'Pants':(.09,.15,.17),'Leather':(.30,.15,.055)}
mats={}
for name,c in palette.items():
 m=bpy.data.materials.new('HNPW_'+name); m.diffuse_color=(*c,1); m.use_nodes=True
 n=m.node_tree.nodes.get('Principled BSDF'); n.inputs['Base Color'].default_value=(*c,1)
 n.inputs['Roughness'].default_value=.72
 if name in ('Gold','GoldLight','Copper'): n.inputs['Metallic'].default_value=.25
 mats[name]=m
groups={}; collisions=[]
def w(p): return Vector((p[0],-p[2],p[1]))
def add(o,name,mat,group):
 o.name=name; o.data.materials.append(mats[mat]); groups.setdefault(group,[]).append(o); return o
def box(name,p,d,mat,group='Town',solid=False):
 bpy.ops.mesh.primitive_cube_add(size=1,location=w(p)); o=bpy.context.object; o.dimensions=(d[0],d[2],d[1])
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); add(o,name,mat,group)
 if solid: collisions.append(o)
 return o
def cylinder(name,p,r,h,mat,group='Town',vertices=16,solid=False,r2=None):
 bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=r,radius2=r if r2 is None else r2,depth=h,location=w(p))
 o=add(bpy.context.object,name,mat,group)
 if solid: collisions.append(o)
 return o
def ico(name,p,d,mat,group='Town',sub=1):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=w(p)); o=bpy.context.object; o.scale=(d[0],d[2],d[1]); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return add(o,name,mat,group)
def beam(name,a,b,width,mat,group='Town'):
 va,vb=w(a),w(b); o=box(name,(0,0,0),(width,(vb-va).length,width),mat,group)
 o.location=(va+vb)*.5; o.rotation_euler=(vb-va).to_track_quat('Z','Y').to_euler(); return o
def mesh(name,verts,faces,mat,group='Town',solid=False):
 me=bpy.data.meshes.new(name); me.from_pydata([w(v) for v in verts],[],faces); me.update()
 o=bpy.data.objects.new(name,me); S.collection.objects.link(o); add(o,name,mat,group)
 import bmesh
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 if solid: collisions.append(o)
 return o
def lathe(name,profile,mat,group='Chedi',segments=64,solid=False):
 verts=[]
 for radius,y in profile:
  for i in range(segments):
   a=2*math.pi*i/segments; verts.append((radius*math.cos(a),y,radius*math.sin(a)))
 faces=[]
 for k in range(len(profile)-1):
  for i in range(segments):
   j=(i+1)%segments; faces.append((k*segments+i,k*segments+j,(k+1)*segments+j,(k+1)*segments+i))
 faces.extend([tuple(reversed(range(segments))),tuple((len(profile)-1)*segments+i for i in range(segments))])
 return mesh(name,verts,faces,mat,group,solid)
def roof(name,x,z,width,depth,y,group='Town',thai=False):
 e=y; apex=y+width*(.80 if thai else .30)
 verts=[(x-width/2,e,z-depth/2),(x+width/2,e,z-depth/2),(x,apex,z-depth/2),
        (x-width/2,e,z+depth/2),(x+width/2,e,z+depth/2),(x,apex,z+depth/2)]
 mesh(name,verts,[(0,3,5,2),(2,5,4,1),(0,2,1),(3,4,5)],'Roof',group)
 for zz in [z-depth/2,z+depth/2]:
  beam('Gable trim',(x-width/2,e,zz),(x,apex,zz),.13,'GoldLight' if thai else 'Ivory',group)
  beam('Gable trim',(x,apex,zz),(x+width/2,e,zz),.13,'GoldLight' if thai else 'Ivory',group)
  if thai: beam('Chofah',(x,apex,zz),(x,apex+1.3,zz-.35),.16,'GoldLight',group)
def tree(x,z,size=1):
 cylinder('Tree trunk',(x,1.5*size,z),.22*size,3*size,'Wood',solid=True,vertices=8)
 for dx,dy,dz in [(0,3.5,0),(-.8,2.9,.15),(.9,3,.3),(0,4.4,.1)]:
  ico('Faceted canopy',(x+dx*size,dy*size,z+dz*size),(1.65*size,1.75*size,1.45*size),random.choice(['Leaf','LeafLight','LeafDark']))
def lamp(x,z):
 cylinder('Lamp pole',(x,2.5,z),.075,5,'Teal',vertices=8)
 beam('Lamp arm',(x,4.9,z),(x+.8,5.2,z),.1,'Teal')
 box('Warm lantern',(x+.8,5.15,z),(.65,.12,.35),'GoldLight')
def fence_x(x0,x1,z):
 for x in range(int(x0),int(x1)+1,3):
  box('White balustrade post',(x,.55,z),(.23,1.1,.23),'White')
  cylinder('Post cap',(x,1.15,z),.18,.16,'GoldLight',vertices=8)
 for y in [.3,.9]: box('Railing',( (x0+x1)/2,y,z),(x1-x0,.10,.11),'White')
def house(x,z,width=9,depth=10,h=5,color='Plaster'):
 box('Shophouse',(x,h/2,z),(width,h,depth),color,solid=True)
 box('Cornice',(x,h-.2,z),(width+.2,.35,depth+.2),'Ivory')
 roof('Tile roof',x,z,width+1,depth+1,h)
 for xx in [x-width*.28,x+width*.28]:
  for zz in [z-depth/2-.04,z+depth/2+.04]:
   box('Shop window',(xx,h*.60,zz),(width*.23,1.6,.09),'Teal')
   box('Window sill',(xx,h*.60-.85,zz),(width*.28,.13,.2),'White')
 for zz in [z-depth/2-.09,z+depth/2+.09]: box('Shop door',(x,1.2,zz),(1.35,2.4,.12),'Wood')
def stall(x,z,color='Red'):
 box('Market counter',(x,.7,z),(2.8,1.4,1.4),'Wood',solid=True)
 for dx in [-1.3,1.3]: cylinder('Stall pole',(x+dx,1.7,z),.055,3.4,'Ivory',vertices=6)
 cylinder('Market parasol',(x,3.2,z),2.15,.85,color,vertices=8,r2=0)
 for dx in [-.8,0,.8]:
  box('Produce crate',(x+dx,1.52,z),(.6,.24,.8),'Ivory')
  for dz in [-.22,.1]: ico('Fruit',(x+dx,1.74,z+dz),(.18,.17,.18),random.choice(['GoldLight','Red','Leaf']),sub=1)
def car(x,z,color='Red',heading=0):
 before=len(groups.get('Town',[]))
 box('Car body',(x,.65,z),(1.8,.8,3.7),color,solid=True)
 box('Car cabin',(x,1.25,z),(1.5,.75,1.9),color)
 box('Windscreen',(x,1.4,z-.97),(1.3,.45,.045),'Glass')
 box('Rear glass',(x,1.4,z+.97),(1.3,.45,.045),'Glass')
 for side in [-1,1]:
  box('Side glass',(x+side*.77,1.4,z),(.04,.46,1.6),'Glass')
  for zz in [-1.1,1.1]:
   o=cylinder('Tyre',(x+side*.87,.39,z+zz),.37,.22,'Pants',vertices=12); o.rotation_euler[1]=math.pi/2
  box('Headlamp',(x+side*.55,.77,z-1.87),(.43,.23,.04),'GoldLight')
 if heading:
  center=w((x,0,z))
  from mathutils import Matrix
  rot=Matrix.Rotation(math.radians(-heading),4,'Z')
  for o in groups['Town'][before:]: o.matrix_world=__import__('mathutils').Matrix.Translation(center)@rot@__import__('mathutils').Matrix.Translation(-center)@o.matrix_world

# Chedi silhouette from jd.jpg: stepped base, bell, collar and finely tapered rings.
lathe('Stepped circular base',[(23,0),(23,.5),(22.6,.6),(22.6,1),(22,1.15),(22,1.7),(21.3,1.8),(21.3,2.5),
 (20.5,2.65),(20.5,3.2),(19.7,3.35),(19.7,4),(19,4.15),(19,4.7),(18.2,4.85),(18.2,5.5),(17.5,5.7),(17.5,6.3)],'Gold')
lathe('Bell body',[(17.5,6.3),(16.5,7.2),(15.3,8.8),(14.3,10.6),(13.6,12.8),(13,15.2),(12.2,17.8),(11.4,19.4),(10.4,20.7),(8.8,21.7),(7,22.1)],'Gold')
for i,y in enumerate([.55,1.1,1.8,2.65,3.35,4.15,4.85,5.65,6.35]):
 rr=23-i*.69; lathe('Base gold bead',[(rr-.13,y-.08),(rr+.13,y),(rr-.13,y+.1)],'GoldLight')
lathe('Harmika collar',[(7.1,22),(7.1,22.7),(6.7,22.9),(6.7,24),(6.9,24.15),(6.9,24.5),(6.3,24.7),(6.3,25.2)],'GoldLight')
for i in range(20):
 a=i*math.tau/20
 box('Collar recess',(6.35*math.cos(a),25.5,6.35*math.sin(a)),(.35,1.15,.45),'Copper','Chedi')
lathe('Upper collar',[(6.65,26.1),(6.7,26.4),(6,26.7)],'GoldLight')
profile=[]
for i in range(32):
 y=26.6+i*.43; radius=5.9*(1-i/33)**1.05
 profile.extend([(radius,y),(radius+.10,y+.12),(max(.05,radius-.10),y+.30)])
profile.extend([(.12,41),(.03,43)])
lathe('Ringed tapering spire',profile,'GoldLight',segments=48)
lathe('Finial',[(.22,40.5),(.24,41.2),(.1,42),(.0,44)],'GoldLight',segments=16)
# Cardinal Thai porticos; front is towards west / station in the world.
for angle in [0,90,180,270]:
 start=len(groups['Chedi']); x,z=0,-23
 for side in [-1,1]:
  box('Portico column',(side*2.5,3.8,z),(.6,7.6,.65),'Ivory','Chedi')
  box('Gold pilaster',(side*2.5,3.7,z-.37),(.18,6.9,.08),'GoldLight','Chedi')
 roof('Thai portico gable',0,z,6.8,5.5,7.8,'Chedi',True)
 roof('Layered gable',0,z+.6,5.1,4.8,9,'Chedi',True)
 box('Portico lintel',(0,7.2,z),(5.5,.7,.6),'Plaster','Chedi')
 # Rotate newly created details around the chedi centre.
 from mathutils import Matrix
 rot=Matrix.Rotation(math.radians(angle),4,'Z')
 for o in groups['Chedi'][start:]: o.matrix_world=rot@o.matrix_world

# Ground: west and east banks, canal below the walk surface, bridges at three crossings.
box('West bank',(-96,-.3,0),(48,.6,140),'Grass',solid=True)
box('East bank',(24,-.3,0),(176,.6,140),'Grass',solid=True)
box('Canal bed',(-67,-1.6,0),(10,.3,140),'Teal')
box('Canal water',(-67,-.55,0),(9.8,.1,140),'Water')
for i in range(45): box('Water glint',(-67+random.uniform(-4,4),-.485,random.uniform(-68,68)),(random.uniform(.2,.8),.01,random.uniform(.8,3)),'WaterLight')
for z in [0,-58,58]:
 box('Bridge deck',(-67,.05,z),(13,.3,12 if z==0 else 8),'Path',solid=True)
 fence_x(-73,-61,z+(6 if z==0 else 4)); fence_x(-73,-61,z-(6 if z==0 else 4))
 for x in [-73,-61]:
  for dz in [-5.8,5.8] if z==0 else [-3.8,3.8]:
   cylinder('Bridge pier',(x,.8,z+dz),.4,1.6,'Ivory',vertices=8)
for side in [-72.2,-61.8]:
 for za,zb in [(-70,-62),(-54,-6),(6,54),(62,70)]:
  box('Canal retaining wall',(side,-.1,(za+zb)/2),(.35,1,zb-za),'Ivory',solid=True)
  box('Canal handrail',(side,1,(za+zb)/2),(.13,.13,zb-za),'White')
  for z in range(za,zb,3): box('Canal post',(side,.5,z),(.2,1.15,.2),'White')
# Central approach and road network from aerial reference.
box('Central avenue',(-29,.025,0),(152,.055,10),'Asphalt')
for z in [-6.1,6.1]: box('Central sidewalk',(-27,.05,z),(157,.1,2.2),'Path')
for x in range(-103,16,6):
 for z in [-.18,.18]: box('Double yellow centre line',(x,.062,z),(3.4,.014,.10),'Yellow')
for x in [-84,-13,105]:
 box('North south street',(x,.025,0),(7,.055,133),'Asphalt')
 for z in range(-64,65,7): box('Road dash',(x,.06,z),(.12,.01,3),'White')
for z in [-58,58]:
 box('Perimeter avenue',(18,.025,z),(180,.055,7),'Asphalt')
 for x in range(-59,105,7): box('Road dash',(x,.06,z),(3,.01,.12),'White')
for x in [-78,-18,10]:
 for z in range(-4,5,2): box('Crosswalk',(x,.065,z),(2.6,.015,.8),'White')
for x in range(-59,16,4):
 for z in [-5.15,5.15]: box('Curb',(x,.12,z),(1.9,.24,.2),'White' if x%8 else 'Red')
# Left station with rail parallel to edge of image.
box('Station platform',(-106,.05,0),(15,.1,47),'Path')
house(-109,14,10,15,4,'Plaster')
for z in range(-21,22,7): box('Platform column',(-101,1.8,z),(.25,3.6,.25),'Teal')
roof('Station canopy',-104,-4,10,30,3.8)
for x in [-116,-114]: box('Rail',(x,.1,0),(.13,.2,138),'Pants')
for z in range(-68,69,2): box('Rail sleeper',(-115,-.02,z),(3,.1,.35),'Wood')
for z0 in [-12,4,20]:
 box('Train coach',(-115,1.5,z0),(2.6,2.2,14),'Ivory',solid=True)
 box('Train teal band',(-115,.7,z0),(2.67,.5,14),'Teal')
 box('Train roof',(-115,2.85,z0),(2.75,.35,14.2),'Roof')
 for z in range(-5,6,2):
  for side in [-1,1]: box('Train window',(-115+side*1.31,1.9,z0+z),(.025,.72,1.3),'Glass')
for x in [-97,-89]:
 for z in [-18,18]: tree(x,z,.95)
# Dense shophouse blocks lining the canal, split for central street.
for z in [-43,-29,-15,15,29,43]:
 for x in [-52,-37]: house(x,z,10,11,random.choice([4.5,5.5,6.5]),random.choice(['Plaster','Ivory','Path']))
for z in [-44,-28,28,44]:
 house(-94,z,12,11,4.8,'Plaster')
for x in [-53,-39,-25]:
 for z in [-9.1,9.1]: stall(x,z,random.choice(['Teal','Red','Blue','Pink']))
# Temple precinct: open square, circular raised terrace and perimeter colonnade.
box('Temple plaza',(53,.06,0),(87,.12,91),'Path')
for x in [10,96]: box('Temple perimeter',(x,.08,0),(3,.16,95),'Ivory')
for z in [-46,46]: box('Temple perimeter',(53,.08,z),(89,.16,3),'Ivory')
# Walkable terrace is a solid disc; stairs connect each cardinal approach.
terrace=cylinder('Upper terrace',(53,1.45,0),29,2.9,'Ivory',vertices=96,solid=True)
for i in range(16):
 # 0.18 metre steps from west approach; 0.5 metre treads.
 x=16+i*.5; h=(i+1)*2.9/16
 box('West stair',(x,h/2,0),(.52,h,8),'Plaster',solid=True)
for side in [-1,1]:
 for i in range(16):
  z=side*(37-i*.5); h=(i+1)*2.9/16
  box('Cardinal stair',(53,h/2,z),(8,h,.52),'Plaster',solid=True)
# East stairs to allow a full circular walk.
for i in range(16):
 x=90-i*.5; h=(i+1)*2.9/16
 box('East stair',(x,h/2,0),(.52,h,8),'Plaster',solid=True)
for a in range(0,360,8):
 # Circular cloister with four open gates. Roof leaves upper walk clear.
 if min(a%90,90-a%90)<12: continue
 t=math.radians(a); x=53+32*math.cos(t); z=32*math.sin(t)
 cylinder('Cloister pillar',(x,1.65,z),.18,3.3,'Ivory',vertices=8)
 o=box('Cloister roof',(x,3.5,z),(4.8,.22,3.6),'Roof'); o.rotation_euler[2]=-t
for x in [17,89]:
 for z in [-36,-21,21,36]: tree(x,z,1.25)
for x in [32,48,64,80]:
 for z in [-40,40]: tree(x,z,1.0)
for x in [0,-21,-76]:
 for z in [-48,-30,-16,16,30,48]: tree(x,z,random.uniform(.8,1.25))
for x in [-88,-59,-42,-25,0]:
 for z in [-7.8,7.8]: lamp(x,z)
# Festival stalls on the lower south square, visible and freely accessible.
for x in [20,32,44,56,68,80,92]: stall(x,-51,random.choice(['Red','Blue','Teal','Pink','Yellow']))
for x,z,c,h in [(-83,28,'Red',0),(-13,-26,'Blue',0),(-43,2.7,'Yellow',90),(-27,-2.7,'Teal',90),(104,24,'Red',0),(-13,40,'Ivory',0)]: car(x,z,c,h)
# Far edge boundary walls with openings only inside the playable map.
for x in [-120,112]: box('Map edge',(x,1.1,0),(.5,2.2,140),'LeafDark',solid=True)
for z in [-70,70]: box('Map edge',(-4,1.1,z),(232,2.2,.5),'LeafDark',solid=True)

def export_group(group,filename,include_collisions=False):
 objects=groups[group]
 by_material={m.name:[o for o in objects if o.data.materials and o.data.materials[0]==m] for m in mats.values()}
 # Merge by material, keeping a small draw-call count for the large town.
 combined=[]
 for material in mats.values():
  selected=by_material[material.name]
  if not selected: continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in selected: o.select_set(True)
  bpy.context.view_layer.objects.active=selected[0]; bpy.ops.object.join()
  o=bpy.context.object; o.name=group+'_'+material.name; combined.append(o)
 if include_collisions:
  # Collision copies are prepared before render meshes are merged.
  combined.append(collision_mesh)
 bpy.ops.object.select_all(action='DESELECT')
 for o in combined:o.select_set(True)
 import bmesh
 for o in combined:
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.00001);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 bpy.context.view_layer.objects.active=combined[0]
 bpy.ops.export_scene.fbx(filepath=str(OUT/filename),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=False)
 tris=0
 for o in combined:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
 return dict(file=filename,triangles_including_collision=tris,mesh_objects=len(combined))
# Copy collision geometry before merging render meshes.
copies=[]
for o in collisions:
 c=o.copy();c.data=o.data.copy();S.collection.objects.link(c);copies.append(c)
bpy.ops.object.select_all(action='DESELECT')
for o in copies:o.select_set(True)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();collision_mesh=bpy.context.object;collision_mesh.name='COLL_Town'
town_report=export_group('Town','HNP_Town.fbx',True)
chedi_report=export_group('Chedi','HNP_Chedi.fbx')
collision_mesh.hide_render=True
# Move chedi into its world position only for source composition/preview (FBX already local).
for o in bpy.data.objects:
 if o.type=='MESH' and o.name.startswith('Chedi_'): o.location+=w((53,2.9,0))
bpy.ops.object.camera_add(location=w((-74,32,-39))); camera=bpy.context.object
camera.rotation_euler=(w((38,13,0))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=42;S.camera=camera
bpy.ops.object.light_add(type='SUN',location=(0,0,60)); sun=bpy.context.object;sun.rotation_euler=(math.radians(30),math.radians(-25),math.radians(-65));sun.data.energy=2.5;sun.data.color=(1,.73,.43);sun.data.angle=.08
S.world.color=(.35,.27,.20)
S.render.engine='CYCLES';S.cycles.samples=16;S.render.resolution_x=1440;S.render.resolution_y=900;S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.render.filepath=str(OUT/'world-preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'art-source/world/Nakornpathom.blend'))
bpy.ops.render.render(write_still=True)
manifest=dict(reference_layout='ref/game-document/image2.png',reference_chedi='ref/jd.jpg',reference_style='ref/style.jpg',
 scale='compressed provisional metres',blender=bpy.app.version_string,palette=palette,assets=[town_report,chedi_report],
 anchors={'station':[-102,.2,0],'bridge':[-67,.2,0],'main_road':[-35,.15,0],'temple':[53,2.9,0]},
 bounds={'x':[-120,112],'z':[-70,70]})
(OUT/'world-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('HNP_WORLD_EXPORT_PASS',json.dumps(manifest))
