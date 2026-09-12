using System;
using System.IO;
using System.Linq;
using HNP.World;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace HNP.Editor {
 public static class HnpTravellerV002Integrator {
  const string ScenePath="Assets/_HNP/Scenes/NakornpathomWorld.unity";
  const string FbxPath="Assets/_HNP/Art/World/HNP_Traveller_Child_Rigged_v002.fbx";
  const string ControllerPath="Assets/_HNP/Art/World/HNP_Traveller_Child_v002.controller";
  const string PrefabPath="Assets/_HNP/Prefabs/World/Traveller_Child_v002.prefab";
  const float Scale=1.310976f;
  static string ProjectRoot=>Directory.GetParent(Application.dataPath).FullName;
  public static void IntegrateBatch(){Integrate();}
  public static void IntegrateAndBuild(){Integrate();HnpWorldBuilder.Build();}
  [MenuItem("HNP/Integrate Traveller Child v002")]
  public static void Integrate(){
   if(EditorApplication.isPlaying)throw new InvalidOperationException("Exit Play Mode before integrating traveller v002.");
   for(int i=0;i<SceneManager.sceneCount;i++)if(SceneManager.GetSceneAt(i).isDirty)throw new InvalidOperationException("Refusing dirty scene: save/checkpoint before v002 integration.");
   if(!File.Exists(Path.Combine(ProjectRoot,FbxPath)))throw new FileNotFoundException("Missing staged traveller FBX",FbxPath);
   var scene=EditorSceneManager.OpenScene(ScenePath,OpenSceneMode.Single);
   if(scene.isDirty)throw new InvalidOperationException("World scene is dirty after opening; refusing overwrite.");
   var backup=Path.Combine(Directory.GetParent(ProjectRoot).FullName,"reports/world/NakornpathomWorld.pre-v002.unity");Directory.CreateDirectory(Path.GetDirectoryName(backup));if(!File.Exists(backup))File.Copy(Path.Combine(ProjectRoot,ScenePath),backup);
   var importer=(ModelImporter)AssetImporter.GetAtPath(FbxPath);
   var clipSettings=importer.defaultClipAnimations;
   foreach(var clip in clipSettings){clip.loopTime=true;clip.loopPose=true;}
   importer.clipAnimations=clipSettings;importer.SaveAndReimport();
   var model=AssetDatabase.LoadAssetAtPath<GameObject>(FbxPath);if(!model)throw new InvalidOperationException("FBX import is not ready.");
   var controller=CreateController(); var wrapper=CreateWrapper(model,controller);
   var game=UnityEngine.Object.FindFirstObjectByType<HnpWorldGame>();if(!game)throw new InvalidOperationException("HnpWorldGame missing from world scene.");
   var player=game.player?game.player.gameObject:null;if(!player)throw new InvalidOperationException("Traveller CharacterController missing from world scene.");
   // The serialized reference survives harmless hierarchy renames (currently "Traveller visual pivot").
   var visual=game.visual;if(!visual)throw new InvalidOperationException("Traveller visual reference missing from HnpWorldGame.");
   foreach(var oldPose in visual.GetComponentsInChildren<HnpTravellerPose>(true))UnityEngine.Object.DestroyImmediate(oldPose);
   while(visual.childCount>0)UnityEngine.Object.DestroyImmediate(visual.GetChild(0).gameObject);
   var instance=(GameObject)PrefabUtility.InstantiatePrefab(wrapper,visual);instance.name="Traveller Child v002";instance.transform.localPosition=Vector3.zero;instance.transform.localRotation=Quaternion.identity;instance.transform.localScale=Vector3.one;
   var bridge=instance.GetComponent<HnpTravellerAnimatorBridge>();bridge.controller=player.GetComponent<CharacterController>();
   var pose=visual.GetComponent<HnpTravellerPose>();if(pose)pose.enabled=false;
   game.pose=null;game.visual=visual;
   EditorSceneManager.MarkSceneDirty(scene);EditorSceneManager.SaveScene(scene,ScenePath);AssetDatabase.SaveAssets();
   Debug.Log("HNP_V002_INTEGRATED scale="+Scale+" axis=FBX -Z forward/Y up, wrapper local identity");
  }
  static AnimatorController CreateController(){
   var clips=AssetDatabase.LoadAllAssetsAtPath(FbxPath).OfType<AnimationClip>().ToArray();
   var idle=clips.FirstOrDefault(c=>c.name.EndsWith("HNP_Traveller_Idle",StringComparison.Ordinal));
   var walk=clips.FirstOrDefault(c=>c.name.EndsWith("HNP_Traveller_Walk",StringComparison.Ordinal));
   if(!idle||!walk)throw new InvalidOperationException("Imported Idle/Walk clips not found.");
   var c=AssetDatabase.LoadAssetAtPath<AnimatorController>(ControllerPath);
   if(!c)c=AnimatorController.CreateAnimatorControllerAtPath(ControllerPath);
   c.parameters=new AnimatorControllerParameter[0];c.AddParameter("Speed",AnimatorControllerParameterType.Float);
   if(c.layers.Length==0)c.AddLayer("Base Layer");
   foreach(var oldState in c.layers[0].stateMachine.states)c.layers[0].stateMachine.RemoveState(oldState.state);
   var sm=c.layers[0].stateMachine;var idleState=sm.AddState("Idle");idleState.motion=idle;sm.defaultState=idleState;var walkState=sm.AddState("Walk");walkState.motion=walk;
   var toWalk=idleState.AddTransition(walkState);toWalk.hasExitTime=false;toWalk.duration=.12f;toWalk.AddCondition(AnimatorConditionMode.Greater,.12f,"Speed");
   var toIdle=walkState.AddTransition(idleState);toIdle.hasExitTime=false;toIdle.duration=.14f;toIdle.AddCondition(AnimatorConditionMode.Less,.08f,"Speed");EditorUtility.SetDirty(c);AssetDatabase.SaveAssets();return c;
  }
  static GameObject CreateWrapper(GameObject model,AnimatorController controller){
   var root=new GameObject("Traveller Child v002");
   var child=(GameObject)PrefabUtility.InstantiatePrefab(model);child.transform.SetParent(root.transform,false);child.transform.localScale=Vector3.one*Scale;
   var animator=child.GetComponent<Animator>();if(!animator)animator=child.AddComponent<Animator>();animator.runtimeAnimatorController=controller;animator.applyRootMotion=false;
   root.AddComponent<HnpTravellerAnimatorBridge>();var prefab=PrefabUtility.SaveAsPrefabAsset(root,PrefabPath);UnityEngine.Object.DestroyImmediate(root);return prefab;
  }
 }
}
