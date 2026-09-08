using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using HNP.World;
internal class CommandScript:IRunCommand {
 public void Execute(ExecutionResult result){
  var town=GameObject.Find("Town — map reference");result.RegisterObjectModification(town.transform);town.transform.rotation=Quaternion.identity;town.transform.localScale=new Vector3(-1,1,1);
  var game=Object.FindFirstObjectByType<HnpWorldGame>();var old=game.visual;
  if(old.GetComponent<HnpTravellerPose>()){
   var wrapper=new GameObject("Traveller visual pivot").transform;wrapper.SetParent(game.player.transform,false);wrapper.localRotation=Quaternion.Euler(0,90,0);old.SetParent(wrapper,false);old.localRotation=Quaternion.identity;old.localScale=new Vector3(-1,1,1);game.visual=wrapper;
   result.RegisterObjectCreation(wrapper.gameObject);
  }
  var model=game.pose.transform;model.localRotation=Quaternion.identity;model.localScale=new Vector3(-1,1,1);
  var cam=new GameObject("Map capture").AddComponent<Camera>();cam.transform.position=new Vector3(-4,200,0);cam.transform.rotation=Quaternion.Euler(90,0,0);cam.orthographic=true;cam.orthographicSize=72.4f;cam.aspect=240f/144.8f;cam.farClipPlane=400;cam.clearFlags=CameraClearFlags.SolidColor;cam.backgroundColor=new Color(.29f,.36f,.19f);
  bool fog=RenderSettings.fog;RenderSettings.fog=false;HNP.Editor.HnpWorldBuilder.Capture(cam,1200,724,"Assets/_HNP/Art/World/WorldMap.png");RenderSettings.fog=fog;result.DestroyObject(cam.gameObject);
  AssetDatabase.ImportAsset("Assets/_HNP/Art/World/WorldMap.png");game.mapTexture=AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/_HNP/Art/World/WorldMap.png");
  PrefabUtility.SaveAsPrefabAsset(game.player.gameObject,"Assets/_HNP/Prefabs/World/Traveller.prefab");
  EditorSceneManager.MarkSceneDirty(game.gameObject.scene);EditorSceneManager.SaveScene(game.gameObject.scene);result.Log("World map axes, traveller forward direction and minimap corrected.");
 }
}
