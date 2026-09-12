using System;
using System.IO;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEditor.Build.Reporting;
using HNP.World;

namespace HNP.Editor {
 public static class HnpWorldBuilder {
  public const string ScenePath="Assets/_HNP/Scenes/NakornpathomWorld.unity";
  const string Art="Assets/_HNP/Art/World";
  static string Root=>Directory.GetParent(Application.dataPath).Parent.FullName;
  public static void Materials(string manifest,string prefix,string model){
   var data=JObject.Parse(File.ReadAllText(Path.Combine(Root,"art-export/world",manifest)));
   var importer=(ModelImporter)AssetImporter.GetAtPath(Art+"/"+model);
   if(!importer)throw new Exception("Missing model "+model);
   foreach(var pair in (JObject)data["palette"]){
    var c=(JArray)pair.Value;string name=prefix+pair.Key;string path=Art+"/Materials/"+name+".mat";
    var m=AssetDatabase.LoadAssetAtPath<Material>(path);
    if(!m){m=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(m,path);}
    m.color=new Color((float)c[0],(float)c[1],(float)c[2]);m.SetFloat("_Smoothness",pair.Key=="Water"?.55f:.12f);
    m.SetFloat("_Metallic",pair.Key.StartsWith("Gold")?.18f:0);m.enableInstancing=true;EditorUtility.SetDirty(m);
    importer.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),name),m);
   }
   importer.materialImportMode=ModelImporterMaterialImportMode.ImportStandard;
   importer.importCameras=false;importer.importLights=false;importer.importAnimation=false;
   importer.SaveAndReimport();
  }
  static GameObject Model(string filename,string name,Vector3 position){var go=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Art+"/"+filename));go.name=name;go.transform.position=position;return go;}
  static Transform Part(Transform root,string name){return root.GetComponentsInChildren<Transform>().First(t=>t.name==name);}
  static void Label(string text,Vector3 position,float size,float yaw){
   var go=new GameObject("Wayfinding "+text);go.transform.position=position;go.transform.rotation=Quaternion.Euler(0,yaw,0);
   var t=go.AddComponent<TextMesh>();t.text=text;t.fontSize=80;t.characterSize=size;t.anchor=TextAnchor.MiddleCenter;t.alignment=TextAlignment.Center;t.color=new Color(1,.91f,.66f);
  }
  [MenuItem("HNP/Create Reference World")]
  public static void Create(){
   if(EditorApplication.isPlaying)throw new Exception("Exit Play Mode first");
   for(int i=0;i<SceneManager.sceneCount;i++)if(SceneManager.GetSceneAt(i).isDirty)throw new Exception("Save current scene before creating the reference world");
   if(File.Exists(ScenePath))throw new Exception("World scene already exists. Open it instead of overwriting.");
   Directory.CreateDirectory(Art+"/Materials");Directory.CreateDirectory("Assets/_HNP/Prefabs/World");AssetDatabase.Refresh();
   Materials("world-manifest.json","HNPW_","HNP_Town.fbx");Materials("world-manifest.json","HNPW_","HNP_Chedi.fbx");Materials("traveller-manifest.json","HNPT_","HNP_Traveller.fbx");
   var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
   var town=Model("HNP_Town.fbx","Town — map reference",Vector3.zero);town.transform.localScale=new Vector3(-1,1,1);
   foreach(var filter in town.GetComponentsInChildren<MeshFilter>()){
    if(filter.name.StartsWith("COLL_")){
     filter.GetComponent<Renderer>().enabled=false;
     var collider=filter.gameObject.AddComponent<MeshCollider>();collider.sharedMesh=filter.sharedMesh;collider.convex=false;
    }
   }
   var chedi=Model("HNP_Chedi.fbx","Phra Pathom Chedi",new Vector3(53,2.9f,0));
   // Core only: the surrounding terrace remains walkable.
   var core=GameObject.CreatePrimitive(PrimitiveType.Cylinder);core.name="Chedi solid core";core.transform.position=new Vector3(53,24.9f,0);core.transform.localScale=new Vector3(45.8f,22,45.8f);UnityEngine.Object.DestroyImmediate(core.GetComponent<Renderer>());
   PrefabUtility.SaveAsPrefabAsset(chedi,"Assets/_HNP/Prefabs/World/PhraPathomChedi.prefab");
   var player=new GameObject("Traveller");player.layer=2;player.transform.position=new Vector3(-101,.3f,0);
   var cc=player.AddComponent<CharacterController>();cc.height=2.15f;cc.center=new Vector3(0,1.08f,0);cc.radius=.32f;cc.stepOffset=.32f;cc.slopeLimit=48;
   var visual=new GameObject("Traveller visual");visual.transform.SetParent(player.transform,false);visual.transform.localRotation=Quaternion.Euler(0,90,0);
   var travellerModel=Model("HNP_Traveller.fbx","Blender traveller",Vector3.zero);travellerModel.transform.SetParent(visual.transform,false);travellerModel.transform.localScale=new Vector3(-1,1,1);
   var pose=visual.AddComponent<HnpTravellerPose>();pose.leftArm=Part(visual.transform,"HNP_ArmL");pose.rightArm=Part(visual.transform,"HNP_ArmR");pose.leftLeg=Part(visual.transform,"HNP_LegL");pose.rightLeg=Part(visual.transform,"HNP_LegR");pose.head=Part(visual.transform,"HNP_Head");
   PrefabUtility.SaveAsPrefabAsset(player,"Assets/_HNP/Prefabs/World/Traveller.prefab");
   var camera=new GameObject("Main Camera",typeof(Camera),typeof(AudioListener)).GetComponent<Camera>();camera.tag="MainCamera";camera.fieldOfView=60;camera.farClipPlane=480;camera.nearClipPlane=.10f;camera.clearFlags=CameraClearFlags.Skybox;
   var additional=camera.gameObject.AddComponent<UniversalAdditionalCameraData>();additional.renderPostProcessing=false;additional.renderShadows=true;
   var skyShader=Shader.Find("HNP/SunsetSky");if(!skyShader)throw new Exception("Sunset shader not imported");
   var sky=new Material(skyShader);AssetDatabase.CreateAsset(sky,Art+"/Materials/Sunset.mat");RenderSettings.skybox=sky;
   RenderSettings.ambientMode=AmbientMode.Trilight;RenderSettings.ambientSkyColor=new Color(.56f,.61f,.67f);RenderSettings.ambientEquatorColor=new Color(.60f,.48f,.32f);RenderSettings.ambientGroundColor=new Color(.28f,.23f,.17f);
   RenderSettings.fog=true;RenderSettings.fogMode=FogMode.Linear;RenderSettings.fogStartDistance=135;RenderSettings.fogEndDistance=380;RenderSettings.fogColor=new Color(.95f,.72f,.44f);
   var sun=new GameObject("Golden hour",typeof(Light)).GetComponent<Light>();sun.type=LightType.Directional;sun.color=new Color(1,.77f,.48f);sun.intensity=1.9f;sun.shadows=LightShadows.Soft;sun.transform.rotation=Quaternion.LookRotation(-new Vector3(-.75f,.55f,-.3f));RenderSettings.sun=sun;
   HnpClearLighting.Apply();
   var game=new GameObject("HNP World Game").AddComponent<HnpWorldGame>();game.player=cc;game.visual=visual.transform;game.viewCamera=camera;game.pose=pose;
   Label("NAKORNPATHOM\nSTATION",new Vector3(-99,3.5f,8),.12f,90);
   Label("YAK BRIDGE",new Vector3(-71,2.2f,5.8f),.08f,90);
   Label("PHRA PATHOM CHEDI",new Vector3(16,2.4f,-6),.09f,90);
   // Small benches reuse the first original Blender asset.
   var bench=AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_HNP/Prefabs/StationBench.prefab");
   if(bench)foreach(var p in new[]{new Vector3(-99,0,-10),new Vector3(-76,0,18),new Vector3(12,0,27),new Vector3(95,0,-27)}){var b=(GameObject)PrefabUtility.InstantiatePrefab(bench);b.transform.position=p;}
   Directory.CreateDirectory(Path.Combine(Root,"reports/world"));
   // Reference-aligned north-up plan. Capture once, not an extra camera every game frame.
   var mapCamera=new GameObject("Map capture",typeof(Camera)).GetComponent<Camera>();mapCamera.transform.position=new Vector3(-4,200,0);mapCamera.transform.rotation=Quaternion.Euler(90,0,0);mapCamera.orthographic=true;mapCamera.orthographicSize=72.4f;mapCamera.aspect=240f/144.8f;mapCamera.farClipPlane=400;mapCamera.clearFlags=CameraClearFlags.SolidColor;mapCamera.backgroundColor=new Color(.29f,.36f,.19f);
   var fog=RenderSettings.fog;RenderSettings.fog=false;Capture(mapCamera,1200,724,Art+"/WorldMap.png");RenderSettings.fog=fog;UnityEngine.Object.DestroyImmediate(mapCamera.gameObject);AssetDatabase.ImportAsset(Art+"/WorldMap.png");game.mapTexture=AssetDatabase.LoadAssetAtPath<Texture2D>(Art+"/WorldMap.png");
   EditorSceneManager.MarkSceneDirty(scene);EditorSceneManager.SaveScene(scene,ScenePath);AssetDatabase.SaveAssets();
   if(SceneView.lastActiveSceneView)SceneView.lastActiveSceneView.LookAt(new Vector3(30,8,0),Quaternion.Euler(25,60,0),100);
   Debug.Log("HNP_WORLD_CREATED: "+ScenePath);
  }
  public static void Capture(Camera cam,int width,int height,string path){
   var rt=new RenderTexture(width,height,24);var old=cam.targetTexture;var prev=RenderTexture.active;
   try{cam.targetTexture=rt;cam.Render();RenderTexture.active=rt;var texture=new Texture2D(width,height,TextureFormat.RGB24,false);texture.ReadPixels(new Rect(0,0,width,height),0,0);texture.Apply();File.WriteAllBytes(path,texture.EncodeToPNG());UnityEngine.Object.DestroyImmediate(texture);}
   finally{cam.targetTexture=old;RenderTexture.active=prev;rt.Release();UnityEngine.Object.DestroyImmediate(rt);}
  }
  [MenuItem("HNP/Build Reference World Web")]
  public static void Build(){BuildAt("builds/web");}
  public static void BuildAt(string relativeOutput){
   if(EditorApplication.isPlaying)throw new Exception("Exit Play Mode first");
   if(SceneManager.GetActiveScene().isDirty)throw new Exception("Save the active scene before building");
   var mobile=AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>("Assets/Settings/Mobile_RPAsset.asset");GraphicsSettings.defaultRenderPipeline=mobile;QualitySettings.SetQualityLevel(0,true);QualitySettings.renderPipeline=mobile;
   PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.WebGL,false);PlayerSettings.SetGraphicsAPIs(BuildTarget.WebGL,new[]{GraphicsDeviceType.OpenGLES3});
   PlayerSettings.WebGL.template="PROJECT:HNP";PlayerSettings.WebGL.compressionFormat=WebGLCompressionFormat.Disabled;
   var r=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{ScenePath},target=BuildTarget.WebGL,locationPathName=Path.Combine(Root,relativeOutput),options=BuildOptions.None});
   var summary=$"{r.summary.result}\nErrors: {r.summary.totalErrors}\nWarnings: {r.summary.totalWarnings}\nBytes: {r.summary.totalSize}\nTime: {r.summary.totalTime}";
   var reportPath=Path.Combine(Root,"reports/world/build-"+DateTime.Now.ToString("yyyyMMdd-HHmmss")+".txt");
   File.WriteAllText(reportPath,summary);
   try{File.WriteAllText(Path.Combine(Root,"reports/world/build.txt"),summary);}catch(IOException){Debug.LogWarning("Previous build.txt is locked; current report: "+reportPath);}
   if(r.summary.result!=BuildResult.Succeeded)throw new Exception("World build failed");
  }
 }
}
