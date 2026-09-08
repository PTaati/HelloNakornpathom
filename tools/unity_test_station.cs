using System;
using System.IO;
using UnityEngine;
using UnityEditor;
using HNP.Prototype;
internal class CommandScript : IRunCommand {
 void Assert(bool value,string message) { if(!value) throw new Exception(message); }
 public void Execute(ExecutionResult result) {
  Assert(EditorApplication.isPlaying,"Not in Play Mode");
  var g=UnityEngine.Object.FindFirstObjectByType<HnpStationGame>();
  Assert(g!=null,"Game missing");
  g.BeginJourney();
  Assert(!g.TryDepart(),"Early departure allowed");
  var start=g.player.transform.position;
  for(int i=0;i<60;i++) g.SimulateMovement(Vector2.up,false,1f/60);
  Assert(g.player.transform.position.z>start.z+3,"Movement failed");
  g.SimulateMovement(Vector2.zero,true,1f/60);
  Assert(g.VerticalSpeed>0,"Jump failed");
  for(int i=0;i<120;i++) g.SimulateMovement(Vector2.zero,false,1f/60);
  Assert(g.player.isGrounded,"Landing failed");
  foreach(var card in g.postcards) {
   g.player.enabled=false; g.player.transform.position=new Vector3(card.position.x,.1f,card.position.z); g.player.enabled=true;
   g.CheckPickups(); g.CheckPickups();
  }
  Assert(g.Collected==3,"Pickups incorrect or duplicated");
  Assert(!g.TryDepart(),"Departure allowed outside gate radius");
  g.player.enabled=false; g.player.transform.position=g.destination.position; g.player.enabled=true;
  Assert(g.TryDepart() && g.Finished,"Ending failed");
  Assert(!g.TryDepart(),"Duplicate departure allowed");
  g.RestartJourney(); Assert(g.Collected==0 && !g.Finished,"Restart failed");
  foreach(var card in g.postcards) Assert(card.gameObject.activeSelf,"Card not restored");
  var bench=GameObject.Find("HNP Station Bench");
  var renderers=bench.GetComponentsInChildren<Renderer>();
  var bounds=renderers[0].bounds; foreach(var r in renderers) { bounds.Encapsulate(r.bounds); foreach(var m in r.sharedMaterials) Assert(m && m.shader && m.shader.name.Contains("Universal"),"Bench material invalid"); }
  Assert(Mathf.Abs(bounds.size.y-1.145f)<.03f,"Bench height wrong: "+bounds.size);
  Assert(bench.GetComponents<BoxCollider>().Length==2,"Bench colliders missing");
  var root=Directory.GetParent(Application.dataPath).Parent.FullName;
  Directory.CreateDirectory(Path.Combine(root,"reports"));
  ScreenCapture.CaptureScreenshot(Path.Combine(root,"reports/station-play.png"));
  result.Log("PASS: movement, jump, landing, pickup idempotency, departure gating, ending, restart, bench dimensions/materials/colliders. Screenshot requested.");
 }
}
