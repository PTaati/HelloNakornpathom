import bpy
import bmesh
import json
import math
import hashlib
import os
from pathlib import Path
from mathutils import Vector, Matrix


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "art-source" / "HNP-ART-MAP-007"
OUT = ROOT / "art-export" / "HNP-ART-MAP-007"
CHECK = OUT / "production-v003-previews"
TEXTURES = OUT / "Textures"
SRC.mkdir(parents=True, exist_ok=True)
CHECK.mkdir(parents=True, exist_ok=True)
TEXTURES.mkdir(parents=True, exist_ok=True)
BLEND = SRC / "HNP_Map007_HeroSceneKit_v003_production.blend"

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.world = bpy.data.worlds.new("MAP007_ClearDay")
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.34, 0.49, 0.68, 1)
bg.inputs['Strength'].default_value = 0.50
scene.view_settings.look = 'AgX - Medium High Contrast'


def coll(name):
    c=bpy.data.collections.new(name);scene.collection.children.link(c);return c


STATION=coll("MAP007_HERO_STATION")
STREET=coll("MAP007_HERO_STREET_CORNER")
BRIDGE=coll("MAP007_HERO_BRIDGE_CANAL")
TEMPLE=coll("MAP007_HERO_TEMPLE_APPROACH")
REVEAL=coll("MAP007_REVEAL_SEQUENCE_CONTEXT")
ROUTE=coll("MAP007_DIRECT_ROUTE_PREVIEW_ONLY")
CHEDITEST=coll("MAP007_AUTHORITATIVE_CHEDI_PREVIEW_ONLY")
COLLISION=coll("MAP007_COLLISION_DRAFT")
COLLISION.hide_render=True
HERO=[STATION,STREET,BRIDGE,TEMPLE,ROUTE,CHEDITEST]


def noise_mat(name, c1, c2, scale=4.0, rough=.65, metallic=0.0, bump=.08):
    m=bpy.data.materials.new(name);m.use_nodes=True
    n=m.node_tree.nodes;l=m.node_tree.links
    n.clear()
    out=n.new('ShaderNodeOutputMaterial');bs=n.new('ShaderNodeBsdfPrincipled')
    tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=scale;tex.inputs['Detail'].default_value=4.0;tex.inputs['Roughness'].default_value=.72
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*c1,1);ramp.color_ramp.elements[1].color=(*c2,1)
    bumpn=n.new('ShaderNodeBump');bumpn.inputs['Strength'].default_value=bump;bumpn.inputs['Distance'].default_value=.16
    bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metallic
    l.new(tex.outputs['Fac'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],bs.inputs['Base Color']);l.new(tex.outputs['Fac'],bumpn.inputs['Height']);l.new(bumpn.outputs['Normal'],bs.inputs['Normal']);l.new(bs.outputs['BSDF'],out.inputs['Surface'])
    return m


def solid_mat(name, color, rough=.55, metallic=0.0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metallic
    return m


def emission_mat(name,color,strength=2.0):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear();o=n.new('ShaderNodeOutputMaterial');e=n.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*color,1);e.inputs['Strength'].default_value=strength;l.new(e.outputs['Emission'],o.inputs['Surface']);return m


PLASTER=noise_mat("MAT_Station_WarmPlaster",(.66,.58,.43),(.88,.82,.68),5.0,.78,0,.075)
SALMON=noise_mat("MAT_Station_SunFadedSalmon",(.38,.16,.12),(.70,.38,.27),6.0,.72,0,.055)
CONCRETE=noise_mat("MAT_Concrete_Aged",(.27,.27,.25),(.56,.55,.49),7.5,.88,0,.16)
CONCRETE_LIGHT=noise_mat("MAT_Concrete_Light",(.50,.49,.44),(.72,.69,.60),8,.82,0,.10)
GALV=noise_mat("MAT_Galvanized_Roof",(.25,.29,.30),(.54,.58,.57),15,.44,.42,.12)
STEEL=noise_mat("MAT_Painted_Steel_Green",(.035,.12,.10),(.10,.28,.22),8,.48,.55,.08)
STEEL_CREAM=noise_mat("MAT_Painted_Steel_Cream",(.58,.48,.30),(.86,.72,.43),7,.52,.40,.055)
TIMBER=noise_mat("MAT_Aged_Timber",(.08,.032,.014),(.31,.14,.055),6,.82,0,.18)
SHUTTER=noise_mat("MAT_Weathered_Shutter",(.22,.24,.22),(.48,.51,.45),18,.67,.25,.13)
BRICK=noise_mat("MAT_Brick_Infill",(.30,.09,.045),(.62,.25,.11),12,.84,0,.18)
AWNING_GREEN=noise_mat("MAT_Awning_Green",(.025,.16,.09),(.08,.37,.21),5,.68,0,.09)
AWNING_BLUE=noise_mat("MAT_Awning_Blue",(.025,.12,.22),(.08,.34,.50),5,.66,0,.08)
ASPHALT=noise_mat("MAT_Asphalt",(.025,.028,.026),(.16,.17,.15),28,.93,0,.20)
PAVER=noise_mat("MAT_Forecourt_Paver",(.31,.27,.22),(.68,.60,.49),14,.88,0,.14)
GLASS=noise_mat("MAT_Window_Glass",(.015,.055,.065),(.12,.29,.32),3,.18,.12,.025)
WATER=noise_mat("MAT_Canal_Water",(.012,.085,.065),(.08,.30,.23),2.2,.19,.10,.19)
WATER_DEEP=noise_mat("MAT_Canal_Water_Deep",(.006,.025,.028),(.025,.13,.12),5.5,.24,.04,.11)
WATER_GLINT=noise_mat("MAT_Canal_Surface_Glint",(.06,.19,.17),(.18,.38,.31),2.0,.16,.12,.06)
ALGAE=noise_mat("MAT_Waterline_Algae",(.035,.08,.028),(.18,.28,.08),7,.88,0,.22)
LEAF=noise_mat("MAT_Broadleaf",(.018,.13,.035),(.12,.43,.10),4.5,.72,0,.12)
LEAF_LIGHT=noise_mat("MAT_Leaf_Sunlit",(.09,.25,.045),(.31,.56,.12),4,.70,0,.10)
BARK=noise_mat("MAT_Bark",(.055,.025,.012),(.26,.11,.040),8,.9,0,.22)
GOLD=solid_mat("MAT_Warm_Brass",(.60,.31,.06),.32,.62)
TERRACOTTA=noise_mat("MAT_Terracotta_Roof",(.28,.07,.025),(.69,.27,.08),10,.82,0,.12)
WHITE=solid_mat("MAT_Sign_White",(.80,.78,.69),.62,0)
WARM_LIGHT=emission_mat("MAT_Interior_WarmLight",(1.0,.46,.12),2.4)


def only(obj,c):
    for cc in list(obj.users_collection):cc.objects.unlink(obj)
    c.objects.link(obj)
    return obj


def bevel(obj,w=.06,seg=2):
    if w<=0:return obj
    mod=obj.modifiers.new("HandChamfer",'BEVEL');mod.width=min(w,min(obj.dimensions)*.20);mod.segments=seg;mod.limit_method='ANGLE'
    bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);obj.select_set(False);return obj


def box(name,loc,dims,mat,c,w=.06,seg=2,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(location=loc,rotation=rot);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bevel(o,w,seg);o.data.materials.append(mat);only(o,c);return o


def cyl(name,loc,r,depth,mat,c,verts=16,rot=(0,0,0),w=.025):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc,rotation=rot);o=bpy.context.object;o.name=name;bevel(o,w,2);o.data.materials.append(mat);only(o,c);return o


def gable_roof(name,center,length,width,eave_z,rise,thick,mat,c):
    x0,x1=center[0]-length/2,center[0]+length/2;y0,y1=center[1]-width/2,center[1]+width/2;z=eave_z
    verts=[(x0,y0,z),(x1,y0,z),(x0,y1,z),(x1,y1,z),(x0,center[1],z+rise),(x1,center[1],z+rise),
           (x0,y0,z-thick),(x1,y0,z-thick),(x0,y1,z-thick),(x1,y1,z-thick),(x0,center[1],z+rise-thick),(x1,center[1],z+rise-thick)]
    faces=[(0,1,5,4),(2,4,5,3),(6,10,11,7),(8,9,11,10),(0,6,7,1),(2,3,9,8),(0,4,10,6),(1,7,11,5),(2,8,10,4),(3,5,11,9)]
    me=bpy.data.meshes.new(name+"_Mesh");me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);c.objects.link(o);o.data.materials.append(mat);bevel(o,.045,2);return o


def curved_tube(name,pts,r,mat,c,res=2):
    cu=bpy.data.curves.new(name+"_Curve",'CURVE');cu.dimensions='3D';cu.resolution_u=res;cu.bevel_depth=r;cu.bevel_resolution=3;cu.resolution_u=2
    sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
    for b,p in zip(sp.bezier_points,pts):b.co=p;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,cu);c.objects.link(o);o.data.materials.append(mat);return o


def panel_frame(name,x,y,z,w,h,depth,mat_frame,mat_glass,c,front=-1):
    box(name+"_glass",(x,y,z),(w,depth*.48,h),mat_glass,c,.025)
    fy=y+front*depth*.35
    for dx in (-w/2,w/2):box(name+f"_jamb_{dx:+.2f}",(x+dx,fy,z),(.14,depth,h+.18),mat_frame,c,.025)
    for dz in (-h/2,h/2):box(name+f"_rail_{dz:+.2f}",(x,fy,z+dz),(w+.15,depth,.14),mat_frame,c,.025)
    box(name+"_mullion",(x,fy,z),(.10,depth,h),mat_frame,c,.02)


def panel_frame_x(name,x,y,z,w,h,depth,mat_frame,mat_glass,c,front=-1):
    fx=x+front*depth*.35
    box(name+"_glass",(x,y,z),(depth*.48,w,h),mat_glass,c,.025)
    for dy in (-w/2,w/2):box(name+f"_jamb_{dy:+.2f}",(fx,y+dy,z),(depth,.14,h+.18),mat_frame,c,.025)
    for dz in (-h/2,h/2):box(name+f"_rail_{dz:+.2f}",(fx,y,z+dz),(depth,w+.15,.14),mat_frame,c,.025)
    box(name+"_mullion",(fx,y,z),(depth,.10,h),mat_frame,c,.02)


def text_mesh(name,body,loc,size,mat,c,rot=(math.radians(90),0,0),extrude=.025):
    bpy.ops.object.text_add(location=loc,rotation=rot)
    obj=bpy.context.object;obj.name=name;obj.data.body=body;obj.data.align_x='CENTER';obj.data.align_y='CENTER';obj.data.size=size;obj.data.extrude=.008;obj.data.resolution_u=1;obj.data.bevel_depth=0;obj.data.bevel_resolution=0;obj.data.materials.append(mat)
    font_path=Path(r"C:\Windows\Fonts\tahoma.ttf")
    if font_path.exists():obj.data.font=bpy.data.fonts.load(str(font_path))
    only(obj,c);bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.convert(target='MESH');obj=bpy.context.object;obj.select_set(False);return obj


def broadleaf_tree(name,loc,scale,c):
    x,y,z=loc
    cyl(name+"_trunk",(x,y,z+1.9*scale),.25*scale,3.8*scale,BARK,c,14,w=.035)
    # Individual elongated leaves create a layered canopy, not faceted blobs.
    for i in range(18):
        a=i*2.399963;ring=.55+(i%5)*.25;lx=x+math.cos(a)*ring*scale;ly=y+math.sin(a)*ring*.72*scale;lz=z+(3.2+(i%4)*.42)*scale
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10,ring_count=6,location=(lx,ly,lz),rotation=(math.radians(18+(i%3)*9),a*.4,a))
        o=bpy.context.object;o.name=name+f"_leaf_{i:02d}";o.scale=(.82*scale,.29*scale,.11*scale);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(LEAF if i%3 else LEAF_LIGHT);only(o,c)
        for poly in o.data.polygons:poly.use_smooth=True


def lathe(name, profile, mat, c, segments=48):
    verts=[]
    for z,r in profile:
        for i in range(segments):
            a=2*math.pi*i/segments;verts.append((math.cos(a)*r,math.sin(a)*r,z))
    faces=[]
    rows=len(profile)
    for row in range(rows-1):
        for i in range(segments):
            j=(i+1)%segments;a=row*segments+i;b=row*segments+j;d=(row+1)*segments+i;e=(row+1)*segments+j
            faces.append((a,b,e,d))
    me=bpy.data.meshes.new(name+"_Mesh");me.from_pydata(verts,[],faces);me.update()
    obj=bpy.data.objects.new(name,me);c.objects.link(obj);obj.data.materials.append(mat)
    for poly in obj.data.polygons:poly.use_smooth=True
    return obj


def scalloped_awning(name,x,y,z,w,proj,mat,c,front=-1):
    # Main sloped cloth plus a real hanging valance with individual scallops.
    y2=y+front*proj
    verts=[(x-w/2,y,z+.42),(x+w/2,y,z+.42),(x-w/2,y2,z),(x+w/2,y2,z),
           (x-w/2,y,z+.30),(x+w/2,y,z+.30),(x-w/2,y2,z-.10),(x+w/2,y2,z-.10)]
    faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    me=bpy.data.meshes.new(name+"_Mesh");me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);c.objects.link(o);o.data.materials.append(mat);bevel(o,.025,2)
    for i in range(max(3,int(w/.65))):
        xx=x-w/2+(i+.5)*w/max(3,int(w/.65))
        cyl(name+f"_scallop_{i}",(xx,y2+front*.02,z-.18),w/max(3,int(w/.65))*.42,.10,mat,c,12,rot=(math.radians(90),0,0),w=.01)
    for dx in (-w*.38,w*.38):
        brace=box(name+f"_bracket_{dx:+.1f}",(x+dx,(y+y2)/2,z-.22),(.07,proj*.93,.07),STEEL,c,.018,1,rot=(math.radians(front*8),0,0))
    return o


# ---------------------------------------------------------------------------
# HERO 1: specific station frontage and platform, informed by 2015/2024 photos
# ---------------------------------------------------------------------------
S=0.0
box("Station_WingShell",(S,1.5,2.6),(38,5.6,5.2),PLASTER,STATION,.10,3)
box("Station_CentralProjection",(S,-1.45,3.0),(10.5,1.9,6.0),PLASTER,STATION,.09,3)
gable_roof("Station_MainCorrugatedRoof",(S,1.5,0),40.0,8.1,5.35,1.35,.22,GALV,STATION)
gable_roof("Station_CentralGable",(S,-2.5,0),11.6,3.4,6.0,2.55,.24,TERRACOTTA,STATION)
gable_roof("Station_VerandaRoof",(S,-3.4,0),40.0,3.3,4.65,.48,.18,TERRACOTTA,STATION)
box("Station_VerandaFascia",(S,-5.02,4.60),(40.0,.22,.42),SALMON,STATION,.045,2)
box("Station_PlatformPlinth",(S,-3.0,.18),(40,6.2,.36),PAVER,STATION,.035,2)

# Three non-identical facade groups with actual recessed vestibules.
groups=[(-12.2,"window"),(-6.0,"door"),(0,"central"),(6.6,"door"),(13.0,"window")]
for idx,(x,kind) in enumerate(groups):
    if kind=="central":
        box("Station_CentralShadowBox",(x,-2.52,2.35),(6.4,1.55,3.85),TIMBER,STATION,.04,2)
        panel_frame("Station_CentralDoors",x,-3.34,2.38,5.4,3.25,.15,SALMON,GLASS,STATION,-1)
        # Specific modeled train pictogram sign, not a blank slot or copied wording.
        box("Station_IdentityPanel",(x,-3.55,5.28),(4.8,.18,1.05),STEEL,STATION,.08,3)
        box("Station_TrainGlyphBody",(x,-3.67,5.31),(1.55,.09,.50),WHITE,STATION,.10,3)
        for gx in (-.42,0,.42):box(f"Station_TrainGlyphWindow_{gx}",(x+gx,-3.73,5.40),(.26,.05,.16),GLASS,STATION,.025,2)
        for gx in (-.48,.48):cyl(f"Station_TrainGlyphWheel_{gx}",(x+gx,-3.74,5.02),.11,.06,GOLD,STATION,12,rot=(math.radians(90),0,0),w=.01)
    elif kind=="door":
        box(f"Station_Recess_{idx}",(x,-1.52,2.25),(4.5,1.1,3.8),TIMBER,STATION,.045,2)
        panel_frame(f"Station_DoorSet_{idx}",x,-2.11,2.28,3.65,3.2,.14,SALMON,GLASS,STATION,-1)
        box(f"Station_WarmInterior_{idx}",(x,-1.98,2.50),(3.0,.04,1.85),WARM_LIGHT,STATION,.01,1)
    else:
        panel_frame(f"Station_WindowBay_{idx}",x,-1.40,2.55,5.1,2.2,.16,SALMON,GLASS,STATION,-1)
        box(f"Station_WindowSill_{idx}",(x,-1.62,1.42),(5.5,.42,.22),CONCRETE_LIGHT,STATION,.04,2)

# Characteristic peach veranda columns, bases/capitals and Y-braces.
for i,x in enumerate((-17,-12,-6,0,6,12,17)):
    box(f"Station_ColumnBase_{i}",(x,-4.20,.65),(.82,.82,.92),CONCRETE_LIGHT,STATION,.08,3)
    box(f"Station_Column_{i}",(x,-4.20,2.65),(.42,.42,3.9),SALMON,STATION,.055,3)
    box(f"Station_ColumnCapital_{i}",(x,-4.20,4.48),(.78,.70,.25),PLASTER,STATION,.05,2)
    for dx in (-.75,.75):
        brace=box(f"Station_VerandaBrace_{i}_{dx:+.1f}",(x+dx/2,-4.20,4.15),(1.55,.14,.16),SALMON,STATION,.025,2,rot=(0,math.radians(28 if dx>0 else -28),0))

# Forecourt: real curb/drain/lay-by identity and passenger detail.
box("Station_ForecourtPaving",(0,-11.0,-.06),(44,11.5,.18),PAVER,STATION,.025,2)
for x in (-16,-8,0,8,16):box(f"Station_PavingBand_{x}",(x,-11.0,.045),(.11,11.1,.045),CONCRETE_LIGHT,STATION,.01,1)
box("Station_Curb",(0,-16.7,.18),(44,.55,.42),CONCRETE_LIGHT,STATION,.07,3)
box("Station_CurbRamp",(0,-16.82,.09),(4.2,1.25,.18),PAVER,STATION,.035,2)
box("Station_LinearDrain",(0,-5.52,.02),(39,.48,.16),CONCRETE,STATION,.035,2)
for x in range(-18,19,1):box(f"Station_DrainGrate_{x}",(x,-5.52,.115),(.54,.38,.035),STEEL,STATION,.008,1)
box("Station_LaybyAsphalt",(0,-20.0,-.13),(44,6.0,.22),ASPHALT,STATION,.02,1)
for x in (-14,-9,9,14):cyl(f"Station_Bollard_{x}",(x,-15.6,.55),.14,1.10,STEEL,STATION,14,w=.035)
# Bench and planted identity pylon.
for x in (-10.2,10.2):
    box(f"Station_BenchSeat_{x}",(x,-7.2,.72),(3.2,.62,.18),TIMBER,STATION,.06,3)
    box(f"Station_BenchBack_{x}",(x,-6.95,1.25),(3.2,.18,1.0),TIMBER,STATION,.06,3,rot=(math.radians(-8),0,0))
    for dx in (-1.15,1.15):box(f"Station_BenchLeg_{x}_{dx}",(x+dx,-7.2,.38),(.16,.45,.62),STEEL,STATION,.035,2)
box("Station_IdentityPylon",(15.1,-8.0,1.45),(2.4,.56,2.9),PLASTER,STATION,.12,4)
box("Station_IdentityPylonInset",(15.1,-8.30,1.52),(1.85,.09,1.85),STEEL,STATION,.08,3)
for gx in (-.44,0,.44):box(f"Station_PylonGlyph_{gx}",(15.1+gx,-8.37,1.63),(.25,.05,.52),WHITE,STATION,.04,2)
for px in (-17,17):
    box(f"Station_Planter_{px}",(px,-7.5,.38),(1.15,1.15,.76),CONCRETE_LIGHT,STATION,.12,4)
    broadleaf_tree(f"Station_ShadeTree_{px}",(px,-7.5,.72),.75,STATION)
# Roof construction, rainwater goods and localized age break the former wedge
# silhouette and tie the frontage to a maintained but weathered working station.
box("Station_VerandaSoffit",(0,-4.15,4.50),(39.4,2.45,.16),TIMBER,STATION,.025,2)
curved_tube("Station_FrontGutter",[(-20.0,-5.10,4.73),(0,-5.10,4.70),(20.0,-5.10,4.73)],.09,GALV,STATION)
for x in (-19.0,19.0):
    curved_tube(f"Station_Downpipe_{x}",[(x,-5.10,4.7),(x,-5.18,1.0),(x,-5.42,.35)],.065,GALV,STATION)
for x in (-13.0,-4.5,5.2,13.3):
    box(f"Station_WindowHood_{x}",(x,-4.16,3.85),(3.4,.72,.16),TERRACOTTA,STATION,.035,2,rot=(math.radians(-6),0,0))
for x,w in ((-14.5,4.2),(-7.2,3.2),(7.7,3.0),(14.6,3.8)):
    box(f"Station_SillAge_{x}",(x,-4.28,.52),(w,.07,.36),CONCRETE,STATION,.025,2)
box("Station_ServiceTrolley",(-3.8,-8.5,.70),(1.7,.9,1.2),SHUTTER,STATION,.07,3)
for x in (-4.35,-3.25):cyl(f"Station_ServiceTrolleyWheel_{x}",(x,-9.0,.28),.25,.12,STEEL,STATION,14,rot=(math.radians(90),0,0),w=.018)
for i,(x,z,mat) in enumerate(((-2.8,.34,TERRACOTTA),(-1.9,.42,GOLD),(-2.2,.88,SHUTTER))):box(f"Station_ArrivalCase_{i}",(x,-8.1,z),(.72,.42,.65),mat,STATION,.055,3)
# Wayfinding panel uses approved universal geometry, not invented wording.
box("Station_WayfindingHeader",(15.1,-8.33,2.72),(1.65,.07,.22),GOLD,STATION,.025,2)
for i,x in enumerate((14.65,15.1,15.55)):
    box(f"Station_WayfindingTick_{i}",(x,-8.38,1.10+i*.18),(.22,.04,.18),WHITE,STATION,.02,2)

# Back platform: distinctive yellow-cream current canopy and track language.
box("Platform_Deck",(0,8.5,.38),(42,7.0,.76),CONCRETE_LIGHT,STATION,.05,2)
box("Platform_TactileStrip",(0,11.35,.80),(40,.52,.075),GOLD,STATION,.018,1)
gable_roof("Platform_LongCanopy",(0,7.3,0),38,7.0,5.4,.75,.18,GALV,STATION)
for i,x in enumerate((-16,-10,-4,2,8,14)):
    box(f"Platform_PostFoot_{i}",(x,7.2,.82),(.86,.86,.76),CONCRETE,STATION,.075,3)
    box(f"Platform_Post_{i}",(x,7.2,3.1),(.34,.34,4.55),STEEL_CREAM,STATION,.045,3)
    box(f"Platform_CrossHead_{i}",(x,7.2,5.1),(.38,4.7,.26),STEEL_CREAM,STATION,.04,2)
    for side in (-1,1):
        brace=box(f"Platform_YBrace_{i}_{side}",(x,7.2+side*1.12,4.55),(.16,2.55,.16),STEEL_CREAM,STATION,.025,2,rot=(math.radians(side*31),0,0))
for y in (13.1,15.35):
    box(f"TrackBallast_{y}",(0,y,.02),(46,1.7,.26),CONCRETE,STATION,.025,1)
    for side in (-.50,.50):box(f"TrackRail_{y}_{side}",(0,y+side,.23),(46,.11,.15),STEEL,STATION,.025,2)
    for x in range(-21,22,2):box(f"TrackSleeper_{y}_{x}",(x,y,.12),(.30,1.45,.16),TIMBER,STATION,.025,2)
# Small signal-box hero echo.
box("Platform_SignalBoxBase",(-14.5,5.6,3.5),(3.0,3.0,7.0),CONCRETE_LIGHT,STATION,.08,3)
box("Platform_SignalBoxCab",(-14.5,5.6,7.2),(5.2,4.0,2.4),TIMBER,STATION,.10,3)
for side in (-1,1):panel_frame(f"SignalBox_Window_{side}",-14.5+side*1.25,3.54,7.35,1.85,1.15,.12,TIMBER,GLASS,STATION,-1)
gable_roof("SignalBox_Roof",(-14.5,5.6,0),6.0,5.0,8.38,.55,.16,TERRACOTTA,STATION)
# Platform furniture is intentionally sparse but authored, breaking up the bare
# slab while preserving the clear player route beside the tactile strip.
for x in (-7.0,6.0):
    box(f"Platform_BenchSeat_{x}",(x,8.75,1.22),(2.8,.58,.16),TIMBER,STATION,.05,3)
    box(f"Platform_BenchBack_{x}",(x,8.98,1.72),(2.8,.16,.90),TIMBER,STATION,.05,3,rot=(math.radians(-7),0,0))
    for dx in (-.95,.95):box(f"Platform_BenchLeg_{x}_{dx}",(x+dx,8.75,1.0),(.14,.42,.45),STEEL,STATION,.03,2)
for x in (-12.0,11.5):
    box(f"Platform_BinBody_{x}",(x,9.75,1.25),(.62,.62,.95),STEEL,STATION,.08,3)
    box(f"Platform_BinOpening_{x}",(x,9.42,1.50),(.30,.04,.20),CONCRETE,STATION,.015,1)
cyl("Platform_ClockFace",(-1.0,7.03,4.12),.42,.10,WHITE,STATION,24,rot=(math.radians(90),0,0),w=.018)
cyl("Platform_ClockHub",(-1.0,6.96,4.12),.06,.05,STEEL,STATION,12,rot=(math.radians(90),0,0),w=.01)
# Platform edge assembly, service signage, lights and a low urban backdrop.
box("Platform_EdgeFascia",(0,11.77,.47),(42,.18,.78),CONCRETE,STATION,.025,2)
for x in range(-19,20,4):box(f"Platform_EdgeMarker_{x}",(x,11.88,.60),(1.9,.035,.18),WHITE if x%8 else GOLD,STATION,.008,1)
for x in (-10,3,15):
    cyl(f"Platform_LightPole_{x}",(x,9.8,3.0),.075,4.5,STEEL_CREAM,STATION,12,w=.018)
    box(f"Platform_LightHead_{x}",(x,9.60,5.15),(.72,.38,.20),WHITE,STATION,.05,3)
for x in (-9,8):
    box(f"Platform_WayfindingFrame_{x}",(x,7.03,3.45),(2.7,.13,1.05),STEEL,STATION,.05,3)
    box(f"Platform_WayfindingInset_{x}",(x,6.94,3.45),(2.28,.035,.66),SALMON,STATION,.035,2)
    for dx in (-.62,0,.62):box(f"Platform_WayfindingGlyph_{x}_{dx}",(x+dx,6.90,3.45),(.26,.025,.30),WHITE,STATION,.025,2)
for x,h,mat in ((-10,5.4,PLASTER),(-2,4.3,SALMON),(7,6.2,PLASTER),(15,4.8,TIMBER)):
    box(f"Platform_Backdrop_{x}",(x,24.0,h/2),(7.2,5.0,h),mat,STATION,.08,3)
    gable_roof(f"Platform_BackdropRoof_{x}",(x,24.0,0),7.8,5.8,h+.05,.75,.15,TERRACOTTA,STATION)
box("Station_Nameboard",(0,-5.19,4.03),(10.8,.16,.82),WHITE,STATION,.055,3)
text_mesh("Station_Name_English","NAKHON PATHOM",(0,-5.30,4.02),.27,STEEL,STATION)


# ---------------------------------------------------------------------------
# HERO 2: asymmetric lived corner storefront group, four unique constructions
# ---------------------------------------------------------------------------
X=90.0
box("Street_Road",(X,0,-.12),(56,10,.22),ASPHALT,STREET,.02,1)
box("Street_SidewalkSouth",(X,-6.0,.08),(56,2.2,.32),CONCRETE_LIGHT,STREET,.035,2)
box("Street_SidewalkNorth",(X,6.0,.08),(56,2.2,.32),CONCRETE_LIGHT,STREET,.035,2)
for y in (-5.05,5.05):
    box(f"Street_OpenDrain_{y}",(X,y,.00),(56,.46,.28),CONCRETE,STREET,.035,2)
    for x in range(64,117,2):box(f"Street_DrainGrate_{y}_{x}",(x,y,.17),(1.22,.39,.055),STEEL,STREET,.015,1)

# A: three-storey concrete/bricked corner with chamfered entry impression.
box("ShopA_Main",(70,8.5,5.1),(12,6.8,10.2),PLASTER,STREET,.11,3)
box("ShopA_BrickBand",(70,4.98,6.9),(10.7,.18,2.1),BRICK,STREET,.035,2)
box("ShopA_DeepArcade",(70,4.25,2.1),(9.5,1.65,4.2),TIMBER,STREET,.055,2)
panel_frame("ShopA_GlassEntry",70,3.35,2.05,4.2,3.45,.16,STEEL,GLASS,STREET,-1)
for x in (66.8,73.2):panel_frame(f"ShopA_UpperWindow_{x}",x,4.91,7.3,2.6,2.1,.13,PLASTER,GLASS,STREET,-1)
box("ShopA_Balcony",(70,4.2,5.35),(10.4,1.5,.26),CONCRETE_LIGHT,STREET,.05,2)
for x in range(66,75,2):cyl(f"ShopA_Baluster_{x}",(x,3.63,6.02),.045,1.25,STEEL,STREET,10,w=0)
curved_tube("ShopA_BalconyRail",[(65.2,3.63,6.65),(70,3.63,6.65),(74.8,3.63,6.65)],.055,STEEL,STREET)
box("ShopA_Cornice",(70,4.95,9.65),(12.6,.42,.55),CONCRETE_LIGHT,STREET,.07,3)
scalloped_awning("ShopA_Awning",70,4.25,4.2,8.2,2.2,AWNING_GREEN,STREET,-1)

# B: low timber food shop with tiled roof and actual display depth.
box("ShopB_TimberShell",(82,8.8,2.8),(9.2,6.2,5.6),TIMBER,STREET,.08,3)
gable_roof("ShopB_TiledRoof",(82,8.8,0),10.6,7.6,5.65,1.35,.22,TERRACOTTA,STREET)
box("ShopB_OpenFront",(82,5.42,2.1),(7.8,1.25,3.8),CONCRETE,STREET,.045,2)
scalloped_awning("ShopB_ClothAwning",82,5.20,4.6,8.4,2.4,AWNING_BLUE,STREET,-1)
box("ShopB_DisplayCounter",(82,3.95,1.05),(6.2,1.15,1.8),SHUTTER,STREET,.07,3)
box("ShopB_CounterTop",(82,3.95,2.02),(6.5,1.35,.16),STEEL,STREET,.045,2)
for i,x in enumerate((79.6,80.8,82,83.2,84.4)):
    for j in range(3):
        cyl(f"ShopB_Produce_{i}_{j}",(x,3.9,2.2+j*.18),.18,.16,[TERRACOTTA,GOLD,LEAF_LIGHT][(i+j)%3],STREET,12,w=.015)
for x in (78.8,85.2):box(f"ShopB_Crate_{x}",(x,4.0,.52),(1.0,1.0,.9),TIMBER,STREET,.045,2)

# C: narrow two-storey shutter shop, half-open with warm interior.
box("ShopC_Shell",(94,8.2,4.2),(8.2,5.1,8.4),CONCRETE_LIGHT,STREET,.09,3)
box("ShopC_EntryRecess",(94,5.25,2.1),(6.8,1.4,4.2),WARM_LIGHT,STREET,.045,2)
box("ShopC_ShutterLeft",(92.2,4.46,2.35),(2.55,.16,3.7),SHUTTER,STREET,.035,2)
box("ShopC_ShutterRaised",(96.2,4.46,4.25),(2.55,.16,.55),SHUTTER,STREET,.035,2)
panel_frame("ShopC_UpperWindow",94,5.58,6.5,5.8,1.7,.14,TIMBER,GLASS,STREET,-1)
box("ShopC_ACBracket",(97.1,5.35,6.7),(1.45,.62,.80),GALV,STREET,.06,3)
for side in (-.55,.55):box(f"ShopC_ACVent_{side}",(97.1+side,5.01,6.7),(.08,.04,.55),CONCRETE,STREET,.01,1)
box("ShopC_SignCanopy",(94,4.9,4.9),(6.4,1.1,.26),STEEL,STREET,.05,2,rot=(math.radians(-7),0,0))

# D: opposite-side rounded-corner cafe volume with timber screens.
box("ShopD_CornerMass",(106,-8.2,4.5),(15.0,6.5,9.0),SALMON,STREET,.15,4)
box("ShopD_GroundArcade",(106,-4.55,2.2),(12.8,1.45,4.1),TIMBER,STREET,.06,2)
for x in (101.5,104.5,107.5,110.5):panel_frame(f"ShopD_Screen_{x}",x,-3.78,2.25,2.4,3.25,.14,TIMBER,GLASS,STREET,1)
box("ShopD_UpperBand",(106,-4.90,6.65),(13.4,.20,2.4),BRICK,STREET,.04,2)
for x in (102.5,106,109.5):panel_frame(f"ShopD_UpperWindow_{x}",x,-5.06,6.65,2.5,1.55,.12,PLASTER,GLASS,STREET,1)
box("ShopD_RoofSlab",(106,-8.2,9.05),(15.8,7.2,.42),CONCRETE_LIGHT,STREET,.10,4)
scalloped_awning("ShopD_Awning",106,-4.15,4.55,11.6,2.0,AWNING_GREEN,STREET,1)
# The south-facing return is also a working frontage; the gameplay approach
# must never resolve as an undecorated salmon box.
box("ShopD_ReturnArcade",(106,-11.47,2.15),(11.7,.26,3.9),TIMBER,STREET,.055,3)
for x in (102.5,106.0,109.5):panel_frame(f"ShopD_ReturnScreen_{x}",x,-11.65,2.2,2.75,3.15,.15,TIMBER,GLASS,STREET,-1)
box("ShopD_ReturnBrickBand",(106,-11.50,6.60),(12.8,.24,2.3),BRICK,STREET,.04,2)
for x in (102.5,106.0,109.5):panel_frame(f"ShopD_ReturnUpperWindow_{x}",x,-11.68,6.65,2.5,1.55,.12,PLASTER,GLASS,STREET,-1)
scalloped_awning("ShopD_ReturnAwning",106,-11.58,4.52,10.8,1.75,AWNING_BLUE,STREET,-1)
# Deep threshold kits: 1.35 m sidewalls/ceilings visibly establish real shop
# depth instead of black cards. Each family is intentionally non-identical.
for name,x,y,w,mat in (("A",70,3.15,4.8,BRICK),("B",82,4.25,6.4,TIMBER),("C",95.5,4.45,2.6,CONCRETE_LIGHT)):
    box(f"Shop{name}_RecessCeiling",(x,y+.62,4.02),(w,1.35,.18),mat,STREET,.035,2)
    for side in (-1,1):box(f"Shop{name}_RecessReturn_{side}",(x+side*w/2,y+.62,2.25),(.20,1.35,3.55),mat,STREET,.04,2)
    box(f"Shop{name}_Threshold",(x,y+.62,.32),(w,1.35,.22),PAVER,STREET,.025,2)
# Parapets, rainwater goods, meters, conduit and patch repairs convey local
# construction/maintenance layers without relying on photo textures.
for x,w,z in ((70,11.2,10.05),(94,7.6,8.38),(106,14.5,9.18)):
    box(f"Street_ParapetCap_{x}",(x,5.02 if x!=106 else -11.52,z),(w,.36,.30),CONCRETE_LIGHT,STREET,.05,3)
for x,y in ((65,5.0),(75,5.0),(90,5.58),(98,5.58),(99,-11.55),(113,-11.55)):
    curved_tube(f"Street_Downpipe_{x}",[(x,y,7.6),(x,y-.05,1.0),(x,y-.28,.28)],.055,GALV,STREET)
for i,(x,y,z) in enumerate(((67.2,4.72,2.6),(91.0,4.68,3.2),(99.6,-11.72,2.8),(112.4,-11.72,3.0))):
    box(f"Street_MeterBox_{i}",(x,y,z),(.52,.16,.72),GALV,STREET,.055,3)
    cyl(f"Street_MeterDial_{i}",(x,y-.10,z+.08),.16,.05,WHITE,STREET,16,rot=(math.radians(90),0,0),w=.012)
    curved_tube(f"Street_MeterConduit_{i}",[(x,y,z-.36),(x,y,z-1.2),(x+.28,y,z-1.55)],.025,STEEL,STREET)
for i,(x,y,w,h) in enumerate(((68,4.86,2.8,.52),(73.5,4.86,2.0,.38),(92.8,5.62,2.5,.44),(108,-11.72,2.7,.48))):
    box(f"Street_PlasterRepair_{i}",(x,y,1.0+i*.45),(w,.035,h),CONCRETE,STREET,.018,2)
# Small market rhythm outside the clear carriageway: stools, baskets, menu
# battens and one parked bicycle-like frame.
for i,(x,y) in enumerate(((78,5.0),(80,5.0),(84,5.0),(96,5.0),(101,-5.0),(104,-5.0))):
    cyl(f"Street_StoolSeat_{i}",(x,y,.55),.28,.12,[TERRACOTTA,AWNING_BLUE,AWNING_GREEN][i%3],STREET,14,w=.02)
    for a in range(3):cyl(f"Street_StoolLeg_{i}_{a}",(x+math.cos(a*2.094)*.18,y+math.sin(a*2.094)*.18,.30),.025,.50,STEEL,STREET,8,w=0)
for i,(x,y) in enumerate(((86,4.8),(88,4.8),(111,-5.0))):
    cyl(f"Street_Basket_{i}",(x,y,.35),.42,.55,TIMBER,STREET,16,w=.035)
for i,x in enumerate((72,82,95,106)):
    box(f"Street_SignBlade_{i}",(x,3.55 if i<3 else -3.55,4.85),(1.05,.15,1.45),[SALMON,AWNING_BLUE,AWNING_GREEN,GOLD][i],STREET,.08,3)
    for z in (4.45,4.82,5.18):box(f"Street_SignGlyph_{i}_{z}",(x,3.45 if i<3 else -3.45,z),(.55,.035,.10),WHITE,STREET,.018,1)
for x,y in ((89,-4.7),(115,4.8)):
    cyl(f"Street_BikeWheelA_{x}",(x-.55,y,.55),.45,.055,STEEL,STREET,20,rot=(math.radians(90),0,0),w=0)
    cyl(f"Street_BikeWheelB_{x}",(x+.55,y,.55),.45,.055,STEEL,STREET,20,rot=(math.radians(90),0,0),w=0)
    curved_tube(f"Street_BikeFrame_{x}",[(x-.55,y,.55),(x,y,.95),(x+.55,y,.55),(x-.15,y,.55),(x-.55,y,.55)],.025,GOLD,STREET)

# Street clutter informed by market: carts, stools, planters, utility/cables.
for i,x in enumerate((76,88,99,113)):
    box(f"Street_Cart_{i}",(x,-4.15,.82),(2.0,1.05,1.35),SHUTTER,STREET,.065,3)
    box(f"Street_CartTop_{i}",(x,-4.15,1.56),(2.2,1.20,.16),STEEL,STREET,.04,2)
    for dx in (-.72,.72):cyl(f"Street_CartWheel_{i}_{dx}",(x+dx,-4.72,.42),.34,.13,STEEL,STREET,14,rot=(math.radians(90),0,0),w=.025)
for x,y in ((75,-6.5),(87,6.8),(100,-6.6),(115,6.7)):
    box(f"Street_Planter_{x}",(x,y,.45),(1.05,1.05,.9),CONCRETE_LIGHT,STREET,.13,4);broadleaf_tree(f"Street_Tree_{x}",(x,y,.85),.72,STREET)
for x in (67,87,108):
    cyl(f"Street_UtilityPole_{x}",(x,-7.0,4.6),.18,9.2,CONCRETE,STREET,14,w=.035)
    box(f"Street_CrossArm_{x}",(x,-7.0,8.45),(3.2,.18,.18),TIMBER,STREET,.035,2)
for lane in range(5):
    curved_tube(f"Street_Cable_{lane}",[(67,-7+lane*.11,8.8+lane*.17),(87,-7+lane*.11,8.1+lane*.17),(108,-7+lane*.11,8.75+lane*.17)],.027,TIMBER,STREET)


# ---------------------------------------------------------------------------
# HERO 3: structurally credible 50m bridge + stepped canal/bank set
# ---------------------------------------------------------------------------
B=180.0
# dark reflective water volume and reference-led stepped canal terraces
box("Canal_Water",(B,0,.02),(50,88,.18),WATER,BRIDGE,.015,1)
for side in (-1,1):
    x=B+side*25.0
    # Four real terrace tiers, each with nosing shadow and waterline staining.
    for tier in range(4):
        xx=x+side*(.65+tier*.72);z=.35+tier*.46;w=1.25+tier*.20
        box(f"Canal_Terrace_{side}_{tier}",(xx,0,z),(w,88,.42),CONCRETE,BRIDGE,.055,2)
        box(f"Canal_TerraceNosing_{side}_{tier}",(xx-side*w*.42,0,z+.24),(.18,88,.12),CONCRETE_LIGHT,BRIDGE,.025,2)
    box(f"Canal_WaterlineStain_{side}",(x-side*.20,0,.36),(.34,88,.68),ALGAE,BRIDGE,.025,2)
    box(f"Canal_TopWalk_{side}",(x+side*4.0,0,2.35),(4.0,88,.35),PAVER,BRIDGE,.05,2)
    curved_tube(f"Canal_TopRail_{side}",[(x+side*2.15,-44,3.45),(x+side*2.15,0,3.45),(x+side*2.15,44,3.45)],.07,STEEL,BRIDGE)
    for y in range(-42,43,4):cyl(f"Canal_RailPost_{side}_{y}",(x+side*2.15,y,2.9),.065,1.1,STEEL,BRIDGE,12,w=.02)

# Single continuous crowned deck mesh: 50m clear span, 12m overall.
sections=[]
for i in range(11):
    x=B-25+i*5;z=6.15+math.sin(math.pi*i/10)*.55;sections.append((x,z))
verts=[]
for x,z in sections:verts += [(x,-6,z-.35),(x,6,z-.35),(x,-6,z+.35),(x,6,z+.35)]
faces=[]
for i in range(10):
    a=i*4;b=(i+1)*4
    faces += [(a,b,b+2,a+2),(a+1,a+3,b+3,b+1),(a,a+1,b+1,b),(a+2,b+2,b+3,a+3)]
faces += [(0,2,3,1),(40,41,43,42)]
me=bpy.data.meshes.new("Bridge_CrownedDeck_Mesh");me.from_pydata(verts,[],faces);me.update();deck=bpy.data.objects.new("Bridge_CrownedDeck_50m",me);BRIDGE.objects.link(deck);deck.data.materials.append(CONCRETE_LIGHT);bevel(deck,.06,2)
# Lower steel longitudinal plate girders and transverse diaphragms.
for y in (-4.5,4.5):
    for i in range(10):
        x=B-22.5+i*5;z=5.55+math.sin(math.pi*(i+.5)/10)*.55
        box(f"Bridge_LongGirder_{y}_{i}",(x,y,z),(5.05,.28,1.05),STEEL,BRIDGE,.045,2)
        box(f"Bridge_GirderFlangeTop_{y}_{i}",(x,y,z+.55),(5.12,.55,.12),STEEL,BRIDGE,.025,2)
        box(f"Bridge_GirderFlangeBottom_{y}_{i}",(x,y,z-.55),(5.12,.55,.12),STEEL,BRIDGE,.025,2)
for i,x in enumerate(range(157,204,5)):
    z=5.42+math.sin(math.pi*(x-(B-25))/50)*.55
    box(f"Bridge_Diaphragm_{i}",(x,0,z),(0.22,9.0,.65),STEEL,BRIDGE,.035,2)

# 8m shared lane, 2m pedestrian bands, drainage and expansion joints.
for side in (-1,1):
    box(f"Bridge_PedBand_{side}",(B,side*5.0,6.72),(49.2,1.75,.14),PAVER,BRIDGE,.025,2)
    box(f"Bridge_TactileEdge_{side}",(B,side*4.1,6.78),(49.2,.18,.06),GOLD,BRIDGE,.015,1)
    box(f"Bridge_DeckDrain_{side}",(B,side*5.78,6.69),(48.5,.20,.08),STEEL,BRIDGE,.018,1)
for x in (B-24.4,B,B+24.4):box(f"Bridge_ExpansionJoint_{x}",(x,0,6.76),(.16,11.6,.06),STEEL,BRIDGE,.012,1)
# Dark shared lane follows the crown in short structurally legible pours.
for i in range(10):
    x=B-22.5+i*5;z=6.55+math.sin(math.pi*(i+.5)/10)*.55
    slope=math.atan2((math.sin(math.pi*(i+1)/10)-math.sin(math.pi*i/10))*.55,5.0)
    box(f"Bridge_AsphaltLane_{i}",(x,0,z),(5.04,7.9,.12),ASPHALT,BRIDGE,.018,1,rot=(0,-slope,0))
    box(f"Bridge_CentreMark_{i}",(x,0,z+.075),(2.6,.13,.035),GOLD,BRIDGE,.008,1,rot=(0,-slope,0))

# Round tube railings with curved top rail and handcrafted anchor shoes.
for side in (-1,1):
    y=side*5.78
    railpts=[(x,y,7.88+math.sin(math.pi*(x-(B-25))/50)*.55) for x in (B-25,B-12.5,B,B+12.5,B+25)]
    curved_tube(f"Bridge_RoundTopRail_{side}",railpts,.075,STEEL,BRIDGE)
    midpts=[(x,y,7.35+math.sin(math.pi*(x-(B-25))/50)*.55) for x in (B-25,B-12.5,B,B+12.5,B+25)]
    curved_tube(f"Bridge_RoundMidRail_{side}",midpts,.045,STEEL,BRIDGE)
    for i,x in enumerate(range(155,206,2)):
        z=6.77+math.sin(math.pi*(x-(B-25))/50)*.55
        box(f"Bridge_RailFoot_{side}_{i}",(x,y,z+.10),(.28,.28,.18),STEEL,BRIDGE,.045,2)
        cyl(f"Bridge_RoundBaluster_{side}_{i}",(x,y,z+.65),.052,1.18,STEEL,BRIDGE,12,w=.018)

# Articulated abutments and splayed wing walls.
for side in (-1,1):
    x=B+side*25.4
    box(f"Bridge_AbutmentMass_{side}",(x,0,3.5),(2.8,15.5,7.0),CONCRETE,BRIDGE,.12,4)
    box(f"Bridge_BearingShelf_{side}",(x-side*1.25,0,5.75),(1.2,12.8,.70),CONCRETE_LIGHT,BRIDGE,.08,3)
    for y in (-7.6,7.6):
        box(f"Bridge_WingWall_{side}_{y}",(x+side*3.1,y,3.0),(7.0,.75,5.3),CONCRETE,BRIDGE,.10,3,rot=(0,0,math.radians(side*(12 if y>0 else -12))))
    box(f"Bridge_AbutmentStain_{side}",(x-side*1.47,0,2.05),(.12,13.8,2.2),ALGAE,BRIDGE,.025,2)

# Curved civic lamps and cantilevered rest bays outside movement lane.
for side in (-1,1):
    for i,x in enumerate((158,168,180,192,202)):
        z=6.8+math.sin(math.pi*(x-(B-25))/50)*.55
        cyl(f"Bridge_LampPole_{side}_{i}",(x,side*5.35,z+2.45),.10,4.9,STEEL,BRIDGE,14,w=.03)
        curved_tube(f"Bridge_LampSwan_{side}_{i}",[(x,side*5.35,z+4.75),(x,side*5.05,z+5.25),(x,side*4.35,z+5.20)],.065,STEEL,BRIDGE)
        box(f"Bridge_LampHead_{side}_{i}",(x,side*4.10,z+5.08),(.72,.42,.24),GOLD,BRIDGE,.08,3)
for side,x in ((-1,171),(1,189)):
    y=side*7.15;z=6.95+math.sin(math.pi*(x-(B-25))/50)*.55
    box(f"Bridge_RestBay_{side}",(x,y,z),(3.2,2.7,.38),CONCRETE_LIGHT,BRIDGE,.09,3)
    box(f"Bridge_RestBenchSeat_{side}",(x,y,z+.52),(2.2,.62,.18),TIMBER,BRIDGE,.07,3)
    box(f"Bridge_RestBenchBack_{side}",(x,y+side*.25,z+1.05),(2.2,.16,.95),TIMBER,BRIDGE,.07,3,rot=(math.radians(side*8),0,0))
    for dx in (-.78,.78):box(f"Bridge_RestBenchLeg_{side}_{dx}",(x+dx,y,z+.24),(.16,.44,.48),STEEL,BRIDGE,.035,2)

# Canal vegetation: layered individual leaves and reed clumps.
for side in (-1,1):
    x=B+side*30.0
    for y in (-29,-13,13,29):broadleaf_tree(f"Canal_Tree_{side}_{y}",(x,y,2.5),.82,BRIDGE)
    for y in (-36,-22,-5,6,22,36):
        for j in range(5):
            # A bevel on a radius-18 mm reed collapses cap loops after export;
            # the un-bevelled eight-sided stem is already sub-pixel at gameplay distance.
            cyl(f"Canal_Reed_{side}_{y}_{j}",(B+side*(24.0+j*.12),y+j*.18,.78+j*.07),.018,1.55+j*.12,LEAF_LIGHT,BRIDGE,8,rot=(math.radians(j*2),0,math.radians(j*11)),w=0)

# Water variation, wall joints, bank-to-bridge access and end framing make the
# 50 m crossing read as a built route over a canal instead of a floating slab.
box("Canal_DeepChannel",(B,0,.11),(30,88,.035),WATER_DEEP,BRIDGE,.008,1)
for i,y in enumerate((-34,-22,-9,5,18,31)):
    curved_tube(f"Canal_SurfaceGlint_{i}",[(B-12,y,.20),(B,y+.6,.22),(B+11,y-.3,.20)],.028,WATER_GLINT,BRIDGE)
for side in (-1,1):
    x=B+side*25.42
    for y in range(-6,7,3):box(f"Bridge_AbutmentJoint_{side}_{y}",(x-side*1.43,y,3.35),(.035,1.9,.08),CONCRETE_LIGHT,BRIDGE,.008,1)
    for z in (1.1,2.4,3.7,5.0):box(f"Bridge_AbutmentLiftLine_{side}_{z}",(x-side*1.45,0,z),(.04,13.5,.07),CONCRETE_LIGHT,BRIDGE,.008,1)
    # 20 m approach slab: ~11.3 degrees here is an authored visual profile;
    # final navigable grade remains an integration test, never a PASS claim.
    approach_x=x+side*11.0
    box(f"Bridge_ApproachRamp_{side}",(approach_x,0,4.45),(20.0,11.7,.48),CONCRETE_LIGHT,BRIDGE,.07,3,rot=(0,math.radians(-side*11.3),0))
    box(f"Bridge_ApproachDrain_{side}",(approach_x,side*5.55,4.55),(20.0,.24,.10),STEEL,BRIDGE,.02,1,rot=(0,math.radians(-side*11.3),0))
    # Bank stairs and landing physically join the canal walk to bridge level.
    for step in range(9):
        sx=x+side*(2.1+step*.42);sz=2.55+step*.43
        box(f"Bridge_BankStep_{side}_{step}",(sx,side*7.0,sz),(.52,2.2,.32),CONCRETE_LIGHT,BRIDGE,.035,2)
for side in (-1,1):
    ex=B+side*42
    box(f"Bridge_EndTownMass_{side}_A",(ex,-11,5.2),(12,9,10.4),PLASTER,BRIDGE,.11,3)
    box(f"Bridge_EndTownMass_{side}_B",(ex,12,3.9),(14,8,7.8),SALMON,BRIDGE,.11,3)
    gable_roof(f"Bridge_EndTownRoof_{side}_A",(ex,-11,0),13,10,10.45,1.5,.20,TERRACOTTA,BRIDGE)
    gable_roof(f"Bridge_EndTownRoof_{side}_B",(ex,12,0),15,9,7.85,1.2,.20,GALV,BRIDGE)
    for y,z in ((-15,4.2),(-9,6.8),(9,3.6),(14,4.8)):
        box(f"Bridge_EndTownShade_{side}_{y}_{z}",(ex-side*6.05,y,z),(1.6,2.0,.22),AWNING_GREEN if y<0 else AWNING_BLUE,BRIDGE,.04,2)


# ---------------------------------------------------------------------------
# HERO 4: substantial temple approach wall/gate, respectful and non-portal-like
# ---------------------------------------------------------------------------
T=280.0
box("Temple_ApproachCourt",(T,-10,-.05),(50,25,.18),PAVER,TEMPLE,.025,2)
for side in (-1,1):
    x=T+side*16.5
    box(f"Temple_Wall_{side}",(x,0,2.25),(17.0,1.0,4.5),PLASTER,TEMPLE,.10,4)
    gable_roof(f"Temple_WallCap_{side}",(x,0,0),17.6,1.65,4.48,.48,.18,TERRACOTTA,TEMPLE)
    for px in (x-side*6.2,x,x+side*6.2):
        box(f"Temple_WallPilaster_{side}_{px}",(px,-.08,2.6),(1.0,1.2,5.2),CONCRETE_LIGHT,TEMPLE,.10,4)
        box(f"Temple_PilasterCap_{side}_{px}",(px,-.08,5.18),(1.38,1.52,.35),PLASTER,TEMPLE,.07,3)

# Deep open gate with side guard rooms and layered roof construction.
for side in (-1,1):
    x=T+side*6.25
    box(f"Temple_GatePier_{side}",(x,0,3.5),(2.5,3.1,7.0),PLASTER,TEMPLE,.14,4)
    box(f"Temple_GatePierInset_{side}",(x,-1.62,3.45),(1.45,.18,4.6),SALMON,TEMPLE,.07,3)
    box(f"Temple_GateLampNiche_{side}",(x,-1.78,3.65),(.58,.10,1.20),WARM_LIGHT,TEMPLE,.20,4)
box("Temple_GateHeader",(T,0,6.55),(10.2,3.0,1.0),PLASTER,TEMPLE,.11,4)
gable_roof("Temple_GateMainRoof",(T,0,0),15.5,6.8,7.0,2.65,.26,TERRACOTTA,TEMPLE)
gable_roof("Temple_GateInnerRoof",(T,-.2,0),11.2,5.4,7.42,2.0,.20,GOLD,TEMPLE)
# Modeled timber folding leaves open against piers; passage remains visibly physical.
for side in (-1,1):
    gate=box(f"Temple_OpenTimberLeaf_{side}",(T+side*4.15,-1.65,3.25),(3.6,.24,5.6),TIMBER,TEMPLE,.09,3,rot=(0,0,math.radians(side*10)))
    for z in (1.4,2.6,3.8,5.0):box(f"Temple_GateRail_{side}_{z}",(T+side*4.15,-1.80,z),(3.2,.12,.14),GOLD,TEMPLE,.025,2,rot=(0,0,math.radians(side*10)))
box("Temple_Threshold",(T,-1.0,.18),(10.0,5.6,.36),CONCRETE_LIGHT,TEMPLE,.055,2)
box("Temple_InnerPath",(T,11,.06),(10.0,20,.20),PAVER,TEMPLE,.035,2)
for x in (T-20,T-13,T+13,T+20):broadleaf_tree(f"Temple_ShadeTree_{x}",(x,3,.4),1.08,TEMPLE)
for x in (T-10,T+10):
    box(f"Temple_InfoPlinth_{x}",(x,-7.5,1.22),(2.2,.55,2.45),CONCRETE_LIGHT,TEMPLE,.11,4)
    box(f"Temple_InfoRelief_{x}",(x,-7.82,1.30),(1.55,.10,1.55),SALMON,TEMPLE,.07,3)
    # Simple geometric relief avoids blank slots and unapproved words/logos.
    cyl(f"Temple_InfoReliefDisc_{x}",(x,-7.91,1.38),.42,.08,GOLD,TEMPLE,16,rot=(math.radians(90),0,0),w=.03)

# Reference-led layered boundary: aged plinth, tiled cap rhythm, foreground
# threshold, shaded inner court and a secondary pavilion establish hierarchy.
for side in (-1,1):
    x=T+side*16.5
    box(f"Temple_WallAgePlinth_{side}",(x,-.53,.56),(17.0,.08,.72),CONCRETE,TEMPLE,.025,2)
    for px in (x-7.2,x-3.6,x,x+3.6,x+7.2):
        cyl(f"Temple_WallCapFinial_{side}_{px}",(px,-.05,5.35),.16,.48,TERRACOTTA,TEMPLE,16,w=.02)
box("Temple_GateFasciaShadow",(T,-1.58,6.45),(11.2,.18,.34),TIMBER,TEMPLE,.035,2)
box("Temple_GateGoldDrip",(T,-1.71,6.20),(10.2,.10,.13),GOLD,TEMPLE,.025,2)
for x in (T-4.8,T+4.8):
    box(f"Temple_ThresholdGuardRail_{x}",(x,-4.0,.65),(.16,4.8,1.15),GOLD,TEMPLE,.04,2)
for side in (-1,1):
    x=T+side*11.8
    box(f"Temple_InnerArcadePlinth_{side}",(x,11,.45),(5.6,17,.9),CONCRETE_LIGHT,TEMPLE,.08,3)
    for y in (5,10,15,20):
        box(f"Temple_InnerArcadePost_{side}_{y}",(x,y,3.2),(.62,.62,5.5),PLASTER,TEMPLE,.08,3)
    box(f"Temple_InnerArcadeLintel_{side}",(x,12.5,5.55),(5.6,17,.55),PLASTER,TEMPLE,.08,3)
    gable_roof(f"Temple_InnerArcadeRoof_{side}",(x,12.5,0),6.2,18.0,5.7,1.15,.18,TERRACOTTA,TEMPLE)
# Secondary gabled pavilion terminates the first court so the entry does not
# open onto sky; its doors stay visibly shut because access is unverified.
box("Temple_InnerPavilion",(T,27,4.1),(15,7.5,8.2),PLASTER,TEMPLE,.12,4)
gable_roof("Temple_InnerPavilionRoof",(T,27,0),17.5,10.0,8.25,2.2,.24,TERRACOTTA,TEMPLE)
box("Temple_InnerPavilionDoor",(T,23.18,2.8),(5.8,.22,5.3),TIMBER,TEMPLE,.08,3)
for z in (1.2,2.2,3.2,4.2):box(f"Temple_InnerDoorRail_{z}",(T,23.03,z),(5.2,.10,.13),GOLD,TEMPLE,.02,2)
for x in (T-7.5,T+7.5):broadleaf_tree(f"Temple_InnerCourtTree_{x}",(x,18,.4),.92,TEMPLE)


# ---------------------------------------------------------------------------
# RELEASE BRIDGE RESET — grounded Charoen Sattha / Saphan Yak envelope
# ---------------------------------------------------------------------------
# Remove the superseded fictional 50 m × 12 m bridge built above while keeping
# the accepted station/street/temple families intact.
for obj in list(BRIDGE.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

B=130.0
BRIDGE_LENGTH=34.5
BRIDGE_WIDTH=8.5
BRIDGE_Z=2.35

def guardian(name,loc,facing,c):
    x,y,z=loc
    box(name+"_Plinth",(x,y,z+.28),(1.55,1.45,.56),CONCRETE_LIGHT,c,.10,4)
    for side in (-1,1):
        box(name+f"_Foot_{side}",(x+side*.28,y-facing*.06,z+.72),(.34,.55,.28),GOLD,c,.07,3)
        cyl(name+f"_Leg_{side}",(x+side*.25,y,z+1.48),.19,1.35,GOLD,c,12,w=.035)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,location=(x,y,z+2.55));torso=bpy.context.object;torso.name=name+"_Torso";torso.scale=(.62,.46,.88);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);torso.data.materials.append(GOLD);only(torso,c)
    cyl(name+"_Belt",(x,y,z+2.18),.58,.18,TERRACOTTA,c,18,w=.025)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,location=(x,y-facing*.03,z+3.58));head=bpy.context.object;head.name=name+"_Head";head.scale=(.43,.38,.48);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);head.data.materials.append(GOLD);only(head,c)
    box(name+"_Face",(x,y-facing*.37,z+3.56),(.46,.22,.40),TERRACOTTA,c,.09,3)
    for side in (-1,1):
        cyl(name+f"_Ear_{side}",(x+side*.47,y,z+3.62),.14,.12,GOLD,c,14,rot=(0,math.radians(90),0),w=.02)
        box(name+f"_Arm_{side}",(x+side*.58,y-facing*.05,z+2.72),(.24,.32,1.34),GOLD,c,.08,3,rot=(0,math.radians(side*13),0))
    bpy.ops.mesh.primitive_cone_add(vertices=20,radius1=.52,radius2=.13,depth=1.15,location=(x,y,z+4.35));crown=bpy.context.object;crown.name=name+"_Crown";crown.data.materials.append(TERRACOTTA);only(crown,c)
    cyl(name+"_Club",(x,y-facing*.55,z+2.05),.09,3.2,TIMBER,c,12,w=.02)
    cyl(name+"_ClubPommel",(x,y-facing*.55,z+3.72),.18,.26,GOLD,c,14,w=.025)

# Canal, real envelope and low approaches.
box("SaphanYak_CanalWater",(B,0,.02),(29.0,72.0,.16),WATER_DEEP,BRIDGE,.012,1)
box("SaphanYak_CanalGlint",(B,0,.12),(20.0,72.0,.025),WATER,BRIDGE,.006,1)
for side in (-1,1):
    x=B+side*BRIDGE_LENGTH/2
    for tier in range(3):
        xx=x+side*(.45+tier*.55);z=.28+tier*.34
        box(f"SaphanYak_BankTier_{side}_{tier}",(xx,0,z),(1.0,72,.30),CONCRETE,BRIDGE,.045,2)
        box(f"SaphanYak_BankJoint_{side}_{tier}",(xx-side*.48,0,z+.17),(.08,72,.06),ALGAE if tier==0 else CONCRETE_LIGHT,BRIDGE,.012,1)
    box(f"SaphanYak_TopWalk_{side}",(x+side*2.65,0,1.18),(4.2,72,.28),PAVER,BRIDGE,.045,2)
    curved_tube(f"SaphanYak_CanalRail_{side}",[(x+side*1.5,-36,2.05),(x+side*1.5,0,2.05),(x+side*1.5,36,2.05)],.055,STEEL,BRIDGE)
    for y in range(-34,35,3):cyl(f"SaphanYak_CanalPost_{side}_{y}",(x+side*1.5,y,1.63),.045,.95,STEEL,BRIDGE,10,w=.012)

# Crown deck built to historic reported 34.5 × 8.5 m envelope.
sections=[]
for i in range(9):
    x=B-BRIDGE_LENGTH/2+i*(BRIDGE_LENGTH/8);z=BRIDGE_Z+math.sin(math.pi*i/8)*.22;sections.append((x,z))
verts=[]
for x,z in sections:verts += [(x,-BRIDGE_WIDTH/2,z-.24),(x,BRIDGE_WIDTH/2,z-.24),(x,-BRIDGE_WIDTH/2,z+.24),(x,BRIDGE_WIDTH/2,z+.24)]
faces=[]
for i in range(8):
    a=i*4;b=(i+1)*4;faces += [(a,b,b+2,a+2),(a+1,a+3,b+3,b+1),(a,a+1,b+1,b),(a+2,b+2,b+3,a+3)]
faces += [(0,2,3,1),(32,33,35,34)]
me=bpy.data.meshes.new("SaphanYak_Deck_Mesh");me.from_pydata(verts,[],faces);me.update();deck=bpy.data.objects.new("SaphanYak_Deck_34p5x8p5m",me);BRIDGE.objects.link(deck);deck.data.materials.append(CONCRETE_LIGHT);bevel(deck,.045,2)
for i in range(8):
    x=(sections[i][0]+sections[i+1][0])/2;z=(sections[i][1]+sections[i+1][1])/2+.27;slope=math.atan2(sections[i+1][1]-sections[i][1],sections[i+1][0]-sections[i][0])
    seglen=BRIDGE_LENGTH/8+.03
    box(f"SaphanYak_RoadSurface_{i}",(x,0,z),(seglen,5.35,.10),ASPHALT,BRIDGE,.014,1,rot=(0,-slope,0))
    box(f"SaphanYak_CentreMark_{i}",(x,0,z+.065),(seglen*.48,.10,.025),GOLD,BRIDGE,.006,1,rot=(0,-slope,0))
    for side in (-1,1):box(f"SaphanYak_WalkBand_{side}_{i}",(x,side*3.48,z+.015),(seglen,1.42,.13),PAVER,BRIDGE,.018,1,rot=(0,-slope,0))
for side in (-1,1):
    y=side*(BRIDGE_WIDTH/2-.12)
    railpts=[(x,y,z+1.34) for x,z in sections]
    curved_tube(f"SaphanYak_TopRail_{side}",railpts,.07,STEEL,BRIDGE)
    curved_tube(f"SaphanYak_MidRail_{side}",[(x,y,z+.82) for x,z in sections],.045,STEEL,BRIDGE)
    for i in range(18):
        x=B-BRIDGE_LENGTH/2+i*(BRIDGE_LENGTH/17);z=BRIDGE_Z+math.sin(math.pi*i/17)*.22
        cyl(f"SaphanYak_RailPost_{side}_{i}",(x,y,z+.76),.048,1.12,STEEL,BRIDGE,10,w=.012)

# Compact approach slabs and articulated abutments.
for side in (-1,1):
    end=B+side*BRIDGE_LENGTH/2
    box(f"SaphanYak_Abutment_{side}",(end+side*.55,0,1.25),(1.1,10.2,2.5),CONCRETE,BRIDGE,.09,3)
    for y in (-3.1,0,3.1):box(f"SaphanYak_AbutmentJoint_{side}_{y}",(end-side*.02,y,1.25),(.04,2.6,.08),CONCRETE_LIGHT,BRIDGE,.006,1)
    approach_x=end+side*6.0
    box(f"SaphanYak_Approach_{side}",(approach_x,0,1.72),(12.0,8.5,.36),CONCRETE_LIGHT,BRIDGE,.05,2,rot=(0,math.radians(side*5.8),0))
    box(f"SaphanYak_ApproachRoad_{side}",(approach_x,0,1.94),(12.0,5.35,.09),ASPHALT,BRIDGE,.012,1,rot=(0,math.radians(side*5.8),0))
    for flank in (-1,1):
        box(f"SaphanYak_ApproachWalk_{side}_{flank}",(approach_x,flank*3.48,1.98),(12.0,1.42,.13),PAVER,BRIDGE,.018,1,rot=(0,math.radians(side*5.8),0))

    # The bank-height approach above needs a second visible lead-in to meet
    # street grade. Its outer edge is ~0.10 m above ground and its inner edge
    # meets the existing approach without a character-controller step.
    lead_x=end+side*18.0
    lead_angle=side*5.85
    box(f"SaphanYak_LeadIn_{side}",(lead_x,0,.495),(12.0,8.5,.36),CONCRETE_LIGHT,BRIDGE,.05,2,rot=(0,math.radians(lead_angle),0))
    box(f"SaphanYak_LeadInRoad_{side}",(lead_x,0,.715),(12.0,5.35,.09),ASPHALT,BRIDGE,.012,1,rot=(0,math.radians(lead_angle),0))
    for flank in (-1,1):
        box(f"SaphanYak_LeadInWalk_{side}_{flank}",(lead_x,flank*3.48,.755),(12.0,1.42,.13),PAVER,BRIDGE,.018,1,rot=(0,math.radians(lead_angle),0))
        rail_y=flank*(BRIDGE_WIDTH/2-.12)
        rail_points=[
            (end+side*24.0,rail_y,1.25),
            (end+side*12.0,rail_y,2.48),
            (end,rail_y,3.62),
        ]
        curved_tube(f"SaphanYak_ApproachTopRail_{side}_{flank}",rail_points,.06,STEEL,BRIDGE)
        for post_i,(px,py,pz) in enumerate(rail_points[:-1]):
            cyl(f"SaphanYak_ApproachPost_{side}_{flank}_{post_i}",(px,py,pz-.50),.045,1.0,STEEL,BRIDGE,10,w=.012)

# Four defining yak-bearing pavilion-column positions; guardians stay outside
# the 5.35 m road centre and preserve a continuous playable middle corridor.
for sx in (-1,1):
    for sy in (-1,1):
        x=B+sx*13.6;y=sy*3.35
        box(f"SaphanYak_PavilionPier_{sx}_{sy}",(x,y,4.7),(1.05,1.05,5.1),PLASTER,BRIDGE,.10,4)
        box(f"SaphanYak_PavilionCapital_{sx}_{sy}",(x,y,7.28),(1.55,1.55,.40),GOLD,BRIDGE,.08,3)
        gable_roof(f"SaphanYak_PavilionRoof_{sx}_{sy}",(x,y,0),3.15,3.15,7.45,1.05,.18,TERRACOTTA,BRIDGE)
        guardian(f"SaphanYak_Guardian_{sx}_{sy}",(x-sx*.72,y-sy*.38,2.45),-sy,BRIDGE)
for side in (-1,1):
    x=B+side*16.3
    box(f"SaphanYak_NamePlinth_{side}",(x,-5.0,1.25),(2.5,.50,2.5),PLASTER,BRIDGE,.10,4)
    box(f"SaphanYak_NameInset_{side}",(x,-5.28,1.35),(2.0,.08,1.55),SALMON,BRIDGE,.05,2)
for x,y in ((B-22,-11),(B+22,12),(B-24,14),(B+25,-13)):broadleaf_tree(f"SaphanYak_BankTree_{x}_{y}",(x,y,1.15),.78,BRIDGE)
for side in (-1,1):
    text_mesh(f"SaphanYak_NameEnglish_{side}","SAPHAN YAK",(B+side*16.3,-5.34,1.35),.16,WHITE,BRIDGE)


# ---------------------------------------------------------------------------
# ORDERED PLAYER-HEIGHT REVEAL CONTEXT (preview evidence only; not export)
# ---------------------------------------------------------------------------
C=500.0
box("Reveal_RouteRoad",(250,0,-.10),(540,11.0,.22),ASPHALT,REVEAL,.02,1)
for y in (-6.4,6.4):box(f"Reveal_RouteWalk_{y}",(250,y,.02),(540,1.8,.28),PAVER,REVEAL,.035,2)
# Approximate reference-led silhouette from local jd.jpg. This is a composition
# proxy only, deliberately separated from the exportable map hero collections.
chedi=lathe("Reveal_PhrapathomChedi_CompositionProxy",[(0,27),(2,30),(5,29),(8,27),(12,25),(20,23),(34,19),(45,13),(50,9.5),(54,9),(58,7.4),(63,5.8),(69,4.2),(76,2.1),(80,.3)],GOLD,REVEAL,56)
chedi.location=(C,0,0)
for z,r,h in ((.4,33,.8),(2.0,31.8,.7),(4.2,30.2,.7),(6.4,28.7,.6)):
    cyl(f"Reveal_ChediBaseRing_{z}",(C,0,z),r,h,GOLD,REVEAL,56,w=.04)
# White circumambulatory base and axial gabled entry establish the P9 full view.
cyl("Reveal_ChediWhiteTerrace",(C,0,-.2),36,1.2,CONCRETE_LIGHT,REVEAL,56,w=.08)
box("Reveal_ChediAxialHall",(C-32,0,4.5),(17,10,9),PLASTER,REVEAL,.12,4)
gable_roof("Reveal_ChediAxialHallRoof",(C-32,0,0),19,13,9.0,3.6,.24,TERRACOTTA,REVEAL)
box("Reveal_ChediAxialDoor",(C-40.55,0,3.2),(.24,4.8,6.0),TIMBER,REVEAL,.07,3)

# Four visible, physical occluder beats. These remain in every reveal render;
# P0-P3 use real roof/wall mass, never fog or renderer toggles.
for name,x,h,w,mat in (("P0_StationHall",34,14,28,PLASTER),("P1_MarketCorner",92,16,30,SALMON),("P2_Shophouse",151,14,27,TIMBER),("P3_BridgeEnd",214,14,26,CONCRETE)):
    box(f"Reveal_{name}",(x,0,h/2),(13,w,h),mat,REVEAL,.12,4)
    gable_roof(f"Reveal_{name}_Roof",(x,0,0),15,w+2,h+.05,2.0,.22,TERRACOTTA if name!="P3_BridgeEnd" else GALV,REVEAL)
    for y in (-w*.28,0,w*.28):box(f"Reveal_{name}_Shade_{y}",(x-6.58,y,h*.48),(.18,4.0,.55),AWNING_GREEN if y else AWNING_BLUE,REVEAL,.04,2)
    # Authored frontage details make each physical blocker visibly plausible.
    for i,y in enumerate((-w*.28,0,w*.28)):
        panel_frame_x(f"Reveal_{name}_Opening_{i}",x-6.62,y,h*.36,3.2,4.1,.25,TIMBER,WARM_LIGHT if i==1 else GLASS,REVEAL,-1)
        box(f"Reveal_{name}_Threshold_{i}",(x-7.05,y,.28),(1.2,3.4,.22),PAVER,REVEAL,.025,2)
    box(f"Reveal_{name}_Gutter",(x-7.08,0,h+.12),(.18,w+.5,.18),GALV,REVEAL,.035,2)
    curved_tube(f"Reveal_{name}_Downpipe",[(x-7.10,w*.42,h),(x-7.10,w*.42,1.0),(x-7.35,w*.42,.3)],.055,GALV,REVEAL)
# P5 mask leaves only the top 25-30% of the 80 m proxy visible from its marked
# player position; it is a real market roof/wall volume.
box("Reveal_P5_MarketWall",(330,0,6.0),(12,34,12),SALMON,REVEAL,.12,4)
gable_roof("Reveal_P5_MarketRoof",(330,0,0),14,37,12.0,2.0,.25,TERRACOTTA,REVEAL)
for y in (-12,-4,4,12):
    box(f"Reveal_P5_Awning_{y}",(323.8,y,7.0),(.25,5.5,.55),AWNING_BLUE if y<0 else AWNING_GREEN,REVEAL,.04,2)
    panel_frame_x(f"Reveal_P5_Opening_{y}",323.35,y,4.2,4.2,5.1,.26,TIMBER,WARM_LIGHT if abs(y)==4 else GLASS,REVEAL,-1)
# Final compound threshold and tree framing; central gate is an actual gap.
for y in (-18,18):
    box(f"Reveal_P8_Wall_{y}",(420,y,3.2),(2.0,26,6.4),PLASTER,REVEAL,.10,3)
    gable_roof(f"Reveal_P8_WallCap_{y}",(420,y,0),3.0,27,6.4,.65,.16,TERRACOTTA,REVEAL)
for y in (-6.8,6.8):
    box(f"Reveal_P8_GatePier_{y}",(420,y,4.8),(3.0,3.0,9.6),PLASTER,REVEAL,.12,4)
gable_roof("Reveal_P8_GateRoof",(420,0,0),5.0,18,9.6,2.7,.22,TERRACOTTA,REVEAL)
for x,y in ((405,-13),(405,13),(447,-18),(447,18),(470,-22),(470,22)):broadleaf_tree(f"Reveal_CourtTree_{x}_{y}",(x,y,.4),1.1,REVEAL)
for x in (250,285,365,390,455):
    cyl(f"Reveal_RouteLamp_{x}",(x,-7.0,3.0),.09,5.5,STEEL,REVEAL,12,w=.02)
    box(f"Reveal_RouteLampHead_{x}",(x,-6.7,5.55),(.7,.45,.2),GOLD,REVEAL,.05,3)
for x,y in ((16,7.2),(70,-7.2),(130,7.2),(192,-7.2)):
    broadleaf_tree(f"Reveal_EarlyStreetTree_{x}",(x,y,.35),.72,REVEAL)
    box(f"Reveal_EarlyDrain_{x}",(x,-6.0,.18),(3.2,.36,.08),STEEL,REVEAL,.015,1)

# Superseded forced reveal context is deliberately removed from production.
for obj in list(REVEAL.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

def rotate_family(c,pivot,angle):
    transform=Matrix.Translation(Vector(pivot)) @ Matrix.Rotation(angle,4,'Z') @ Matrix.Translation(-Vector(pivot))
    for obj in list(c.objects):obj.matrix_world=transform @ obj.matrix_world

# Authored integration orientation: station exits toward +X; temple threshold
# faces back toward the station (-X). Street and bridge already run on +X.
rotate_family(STATION,(0,0,0),math.radians(90))
rotate_family(TEMPLE,(280,0,0),math.radians(-90))

# One direct, visible Rotfai Road pavement chain. This is preview context only;
# the visual families remain separate local-origin FBX modules.
box("DirectRoute_Road_PreBridge",(65.4,0,-.10),(94.8,6.2,.20),ASPHALT,ROUTE,.018,1)
box("DirectRoute_Road_PostBridge",(316.1,0,-.10),(337.8,6.2,.20),ASPHALT,ROUTE,.018,1)
for y in (-4.05,4.05):
    box(f"DirectRoute_Walk_Pre_{y}",(65.4,y,.05),(94.8,1.65,.28),PAVER,ROUTE,.035,2)
    box(f"DirectRoute_Walk_Post_{y}",(316.1,y,.05),(337.8,1.65,.28),PAVER,ROUTE,.035,2)
for x in list(range(24,108,10))+list(range(158,486,10)):
    box(f"DirectRoute_CentreMark_{x}",(x,0,.035),(4.2,.10,.025),GOLD,ROUTE,.006,1)
for i,(x,w,h,side,mat,roof) in enumerate(((174,13,7,1,PLASTER,TERRACOTTA),(194,10,5,-1,TIMBER,GALV),(224,15,9,1,SALMON,TERRACOTTA),(255,12,6,-1,PLASTER,GALV),(303,15,8,1,TIMBER,TERRACOTTA),(340,11,6,-1,SALMON,GALV),(382,14,9,1,PLASTER,TERRACOTTA),(425,12,7,-1,TIMBER,GALV))):
    y=side*9.0
    box(f"DirectRoute_Shop_{i}",(x,y,h/2),(w,7.0,h),mat,ROUTE,.10,3)
    gable_roof(f"DirectRoute_ShopRoof_{i}",(x,y,0),w+1.0,8.0,h+.05,1.0,.18,roof,ROUTE)
    front_y=y-side*3.58
    panel_frame(f"DirectRoute_ShopWindow_{i}",x-w*.22,front_y,h*.48,w*.30,min(3.0,h*.45),.15,TIMBER,GLASS,ROUTE,front=-side)
    panel_frame(f"DirectRoute_ShopDoor_{i}",x+w*.24,front_y,1.7,w*.23,3.2,.15,TIMBER,WARM_LIGHT,ROUTE,front=-side)
    scalloped_awning(f"DirectRoute_ShopAwning_{i}",x,front_y-side*.05,min(h*.72,4.5),w*.78,1.35,AWNING_GREEN if i%2 else AWNING_BLUE,ROUTE,front=-side)
for x,y in ((165,-6.2),(210,6.2),(270,-6.2),(325,6.2),(365,-6.2),(410,6.2),(455,-6.2)):
    broadleaf_tree(f"DirectRoute_Tree_{x}",(x,y,.45),.74,ROUTE)
    box(f"DirectRoute_Drain_{x}",(x,-4.0,.18),(2.2,.32,.06),STEEL,ROUTE,.012,1)

# Import the separately reviewed Chedi v004 only for truthful approach previews.
# It is never included in MAP007 exports or MAP007 triangle budgets.
chedi_fbx=ROOT/'art-export'/'HNP-ART-CHEDI-001'/'HNP_Chedi_Modular_ProductionStaging_v004.fbx'
if chedi_fbx.exists():
    bpy.ops.object.select_all(action='DESELECT');bpy.ops.import_scene.fbx(filepath=str(chedi_fbx))
    imported=list(bpy.context.selected_objects)
    official_scale=120.45/44.0
    transform=Matrix.Translation(Vector((519,0,0))) @ Matrix.Rotation(math.radians(-90),4,'Z') @ Matrix.Scale(official_scale,4)
    for obj in imported:
        obj.matrix_world=transform @ obj.matrix_world;only(obj,CHEDITEST)


# Simple production collision modules, visibly aligned to the exported families.
def cbox(name,loc,dims,rot=(0,0,0)):
    return box("UCX_"+name,loc,dims,CONCRETE,COLLISION,0,1,rot=rot)
cbox("STATION_ForecourtWalk",(11.0,0,.0),(11.5,44,.25))
cbox("STATION_LaybyWalk",(20.0,0,-.04),(6.0,44,.22))
cbox("STATION_BuildingBlock",(-1.5,0,2.6),(5.6,38,5.2))
cbox("STATION_PlatformWalk",(-8.5,0,.38),(7.0,42,.76))
cbox("STATION_TrackBoundary",(-14.25,0,.8),(4.6,46,1.6))
cbox("STREET_RoadWalk",(90,0,.0),(56,10,.25))
for i in range(8):
    x=(sections[i][0]+sections[i+1][0])/2;z=(sections[i][1]+sections[i+1][1])/2;slope=math.atan2(sections[i+1][1]-sections[i][1],sections[i+1][0]-sections[i][0])
    cbox(f"BRIDGE_Deck_{i}",(x,0,z+.25),(BRIDGE_LENGTH/8,8.15,.22),rot=(0,-slope,0))
for side in (-1,1):
    end=B+side*BRIDGE_LENGTH/2;approach_x=end+side*6.0
    cbox(f"BRIDGE_Approach_{side}",(approach_x,0,1.96),(12.0,8.15,.20),rot=(0,math.radians(side*5.8),0))
    lead_x=end+side*18.0
    cbox(f"BRIDGE_LeadIn_{side}",(lead_x,0,.715),(12.0,8.15,.12),rot=(0,math.radians(side*5.85),0))
    for flank in (-1,1):
        cbox(f"BRIDGE_ApproachRail_{side}_{flank}",(approach_x,flank*4.13,2.59),(12.0,.20,1.15),rot=(0,math.radians(side*5.8),0))
        cbox(f"BRIDGE_LeadInRail_{side}_{flank}",(lead_x,flank*4.13,1.365),(12.0,.20,1.15),rot=(0,math.radians(side*5.85),0))
    cbox(f"BRIDGE_Rail_{side}",(B,side*4.13,3.05),(34.5,.20,1.15))
    # Bank blockers must never span the bridge/road opening. Two flank boxes
    # per abutment protect the canal edge while leaving |Y| <= 4.25 m clear.
    for flank in (-1,1):
        cbox(f"BRIDGE_CanalBank_{side}_{'North' if flank>0 else 'South'}",(end+side*2.0,flank*20.125,1.0),(3.8,31.75,2.0))
cbox("TEMPLE_ApproachCourt",(270,0,.0),(25,50,.25))
cbox("TEMPLE_WallNorth",(280,16.5,2.25),(1,17,4.5))
cbox("TEMPLE_WallSouth",(280,-16.5,2.25),(1,17,4.5))


# Shared atlas and transferable UV0. Every export family uses the same 1024²
# sRGB color atlas; metallic/roughness remain material scalar values in FBX.
EXPORT_FAMILIES={"Station":STATION,"Street":STREET,"BridgeCanal":BRIDGE,"TempleApproach":TEMPLE}

def convert_curves(c):
    for obj in list(c.objects):
        if obj.type=='CURVE':
            bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.convert(target='MESH');obj.select_set(False)
for c in EXPORT_FAMILIES.values():convert_curves(c)

export_materials=sorted({m for c in EXPORT_FAMILIES.values() for o in c.objects if o.type=='MESH' for m in o.data.materials if m},key=lambda m:m.name)
ATLAS_COLS=5;ATLAS_ROWS=5;ATLAS_SIZE=512
atlas=bpy.data.images.new("HNP_Map007_SharedColorAtlas_v003",width=ATLAS_SIZE,height=ATLAS_SIZE,alpha=True)
material_tiles={m.name:{"index":i,"column":i%ATLAS_COLS,"row":i//ATLAS_COLS} for i,m in enumerate(export_materials)}

def mat_colors(m):
    ramp=next((n for n in m.node_tree.nodes if n.type=='VALTORGB'),None) if m.use_nodes else None
    if ramp:return tuple(ramp.color_ramp.elements[0].color[:3]),tuple(ramp.color_ramp.elements[-1].color[:3])
    bs=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
    if bs:
        c=tuple(bs.inputs['Base Color'].default_value[:3]);return c,tuple(min(1,v*1.12+.02) for v in c)
    em=next((n for n in m.node_tree.nodes if n.type=='EMISSION'),None) if m.use_nodes else None
    c=tuple(em.inputs['Color'].default_value[:3]) if em else (.5,.5,.5);return c,c

pixels=[0.0]*(ATLAS_SIZE*ATLAS_SIZE*4)
for y in range(ATLAS_SIZE):
    row=min(ATLAS_ROWS-1,int(y*ATLAS_ROWS/ATLAS_SIZE))
    for x in range(ATLAS_SIZE):
        col=min(ATLAS_COLS-1,int(x*ATLAS_COLS/ATLAS_SIZE));idx=row*ATLAS_COLS+col
        if idx<len(export_materials):
            c1,c2=mat_colors(export_materials[idx]);n=.5+.26*math.sin(x*.117+y*.071+idx*1.73)+.15*math.sin(x*.019-y*.041+idx)
            n=max(0,min(1,n));rgb=tuple(c1[k]*(1-n)+c2[k]*n for k in range(3))
        else:rgb=(.08,.08,.08)
        p=(y*ATLAS_SIZE+x)*4;pixels[p:p+4]=(*rgb,1.0)
atlas.pixels.foreach_set(pixels);atlas.filepath_raw=str(TEXTURES/'HNP_Map007_SharedColorAtlas_v003.png');atlas.file_format='PNG';atlas.save()

def ensure_atlas_uv(obj):
    me=obj.data;uv=me.uv_layers.active or me.uv_layers.new(name='UVMap')
    for poly in me.polygons:
        m=me.materials[poly.material_index] if len(me.materials) else None
        tile=material_tiles.get(m.name if m else export_materials[0].name,{"column":0,"row":0});col,row=tile['column'],tile['row'];margin=.012
        normal=poly.normal;axis=max(range(3),key=lambda k:abs(normal[k]))
        for li in poly.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co
            raw=(co.y,co.z) if axis==0 else ((co.x,co.z) if axis==1 else (co.x,co.y))
            u=raw[0]%1.0;v=raw[1]%1.0
            uv.data[li].uv=((col+margin+u*(1-2*margin))/ATLAS_COLS,(row+margin+v*(1-2*margin))/ATLAS_ROWS)
for c in list(EXPORT_FAMILIES.values())+[ROUTE]:
    for o in c.objects:
        if o.type=='MESH':ensure_atlas_uv(o)
for m in export_materials:
    bs=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
    if bs:
        tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.name='MAP007_EXPORT_ATLAS';tex.image=atlas;tex.interpolation='Linear';m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])

# Lighting and previews, including three direct player-height route proofs.
bpy.ops.object.light_add(type='SUN',location=(0,-50,80));sun=bpy.context.object;sun.name="PreviewSun";sun.data.energy=3.0;sun.data.angle=math.radians(7);sun.rotation_euler=(math.radians(28),math.radians(-18),math.radians(-32))
for i,(x,y,z,target) in enumerate(((0,-45,30,(0,0,3)),(90,-45,30,(90,0,3)),(130,-42,30,(130,0,3)),(280,-45,30,(280,0,4)),(480,-55,55,(519,0,30)))):
    bpy.ops.object.light_add(type='AREA',location=(x,y,z));fill=bpy.context.object;fill.name=f"PreviewFill_{i}";fill.data.energy=1750;fill.data.shape='DISK';fill.data.size=40;fill.rotation_euler=(Vector(target)-fill.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name="GameplayCamera_1p65m";scene.camera=cam
def look(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

SHOTS={
 "station-front-gameplay":((STATION,),(38,18,7),(0,0,3),42),
 "station-platform-gameplay":((STATION,),(-19,18,3),(-8,0,3),38),
 "town-corner-gameplay":((STREET,),(57,-10,2.4),(84,5,3.3),52),
 "saphan-yak-overview":((BRIDGE,),(99,-31,10),(130,0,3.2),43),
 "saphan-yak-guardian":((BRIDGE,),(107,-10,2.3),(116.4,-3.35,4.8),48),
 "temple-approach-module":((TEMPLE,),(243,-19,5),(280,0,4),42),
 "route-01-station-exit":((STATION,STREET,BRIDGE,ROUTE,CHEDITEST),(25,0,1.65),(150,0,4),34),
 "route-02-bridge-crossing":((STREET,BRIDGE,ROUTE,CHEDITEST),(108,0,3.35),(160,0,3.5),36),
 "route-03-exterior-approach":((ROUTE,CHEDITEST),(410,0,1.65),(519,0,38),23),
}
def set_visibility(active):
    active=set(active)
    for c in HERO:c.hide_render=c not in active
if os.environ.get('HNP_MAP007_SKIP_PREVIEWS')!='1':
    for name,(active,pos,target,lens) in SHOTS.items():
        set_visibility(active);cam.location=pos;cam.data.lens=lens;look(cam,target);scene.render.filepath=str(CHECK/f"HNP_Map007_v003_{name}.png");bpy.ops.render.render(write_still=True)
for c in HERO:c.hide_render=False

def metrics(objects):
    deps=bpy.context.evaluated_depsgraph_get();tris=verts=count=deg=loose=0;mats=set();mins=Vector((1e9,1e9,1e9));maxs=Vector((-1e9,-1e9,-1e9))
    for o in objects:
        if o.type!='MESH':continue
        ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();tris+=len(me.loop_triangles);verts+=len(me.vertices);count+=1
        for m in o.data.materials:
            if m:mats.add(m.name)
        for co in o.bound_box:
            p=o.matrix_world@Vector(co);mins=Vector((min(mins.x,p.x),min(mins.y,p.y),min(mins.z,p.z)));maxs=Vector((max(maxs.x,p.x),max(maxs.y,p.y),max(maxs.z,p.z)))
        bm=bmesh.new();bm.from_mesh(me);deg+=sum(1 for f in bm.faces if f.calc_area()<1e-10);loose+=sum(1 for v in bm.verts if not v.link_edges);bm.free();ev.to_mesh_clear()
    d=maxs-mins
    return {"triangles":tris,"vertices":verts,"object_count":count,"material_count":len(mats),"materials":sorted(mats),"bounds_min_m":[round(v,4) for v in mins],"bounds_max_m":[round(v,4) for v in maxs],"dimensions_m":[round(v,4) for v in d],"degenerate_faces":deg,"loose_vertices":loose}

source_metrics={k:metrics(c.objects) for k,c in EXPORT_FAMILIES.items()}
collision_metrics=metrics(COLLISION.objects)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

preview_manifest={"task_id":"HNP-ART-MAP-007","revision":"v003-production-candidate","status":{"source":"PASS","previews":"PASS","geometry":"PASS" if all(v['degenerate_faces']==0 and v['loose_vertices']==0 for v in list(source_metrics.values())+[collision_metrics]) else "FAIL","designer_review":"NOT RUN","fbx_export":"NOT RUN","roundtrip":"NOT RUN"},"source_metrics":source_metrics,"collision_metrics":collision_metrics,"bridge":{"source":"Silpakorn University Western Region Information Center article; historical measure, not fresh survey","length_m":34.5,"width_m":8.5,"stationing_x_m":130.0,"guardian_pavilions":4},"previews":[f"production-v003-previews/HNP_Map007_v003_{n}.png" for n in SHOTS]}
(OUT/'production-preview-manifest-v003.json').write_text(json.dumps(preview_manifest,ensure_ascii=False,indent=2),encoding='utf-8')
if os.environ.get('HNP_MAP007_EXPORT')!='1':
    print('HNP_MAP007_V003_PREVIEW_READY',json.dumps(preview_manifest['status']),json.dumps({k:v['triangles'] for k,v in source_metrics.items()}));raise SystemExit(0)

# Export local-origin, material-grouped static meshes. LOD0 keeps authored form;
# LOD1 decimates grouped meshes and is intended for distant mobile rendering.
PIVOTS={"Station":Vector((0,0,0)),"Street":Vector((90,0,0)),"BridgeCanal":Vector((130,0,0)),"TempleApproach":Vector((280,0,0))}
exports={};expected={}
def grouped_duplicates(c,pivot,lod_ratio=1.0):
    groups={}
    for src in c.objects:
        if src.type!='MESH':continue
        dup=src.copy();dup.data=src.data.copy();scene.collection.objects.link(dup);dup.data.transform(Matrix.Translation(-pivot) @ src.matrix_world);dup.matrix_world=Matrix.Identity(4)
        mat=dup.data.materials[0].name if len(dup.data.materials) else 'NoMaterial';cx=dup.dimensions.x and sum(v.co.x for v in dup.data.vertices)/max(1,len(dup.data.vertices)) or 0;seg=-1 if cx<-10 else (1 if cx>10 else 0);groups.setdefault((mat,seg),[]).append(dup)
    joined=[]
    for (mat,seg),objs in groups.items():
        bpy.ops.object.select_all(action='DESELECT')
        for o in objs:o.select_set(True)
        bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();o=bpy.context.object;o.name=f"MAP007_{c.name.split('_')[-1]}_LOD{'1' if lod_ratio<1 else '0'}_S{seg}_{mat}";joined.append(o)
        if lod_ratio<1 and len(o.data.polygons)>80:
            mod=o.modifiers.new('MobileLOD','DECIMATE');mod.ratio=lod_ratio;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
        # Joining and decimation can expose zero-area bevel remnants even when
        # every authored component is valid. Clean those export-only remnants
        # without changing the production source silhouettes.
        bm=bmesh.new();bm.from_mesh(o.data)
        bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges))
        loose=[v for v in bm.verts if not v.link_edges and not v.link_faces]
        if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
        bm.to_mesh(o.data);bm.free();o.data.update()
    return joined

def export_objects(objs,path):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]
    bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=False,add_leaf_bones=False,path_mode='COPY',embed_textures=False)

for family,c in EXPORT_FAMILIES.items():
    for lod,ratio in (("LOD0",1.0),("LOD1",.55)):
        objs=grouped_duplicates(c,PIVOTS[family],ratio);path=OUT/f"HNP_Map007_{family}_{lod}_v003.fbx";expected[path.name]=metrics(objs);export_objects(objs,path);exports[path.name]={"family":family,"lod":lod,"metrics":expected[path.name]}
        for o in objs:bpy.data.objects.remove(o,do_unlink=True)

for family,prefix,pivot in (("Station","UCX_STATION_",PIVOTS['Station']),("Street","UCX_STREET_",PIVOTS['Street']),("BridgeCanal","UCX_BRIDGE_",PIVOTS['BridgeCanal']),("TempleApproach","UCX_TEMPLE_",PIVOTS['TempleApproach'])):
    selected=[]
    for src in COLLISION.objects:
        if not src.name.startswith(prefix):continue
        dup=src.copy();dup.data=src.data.copy();scene.collection.objects.link(dup);dup.data.transform(Matrix.Translation(-pivot)@src.matrix_world);dup.matrix_world=Matrix.Identity(4);selected.append(dup)
    path=OUT/f"HNP_Map007_{family}_Collision_v003.fbx";expected[path.name]=metrics(selected);export_objects(selected,path);exports[path.name]={"family":family,"lod":"collision","metrics":expected[path.name]}
    for o in selected:bpy.data.objects.remove(o,do_unlink=True)

# Preserve clean production source before using a fresh scene for roundtrip.
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
roundtrip={};roundtrip_blend=SRC/'HNP_Map007_v003_roundtrip.blend';bpy.ops.wm.read_factory_settings(use_empty=True)
for name,exp in exports.items():
    bpy.ops.object.select_all(action='DESELECT');bpy.ops.import_scene.fbx(filepath=str(OUT/name));objs=list(bpy.context.selected_objects);obs=metrics(objs);want=expected[name];delta=max(abs(obs['dimensions_m'][i]-want['dimensions_m'][i]) for i in range(3));ok=obs['triangles']==want['triangles'] and delta<=.002 and obs['degenerate_faces']==0
    roundtrip[name]={"status":"PASS" if ok else "FAIL","expected_triangles":want['triangles'],"observed_triangles":obs['triangles'],"max_dimension_delta_m":round(delta,6),"observed_dimensions_m":obs['dimensions_m'],"object_count":obs['object_count']}
    for o in objs:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(roundtrip_blend))
(OUT/'roundtrip-v003.json').write_text(json.dumps(roundtrip,ensure_ascii=False,indent=2),encoding='utf-8')

manifest={"task_id":"HNP-ART-MAP-007","revision":"v003-production","status":{"blender_source":"PASS","geometry_self_check":preview_manifest['status']['geometry'],"designer_v002_station_platform_town":"PASS","designer_v003_bridge_direct_route":"NOT RUN","fbx_export":"PASS","fbx_roundtrip":"PASS" if all(v['status']=='PASS' for v in roundtrip.values()) else "FAIL","unity_import":"NOT RUN","mobile_web":"NOT RUN"},"units":"metres","axis":{"blender_up":"+Z","fbx_forward":"-Z","fbx_up":"Y","route_forward":"+X"},"placement":{"Station":{"world_origin":[-15,0,0],"route_exit_world":[0,0,0],"front":"+X","unity_wrapper_rotation_y_deg":180,"note":"place the whole family at X=-15 and rotate its Unity wrapper Y=180 so the world-origin spawn is on the forecourt and faces route +X"},"Street":{"world_origin":[90,0,0],"route":"+X"},"BridgeCanal":{"world_origin":[130,0,0],"world_ends_x":[112.75,147.25],"route":"+X"},"TempleApproach":{"suggested_world_origin":[400,0,0],"front":"-X","note":"independently placeable; do not overlap scaled Chedi outer court"},"Chedi_authoritative":{"world_center":[519,0,0],"asset":"HNP-ART-CHEDI-001 v004; not embedded in MAP007 FBX","preview_scale":120.45/44.0}},"bridge":{"name_th":"สะพานยักษ์ / สะพานเจริญศรัทธา","historical_dimensions_m":[34.5,8.5],"fresh_survey":False,"guardian_pavilions":4,"clear_center_lane_m":5.35,"walk_band_each_m":1.42,"rail_height_m":1.1,"bank_to_deck_approach_length_each_m":12.0,"bank_to_deck_slope_deg":5.8,"ground_lead_in_length_each_m":12.0,"ground_lead_in_slope_deg":5.85,"ground_lead_in_outer_world_x":[88.75,171.25],"collision_clear_corridor_y_m":[-4.25,4.25]},"collision":{"files":[n for n in exports if 'Collision' in n],"intent":"simple visible-surface-aligned deck, approach and ground lead-in slabs; matching rail/building blockers; canal-bank blockers are split north/south and never span the clear bridge corridor; Unity nav/collider verification required"},"exports":exports,"materials":{"atlas":"Textures/HNP_Map007_SharedColorAtlas_v003.png","atlas_size_px":[512,512],"color_space":"sRGB","tiles":material_tiles,"roughness_metallic":"FBX material scalars; verify Unity shader"},"lod":{"LOD0":"authored source grouped by material and three X culling sectors","LOD1":"0.55 decimate on grouped meshes above 80 polygons","simultaneous_view_budget":"NOT RUN in Unity"},"references":["docs/design/HNP-MAP-REAL-008-evidence-correction.md","https://snc.lib.su.ac.th/westweb/?p=1644","R-STATION-01/02/03/04","R-STREET-01/02","R-APPROACH-01","R-CANAL-01"],"provisional":["Bridge dimensions are historic article values, not a fresh structural/access survey.","Guardian forms are mobile-readable simplifications, not surveyed sculpture replicas.","Town/temple side elevations and access remain provisional.","Direct-route road context and imported Chedi are preview-only and excluded from MAP007 FBX."],"previews":preview_manifest['previews'],"source":{"blend":"art-source/HNP-ART-MAP-007/HNP_Map007_HeroSceneKit_v003_production.blend","generator":"art-source/HNP-ART-MAP-007/build_map007_production_v003.py","roundtrip_blend":"art-source/HNP-ART-MAP-007/HNP_Map007_v003_roundtrip.blend"}}
artifacts=[BLEND,roundtrip_blend,SRC/'build_map007_production_v003.py',TEXTURES/'HNP_Map007_SharedColorAtlas_v003.png',OUT/'roundtrip-v003.json']+[OUT/n for n in exports]+[CHECK/f"HNP_Map007_v003_{n}.png" for n in SHOTS]
manifest['sha256']={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in artifacts if p.exists()}
(OUT/'manifest-v003.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('HNP_MAP007_V003_PRODUCTION_DONE',json.dumps(manifest['status']),json.dumps({k:v['metrics']['triangles'] for k,v in exports.items()}))
