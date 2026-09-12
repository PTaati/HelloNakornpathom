using System;
using System.Collections.Generic;
using System.IO;
using Newtonsoft.Json;
using UnityEngine;

namespace HNP.Editor {
 public static class HnpTemple009Tests {
  // Real scene geometry + player-sized CharacterController.Move; no changes to the saved player.
  public static void Run(string output){
   var rows=new List<object>();var probe=new GameObject("Temporary temple traversal probe");
   var cc=probe.AddComponent<CharacterController>();cc.height=2.15f;cc.radius=.32f;cc.center=new(0,1.08f,0);cc.stepOffset=.32f;cc.slopeLimit=48;
   try{
    foreach(var outward in new[]{Vector3.forward,Vector3.back,Vector3.left,Vector3.right}){
     cc.enabled=false;probe.transform.position=new Vector3(53,.4f,0)+outward*40;cc.enabled=true;Physics.SyncTransforms();
     float vertical=0,gateDeviation=0;
     for(int i=0;i<260;i++){if(cc.isGrounded&&vertical<0)vertical=-2;vertical-=19f/60;cc.Move((-outward*5.4f+Vector3.up*vertical)/60);var delta=probe.transform.position-new Vector3(53,0,0);delta.y=0;if(delta.magnitude>=29&&delta.magnitude<=38)gateDeviation=Mathf.Max(gateDeviation,(delta-outward*Vector3.Dot(delta,outward)).magnitude);}
     var position=probe.transform.position;float radius=Vector2.Distance(new(position.x,position.z),new(53,0));
     bool pass=radius>=22.65f&&radius<30&&position.y>2.6f&&position.y<8&&gateDeviation<.1f;
     rows.Add(new{test="cardinal stair approach",outward=outward.ToString(),position=new[]{position.x,position.y,position.z},radius,gateDeviation,status=pass?"PASS":"FAIL"});
     if(!pass)throw new Exception("Temple route blocked or floor missing: "+outward+" "+position);
    }
    // Rear semicircle avoids the intentional front shrine and checks preserved upper court seams.
    foreach(float sign in new[]{-1f,1f}){
     cc.enabled=false;probe.transform.position=new Vector3(53,3.1f,27);cc.enabled=true;Physics.SyncTransforms();
     float vertical=0;float travel=0;
     for(int i=0;i<480;i++){
      var delta=probe.transform.position-new Vector3(53,0,0);delta.y=0;var tangent=Vector3.Cross(Vector3.up,delta.normalized)*sign;
      var correction=delta.normalized*Mathf.Clamp((27-delta.magnitude)*2,-1,1);
      if(cc.isGrounded&&vertical<0)vertical=-2;vertical-=19f/60;
      var before=probe.transform.position;cc.Move(((tangent+correction)*5.4f+Vector3.up*vertical)/60);travel+=Vector2.Distance(new(before.x,before.z),new(probe.transform.position.x,probe.transform.position.z));
     }
     bool pass=travel>35&&probe.transform.position.y>2.6f;
     rows.Add(new{test="upper court arc",sign,travel,position=new[]{probe.transform.position.x,probe.transform.position.y,probe.transform.position.z},status=pass?"PASS":"FAIL"});
     if(!pass)throw new Exception("Upper court traversal blocked");
    }
   }finally{UnityEngine.Object.DestroyImmediate(probe);File.WriteAllText(output,JsonConvert.SerializeObject(rows,Formatting.Indented));}
  }
 }
}
