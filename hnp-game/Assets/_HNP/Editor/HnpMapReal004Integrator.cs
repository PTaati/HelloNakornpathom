using System;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace HNP.Editor {
 public static class HnpMapReal004Integrator {
  static readonly Vector3[] P={new(0,0,0),new(0,0,-28),new(42,0,-45),new(118,0,-45),new(166,0,-28),new(216,0,-28),new(266,0,-28),new(316,0,2),new(384,0,2),new(450,0,0),new(515,0,0)};
  static Material mat,road,water,gold; static Transform root;
  static GameObject G(string n,Vector3 p,Vector3 s,Material m,bool col=true){var g=GameObject.CreatePrimitive(PrimitiveType.Cube);g.name=n;g.transform.SetParent(root);g.transform.position=p;g.transform.localScale=s;g.GetComponent<Renderer>().sharedMaterial=m;if(!col)UnityEngine.Object.DestroyImmediate(g.GetComponent<Collider>());return g;}
  static void Segment(string n,Vector3 a,Vector3 b,float w,Material m,float y=0){var d=b-a;var g=G(n,(a+b)*.5f+Vector3.up*y,new(w,.22f,d.magnitude),m);g.transform.rotation=Quaternion.LookRotation(d.normalized,Vector3.up);}
  static void Rail(Vector3 a,Vector3 b,float z){var d=b-a;var g=G("Bridge rail",(a+b)*.5f+new Vector3(0,1.1f,z),new(.16f,1.1f,d.magnitude),gold);g.transform.rotation=Quaternion.LookRotation(d.normalized,Vector3.up);}
  static GameObject FindInactive(string name)=>SceneManager.GetActiveScene().GetRootGameObjects().SelectMany(x=>x.GetComponentsInChildren<Transform>(true)).Select(x=>x.gameObject).FirstOrDefault(x=>x.name==name);
  public static void Integrate(){
   if(EditorApplication.isPlaying)throw new Exception("Exit Play Mode first");var s=SceneManager.GetActiveScene();if(s.isDirty)throw new Exception("Scene must be clean/checkpointed");
   var old=GameObject.Find("MapB_Composed +69deg (presentation)");if(old)old.SetActive(false);
   var prior=GameObject.Find("MapB_VisualFlow_004");if(prior)UnityEngine.Object.DestroyImmediate(prior);
   var r=new GameObject("MapB_VisualFlow_004");root=r.transform;
   mat=new Material(Shader.Find("Universal Render Pipeline/Lit")){color=new Color(.64f,.52f,.38f)};road=new Material(Shader.Find("Universal Render Pipeline/Lit")){color=new Color(.22f,.24f,.23f)};water=new Material(Shader.Find("Universal Render Pipeline/Lit")){color=new Color(.08f,.31f,.38f)};gold=new Material(Shader.Find("Universal Render Pipeline/Lit")){color=new Color(.76f,.48f,.12f)};
   // P0–P10 physical, continuous corridor; bridge P4–P6 has its own deck and rails.
   for(int i=0;i<P.Length-1;i++)Segment("Walk corridor P"+i+"-P"+(i+1),P[i],P[i+1],i==4||i==5?12:(i==0||i==3||i==5||i==8?10:8),mat);
   G("Station facade — faces street -Z",new(0,4,12),new(30,8,2),road);G("Station canopy",new(0,5,-20),new(18,.4f,10),gold);G("Rail boundary — non walkable",new(0,1,24),new(38,2,2),road);
   // L-corner/facades intentionally occlude Chedi from P0–P3.
   G("Urban occluder north P2-P3",new(80,4,-31),new(96,8,4),road);G("Urban L corner occluder",new(128,4,-12),new(5,8,44),road);G("Market awnings",new(80,6,-34),new(90,1,8),gold,false);
   // Canal void and banks are colliding visual assets; only the deck crosses it.
   G("Canal water — provisional",new(216,-2,-28),new(50,3,40),water,false);G("Canal north bank",new(216,0,-50),new(56,2,4),road);G("Canal south bank",new(216,0,-6),new(56,2,4),road);
   G("GIANT BRIDGE DECK 50m",new(216,.12f,-28),new(50,.24f,12),mat);Rail(new(166,0,-28),new(266,0,-28),-5.8f);Rail(new(166,0,-28),new(266,0,-28),5.8f);foreach(var x in new[]{166,266}){G("Bridge portal north",new(x,4,-34),new(3,8,2),gold);G("Bridge portal south",new(x,4,-22),new(3,8,2),gold);}
   for(int x=176;x<266;x+=10){G("Bridge lamp",new(x,4,-34),new(.35f,7,.35f),gold);G("Bridge lamp",new(x,4,-22),new(.35f,7,.35f),gold);} 
   G("East bank frontage occluder",new(336,4,18),new(70,8,4),road);G("Compound wall — access under verification",new(414,4,17),new(42,8,4),road);
   // Full reveal is delayed to P9; Chedi is a real existing hero asset, repositioned, not duplicated.
   // Exterior prayer threshold precedes the v004 hero collider, which begins near x=505.
   var prayer=FindInactive("Prayer point");if(prayer)prayer.transform.position=new(500,2.9f,0);
   var hero=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_HNP/Prefabs/World/PhraPathomChedi_v004.prefab"));
   hero.name="Phra Pathom Chedi v004 Flow Hero";hero.transform.SetParent(root);hero.transform.position=new(541,2.9f,0);
   var interaction=hero.GetComponent<HNP.World.HnpWorldPrayerInteraction>();if(interaction&&prayer){var so=new SerializedObject(interaction);so.FindProperty("prayerPoint").objectReferenceValue=prayer.transform;so.ApplyModifiedPropertiesWithoutUndo();}
   G("Temple reveal court",new(465,0,0),new(42,.22f,34),mat);G("Exterior ring approach",new(515,0,0),new(40,.22f,24),mat);
   var traveller=GameObject.Find("Traveller");if(traveller){var cc=traveller.GetComponent<CharacterController>();cc.enabled=false;traveller.transform.position=new(0,.3f,0);cc.enabled=true;}
   var game=UnityEngine.Object.FindFirstObjectByType<HNP.World.HnpWorldGame>();if(game){game.SetHeading(180);game.ReturnToStation();}
   EditorSceneManager.MarkSceneDirty(s);EditorSceneManager.SaveScene(s);AssetDatabase.SaveAssets();Physics.SyncTransforms();Debug.Log("HNP_MAP_REAL_004_LAYOUT_READY P0-P10 bridge=50m prayer=(515,0)");
  }
 }
}
