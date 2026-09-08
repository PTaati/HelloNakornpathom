using UnityEngine;
using UnityEditor;
internal class CommandScript : IRunCommand
{
    public void Execute(ExecutionResult result)
    {
        HNP.Editor.HnpPrototypeBuilder.Create();
        result.RegisterObjectCreation(GameObject.Find("HNP Station Game"));
        result.Log("Station scene created and saved.");
    }
}
