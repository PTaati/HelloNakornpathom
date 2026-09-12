using UnityEngine;
using UnityEditor;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
namespace HNP.Editor {
 public static class HnpClearLighting {
  public static void Apply(){
   RenderSettings.ambientMode=AmbientMode.Trilight;
   RenderSettings.ambientSkyColor=new Color(.66f,.77f,.92f);
   RenderSettings.ambientEquatorColor=new Color(.65f,.69f,.66f);
   RenderSettings.ambientGroundColor=new Color(.35f,.39f,.32f);
   RenderSettings.fog=true;RenderSettings.fogMode=FogMode.Linear;
   RenderSettings.fogStartDistance=240;RenderSettings.fogEndDistance=650;RenderSettings.fogColor=new Color(.76f,.85f,.91f);
   var sun=RenderSettings.sun;
   if(sun){sun.color=new Color(1,.95f,.84f);sun.intensity=1.35f;sun.shadowStrength=.78f;sun.shadowBias=.035f;sun.shadowNormalBias=.25f;sun.shadows=LightShadows.Soft;sun.transform.rotation=Quaternion.LookRotation(-new Vector3(-.75f,.8f,-.3f));EditorUtility.SetDirty(sun);}
   var sky=RenderSettings.skybox;
   if(sky){sky.SetColor("_Top",new Color(.19f,.50f,.78f));sky.SetColor("_Horizon",new Color(.89f,.88f,.73f));EditorUtility.SetDirty(sky);}
   var pipeline=AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>("Assets/Settings/Mobile_RPAsset.asset");
   if(pipeline){pipeline.msaaSampleCount=4;pipeline.renderScale=1;pipeline.shadowDistance=120;EditorUtility.SetDirty(pipeline);}
   var core=GameObject.Find("Chedi solid core");
   if(core){core.transform.position=new Vector3(53,29.96f,0);core.transform.localScale=new Vector3(40.3f,27.06f,40.3f);}
  }
 }
}
