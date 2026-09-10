"""Original Blender assets, revision 003. Coordinates below are game X/Y-up/Z.
References: ref/jd.jpg (monument), ref/style.jpg (palette/vehicles).
Architectural ornament and vehicle designs are stylized, not surveyed replicas.
Run in an isolated --background --factory-startup Blender process.
"""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'art-export/hnp-world-003'; OUT.mkdir(parents=True,exist_ok=True)
SRC=Path(__file__).parent
S=bpy.context.scene
for existing in S.objects:existing.hide_render=True
S.unit_settings.system='METRIC'
collection=bpy.data.collections.new('HNP_WORLD_003'); S.collection.children.link(collection)
palette={'Gold':(.83,.44,.055),'GoldEdge':(1,.66,.16),'Ivory':(.94,.91,.81),
 'Inset':(.095,.066,.042),'Body':(.73,.14,.105),'Glass':(.035,.095,.13),
 'Rubber':(.025,.03,.035),'Chrome':(.55,.63,.64),'Light':(1,.86,.51),
 'TailLight':(.8,.025,.012),'BirdGrey':(.34,.42,.46),'BirdWing':(.13,.19,.24)}
M={}
for n,c in palette.items():
 m=bpy.data.materials.new('HNP3_'+n); m.diffuse_color=(*c,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1)
 bs.inputs['Roughness'].default_value=.42 if n in ('Gold','Body','Chrome') else .7
 bs.inputs['Metallic'].default_value=.28 if n in ('Gold','GoldEdge','Chrome') else 0
 M[n]=m
atlas=bpy.data.images.new('HNP003 shared palette',width=32,height=2)
colors=list(palette.values());pixels=[]
for y in range(2):
 for x in range(32):pixels.extend((*colors[min(len(colors)-1,x//2)],1))
atlas.pixels=pixels;atlas.filepath_raw=str(OUT/'HNP003_Palette.png');atlas.file_format='PNG';atlas.save()
am=bpy.data.materials.new('HNP3_Atlas');am.use_nodes=True;tex=am.node_tree.nodes.new('ShaderNodeTexImage');tex.image=atlas;tex.interpolation='Closest';am.node_tree.links.new(tex.outputs['Color'],am.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);M['Atlas']=am
def w(p):return Vector((p[0],-p[2],p[1]))
def own(o,n,mat):
 o.name=n
 for c in list(o.users_collection):c.objects.unlink(o)
 collection.objects.link(o)
 if mat:o.data.materials.append(M[mat])
 return o
def cube(n,p,d,mat,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=w(p));o=own(bpy.context.object,n,mat)
 o.dimensions=(d[0],d[2],d[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Crafted edges','BEVEL');mod.width=bevel;mod.segments=2
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
def mesh(n,vs,fs,mat):
 me=bpy.data.meshes.new(n);me.from_pydata([w(v) for v in vs],[],fs);me.update()
 o=bpy.data.objects.new(n,me);collection.objects.link(o);me.materials.append(M[mat])
 import bmesh
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 return o
def lathe(n,profile,mat,segments=64):
 vs=[(r*math.cos(i*math.tau/segments),h,r*math.sin(i*math.tau/segments)) for r,h in profile for i in range(segments)]
 fs=[]
 for j in range(len(profile)-1):
  for i in range(segments):k=j*segments+i;l=j*segments+(i+1)%segments;fs.append((k,l,l+segments,k+segments))
 fs.extend([tuple(reversed(range(segments))),tuple((len(profile)-1)*segments+i for i in range(segments))])
 o=mesh(n,vs,fs,mat)
 for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
 return o
def sphere(n,p,d,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=1,location=w(p));o=own(bpy.context.object,n,mat)
 o.scale=(d[0],d[2],d[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for f in o.data.polygons:f.use_smooth=True
 return o
def beam(n,a,b,r,mat):
 va,vb=w(a),w(b);bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r,depth=(vb-va).length,location=(va+vb)/2)
 o=own(bpy.context.object,n,mat);o.rotation_euler=(vb-va).to_track_quat('Z','Y').to_euler();return o
def ring(n,p,r,h,mat):
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=h,location=w(p));return own(bpy.context.object,n,mat)
def objects():return list(collection.objects)
records=[]
def export(name,obs,preview=True):
 if name!='HNP_Chedi_v003':
  for o in obs:
   if o.type!='MESH' or o.data.materials[0]==M['Body']:continue
   matname=o.data.materials[0].name.replace('HNP3_','');idx=list(palette).index(matname)
   uv=o.data.uv_layers.active or o.data.uv_layers.new(name='Palette')
   for entry in uv.data:entry.uv=((idx*2+1)/32,.5)
   o.data.materials.clear();o.data.materials.append(am)
 # Merge stationary geometry by material; retain animated wheel/wing pivots.
 fixed=[o for o in obs if not o.name.startswith(('Wheel','Wing_')) and o.type=='MESH']
 merged=[]
 bymat=[(mat,[o for o in fixed if o.data.materials[0]==mat]) for mat in M.values()]
 for mat,chosen in bymat:
  if not chosen:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in chosen:o.select_set(True)
  bpy.context.view_layer.objects.active=chosen[0];bpy.ops.object.join();o=bpy.context.object;o.name=name+'_'+mat.name;merged.append(o)
 remaining=[o for o in collection.objects if o.name.startswith(('Wheel','Wing_'))]
 obs=merged+remaining
 for o in obs:
  if o.type=='MESH' and not o.data.uv_layers:
   o.data.uv_layers.new(name='UVMap')
   for f in o.data.polygons:
    for li in f.loop_indices:
     v=o.data.vertices[o.data.loops[li].vertex_index].co;o.data.uv_layers.active.data[li].uv=(v.x*.08,v.z*.08)
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]
 path=OUT/(name+'.fbx')
 bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=False)
 coords=[o.matrix_world@Vector(v) for o in obs if o.type=='MESH' for v in o.bound_box]
 dims=[max(v[i] for v in coords)-min(v[i] for v in coords) for i in range(3)]
 tris=0
 for o in obs:
  if o.type=='MESH':o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
 rec={'file':path.name,'triangles':tris,'dimensions_blender_xyz':dims,'materials':sorted({m.name for o in obs if o.type=='MESH' for m in o.data.materials}), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'forward_blender':'-Y','unit':'metres','pivot':'ground origin','roundtrip':'NOT RUN'}
 records.append(rec)
 bpy.ops.wm.save_as_mainfile(filepath=str(SRC/(name+'.blend')))
 if preview:render(name,dims)
 # Real isolated import comparison, then discard only this task collection.
 before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(path));imp=[o for o in bpy.data.objects if o not in before]
 pts=[o.matrix_world@Vector(v) for o in imp if o.type=='MESH' for v in o.bound_box]
 rd=[max(v[i] for v in pts)-min(v[i] for v in pts) for i in range(3)]
 rec['roundtrip_dimensions']=rd;rec['roundtrip']='PASS' if max(abs(a-b) for a,b in zip(dims,rd))<.01 else 'FAIL'
 for o in imp:bpy.data.objects.remove(o,do_unlink=True)
 for o in list(collection.objects):bpy.data.objects.remove(o,do_unlink=True)
def render(name,dims):
 extent=max(dims);target=Vector((0,0,dims[2]*.42))
 pos=target+Vector((extent*.9,-extent*1.6,extent*.55))
 if name=='HNP_Chedi_v003':pos=Vector((25,110,32));target=Vector((0,0,20))
 bpy.ops.object.camera_add(location=pos);cam=bpy.context.object;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=extent*1.22;S.camera=cam
 bpy.ops.object.light_add(type='AREA',location=(extent*-1,extent*-1,extent*1.6));key=bpy.context.object;key.data.energy=extent*extent*100;key.data.shape='DISK';key.data.size=extent*.8;key.rotation_euler=(target-key.location).to_track_quat('-Z','Y').to_euler();key.data.color=(1,.85,.64)
 S.world.use_nodes=True;S.world.node_tree.nodes.get('Background').inputs[0].default_value=(.38,.46,.55,1);S.world.node_tree.nodes.get('Background').inputs[1].default_value=.5
 S.render.engine='CYCLES';S.cycles.samples=24;S.render.resolution_x=1000;S.render.resolution_y=1000;S.render.resolution_percentage=100
 S.view_settings.view_transform='AgX';S.render.filepath=str(OUT/(name+'-preview.png'));bpy.ops.render.render(write_still=True)
 for o in (cam,key):bpy.data.objects.remove(o,do_unlink=True)

# Proportions restored after v002's narrow/tall scaling. Base diameter 46, height44.
base=[(23,0),(23,.65)]
for i in range(7):
 r=22.65-i*.9;y=.65+i*.94;base.extend([(r,y),(r,y+.55),(r-.18,y+.65),(r-.18,y+.82)])
base.extend([(16.4,7.6),(16.25,8)])
lathe('Tiered plinth',base,'Gold')
for i in range(7):
 r=22.65-i*.9;y=.72+i*.94;lathe('Moulding',[(r-.12,y),(r+.10,y+.07),(r+.10,y+.17),(r-.12,y+.24)],'GoldEdge')
lathe('Bell',[(16.25,8),(15.8,8.7),(15.3,9.4),(14.7,10.5),(14.1,11.8),(13.6,13.3),(13.1,14.9),(12.5,16.5),(11.8,18),(10.9,19.4),(9.8,20.5),(8.5,21.4),(7.05,22)],'Gold')
lathe('Neck',[(7.05,22),(7.05,22.5),(6.55,22.7),(6.55,23.8),(6.9,24),(6.9,24.35),(6.15,24.5)],'GoldEdge')
lathe('Dark gallery',[(5.8,24.3),(5.8,25.75)],'Inset')
for i in range(28):
 a=i*math.tau/28
 beam('Gallery columns',(6*math.cos(a),24.3,6*math.sin(a)),(6*math.cos(a),25.7,6*math.sin(a)),.19,'GoldEdge')
lathe('Gallery cornice',[(6.25,25.65),(6.65,25.8),(6.65,26.1),(5.7,26.3)],'GoldEdge')
prof=[]
for i in range(38):
 y=26.3+i*.43;r=5.65*(1-i/39)**1.14;prof.extend([(r,y),(r+.075,y+.12),(max(.04,r-.09),y+.33)])
prof.extend([(.16,43),(.06,43.6)])
lathe('Ribbed spire',prof,'Gold',48);lathe('Finial',[(.16,42.6),(.22,42.9),(.10,43.4),(.005,44)],'GoldEdge',16)
# White front shrine, facing toward local -Z; Unity rotates shrine toward station.
before_shrine=set(collection.objects)
for side in (-1,1):
 cube('White pillars',(side*2.7,4.1,-24),( .7,8.2,.8),'Ivory',.06)
 cube('Gold inset',(side*2.7,4.0,-24.43),(.18,7.7,.06),'GoldEdge')
 for y in (.4,1,7.5,8):cube('Pillar capital',(side*2.7,y,-24),(1,.25,1),'Ivory',.04)
cube('Niche backdrop',(0,4.7,-22.5),(4.8,8.2,.3),'Inset')
for layer in range(3):
 z=-24.6+layer*.45;half=3.7-layer*.43;bottom=8.1+layer*.6;peak=13.2+layer*.55
 mesh('Gabled face',[(-half,bottom,z),(half,bottom,z),(0,peak,z),(-half,bottom,z+.35),(half,bottom,z+.35),(0,peak,z+.35)],[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)],'Ivory')
 for side in (-1,1):
  beam('Gold gable line',(side*half,bottom,z-.08),(0,peak,z-.08),.095,'GoldEdge')
  for k in range(1,9):
   t=k/10;x=side*half*(1-t);y=bottom+(peak-bottom)*t;sphere('Gable ornament',(x,y,z-.13),(.10,.16,.08),'GoldEdge')
 beam('Chofah',(0,peak-.1,z),(0,peak+.8,z-.25),.1,'Ivory')
# Small standing Buddha silhouette in the niche, contextual not scanned sculpture.
sphere('Buddha head',(0,6.7,-23.3),(.34,.46,.30),'GoldEdge')
lathe('Buddha robe',[(.65,1.2),(.48,2),(.46,4.5),(.55,5.8),(.3,6.2)],'GoldEdge',24)
robe=collection.objects.get('Buddha robe');robe.location=w((0,0,-23.3))
beam('Buddha arm',(.45,5.7,-23.3),(.8,4.2,-23.3),.15,'GoldEdge')
beam('Raised arm',(-.45,5.7,-23.3),(-.85,5.3,-23.3),.14,'GoldEdge');beam('Raised hand',(-.85,5.3,-23.3),(-.85,6.3,-23.3),.12,'GoldEdge')
cube('Shrine dais',(0,.6,-23.3),(2.5,1.2,1.7),'Ivory',.08)
for o in set(collection.objects)-before_shrine:
 inv=o.matrix_world.inverted()
 for v in o.data.vertices:
  p=o.matrix_world@v.co;p.x*=1.5;p.z*=1.2;p.y+=2;v.co=inv@p
export('HNP_Chedi_v003',objects())

def vehicle(kind):
 color={'Sedan':(.93,.62,.08),'Hatchback':(.15,.43,.74),'Pickup':(.7,.10,.08),'Minibus':(.055,.43,.37)}[kind]
 M['Body'].diffuse_color=(*color,1);M['Body'].node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*color,1)
 length=6.8 if kind=='Minibus' else 4.4 if kind=='Pickup' else 3.8 if kind=='Sedan' else 3.25
 width=2.05 if kind=='Minibus' else 1.76;front=length/2
 cube('Chassis',(0,.46,0),(width-.12,.32,length-.15),'Rubber',.13)
 cube('Body shell',(0,.82,0),(width,.72,length),'Body',.18)
 if kind=='Minibus':cab=(width-.10,1.58,length-.65);cp=(0,1.68,-.06)
 elif kind=='Pickup':cab=(width-.22,.86,1.65);cp=(0,1.46,.50)
 elif kind=='Hatchback':cab=(width-.20,.84,2.15);cp=(0,1.43,-.16)
 else:cab=(width-.24,.80,1.95);cp=(0,1.40,-.05)
 cabin=cube('Passenger cabin',cp,cab,'Body',.13)
 for v in cabin.data.vertices:
  t=max(0,min(1,(v.co.z/cab[1]+.5)));v.co.y*=1-t*.22;v.co.x*=1-t*.08
 glassY=cp[1]+.07;gh=cab[1]*.60
 for end in (-1,1):
  y0=glassY-gh/2;y1=glassY+gh/2;z0=cp[2]+end*cab[2]/2*(1-(y0-cp[1]+cab[1]/2)/cab[1]*.22)+end*.014;z1=cp[2]+end*cab[2]/2*(1-(y1-cp[1]+cab[1]/2)/cab[1]*.22)+end*.014
  a=cab[0]/2-.12;b=a-.025
  mesh('Windshield',[(-a,y0,z0),(a,y0,z0),(b,y1,z1),(-b,y1,z1)],[(0,1,2,3)],'Glass')
 for side in (-1,1):
  count=5 if kind=='Minibus' else 2
  for k in range(count):
   z=cp[2]-cab[2]/2+(k+.5)*cab[2]/count
   a=cab[2]/count/2-.09;y0=glassY-gh/2;y1=glassY+gh/2
   x0=side*cab[0]/2*(1-(y0-cp[1]+cab[1]/2)/cab[1]*.08)+side*.015;x1=side*cab[0]/2*(1-(y1-cp[1]+cab[1]/2)/cab[1]*.08)+side*.015
   lo=cp[2]+(z-a-cp[2])*.93;hi=cp[2]+(z+a-cp[2])*.93;lot=cp[2]+(z-a-cp[2])*.81;hit=cp[2]+(z+a-cp[2])*.81
   mesh('Side window',[(x0,y0,lo),(x0,y0,hi),(x1,y1,hit),(x1,y1,lot)],[(0,1,2,3)],'Glass')
   cube('Door handle',(side*(width/2+.008),1.05,z),(.045,.07,.20),'Chrome',.02)
  for z in (-length*.30,length*.30):
   wheel=ring('Wheel_%s_%s'%(side,z),(side*(width/2-.01),.39,z),.39,.24,'Rubber');wheel.rotation_euler[1]=math.pi/2
   rim=ring('WheelRim',(side*(width/2+.125),.39,z),.24,.026,'Chrome');rim.rotation_euler[1]=math.pi/2
  cube('Mirror',(side*(width/2+.19),1.41,cp[2]+cab[2]*.35),(.24,.20,.35),'Body',.05)
  cube('Headlight',(side*width*.30,.89,front+.006),(.44,.25,.035),'Light',.035)
  cube('Rear light',(side*width*.35,.91,-front-.008),(.22,.33,.035),'TailLight',.04)
 for z in (-front-.025,front+.025):
  cube('Bumper',(0,.53,z),(width-.15,.14,.12),'Chrome',.05)
  cube('Plate',(0,.76,z+.014*(1 if z>0 else -1)),(.42,.17,.03),'Ivory',.01)
 cube('Grille',(0,.95,front+.014),(.60,.21,.028),'Rubber',.02)
 for x in (-.20,0,.20):cube('Grille slat',(x,.95,front+.035),(.035,.16,.025),'Chrome')
 if kind=='Pickup':
  cube('Pickup open bed',(0,1.19,-1.20),(width-.25,.06,1.65),'Rubber',.02)
  for side in (-1,1):cube('Bed rails',(side*(width/2-.06),1.27,-1.20),(.13,.28,1.70),'Body',.04)
 if kind=='Sedan':cube('Taxi roof sign',(0,1.92,0),(.62,.20,.29),'Light',.04)
 export('HNP_'+kind+'_v003',objects())
for kind in ('Sedan','Hatchback','Pickup','Minibus'):vehicle(kind)

# Pigeon: pointed beak, rounded chest, forked tail and articulated tapered feather wings.
sphere('Pigeon body',(0,.22,0),(.18,.21,.36),'BirdGrey')
sphere('Pigeon chest',(0,.28,.22),(.15,.19,.20),'BirdGrey')
sphere('Pigeon head',(0,.41,.29),(.13,.14,.14),'BirdGrey')
mesh('Beak',[(-.06,.39,.38),(.06,.39,.38),(0,.37,.55),(0,.45,.40)],[(0,1,2),(0,3,1),(0,2,3),(1,3,2)],'GoldEdge')
for side in (-1,1):sphere('Bird eye',(side*.119,.44,.31),(.023,.026,.025),'Inset')
mesh('Tail',[(-.10,.21,-.23),(.10,.21,-.23),(.18,.18,-.60),(0,.20,-.54),(-.18,.18,-.60)],[(0,1,2,3,4)],'BirdWing')
for side,n in ((-1,'Wing_L'),(1,'Wing_R')):
 vs=[(side*.1,.27,.13),(side*.40,.30,.24),(side*.78,.26,.08),(side*1.05,.20,-.15),(side*.76,.19,-.26),(side*.44,.23,-.25),(side*.16,.24,-.14)]
 wing=mesh(n,vs,[tuple(range(7)),tuple(reversed(range(7)))],'BirdWing')
 pivot=w((side*.12,.26,0))
 for v in wing.data.vertices:v.co-=pivot
 wing.location=pivot
export('HNP_Pigeon_v003',objects())
M['Body'].diffuse_color=(.86,.80,.61,1);M['Body'].node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.86,.80,.61,1)
for center in (-4.5,4.5):
 cube('Rail carriage',(0,1.5,center),(2.6,2.35,8.1),'Body',.16)
 cube('Rail roof',(0,2.77,center),(2.70,.34,8.25),'Chrome',.13)
 cube('Rail teal band',(0,.68,center),(2.62,.40,8.12),'BirdWing',.03)
 for side in (-1,1):
  for k in range(6):cube('Rail window',(side*1.315,1.94,center-3.1+k*1.20),(.025,.72,.91),'Glass',.05)
  for dz in (-2.7,2.7):
   wheel=ring('Wheel_Train',(side*1.02,.36,center+dz),.36,.20,'Rubber');wheel.rotation_euler[1]=math.pi/2
 cube('Rail end glass',(0,1.93,center+4.07),(1.85,.73,.026),'Glass',.04)
 for side in (-1,1):cube('Rail lamps',(side*.87,1.20,center+4.08),(.26,.26,.04),'Light',.03)
cube('Rail coupling',(0,.65,0),(.35,.24,1.1),'Rubber',.03)
export('HNP_Train_v003',objects())
(OUT/'manifest.json').write_text(json.dumps({'task':'HNP-WORLD-003','references':['ref/style.jpg','ref/jd.jpg'],'palette':{'HNP3_'+k:list(v) for k,v in palette.items()},'atlas':{'material':'HNP3_Atlas','texture':'HNP003_Palette.png','filter':'Point','srgb':True},'assets':records,'unity_validation':'NOT RUN','architectural_detail':'stylized/provisional; silhouette photo-referenced'},indent=2),encoding='utf8')
print('HNP003_ASSET_EXPORT_COMPLETE',json.dumps(records))
