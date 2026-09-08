using UnityEngine;
using HNP.World;
internal class CommandScript:IRunCommand {
 public void Execute(ExecutionResult result){
 var g=Object.FindFirstObjectByType<HnpWorldGame>();g.Begin();
 var r=GameObject.Find("Town_HNPW_Teal").GetComponent<Renderer>();r.enabled=false;
 HNP.Editor.HnpWorldBuilder.Capture(g.viewCamera,1280,720,"../reports/world/player-debug.png");
 r.enabled=true;result.Log("Player view captured with teal mesh hidden temporarily");
 }
}
