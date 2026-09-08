using UnityEditor;
internal class CommandScript : IRunCommand {
 public void Execute(ExecutionResult result) {
  EditorApplication.isPlaying=true;
  result.Log("Play Mode requested.");
 }
}
