using System.IO;
using System.Security.Cryptography;
using UnityEngine;

namespace HNP.World {
 /// <summary>Read-only Web/Play diagnostic for the v010 reference-photo shrine.</summary>
 public sealed class HnpShrine010Diagnostics : MonoBehaviour {
  public HnpWorldGame game; public Renderer photoRenderer;
  public void LogShrineDiagnostics(){
   var m=photoRenderer?photoRenderer.sharedMaterial:null;var t=m?m.mainTexture as Texture2D:null;
   var snapshot=new Snapshot{renderer=photoRenderer?photoRenderer.name:"MISSING",enabled=photoRenderer&&photoRenderer.enabled,material=m?m.name:"MISSING",shader=m&&m.shader?m.shader.name:"MISSING",texture=t?t.name:"MISSING",aspect=t?(float)t.width/t.height:0,unlit=m&&m.shader&&m.shader.name.IndexOf("Unlit",System.StringComparison.OrdinalIgnoreCase)>=0,player=game&&game.player?game.player.transform.position:Vector3.zero,camera=game&&game.viewCamera?game.viewCamera.transform.position:Vector3.zero};
   Debug.Log("HNP010_QA "+JsonUtility.ToJson(snapshot));
  }
  [System.Serializable] class Snapshot{public string renderer,material,shader,texture;public bool enabled,unlit;public float aspect;public Vector3 player,camera;}
 }
}
