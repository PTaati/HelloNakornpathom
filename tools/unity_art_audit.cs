using UnityEngine;
using HNP.World;
internal class CommandScript:IRunCommand {
 public void Execute(ExecutionResult result){
  var game=Object.FindFirstObjectByType<HnpWorldGame>();result.Log("player="+game.player.transform.position+" visual="+game.visual.lossyScale+" camera="+game.viewCamera.transform.position);
  var t=GameObject.Find("Town_HNPW_Teal").transform;result.Log("TEAL local pos="+t.localPosition+" rot="+t.localEulerAngles+" scale="+t.localScale+" meshbounds="+t.GetComponent<MeshFilter>().sharedMesh.bounds);
 }
}
