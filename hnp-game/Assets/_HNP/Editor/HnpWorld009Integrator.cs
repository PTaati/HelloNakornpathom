using System;
using System.IO;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using HNP.World;

namespace HNP.Editor {
 public static class HnpWorld009Integrator {
  const string Art="Assets/_HNP/Art/World009";
  const string ChediPath="Assets/_HNP/Art/World003/HNP_Chedi_v003.fbx";
  const string TownPath="Assets/_HNP/Art/World/HNP_Town.fbx";
  static string Root=>Directory.GetParent(Application.dataPath).Parent.FullName;
  static string Staging=>Path.Combine(Root,"art-export/hnp-world-009");
  static string Evidence=>Path.Combine(Root,"reports/world/world009-integration");
  public static void CheckScripts(){Debug.Log("HNP009_COMPILE_PASS Unity="+Application.unityVersion+" project="+Application.dataPath);}
  public static void CheckBaselineRoutes(){
   if(EditorApplication.isPlaying)throw new Exception("Exit Play Mode first");
   for(int i=0;i<SceneManager.sceneCount;i++)if(SceneManager.GetSceneAt(i).isDirty)throw new Exception("Checkpoint dirty scene first");
   EditorSceneManager.OpenScene(HnpWorldBuilder.ScenePath,OpenSceneMode.Single);
   Directory.CreateDirectory(Evidence);HnpTemple009Tests.Run(Path.Combine(Evidence,"baseline-temple-routes.json"));
   Debug.Log("HNP009_BASELINE_ROUTES_PASS");
  }

  public static void IntegrateAndBuild(){
   if(EditorApplication.isPlaying)throw new Exception("Exit Play Mode before integration");
   for(int i=0;i<SceneManager.sceneCount;i++)if(SceneManager.GetSceneAt(i).isDirty)throw new Exception("Checkpoint dirty scene before integration");
   Directory.CreateDirectory(Evidence);
   string backup=Path.Combine(Evidence,"NakornpathomWorld.pre-v009.unity");
   if(!File.Exists(backup))File.Copy(HnpWorldBuilder.ScenePath,backup);
   Directory.CreateDirectory(Art+"/Materials");
   string chediGuid=AssetDatabase.AssetPathToGUID(ChediPath),townGuid=AssetDatabase.AssetPathToGUID(TownPath);
   // Existing FBX paths and their .meta/GUIDs remain unchanged.
   File.Copy(Path.Combine(Staging,"HNP_Chedi_v009.fbx"),ChediPath,true);
   File.Copy(Path.Combine(Staging,"HNP_Town_v009.fbx"),TownPath,true);
   var manifest=JObject.Parse(File.ReadAllText(Path.Combine(Staging,"manifest.json")));
   var supportFiles=new[]{"light-profile.json","HNP_TempleSurroundings_v009.fbx"}.Concat(((JObject)manifest["texture_mappings"]).Properties().Select(p=>(string)(p.Value is JObject?p.Value["file"]:p.Value)));
   foreach(var file in supportFiles)File.Copy(Path.Combine(Staging,file),Art+"/"+file,true);
   AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
   ConfigureModel(ChediPath);ConfigureModel(Art+"/HNP_TempleSurroundings_v009.fbx");
   if(chediGuid!=AssetDatabase.AssetPathToGUID(ChediPath)||townGuid!=AssetDatabase.AssetPathToGUID(TownPath))throw new Exception("Existing model GUID changed");
   File.WriteAllText(Path.Combine(Evidence,"asset-identity.json"),new JObject{["status"]="PASS",["chediGuid"]=chediGuid,["townGuid"]=townGuid}.ToString());
   var scene=EditorSceneManager.OpenScene(HnpWorldBuilder.ScenePath,OpenSceneMode.Single);
   // Reinstantiate changed mesh hierarchies so stale FBX file IDs cannot hide or expose the wrong mesh.
   var oldTown=scene.GetRootGameObjects().FirstOrDefault(o=>o.name.StartsWith("Town"));
   if(oldTown)UnityEngine.Object.DestroyImmediate(oldTown);
   var town=Instance(TownPath,"Town — map reference");town.transform.localScale=new(-1,1,1);
   foreach(var f in town.GetComponentsInChildren<MeshFilter>())if(f.name.StartsWith("COLL_")){f.GetComponent<Renderer>().enabled=false;f.gameObject.AddComponent<MeshCollider>().sharedMesh=f.sharedMesh;}
   var old=GameObject.Find("Phra Pathom Chedi");if(old)UnityEngine.Object.DestroyImmediate(old);
   var chedi=Instance(ChediPath,"Phra Pathom Chedi");chedi.transform.SetPositionAndRotation(new(53,2.9f,0),Quaternion.Euler(0,90,0));
   foreach(var f in chedi.GetComponentsInChildren<MeshFilter>()){f.gameObject.AddComponent<MeshCollider>().sharedMesh=f.sharedMesh;if(f.name.StartsWith("COLL_"))f.GetComponent<Renderer>().enabled=false;}
   var previous=GameObject.Find("Temple reference details");if(previous)UnityEngine.Object.DestroyImmediate(previous);
   var details=Instance(Art+"/HNP_TempleSurroundings_v009.fbx","Temple reference details");details.transform.SetPositionAndRotation(chedi.transform.position,chedi.transform.rotation);
   foreach(var f in details.GetComponentsInChildren<MeshFilter>()){
    if(f.name.StartsWith("COLL_")){f.GetComponent<Renderer>().enabled=false;f.gameObject.AddComponent<MeshCollider>().sharedMesh=f.sharedMesh;}
    else if(f.GetComponent<Renderer>().sharedMaterials.Any(m=>m.name.Contains("White")||m.name.Contains("Ivory")||m.name.Contains("Roof")))f.gameObject.AddComponent<MeshCollider>().sharedMesh=f.sharedMesh;
   }
   PrefabUtility.SaveAsPrefabAsset(chedi,"Assets/_HNP/Prefabs/World/PhraPathomChedi.prefab");
   var game=UnityEngine.Object.FindAnyObjectByType<HnpWorldGame>();
   var night=game.GetComponent<HnpNightLighting>();night.monumentLightProfile=AssetDatabase.LoadAssetAtPath<TextAsset>(Art+"/light-profile.json");
   if(!night.monumentLightProfile)throw new Exception("Missing reference-aligned light profile");
   var boundary=GameObject.Find("Chedi solid core").GetComponent<MeshCollider>();
   HnpCollision008Tests.Run(boundary,Path.Combine(Evidence,"collision.json"));
   HnpTemple009Tests.Run(Path.Combine(Evidence,"temple-routes.json"));
   Validate(scene);
   Capture("front",new(-22,14,0),new(53,20,0));
   Capture("three-quarter",new(-3,29,-55),new(53,15,0));
   Capture("courtyard",new(28,8,21),new(53,11,0));
   Capture("arcade",new(53,5.5f,27),new(68,2.4f,32));
   var map=new GameObject("Temporary map capture",typeof(Camera)).GetComponent<Camera>();
   map.transform.SetPositionAndRotation(new(-4,200,0),Quaternion.Euler(90,0,0));map.orthographic=true;map.orthographicSize=72.4f;map.aspect=240f/144.8f;map.farClipPlane=400;
   bool fog=RenderSettings.fog;RenderSettings.fog=false;
   try{HnpWorldBuilder.Capture(map,1200,724,"Assets/_HNP/Art/World/WorldMap.png");}
   finally{RenderSettings.fog=fog;UnityEngine.Object.DestroyImmediate(map.gameObject);}
   AssetDatabase.ImportAsset("Assets/_HNP/Art/World/WorldMap.png");game.mapTexture=AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/_HNP/Art/World/WorldMap.png");
   EditorUtility.SetDirty(game);EditorUtility.SetDirty(night);EditorSceneManager.MarkSceneDirty(scene);EditorSceneManager.SaveScene(scene);AssetDatabase.SaveAssets();
   Debug.Log("HNP009_INTEGRATION_PASS");BuildOnly();
  }
  public static void BuildOnly(){HnpWorldBuilder.BuildAt("builds/world009-r2/web");}
  static GameObject Instance(string path,string name){var model=AssetDatabase.LoadAssetAtPath<GameObject>(path);if(!model)throw new Exception("Missing model "+path);var go=(GameObject)PrefabUtility.InstantiatePrefab(model);go.name=name;return go;}
  static void ConfigureModel(string path){
   var importer=(ModelImporter)AssetImporter.GetAtPath(path);importer.importAnimation=false;importer.importCameras=false;importer.importLights=false;
   var manifest=JObject.Parse(File.ReadAllText(Path.Combine(Staging,"manifest.json")));
   var palette=(JObject)manifest["palette"];
   foreach(var pair in palette){
    var rgba=(JArray)pair.Value;string name=pair.Key,mp=Art+"/Materials/"+name+".mat";
    var material=AssetDatabase.LoadAssetAtPath<Material>(mp);if(!material){material=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(material,mp);}
    material.color=new((float)rgba[0],(float)rgba[1],(float)rgba[2]);material.enableInstancing=true;
    bool metal=name.Contains("Gold")&&!name.Contains("Brick");
    material.SetFloat("_Smoothness",metal?.32f:.19f);material.SetFloat("_Metallic",metal?.22f:0);
    var mapping=manifest["texture_mappings"]?[name];var textureName=(string)(mapping is JObject?mapping["file"]:mapping);
    if(!string.IsNullOrEmpty(textureName)){
     string tp=Art+"/"+textureName;var ti=(TextureImporter)AssetImporter.GetAtPath(tp);ti.sRGBTexture=true;ti.mipmapEnabled=true;ti.wrapMode=TextureWrapMode.Repeat;ti.filterMode=FilterMode.Trilinear;ti.maxTextureSize=1024;ti.SaveAndReimport();
     var texture=AssetDatabase.LoadAssetAtPath<Texture2D>(tp);material.SetTexture("_BaseMap",texture);material.SetTexture("_EmissionMap",texture);material.color=Color.white;
    }
    EditorUtility.SetDirty(material);importer.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),name),material);
   }
   importer.SaveAndReimport();
  }
  static void Capture(string name,Vector3 position,Vector3 target){var c=new GameObject("Temporary reference capture",typeof(Camera)).GetComponent<Camera>();try{c.transform.position=position;c.transform.LookAt(target);c.fieldOfView=58;c.farClipPlane=480;HnpWorldBuilder.Capture(c,1280,900,Path.Combine(Evidence,name+".png"));}finally{UnityEngine.Object.DestroyImmediate(c.gameObject);}}
  static void Validate(Scene scene){
   int meshes=0,triangles=0,missing=0;
   foreach(var root in scene.GetRootGameObjects()){
    foreach(var t in root.GetComponentsInChildren<Transform>(true))missing+=GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject);
    foreach(var f in root.GetComponentsInChildren<MeshFilter>(true)){if(!f.sharedMesh)missing++;else{meshes++;for(int sub=0;sub<f.sharedMesh.subMeshCount;sub++)triangles+=(int)f.sharedMesh.GetIndexCount(sub)/3;}}
    foreach(var r in root.GetComponentsInChildren<Renderer>(true)){missing+=r.sharedMaterials.Count(m=>!m);if(r.name.StartsWith("COLL_")&&r.enabled)throw new Exception("Collision mesh is visible: "+r.name);}
   }
   File.WriteAllText(Path.Combine(Evidence,"scene-validation.json"),new JObject{["status"]=missing==0?"PASS":"FAIL",["meshes"]=meshes,["staticTriangles"]=triangles,["missingReferences"]=missing,["physicalMobile"]="NOT RUN"}.ToString());
   if(missing>0)throw new Exception("Missing scene references: "+missing);
  }
 }
}
