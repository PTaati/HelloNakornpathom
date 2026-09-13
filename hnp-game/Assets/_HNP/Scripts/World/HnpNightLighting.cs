using System.Collections.Generic;
using System.Linq;
using UnityEngine;
namespace HNP.World {
 public sealed class HnpNightLighting:MonoBehaviour {
  public HnpWorldGame game;public Material vehicleAtlas;public Shader glowShader;public TextAsset monumentLightProfile;
  [System.Serializable]class MonumentProfile{public Vector2[] bell,rings;public Outline[] shrine;}
  [System.Serializable]class Outline{public string name;public Vector3[] points;public float width=.08f;}
  Material atlas,glow;Transform display,monument;float night=-1;readonly List<Fixture> fixtures=new();readonly List<Material> monumentMaterials=new();
  int cars;float nextSelection;
  class Fixture{public Light light;public float intensity;public bool landmark;}
  void Awake(){atlas=new Material(vehicleAtlas);atlas.EnableKeyword("_EMISSION");glow=new Material(glowShader);glow.color=new Color(1,.56f,.09f,1);display=new GameObject("Night light outlines").transform;display.SetParent(transform,false);}
  void Start(){
   // Bounded lamps along the active direct station → Saphan Yak → Chedi route.
   foreach(float x in new[]{24f,62f,98f,158f,222f,286f,350f,410f})foreach(float z in new[]{-7.8f,7.8f}){
    var p=new Vector3(x+.8f,5.08f,z);Line("Street lantern",new[]{p+Vector3.left*.28f,p+Vector3.right*.28f},.16f);
    Lamp("Street light",transform,p,Vector3.down,LightType.Spot,17,80,new Color(1,.74f,.36f),false,125);
   }
   // Integration deliberately names the active instance "... Flow Hero". Find a live v004 renderer root
   // rather than depending on one historical scene-object name.
   var chedi=GameObject.Find("Phra Pathom Chedi v004")??GameObject.Find("Phra Pathom Chedi v004 Flow Hero")??GameObject.Find("Phra Pathom Chedi v002")??GameObject.Find("Phra Pathom Chedi");
   if(!chedi){var candidate=FindObjectsByType<Renderer>(FindObjectsInactive.Exclude,FindObjectsSortMode.None).FirstOrDefault(x=>x.name.Contains("HNP_Chedi_v004"));if(candidate)chedi=candidate.transform.root.gameObject;}
   if(!chedi)throw new System.InvalidOperationException("No active Phra Pathom Chedi instance is available for night lighting.");
   monument=chedi.transform;
    foreach(var r in chedi.GetComponentsInChildren<Renderer>()){var materials=r.materials;foreach(var m in materials){if(!m.HasProperty("_EmissionColor"))continue;m.EnableKeyword("_EMISSION");monumentMaterials.Add(m);}r.materials=materials;}
   if(monumentLightProfile){
    var profile=JsonUtility.FromJson<MonumentProfile>(monumentLightProfile.text);
    Vector3 Surface(float r,float h,float a)=>chedi.transform.TransformPoint(new Vector3(r*Mathf.Cos(a),h,r*Mathf.Sin(a)));
    if(profile.bell!=null)for(int i=0;i<20;i++){float a=i*Mathf.PI*2/20;Line("Bell light rib",profile.bell.Select(v=>Surface(v.x+.07f,v.y,a)).ToArray(),.085f);}
    if(profile.rings!=null)foreach(var v in profile.rings)Line("Chedi light ring",Enumerable.Range(0,97).Select(i=>Surface(v.x+.07f,v.y,i*Mathf.PI*2/96)).ToArray(),.085f);
    if(profile.shrine!=null)foreach(var outline in profile.shrine)if(outline.points!=null&&outline.points.Length>1)Line(outline.name,outline.points.Select(v=>chedi.transform.TransformPoint(v)).ToArray(),Mathf.Max(.035f,outline.width));
   }else{
   Vector2[] bell={new(16.25f,8),new(15.8f,8.7f),new(15.3f,9.4f),new(14.7f,10.5f),new(14.1f,11.8f),new(13.6f,13.3f),new(13.1f,14.9f),new(12.5f,16.5f),new(11.8f,18),new(10.9f,19.4f),new(9.8f,20.5f),new(8.5f,21.4f),new(7.05f,22)};
   Vector3 C(float radius,float h,float angle)=>chedi.transform.TransformPoint(new Vector3(radius*Mathf.Cos(angle),h,radius*Mathf.Sin(angle)));
   for(int i=0;i<20;i++){float angle=i*Mathf.PI*2/20;Line("Bell light rib",bell.Select(v=>C(v.x+.10f,v.y,angle)).ToArray(),.13f);}
   void Ring(float radius,float h){Line("Chedi light ring",Enumerable.Range(0,97).Select(i=>C(radius,h,i*Mathf.PI*2/96)).ToArray(),.13f);}
   for(int i=0;i<7;i++)Ring(22.8f-i*.9f,.88f+i*.94f);
   Ring(7.13f,22.45f);Ring(6.98f,24.2f);Ring(6.73f,25.95f);
   for(int i=0;i<38;i+=3)Ring(5.65f*Mathf.Pow(1-i/39f,1.14f)+.12f,26.42f+i*.43f);
   // Gable/column outlines use the same shrine scale/placement as the Blender source.
   Vector3 Shrine(float x,float y,float z)=>chedi.transform.TransformPoint(new Vector3(x*1.5f,y*1.2f,z-2));
   Line("Portico light gable",new[]{Shrine(-3.7f,8.1f,-24.78f),Shrine(0,13.2f,-24.78f),Shrine(3.7f,8.1f,-24.78f)},.11f);
   foreach(float side in new[]{-1f,1f})Line("Portico light column",new[]{Shrine(side*2.7f,.2f,-24.5f),Shrine(side*2.7f,8.1f,-24.5f)},.10f);
   }
   var chediCenter=chedi.transform.position;float monumentScale=chedi.transform.lossyScale.x;
   var floodWest=chediCenter+new Vector3(-36,9,-18)*monumentScale;var floodEast=chediCenter+new Vector3(-36,12,18)*monumentScale;var portico=chediCenter+new Vector3(-43,13,0)*monumentScale;
   Lamp("Chedi flood west",transform,floodWest,chediCenter+new Vector3(0,16,0)*monumentScale-floodWest,LightType.Spot,65*monumentScale,160,new Color(1,.65f,.28f),true,70);
   Lamp("Chedi flood east",transform,floodEast,chediCenter+new Vector3(0,19,0)*monumentScale-floodEast,LightType.Spot,65*monumentScale,160,new Color(1,.65f,.28f),true,70);
   Lamp("Portico flood",transform,portico,chediCenter+new Vector3(-26,11,0)*monumentScale-portico,LightType.Spot,32*monumentScale,80,new Color(1,.89f,.64f),true,55);
   Update();
  }
  void Line(string name,Vector3[] positions,float width){var go=new GameObject(name);go.transform.SetParent(display,false);var line=go.AddComponent<LineRenderer>();line.sharedMaterial=glow;line.useWorldSpace=true;line.widthMultiplier=width;line.positionCount=positions.Length;line.SetPositions(positions);line.numCornerVertices=2;line.numCapVertices=2;line.shadowCastingMode=UnityEngine.Rendering.ShadowCastingMode.Off;line.receiveShadows=false;}
  void Lamp(string name,Transform parent,Vector3 position,Vector3 direction,LightType type,float range,float intensity,Color color,bool landmark=false,float angle=65){var go=new GameObject(name);go.transform.SetParent(parent,false);if(parent==transform)go.transform.position=position;else go.transform.localPosition=position;go.transform.rotation=Quaternion.LookRotation(direction,Mathf.Abs(direction.normalized.y)>.99f?Vector3.forward:Vector3.up);var light=go.AddComponent<Light>();light.type=type;light.range=range;light.spotAngle=angle;light.innerSpotAngle=angle*.65f;light.color=color;light.shadows=LightShadows.None;light.enabled=false;fixtures.Add(new Fixture{light=light,intensity=intensity,landmark=landmark});}
  public void AttachVehicle(GameObject vehicle,int type){cars++;foreach(var r in vehicle.GetComponentsInChildren<Renderer>()){var ms=r.sharedMaterials;for(int i=0;i<ms.Length;i++)if(ms[i]&&ms[i].name.Contains("Atlas"))ms[i]=atlas;r.sharedMaterials=ms;}
   float length=type==3?6.8f:type==2?4.4f:type==0?3.8f:3.25f,width=type==3?2.05f:1.76f;
   foreach(float side in new[]{-1f,1f})Lamp("Vehicle headlight",vehicle.transform,new(side*width*.30f,.89f,length/2+.06f),new Vector3(0,-.18f,1),LightType.Spot,19,40,new Color(1,.91f,.70f),false,50);
   Lamp("Vehicle cabin light",vehicle.transform,new(0,1.7f,0),Vector3.down,LightType.Point,3,2,new Color(1,.75f,.42f));
  }
  void Update(){if(!game||!atlas)return;float value=1-Mathf.SmoothStep(0,1,Mathf.InverseLerp(.1f,.8f,game.Daylight));
   if(Mathf.Abs(value-night)>.002f){night=value;nextSelection=0;atlas.SetColor("_EmissionColor",Color.white*night*1.7f);glow.color=new Color(1,.58f,.13f,night);display.gameObject.SetActive(night>.01f);foreach(var m in monumentMaterials){float amount=m.name.Contains("Ivory")?.28f:m.name.Contains("Inset")?0:.18f;m.SetColor("_EmissionColor",m.color*amount*night);}}
   // Reserve four nearby street lights so traffic cannot starve the road lighting.
   if(Time.unscaledTime>=nextSelection){nextSelection=Time.unscaledTime+.2f;int streets=0,vehicles=0;foreach(var f in fixtures.OrderBy(f=>Vector3.SqrMagnitude(f.light.transform.position-game.player.transform.position))){bool chosen=f.landmark||(f.light.name=="Street light"?streets++<4:vehicles++<8);f.light.enabled=night>.01f&&chosen;}}
   foreach(var f in fixtures)f.light.intensity=f.intensity*Mathf.Max(0,night);
  }
  [System.Serializable]class Snapshot{public float night,emission;public int street,headlights,cabin,lit,outlinedCars,templeRenderers;public string monumentProfile;public bool collider;public Vector3 player;}
  public void LogNightDiagnostics(){Debug.Log("HNP008_QA "+JsonUtility.ToJson(new Snapshot{night=night,emission=atlas.GetColor("_EmissionColor").maxColorComponent,street=fixtures.Count(f=>f.light.name=="Street light"),headlights=fixtures.Count(f=>f.light.name=="Vehicle headlight"),cabin=fixtures.Count(f=>f.light.name=="Vehicle cabin light"),lit=fixtures.Count(f=>f.light.enabled),outlinedCars=cars,monumentProfile=monumentLightProfile?monumentLightProfile.name:"legacy003",templeRenderers=monument?monument.GetComponentsInChildren<Renderer>().Count(r=>r.enabled):0,collider=monument&&monument.GetComponentsInChildren<Collider>().Any(c=>c.enabled),player=game.player.transform.position}));}
 }
}
