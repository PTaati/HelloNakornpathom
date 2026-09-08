using System;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using HNP.Editor;
using HNP.World;
internal class CommandScript:IRunCommand {
 public void Execute(ExecutionResult result){
  if(EditorApplication.isPlaying)throw new Exception("Exit Play Mode first");
  var game=UnityEngine.Object.FindFirstObjectByType<HnpWorldGame>();
  if(!game)throw new Exception("Open the world scene first");
  if(game.gameObject.scene.isDirty)throw new Exception("Save current scene before art changes");
  HnpWorldBuilder.Materials("world-manifest.json","HNPW_","HNP_Town.fbx");
  HnpWorldBuilder.Materials("world-manifest.json","HNPW_","HNP_Chedi.fbx");
  HnpClearLighting.Apply();
  var cam=new GameObject("Map capture").AddComponent<Camera>();cam.transform.position=new Vector3(-4,200,0);cam.transform.rotation=Quaternion.Euler(90,0,0);cam.orthographic=true;cam.orthographicSize=72.4f;cam.aspect=240f/144.8f;cam.farClipPlane=400;
  bool fog=RenderSettings.fog;RenderSettings.fog=false;HnpWorldBuilder.Capture(cam,1200,724,"Assets/_HNP/Art/World/WorldMap.png");RenderSettings.fog=fog;result.DestroyObject(cam.gameObject);
  AssetDatabase.ImportAsset("Assets/_HNP/Art/World/WorldMap.png");game.mapTexture=AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/_HNP/Art/World/WorldMap.png");
  AssetDatabase.SaveAssets();EditorSceneManager.MarkSceneDirty(game.gameObject.scene);EditorSceneManager.SaveScene(game.gameObject.scene);
  result.Log("Slender chedi imported; clear daylight palette, shadows and minimap saved.");
 }
}
