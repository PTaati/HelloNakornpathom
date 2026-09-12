using System;
using UnityEditor;
using UnityEngine.SceneManagement;

namespace HNP.Editor {
 public static class HnpLatestWebBuild {
  public static void Build(){
   if(EditorApplication.isPlaying)throw new Exception("Exit Play Mode before building.");
   for(int i=0;i<SceneManager.sceneCount;i++)if(SceneManager.GetSceneAt(i).isDirty)throw new Exception("Save/checkpoint pending scene changes before building.");
   // Build the current saved project; do not rerun historical art integration.
   HnpWorldBuilder.BuildAt("builds/web");
  }
 }
}
