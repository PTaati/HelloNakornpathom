using System;
using System.IO;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using HNP.World;
namespace HNP.Editor {
 public static class HnpWorld003Integrator {
  const string Art="Assets/_HNP/Art/World003";
  static string Root=>Directory.GetParent(Application.dataPath).Parent.FullName;
  public static void IntegrateAndBuild(){Integrate();BuildOnly();}
  public static void BuildOnly(){HnpWorldBuilder.BuildAt("builds/world003-r3/web");}
  public static void BuildCamera004(){HnpWorldBuilder.BuildAt("builds/world004/web");}
  public static void BuildSprint007(){HnpWorldBuilder.BuildAt("builds/world007/web");}
  public static void BuildNight008(){
   if(EditorApplication.isPlaying||SceneManager.GetActiveScene().isDirty)throw new Exception("Checkpoint Editor first");
   foreach(string kind in new[]{"Sedan","Hatchback","Pickup","Minibus"}){string file="HNP_"+kind+"_v003.fbx";File.Copy(Path.Combine(Root,"art-export/hnp-world-008",file),Art+"/"+file,true);}AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
   var scene=EditorSceneManager.OpenScene(HnpWorldBuilder.ScenePath,OpenSceneMode.Single);
   var backup=Path.Combine(Root,"reports/world/NakornpathomWorld.pre-v008.unity");if(!File.Exists(backup))File.Copy(HnpWorldBuilder.ScenePath,backup);
   var core=GameObject.Find("Chedi solid core");foreach(var c in core.GetComponents<Collider>())UnityEngine.Object.DestroyImmediate(c);
   core.transform.position=new(53,23,0);core.transform.localScale=new(46,25,46);var boundary=core.AddComponent<MeshCollider>();boundary.sharedMesh=core.GetComponent<MeshFilter>().sharedMesh;boundary.convex=false;
   var chedi=GameObject.Find("Phra Pathom Chedi");foreach(var f in chedi.GetComponentsInChildren<MeshFilter>()){var c=f.GetComponent<MeshCollider>();if(!c)c=f.gameObject.AddComponent<MeshCollider>();c.sharedMesh=f.sharedMesh;}
   var emission=new Texture2D(32,2,TextureFormat.RGBA32,false);var colors=new Color[64];
   for(int y=0;y<2;y++)for(int x=0;x<32;x++){int index=x/2;colors[y*32+x]=index==5?new Color(.20f,.10f,.028f):index==8?new Color(1,.83f,.47f):index==9?new Color(.6f,.012f,.002f):Color.black;}
   emission.SetPixels(colors);emission.Apply();string ep=Art+"/VehicleNightEmission.png";File.WriteAllBytes(ep,emission.EncodeToPNG());AssetDatabase.ImportAsset(ep);UnityEngine.Object.DestroyImmediate(emission);
   var ti=(TextureImporter)AssetImporter.GetAtPath(ep);ti.sRGBTexture=false;ti.filterMode=FilterMode.Point;ti.mipmapEnabled=false;ti.textureCompression=TextureImporterCompression.Uncompressed;ti.SaveAndReimport();
   var atlas=AssetDatabase.LoadAssetAtPath<Material>(Art+"/Materials/HNP3_Atlas.mat");atlas.EnableKeyword("_EMISSION");atlas.SetTexture("_EmissionMap",AssetDatabase.LoadAssetAtPath<Texture2D>(ep));atlas.SetColor("_EmissionColor",Color.white);EditorUtility.SetDirty(atlas);
   var game=UnityEngine.Object.FindAnyObjectByType<HnpWorldGame>();var night=game.GetComponent<HnpNightLighting>();if(!night)night=game.gameObject.AddComponent<HnpNightLighting>();night.game=game;night.vehicleAtlas=atlas;night.glowShader=Shader.Find("HNP/NightGlow");
   var rp=AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>("Assets/Settings/Mobile_RPAsset.asset");var serializedRp=new SerializedObject(rp);serializedRp.FindProperty("m_AdditionalLightsRenderingMode").intValue=(int)LightRenderingMode.PerPixel;serializedRp.ApplyModifiedPropertiesWithoutUndo();rp.maxAdditionalLightsCount=8;EditorUtility.SetDirty(rp);
   Physics.SyncTransforms();int passed=0;
   foreach(var dir in new[]{Vector3.forward,Vector3.back,Vector3.left,Vector3.right})foreach(float y in new[]{.2f,3.1f,5f}){var ray=new Ray(new Vector3(53,y,0)+dir*30,-dir);if(!boundary.Raycast(ray,out var hit,40)||hit.distance<6||hit.distance>8)throw new Exception("Chedi boundary ray failed "+dir+" y="+y);passed++;}
   HnpCollision008Tests.Run(boundary,Path.Combine(Root,"reports/world/world008-collision.json"));
   EditorUtility.SetDirty(night);EditorSceneManager.MarkSceneDirty(scene);EditorSceneManager.SaveScene(scene);AssetDatabase.SaveAssets();Debug.Log("HNP008_COLLIDER_PASS cardinal rays="+passed);
   HnpWorldBuilder.BuildAt("builds/world008-r4/web");
  }
  public static void BuildTime006(){
   if(EditorApplication.isPlaying||SceneManager.GetActiveScene().isDirty)throw new Exception("Checkpoint Editor first");
   var controller=AssetDatabase.LoadAssetAtPath<AnimatorController>(Art+"/Traveller003.controller");
   var states=controller.layers[0].stateMachine.states.Select(s=>s.state).ToArray();var run=states.Single(s=>s.name=="Run");run.motion=states.Single(s=>s.name=="Walk").motion;run.speed=HnpWorldGame.RunMultiplier;
   EditorUtility.SetDirty(controller);AssetDatabase.SaveAssets();Debug.Log("HNP006_RUN_PASS multiplier="+run.speed+" speed="+HnpWorldGame.RunSpeed);
   HnpWorldBuilder.BuildAt("builds/world006/web");
  }
  public static void BuildMotion005(){
   if(EditorApplication.isPlaying||SceneManager.GetActiveScene().isDirty)throw new Exception("Checkpoint Editor before motion update");
   var controller=AssetDatabase.LoadAssetAtPath<AnimatorController>(Art+"/Traveller003.controller");
   var states=controller.layers[0].stateMachine.states.Select(s=>s.state).ToArray();
   var idle=states.Single(s=>s.name=="Idle");var walk=states.Single(s=>s.name=="Walk");var run=states.Single(s=>s.name=="Run");
   var source=AssetDatabase.LoadAllAssetsAtPath(Art+"/HNP_Traveller_v003.fbx").OfType<AnimationClip>().First(c=>!c.name.StartsWith("__preview__")&&c.name.EndsWith("HNP_Traveller_Idle"));
   var path=Art+"/TravellerStill005.anim";var still=AssetDatabase.LoadAssetAtPath<AnimationClip>(path);
   if(!still){still=new AnimationClip();AssetDatabase.CreateAsset(still,path);}still.ClearCurves();still.frameRate=24;
   foreach(var binding in AnimationUtility.GetCurveBindings(source)){float value=AnimationUtility.GetEditorCurve(source,binding).Evaluate(0);AnimationUtility.SetEditorCurve(still,binding,AnimationCurve.Constant(0,1,value));}
   idle.motion=still;run.motion=walk.motion;run.speed=9f/5.4f;idle.speed=1;walk.speed=1;
   EditorUtility.SetDirty(still);EditorUtility.SetDirty(controller);AssetDatabase.SaveAssets();
   Debug.Log("HNP005_MOTION_PASS idle=constant run=Walk speed="+run.speed);
   HnpWorldBuilder.BuildAt("builds/world005/web");
  }
  public static void Integrate(){
   if(EditorApplication.isPlaying)throw new Exception("Exit Play first");for(int i=0;i<SceneManager.sceneCount;i++)if(SceneManager.GetSceneAt(i).isDirty)throw new Exception("Dirty scene: checkpoint required");
   var scene=EditorSceneManager.OpenScene(HnpWorldBuilder.ScenePath,OpenSceneMode.Single);
   var backup=Path.Combine(Root,"reports/world/NakornpathomWorld.pre-v003.unity");if(!File.Exists(backup))File.Copy(HnpWorldBuilder.ScenePath,backup);
   Directory.CreateDirectory(Art+"/Materials");
   foreach(var file in Directory.GetFiles(Path.Combine(Root,"art-export/hnp-world-003"))){if(file.EndsWith(".fbx")||file.EndsWith("HNP003_Palette.png"))File.Copy(file,Art+"/"+Path.GetFileName(file),true);}
   File.Copy(Path.Combine(Root,"art-export/hnp-world-003/HNP_Town_v003.fbx"),"Assets/_HNP/Art/World/HNP_Town.fbx",true);
   AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
   var texturePath=Art+"/HNP003_Palette.png";var ti=(TextureImporter)AssetImporter.GetAtPath(texturePath);ti.sRGBTexture=true;ti.filterMode=FilterMode.Point;ti.wrapMode=TextureWrapMode.Clamp;ti.mipmapEnabled=false;ti.textureCompression=TextureImporterCompression.Uncompressed;ti.SaveAndReimport();
   var atlas=AssetDatabase.LoadAssetAtPath<Texture2D>(texturePath);var data=JObject.Parse(File.ReadAllText(Path.Combine(Root,"art-export/hnp-world-003/manifest.json")));
   foreach(var token in (JArray)data["assets"]){var file=(string)token["file"];var importer=(ModelImporter)AssetImporter.GetAtPath(Art+"/"+file);importer.importAnimation=false;importer.importCameras=false;importer.importLights=false;
    foreach(string name in ((JArray)token["materials"]).Values<string>()){
     var m=Mat(name);if(name=="HNP3_Atlas"){m.color=Color.white;m.SetTexture("_BaseMap",atlas);}
     else {var c=(JArray)data["palette"][name];m.color=new((float)c[0],(float)c[1],(float)c[2]);}
     m.SetFloat("_Smoothness",name.Contains("Gold")?.36f:.32f);m.SetFloat("_Metallic",name.Contains("Gold")?.28f:0);EditorUtility.SetDirty(m);importer.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),name),m);
    }importer.SaveAndReimport();
   }
   var game=UnityEngine.Object.FindAnyObjectByType<HnpWorldGame>();if(!game)throw new Exception("World game missing");game.interfaceFont=AssetDatabase.LoadAssetAtPath<Font>("Assets/_HNP/UI/Fonts/Sarabun-Regular.ttf");if(!game.interfaceFont)throw new Exception("Thai font missing");
   var oldTown=scene.GetRootGameObjects().FirstOrDefault(o=>o.name.StartsWith("Town"));if(oldTown)UnityEngine.Object.DestroyImmediate(oldTown);
   var town=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_HNP/Art/World/HNP_Town.fbx"));town.name="Town — map reference";town.transform.localScale=new(-1,1,1);
   foreach(var mesh in town.GetComponentsInChildren<MeshFilter>())if(mesh.name.StartsWith("COLL_")){mesh.GetComponent<Renderer>().enabled=false;var collider=mesh.gameObject.AddComponent<MeshCollider>();collider.sharedMesh=mesh.sharedMesh;}
   var oldChedi=GameObject.Find("Phra Pathom Chedi");if(oldChedi)UnityEngine.Object.DestroyImmediate(oldChedi);
   var chedi=Instance("HNP_Chedi_v003.fbx");chedi.name="Phra Pathom Chedi";chedi.transform.position=new(53,2.9f,0);chedi.transform.rotation=Quaternion.Euler(0,90,0);
   PrefabUtility.SaveAsPrefabAsset(chedi,"Assets/_HNP/Prefabs/World/PhraPathomChedi.prefab");
   var core=GameObject.Find("Chedi solid core");if(core){core.transform.position=new(53,24.9f,0);core.transform.localScale=new(45.8f,22,45.8f);}
   var travellerPath=Art+"/HNP_Traveller_v003.fbx";var rigImporter=(ModelImporter)AssetImporter.GetAtPath(travellerPath);rigImporter.animationType=ModelImporterAnimationType.Generic;var clips=rigImporter.defaultClipAnimations;foreach(var c in clips){c.loopTime=true;c.loopPose=true;}rigImporter.clipAnimations=clips;
   foreach(var material in AssetDatabase.LoadAllAssetsAtPath(travellerPath).OfType<Material>()){var m=Mat(material.name);m.color=material.color;rigImporter.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),material.name),m);}rigImporter.SaveAndReimport();
   var imported=AssetDatabase.LoadAllAssetsAtPath(travellerPath).OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__preview__",StringComparison.Ordinal)).ToArray();
   var controllerPath=Art+"/Traveller003.controller";var controller=AssetDatabase.LoadAssetAtPath<AnimatorController>(controllerPath);if(!controller)controller=AnimatorController.CreateAnimatorControllerAtPath(controllerPath);
   controller.parameters=new AnimatorControllerParameter[0];controller.AddParameter("Speed",AnimatorControllerParameterType.Float);var sm=controller.layers[0].stateMachine;foreach(var state in sm.states)sm.RemoveState(state.state);
   AnimatorState State(string name){var clip=imported.FirstOrDefault(c=>c.name.EndsWith("HNP_Traveller_"+name,StringComparison.Ordinal));if(!clip)throw new Exception("Missing clip "+name);var state=sm.AddState(name);state.motion=clip;return state;}
   var idle=State("Idle");var walk=State("Walk");var run=State("Run");sm.defaultState=idle;
   void Transition(AnimatorState from,AnimatorState to,AnimatorConditionMode mode,float threshold){var tr=from.AddTransition(to);tr.hasExitTime=false;tr.duration=.14f;tr.AddCondition(mode,threshold,"Speed");}
   Transition(idle,walk,AnimatorConditionMode.Greater,.12f);Transition(walk,idle,AnimatorConditionMode.Less,.08f);Transition(walk,run,AnimatorConditionMode.Greater,7);Transition(run,idle,AnimatorConditionMode.Less,.08f);Transition(run,walk,AnimatorConditionMode.Less,7);
   while(game.visual.childCount>0)UnityEngine.Object.DestroyImmediate(game.visual.GetChild(0).gameObject);
   foreach(var pose in game.visual.GetComponents<HnpTravellerPose>())UnityEngine.Object.DestroyImmediate(pose);game.pose=null;
   var traveller=Instance("HNP_Traveller_v003.fbx");traveller.transform.SetParent(game.visual,false);traveller.transform.localScale=Vector3.one*1.310976f;
   var anim=traveller.GetComponent<Animator>();if(!anim)anim=traveller.AddComponent<Animator>();anim.runtimeAnimatorController=controller;anim.applyRootMotion=false;
   var bridge=traveller.AddComponent<HnpTravellerAnimatorBridge>();bridge.controller=game.player;
   var life=game.GetComponent<HnpWorldLife>();if(!life)life=game.gameObject.AddComponent<HnpWorldLife>();life.game=game;life.vehicleModels=new[]{"Sedan","Hatchback","Pickup","Minibus"}.Select(n=>AssetDatabase.LoadAssetAtPath<GameObject>(Art+"/HNP_"+n+"_v003.fbx")).ToArray();life.birdModel=AssetDatabase.LoadAssetAtPath<GameObject>(Art+"/HNP_Pigeon_v003.fbx");life.trainModel=AssetDatabase.LoadAssetAtPath<GameObject>(Art+"/HNP_Train_v003.fbx");
   // Old world-space text is replaced by the compact Thai HUD rather than floating English signs.
   foreach(var label in UnityEngine.Object.FindObjectsByType<TextMesh>(FindObjectsSortMode.None))if(label.gameObject.name.StartsWith("Wayfinding"))UnityEngine.Object.DestroyImmediate(label.gameObject);
   RenderSettings.ambientMode=AmbientMode.Trilight;RenderSettings.ambientSkyColor=new(.5f,.53f,.60f);RenderSettings.ambientEquatorColor=new(.53f,.4f,.28f);RenderSettings.ambientGroundColor=new(.24f,.23f,.18f);
   RenderSettings.fog=true;RenderSettings.fogMode=FogMode.Linear;RenderSettings.fogStartDistance=115;RenderSettings.fogEndDistance=360;RenderSettings.fogColor=new(.98f,.65f,.35f);
   var sky=RenderSettings.skybox;sky.SetColor("_Top",new(.64f,.44f,.37f));sky.SetColor("_Horizon",new(1,.76f,.39f));sky.SetFloat("_Daylight",1);EditorUtility.SetDirty(sky);
   var sun=RenderSettings.sun;sun.color=new(1,.82f,.58f);sun.intensity=1.6f;sun.shadowStrength=.7f;sun.shadowBias=.035f;sun.shadowNormalBias=.22f;sun.shadows=LightShadows.Soft;sun.transform.rotation=Quaternion.LookRotation(-new Vector3(.7f,.38f,-.65f));
   var rp=AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>("Assets/Settings/Mobile_RPAsset.asset");rp.msaaSampleCount=4;rp.shadowDistance=145;rp.renderScale=1;EditorUtility.SetDirty(rp);
   game.viewCamera.GetUniversalAdditionalCameraData().renderPostProcessing=false;
   EditorUtility.SetDirty(controller);EditorUtility.SetDirty(game);EditorUtility.SetDirty(life);EditorSceneManager.MarkSceneDirty(scene);EditorSceneManager.SaveScene(scene);AssetDatabase.SaveAssets();
   int missing=UnityEngine.Object.FindObjectsByType<MeshFilter>(FindObjectsSortMode.None).Count(m=>!m.sharedMesh);if(missing>0)throw new Exception("Missing meshes: "+missing);
   Debug.Log("HNP003_INTEGRATION_PASS clips="+string.Join(",",imported.Select(c=>c.name))+" font="+game.interfaceFont.name);
  }
  static GameObject Instance(string name)=> (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Art+"/"+name));
  static Material Mat(string name){var path=Art+"/Materials/"+name+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);if(!m){m=new Material(Shader.Find("Universal Render Pipeline/Lit"));m.enableInstancing=true;AssetDatabase.CreateAsset(m,path);}return m;}
 }
}
