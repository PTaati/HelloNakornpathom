using UnityEditor;
internal class CommandScript : IRunCommand
{
    public void Execute(ExecutionResult result)
    {
        EditorApplication.delayCall += () => AssetDatabase.Refresh();
        result.Log("Asset refresh scheduled.");
    }
}
