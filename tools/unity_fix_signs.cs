using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
internal class CommandScript : IRunCommand {
 public void Execute(ExecutionResult result) {
  if(EditorApplication.isPlaying) throw new System.Exception("Exit Play Mode first");
  foreach(var text in Object.FindObjectsByType<TextMesh>(FindObjectsSortMode.None)) {
   if(!text.name.StartsWith("Sign ")) continue;
   result.RegisterObjectModification(text); result.RegisterObjectModification(text.transform);
   text.transform.localRotation=Quaternion.identity;
   text.characterSize=text.text=="NAKORNPATHOM"?.07f:.085f;
  }
  EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene());
  result.Log("Fixed and saved station signs.");
 }
}
