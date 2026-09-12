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
 public static class HnpWorld010Integrator {
  const string Art="Assets/_HNP/Art/World010";
  const string ChediPath="Assets/_HNP/Art/World003/HNP_Chedi_v003.fbx";
  
  static string Root=>Directory.GetParent(Application.dataPath).Parent.FullName;
  static string Staging=>Path.Combine(Root,"art-export/hnp-world-010");
  static string Evidence=>Path.Combine(Root,"reports/world/world010-integration");
  public static void CheckScripts(){Debug.Log("HNP010_COMPILE_PASS Unity="+Application.unityVersion+" project="+Application.dataPath);}
  public static void CheckBaselineRoutes(){
   if(EditorApplication.isPlaying)throw new Exception("Exit Play Mode first");
   for(int i=0;i<SceneManager.sceneCount;i++)if(SceneManager.GetSceneAt(i).isDirty)throw new Exception("Checkpoint dirty scene first");
   EditorSceneManager.OpenScene(HnpWorldBuilder.ScenePath,OpenSceneMode.Single);
   Directory.CreateDirectory(Evidence);HnpTemple009Tests.Run(Path.Combine(Evidence,"baseline-temple-routes.json"));
   Debug.Log("HNP010_BASELINE_ROUTES_PASS");
  }

  public static void IntegrateAndBuild(){
   if(EditorApplication.isPlaying)throw new Exception("Exit Play Mode before integration");
   for(int i=0;i<SceneManager.sceneCount;i++)if(SceneManager.GetSceneAt(i).isDirty)throw new Exception("Checkpoint dirty scene before integration");
   Directory.CreateDirectory(Evidence);
   string backup=Path.Combine(Evidence,"NakornpathomWorld.pre-v010.unity");
   if(!File.Exists(backup))File.Copy(HnpWorldBuilder.ScenePath,backup);
   Directory.CreateDirectory(Art+"/Materials");
   string chediGuid=AssetDatabase.AssetPathToGUID(ChediPath);
   if(string.IsNullOrEmpty(chediGuid))throw new Exception("Existing Chedi asset/GUID missing");
   var manifest=JObject.Parse(File.ReadAllText(Path.Combine(Staging,"manifest.json")));
   string photoFile=PhotoFile(manifest);
   if(string.IsNullOrEmpty(photoFile)||Hash(Path.Combine(Staging,photoFile))!=Hash(Path.Combine(Root,"ref/pra.jpg")))throw new Exception("Staged photo must match ref/pra.jpg exactly");
   // Existing FBX paths and their .meta/GUIDs remain unchanged.
   File.Copy(Path.Combine(Staging,"HNP_Chedi_v010.fbx"),ChediPath,true);
   
   var supportFiles=new[]{"light-profile.json"}.Concat(((JObject)manifest["texture_mappings"]).Properties().Select(p=>(string)(p.Value is JObject?p.Value["file"]:p.Value)));
   foreach(var file in supportFiles)File.Copy(Path.Combine(Staging,file),Art+"/"+file,true);
   AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
   ConfigureModel(ChediPath);
   if(chediGuid!=AssetDatabase.AssetPathToGUID(ChediPath))throw new Exception("Existing model GUID changed");
   File.WriteAllText(Path.Combine(Evidence,"asset-identity.json"),new JObject{["status"]="PASS",["chediGuid"]=chediGuid}.ToString());
   var scene=EditorSceneManager.OpenScene(HnpWorldBuilder.ScenePath,OpenSceneMode.Single);
   var old=GameObject.Find("Phra Pathom Chedi");if(old)UnityEngine.Object.DestroyImmediate(old);
   var chedi=Instance(ChediPath,"Phra Pathom Chedi");chedi.transform.SetPositionAndRotation(new(53,2.9f,0),Quaternion.Euler(0,90,0));
   foreach(var f in chedi.GetComponentsInChildren<MeshFilter>()){f.gameObject.AddComponent<MeshCollider>().sharedMesh=f.sharedMesh;if(f.name.StartsWith("COLL_"))f.GetComponent<Renderer>().enabled=false;}
   PrefabUtility.SaveAsPrefabAsset(chedi,"Assets/_HNP/Prefabs/World/PhraPathomChedi.prefab");
   var game=UnityEngine.Object.FindAnyObjectByType<HnpWorldGame>();
   var night=game.GetComponent<HnpNightLighting>();night.monumentLightProfile=AssetDatabase.LoadAssetAtPath<TextAsset>(Art+"/light-profile.json");
   if(!night.monumentLightProfile)throw new Exception("Missing reference-aligned light profile");
   var boundary=GameObject.Find("Chedi solid core").GetComponent<MeshCollider>();
   HnpCollision008Tests.Run(boundary,Path.Combine(Evidence,"collision.json"));
   HnpTemple009Tests.Run(Path.Combine(Evidence,"temple-routes.json"));
   Validate(scene);
   ValidatePhoto(chedi,game,manifest,chediGuid);
   Capture("front",new(-22,14,0),new(53,20,0));
   Capture("three-quarter",new(-3,29,-55),new(53,15,0));
   Capture("shrine-front",new(14,8.2f,0),new(29,8.2f,0));
   Capture("shrine-oblique",new(18,12,-14),new(33,9,0));
   Capture("arcade",new(53,5.5f,27),new(68,2.4f,32));
   var map=new GameObject("Temporary map capture",typeof(Camera)).GetComponent<Camera>();
   map.transform.SetPositionAndRotation(new(-4,200,0),Quaternion.Euler(90,0,0));map.orthographic=true;map.orthographicSize=72.4f;map.aspect=240f/144.8f;map.farClipPlane=400;
   bool fog=RenderSettings.fog;RenderSettings.fog=false;
   try{HnpWorldBuilder.Capture(map,1200,724,"Assets/_HNP/Art/World/WorldMap.png");}
   finally{RenderSettings.fog=fog;UnityEngine.Object.DestroyImmediate(map.gameObject);}
   AssetDatabase.ImportAsset("Assets/_HNP/Art/World/WorldMap.png");game.mapTexture=AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/_HNP/Art/World/WorldMap.png");
   EditorUtility.SetDirty(game);EditorUtility.SetDirty(night);EditorSceneManager.MarkSceneDirty(scene);EditorSceneManager.SaveScene(scene);AssetDatabase.SaveAssets();
   Debug.Log("HNP010_INTEGRATION_PASS");BuildOnly();
  }
  public static void BuildOnly(){HnpWorldBuilder.BuildAt("builds/web");}
  static GameObject Instance(string path,string name){var model=AssetDatabase.LoadAssetAtPath<GameObject>(path);if(!model)throw new Exception("Missing model "+path);var go=(GameObject)PrefabUtility.InstantiatePrefab(model);go.name=name;return go;}
  static void ConfigureModel(string path){
   var importer=(ModelImporter)AssetImporter.GetAtPath(path);importer.importAnimation=false;importer.importCameras=false;importer.importLights=false;
   var manifest=JObject.Parse(File.ReadAllText(Path.Combine(Staging,"manifest.json")));
   var palette=(JObject)manifest["palette"];
   foreach(var pair in palette){
    var rgba=(JArray)pair.Value;string name=pair.Key,mp=Art+"/Materials/"+name+".mat";
    var mapping=manifest["texture_mappings"]?[name];var textureName=(string)(mapping is JObject?mapping["file"]:mapping);
    bool isPhoto=textureName==PhotoFile(manifest);var shader=Shader.Find(isPhoto?"Universal Render Pipeline/Unlit":"Universal Render Pipeline/Lit");
    var material=AssetDatabase.LoadAssetAtPath<Material>(mp);if(!material){material=new Material(shader);AssetDatabase.CreateAsset(material,mp);}material.shader=shader;
    material.color=new((float)rgba[0],(float)rgba[1],(float)rgba[2]);material.enableInstancing=true;
    bool metal=name.Contains("Gold")&&!name.Contains("Brick");
    if(!isPhoto){material.SetFloat("_Smoothness",metal?.32f:.19f);material.SetFloat("_Metallic",metal?.22f:0);}
    if(!string.IsNullOrEmpty(textureName)){
     string tp=Art+"/"+textureName;var ti=(TextureImporter)AssetImporter.GetAtPath(tp);ti.sRGBTexture=true;ti.mipmapEnabled=true;ti.wrapMode=isPhoto?TextureWrapMode.Clamp:TextureWrapMode.Repeat;if(isPhoto){ti.npotScale=TextureImporterNPOTScale.None;ti.textureCompression=TextureImporterCompression.Uncompressed;}ti.filterMode=FilterMode.Trilinear;ti.maxTextureSize=1024;ti.SaveAndReimport();
     var texture=AssetDatabase.LoadAssetAtPath<Texture2D>(tp);material.SetTexture("_BaseMap",texture);if(!isPhoto)material.SetTexture("_EmissionMap",texture);material.color=Color.white;
    }
    EditorUtility.SetDirty(material);importer.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),name),material);
   }
   importer.SaveAndReimport();
  }
  static string PhotoFile(JObject manifest)=>Path.GetFileName((string)manifest["photo_texture"]??(string)manifest["photo"]?["copy"]);
  static string Hash(string path){using var sha=System.Security.Cryptography.SHA256.Create();using var stream=File.OpenRead(path);return string.Concat(sha.ComputeHash(stream).Select(b=>b.ToString("x2")));}
  static void ValidatePhoto(GameObject chedi,HnpWorldGame game,JObject manifest,string guid){
   var photo=chedi.GetComponentsInChildren<Renderer>().Single(r=>r.sharedMaterials.Any(m=>m.shader.name=="Universal Render Pipeline/Unlit"));
   var texture=(Texture2D)photo.sharedMaterial.mainTexture;var hash=Hash(Path.Combine(Root,"ref/pra.jpg"));
   if(!photo.enabled||!texture||Hash(AssetDatabase.GetAssetPath(texture))!=hash||Mathf.Abs((float)texture.width/texture.height-387f/792)>.002f)throw new Exception("Photo reference mismatch");
   var collider=photo.GetComponent<MeshCollider>();if(collider)UnityEngine.Object.DestroyImmediate(collider);
   Physics.SyncTransforms();var mesh=photo.GetComponent<MeshFilter>().sharedMesh;var rays=new JArray();
   foreach(var local in mesh.vertices.Select(v=>Vector3.Lerp(v,mesh.bounds.center,.1f)).Append(mesh.bounds.center)){
    var target=photo.transform.TransformPoint(local);var from=target+Vector3.left*12;
    bool blocked=Physics.Raycast(from,Vector3.right,out var hit,11.99f);
    rays.Add(new JObject{["blocked"]=blocked,["hit"]=blocked?hit.collider.name:"none"});if(blocked)throw new Exception("Photo occluded by "+hit.collider.name);
   }
   var diag=game.GetComponent<HnpShrine010Diagnostics>()??game.gameObject.AddComponent<HnpShrine010Diagnostics>();diag.game=game;diag.photoRenderer=photo;EditorUtility.SetDirty(diag);
   PrefabUtility.SaveAsPrefabAsset(chedi,"Assets/_HNP/Prefabs/World/PhraPathomChedi.prefab");
   File.WriteAllText(Path.Combine(Evidence,"photo-validation.json"),new JObject{["status"]="PASS",["referenceSha256"]=hash,["chediGuid"]=guid,["width"]=texture.width,["height"]=texture.height,["renderer"]=photo.name,["frontRays"]=rays,["physicalMobile"]="NOT RUN"}.ToString());
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
