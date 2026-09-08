using UnityEngine;
internal class CommandScript:IRunCommand {
 public void Execute(ExecutionResult result){HNP.Editor.HnpWorldBuilder.Create();result.RegisterObjectCreation(GameObject.Find("HNP World Game"));result.Log("Reference world saved");}
}
