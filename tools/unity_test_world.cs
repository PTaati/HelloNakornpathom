using System;
using System.IO;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using HNP.World;
internal class CommandScript:IRunCommand {
 void Check(bool ok,string message){if(!ok)throw new Exception(message);}
 HnpWorldGame game;
 void Walk(Vector3 destination){
  for(int i=0;i<6000;i++){
   var d=destination-game.player.transform.position;d.y=0;
   if(d.magnitude<.22f)return;
   game.SetHeading(Mathf.Atan2(d.x,d.z)*Mathf.Rad2Deg);
   game.Step(Vector2.up*Mathf.Min(1,d.magnitude*2),false,true,1f/60);
   Check(game.player.transform.position.y>-.7f,"Fell below walkable world");
  }
  throw new Exception("Blocked travelling to "+destination+" from "+game.player.transform.position);
 }
 public void Execute(ExecutionResult result){
  Check(EditorApplication.isPlaying,"Play Mode required");game=UnityEngine.Object.FindFirstObjectByType<HnpWorldGame>();Check(game!=null,"World game missing");
  game.Begin();game.ReturnToStation();
  var checks=new List<string>();
  Walk(new Vector3(-67,0,0));checks.Add("Station to central bridge");
  Walk(new Vector3(-30,0,0));checks.Add("Bridge to old market");
  Walk(new Vector3(27,3,0));Check(game.player.transform.position.y>2.6f,"West stairs did not reach terrace");checks.Add("Market to upper terrace via stairs");
  for(int a=180;a<=540;a+=10){float r=a*Mathf.Deg2Rad;Walk(new Vector3(53+26*Mathf.Cos(r),3,26*Mathf.Sin(r)));}
  checks.Add("Full 360-degree upper terrace loop");
  Walk(new Vector3(27,3,0));Walk(new Vector3(10,0,0));Check(game.player.transform.position.y<.8f,"Stairs descent failed");
  Walk(new Vector3(7,0,-45));Walk(new Vector3(100,0,-45));Walk(new Vector3(100,0,48));Walk(new Vector3(7,0,48));checks.Add("South fair, east plaza and north plaza reachable");
  Walk(new Vector3(7,0,58));Walk(new Vector3(-13,0,58));Walk(new Vector3(-80,0,58));checks.Add("Northern bridge traversable via perimeter road");
  Walk(new Vector3(-80,0,-58));Walk(new Vector3(-13,0,-58));checks.Add("Southern bridge traversable");
  Walk(new Vector3(-8,0,-58));Walk(new Vector3(-8,0,0));Walk(new Vector3(-101,0,0));checks.Add("Return to station on foot");
  for(int i=0;i<60;i++)game.Step(Vector2.zero,false,false,1f/60);
  game.Step(Vector2.zero,true,false,1f/60);Check(game.VerticalSpeed>0,"Jump failed");
  for(int i=0;i<120;i++)game.Step(Vector2.zero,false,false,1f/60);Check(game.player.isGrounded,"Landing failed");checks.Add("Jump and landing");
  var root=Directory.GetParent(Application.dataPath).Parent.FullName;File.WriteAllLines(Path.Combine(root,"reports/world/traversal.txt"),checks);
  game.ReturnToStation();
  result.Log("PASS "+string.Join("; ",checks));
 }
}
