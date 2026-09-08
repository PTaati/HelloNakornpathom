using UnityEditor;
internal class CommandScript : IRunCommand {
 public void Execute(ExecutionResult result) {
  HNP.Editor.HnpPrototypeBuilder.BuildWeb();
  result.Log("Web build completed; inspect reports/web-build.txt.");
 }
}
