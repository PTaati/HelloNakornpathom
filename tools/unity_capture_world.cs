using System.IO;
using UnityEngine;
using HNP.World;
internal class CommandScript:IRunCommand {
 public void Execute(ExecutionResult result){
  var root=Directory.GetParent(Application.dataPath).Parent.FullName;
  var camera=new GameObject("Temporary evidence camera").AddComponent<Camera>();camera.fieldOfView=55;camera.farClipPlane=500;camera.clearFlags=CameraClearFlags.Skybox;
  camera.transform.position=new Vector3(-43,7,-3);camera.transform.LookAt(new Vector3(53,14,0));HNP.Editor.HnpWorldBuilder.Capture(camera,1440,900,Path.Combine(root,"reports/world/approach.png"));
  camera.transform.position=new Vector3(-100,115,-125);camera.transform.LookAt(new Vector3(0,0,0));HNP.Editor.HnpWorldBuilder.Capture(camera,1600,1000,Path.Combine(root,"reports/world/aerial.png"));
  result.DestroyObject(camera.gameObject);
  var game=UnityEngine.Object.FindFirstObjectByType<HnpWorldGame>();if(game){game.Begin();game.ReturnToStation();}
  ScreenCapture.CaptureScreenshot(Path.Combine(root,"reports/world/gameplay.png"));result.Log("Reference-world screenshots captured.");
 }
}
