using System;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace HNP.Editor {
 public static class HnpMapReal004Integrator {
  // Direct station-to-Chedi corridor. The final short ascent is derived from the authored M02 stair geometry.
  static readonly Vector3[] P={new(0,0,0),new(112.75f,0,0),new(130,0,0),new(147.25f,0,0),new(400,0,0),new(425,0,0)};
  static Material mat,road,water,gold; static Transform root;
  static GameObject G(string n,Vector3 p,Vector3 s,Material m,bool col=true){var g=GameObject.CreatePrimitive(PrimitiveType.Cube);g.name=n;g.transform.SetParent(root);g.transform.position=p;g.transform.localScale=s;g.GetComponent<Renderer>().sharedMaterial=m;if(!col)UnityEngine.Object.DestroyImmediate(g.GetComponent<Collider>());return g;}
  static void Segment(string n,Vector3 a,Vector3 b,float w,Material m,float y=0){var d=b-a;var g=G(n,(a+b)*.5f+Vector3.up*y,new(w,.22f,d.magnitude),m);g.transform.rotation=Quaternion.LookRotation(d.normalized,Vector3.up);}
  static void Rail(Vector3 a,Vector3 b,float z){var d=b-a;var g=G("Bridge rail",(a+b)*.5f+new Vector3(0,1.1f,z),new(.16f,1.1f,d.magnitude),gold);g.transform.rotation=Quaternion.LookRotation(d.normalized,Vector3.up);}
  static GameObject Ramp(string n,Vector3 start,Vector3 end,float width,Material material){
   Vector3 half=Vector3.forward*(width*.5f),low=Vector3.down*.12f;var mesh=new Mesh{name=n+" mesh"};
   mesh.vertices=new[]{start-half,start+half,end-half,end+half,start-half+low,start+half+low,end-half+low,end+half+low};
   // Open ends let the controller transfer continuously from court → ramp → existing M02 landing.
   mesh.triangles=new[]{0,1,2,2,1,3,4,6,5,6,7,5,0,2,4,2,6,4,1,5,3,3,5,7};mesh.RecalculateNormals();mesh.RecalculateBounds();
   var go=new GameObject(n,typeof(MeshFilter),typeof(MeshRenderer),typeof(MeshCollider));go.transform.SetParent(root);go.GetComponent<MeshFilter>().sharedMesh=mesh;go.GetComponent<MeshRenderer>().sharedMaterial=material;go.GetComponent<MeshCollider>().sharedMesh=mesh;return go;
  }
  // Flat accessible terrace: deliberately has no vertical entry lip.  It joins the ramp at the
  // same top plane, so the CharacterController cannot collide with an invisible step face.
  static GameObject Landing(string n,Vector3 start,Vector3 end,float width,Material material){
   Vector3 half=Vector3.forward*(width*.5f);var mesh=new Mesh{name=n+" mesh"};mesh.vertices=new[]{start-half,start+half,end-half,end+half};mesh.triangles=new[]{0,1,2,2,1,3};mesh.RecalculateNormals();mesh.RecalculateBounds();
   var go=new GameObject(n,typeof(MeshFilter),typeof(MeshRenderer),typeof(MeshCollider));go.transform.SetParent(root);go.GetComponent<MeshFilter>().sharedMesh=mesh;go.GetComponent<MeshRenderer>().sharedMaterial=material;go.GetComponent<MeshCollider>().sharedMesh=mesh;return go;
  }
  static void BindPrayerPhoto(GameObject hero){
   const string texturePath="Assets/_HNP/Art/ChediV004/HNP_Chedi_PrayerPhoto_pra_v004.jpg",materialPath="Assets/_HNP/Art/ChediV004/HNP_Chedi_PrayerPhoto_Runtime.mat";
   var texture=AssetDatabase.LoadAssetAtPath<Texture2D>(texturePath);if(!texture)throw new Exception("v004 prayer photo texture was not imported");
   var material=AssetDatabase.LoadAssetAtPath<Material>(materialPath);if(!material){material=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(material,materialPath);}
   material.SetTexture("_BaseMap",texture);material.mainTexture=texture;material.SetColor("_BaseColor",Color.white);material.SetInt("_Cull",0);EditorUtility.SetDirty(material);
   foreach(var renderer in hero.GetComponentsInChildren<MeshRenderer>(true).Where(x=>x.name.Contains("M04_PrayerDepth")&&x.name.Contains("PrayerPhoto")))renderer.sharedMaterial=material;
  }
  static void ReplaceFacadeWithV005(GameObject hero){
   const string facadePath="Assets/_HNP/Art/ChediV004/HNP_Chedi_M03_ReferenceFacade_v005.fbx";
   var source=AssetDatabase.LoadAssetAtPath<GameObject>(facadePath);if(!source)throw new Exception("v005 sanctuary facade FBX was not imported");
   var bindings=hero.GetComponentsInChildren<MeshRenderer>(true).Where(x=>x.name.Contains("M03_ReferenceFacade")).SelectMany(x=>x.sharedMaterials).Where(x=>x).GroupBy(x=>x.name).ToDictionary(x=>x.Key,x=>x.First());
   foreach(var f in hero.GetComponentsInChildren<MeshFilter>(true).Where(x=>x.name.Contains("M03_ReferenceFacade")).ToArray())UnityEngine.Object.DestroyImmediate(f.gameObject);
   var facade=(GameObject)PrefabUtility.InstantiatePrefab(source);facade.name="M03 sanctuary facade v005 — aperture validated";facade.transform.SetParent(hero.transform,false);
   foreach(var renderer in facade.GetComponentsInChildren<MeshRenderer>(true)){var materials=renderer.sharedMaterials;for(int i=0;i<materials.Length;i++)if(materials[i]&&bindings.TryGetValue(materials[i].name,out var bound))materials[i]=bound;renderer.sharedMaterials=materials;}
  }
  static GameObject FindInactive(string name)=>SceneManager.GetActiveScene().GetRootGameObjects().SelectMany(x=>x.GetComponentsInChildren<Transform>(true)).Select(x=>x.gameObject).FirstOrDefault(x=>x.name==name);
  public static void Integrate(){
   if(EditorApplication.isPlaying)throw new Exception("Exit Play Mode first");var s=SceneManager.GetActiveScene();if(s.isDirty)throw new Exception("Scene must be clean/checkpointed");
   var old=GameObject.Find("MapB_Composed +69deg (presentation)");if(old)old.SetActive(false);
   var prior=GameObject.Find("MapB_VisualFlow_004");if(prior)UnityEngine.Object.DestroyImmediate(prior);
   var r=new GameObject("MapB_VisualFlow_004");root=r.transform;
   mat=new Material(Shader.Find("Universal Render Pipeline/Lit")){color=new Color(.64f,.52f,.38f)};road=new Material(Shader.Find("Universal Render Pipeline/Lit")){color=new Color(.22f,.24f,.23f)};water=new Material(Shader.Find("Universal Render Pipeline/Lit")){color=new Color(.08f,.31f,.38f)};gold=new Material(Shader.Find("Universal Render Pipeline/Lit")){color=new Color(.76f,.48f,.12f)};
   for(int i=0;i<P.Length-1;i++)Segment("Visible direct walk corridor P"+i+"-P"+(i+1),P[i],P[i+1],8,mat);
   G("Rotfai Road — provisional width",new(260,-.14f,0),new(560,.12f,22),road,false);
   G("Station facade — faces +X street",new(-12,4,0),new(2,8,30),road);G("Station canopy",new(0,5,0),new(10,.4f,18),gold);G("Rail boundary — non walkable",new(-18,1,0),new(2,2,38),road);
   G("Canal water — provisional",new(130,-2,0),new(34.5f,3,46),water,false);G("Canal bank north",new(130,0,24),new(40,2,3),road);G("Canal bank south",new(130,0,-24),new(40,2,3),road);
   G("Saphan Yak deck 34.5m x 8.5m",new(130,.12f,0),new(34.5f,.24f,8.5f),mat);Rail(new(112.75f,0,0),new(147.25f,0,0),-4.1f);Rail(new(112.75f,0,0),new(147.25f,0,0),4.1f);
   foreach(var x in new[]{112.75f,147.25f}){G("Saphan Yak guardian plinth north",new(x,1.2f,5.2f),new(2,2.4f,2),gold);G("Saphan Yak guardian plinth south",new(x,1.2f,-5.2f),new(2,2.4f,2),gold);}
   // The court begins before the actual western stair foot and remains visibly under the approach.
   G("Temple exterior court",new(450,0,0),new(160,.22f,120),mat);G("Exterior ring approach",new(430,0,0),new(28,.22f,24),mat);
   var prayer=FindInactive("Prayer point");
   var hero=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_HNP/Prefabs/World/PhraPathomChedi_v004.prefab"));
   hero.name="Phra Pathom Chedi v004 Flow Hero";hero.transform.SetParent(root);hero.transform.SetPositionAndRotation(new(519,2.9f,0),Quaternion.Euler(0,180,0));
   ReplaceFacadeWithV005(hero);
   BindPrayerPhoto(hero);
   // M05 is a joined export helper; use the authored M01–M04 exterior/interior floors, stair flights and walls
   // as non-convex static colliders so the visible circumambulation route remains physically traversable.
   foreach(var c in hero.GetComponentsInChildren<Collider>(true))if(c.name.Contains("M05_Collision"))UnityEngine.Object.DestroyImmediate(c);
   foreach(var f in hero.GetComponentsInChildren<MeshFilter>(true)){
    if(f.name.Contains("PrayerPhoto"))continue;
    // M02 Ivory/trim meshes form decorative vertical lips. Only the authored stone route is walkable;
    // retaining its collider plus the aligned access ramp prevents a material seam from blocking entry.
    if(f.name.Contains("M02_Route")&&!f.name.Contains("Stone"))continue;
    if(f.name.Contains("M01_Core")||f.name.Contains("M02_Route")||f.name.Contains("M03_ReferenceFacade")||f.name.Contains("M04_PrayerDepth")){var c=f.GetComponent<MeshCollider>();if(!c)c=f.gameObject.AddComponent<MeshCollider>();c.sharedMesh=f.sharedMesh;c.convex=false;}
   }
   // Point the actual imported prayer floor west toward the station. This works from renderer world geometry,
   // not from an assumed FBX axis or a hard-coded rotation.
   var prayerFloor=hero.GetComponentsInChildren<MeshRenderer>(true).FirstOrDefault(x=>x.name.Contains("M04_PrayerDepth")&&x.name.Contains("Stone"));
   if(!prayerFloor)throw new Exception("v004 prayer floor renderer is missing");var facing=prayerFloor.bounds.center-hero.transform.position;facing.y=0;if(facing.sqrMagnitude<.001f)throw new Exception("v004 prayer floor has no horizontal facing vector");
   hero.transform.rotation=Quaternion.FromToRotation(facing.normalized,Vector3.left)*hero.transform.rotation;
   // TAT official height, derived from the aggregate visible world renderer bounds.
   var visible=hero.GetComponentsInChildren<Renderer>(true).Where(x=>x.enabled).ToArray();var aggregate=visible[0].bounds;foreach(var v in visible)aggregate.Encapsulate(v.bounds);float officialScale=120.45f/aggregate.size.y;hero.transform.localScale=Vector3.one*officialScale;Physics.SyncTransforms();
   var routeStone=hero.GetComponentsInChildren<MeshRenderer>(true).FirstOrDefault(x=>x.name.Contains("M02_Route")&&x.name.Contains("Stone"));if(!routeStone)throw new Exception("v004 M02 stone stair renderer is missing");
   // The sampled lowest tread becomes level with the surrounding court top (0.11m).
   var stairFoot=new Vector3(routeStone.bounds.min.x+.75f,200,0);var routeCollider=routeStone.GetComponent<MeshCollider>();if(!routeCollider||!routeCollider.Raycast(new Ray(stairFoot,Vector3.down),out var stairHit,300))throw new Exception("Unable to sample authored western M02 stair foot");hero.transform.position+=Vector3.up*(.11f-stairHit.point.y);Physics.SyncTransforms();
   // Eight source steps rise 2.40 source metres. A narrow visible stone ramp follows the same flight,
   // keeping the avatar on an apparent surface without making rails/guardians climbable.
   var rampStart=new Vector3(routeStone.bounds.min.x+.75f,.11f,0);var rampEnd=new Vector3(438,.11f+2.4f*officialScale,0);Ramp("M02 west access ramp — aligned authored stair",rampStart,rampEnd,6f,routeStone.sharedMaterial);Physics.SyncTransforms();
   // A low U-shaped stone landing follows the visible west-front terrace outside the sanctuary sidewalls.
   // It connects the stair top to the upper annulus on both sides without routing through the room wall.
   float upperY=rampEnd.y-.11f;Ramp("M02 west upper landing front",new(438,upperY+.11f,0),new(444,upperY+.11f,0),44,routeStone.sharedMaterial);
   G("M02 west upper landing north",new(450,upperY,18),new(18,.22f,8),routeStone.sharedMaterial);G("M02 west upper landing south",new(450,upperY,-18),new(18,.22f,8),routeStone.sharedMaterial);
   // Bind only to the imported floor after final facing/scale; never to a grass marker.
   var floorOrigin=prayerFloor.bounds.center+Vector3.up*2f;if(!Physics.Raycast(floorOrigin,Vector3.down,out var floorHit,5f,~0,QueryTriggerInteraction.Ignore))throw new Exception("Unable to sample imported prayer floor");if(prayer)prayer.transform.position=floorHit.point+Vector3.up*.18f;
   var interaction=hero.GetComponent<HNP.World.HnpWorldPrayerInteraction>();if(interaction&&prayer){var so=new SerializedObject(interaction);so.FindProperty("prayerPoint").objectReferenceValue=prayer.transform;so.ApplyModifiedPropertiesWithoutUndo();}
   var traveller=GameObject.Find("Traveller");if(traveller){var cc=traveller.GetComponent<CharacterController>();cc.enabled=false;traveller.transform.position=new(0,.3f,0);cc.enabled=true;}
   var game=UnityEngine.Object.FindFirstObjectByType<HNP.World.HnpWorldGame>();if(game){
    game.SetHeading(90);game.ReturnToStation();game.viewCamera.farClipPlane=700;RenderSettings.fogEndDistance=620;
    var map=new GameObject("Map004 route map capture",typeof(Camera)).GetComponent<Camera>();map.transform.SetPositionAndRotation(new(297.5f,200,0),Quaternion.Euler(90,0,0));map.orthographic=true;map.orthographicSize=206.642f;map.aspect=1200f/724f;map.farClipPlane=400;
    const string mapPath="Assets/_HNP/Art/World/WorldMap_officialscale.png";bool fog=RenderSettings.fog;RenderSettings.fog=false;try{HnpWorldBuilder.Capture(map,1200,724,mapPath);AssetDatabase.ImportAsset(mapPath);game.mapTexture=AssetDatabase.LoadAssetAtPath<Texture2D>(mapPath);}catch(System.IO.IOException){Debug.LogWarning("Map capture deferred: official-scale map output is locked by another reader.");}finally{RenderSettings.fog=fog;UnityEngine.Object.DestroyImmediate(map.gameObject);}EditorUtility.SetDirty(game);
   }
   EditorSceneManager.MarkSceneDirty(s);EditorSceneManager.SaveScene(s);AssetDatabase.SaveAssets();Physics.SyncTransforms();Debug.Log($"HNP_MAP_REAL_DIRECT_LAYOUT_READY bridge=34.5x8.5m center=130 officialHeroScale={officialScale:F5} prayer={prayer?.transform.position} entrance=west");
  }
 }
}
