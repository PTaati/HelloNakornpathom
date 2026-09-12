using System;
using System.Collections.Generic;
using System.IO;
using Newtonsoft.Json;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEditor.SceneManagement;
namespace HNP.Editor {
 public static class HnpCollision008Tests {
  public static void Run(MeshCollider source,string reportPath){
   var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Additive);var rows=new List<object>();var offset=new Vector3(1000,0,1000);
   try{
    var solid=new GameObject("Test monument");SceneManager.MoveGameObjectToScene(solid,scene);solid.transform.position=source.transform.position+offset;solid.transform.rotation=source.transform.rotation;solid.transform.localScale=source.transform.lossyScale;solid.AddComponent<MeshCollider>().sharedMesh=source.sharedMesh;
    var ground=new GameObject("Test ground");SceneManager.MoveGameObjectToScene(ground,scene);ground.transform.position=new Vector3(53,-.5f,0)+offset;ground.AddComponent<BoxCollider>().size=new(200,1,200);
    foreach(var dir in new[]{Vector3.forward,Vector3.back,Vector3.left,Vector3.right})foreach(float speed in new[]{5.4f,27f})foreach(bool jump in new[]{false,true}){
     var probe=new GameObject("Player-sized probe");SceneManager.MoveGameObjectToScene(probe,scene);probe.transform.position=new Vector3(53,.08f,0)+offset+dir*30;var cc=probe.AddComponent<CharacterController>();cc.height=2.15f;cc.radius=.32f;cc.center=Vector3.up*1.075f;cc.stepOffset=.3f;cc.skinWidth=.04f;
     Physics.SyncTransforms();float vertical=jump?6.2f:0,minRadius=30;
     for(int frame=0;frame<240;frame++){if(cc.isGrounded&&vertical<0)vertical=-2;vertical-=19f/60;cc.Move((-dir*speed+Vector3.up*vertical)/60);var p=probe.transform.position-offset-new Vector3(53,0,0);p.y=0;minRadius=Mathf.Min(minRadius,p.magnitude);}
     float finalRadius=Vector2.Distance(new Vector2(probe.transform.position.x-offset.x,probe.transform.position.z-offset.z),new Vector2(53,0));bool pass=minRadius>=22.65f&&finalRadius<24;
     rows.Add(new{direction=dir.ToString(),speed,jump,minRadius,finalRadius,status=pass?"PASS":"FAIL"});UnityEngine.Object.DestroyImmediate(probe);if(!pass)throw new Exception("Chedi penetration/test approach failure: "+JsonConvert.SerializeObject(rows[rows.Count-1]));
    }
    Debug.Log("HNP008_CHARACTER_COLLISION_PASS cases="+rows.Count);
   }finally{File.WriteAllText(reportPath,JsonConvert.SerializeObject(rows,Formatting.Indented));EditorSceneManager.CloseScene(scene,true);}
  }
 }
}
