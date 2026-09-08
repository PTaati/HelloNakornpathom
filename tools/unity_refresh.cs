using UnityEditor;
internal class CommandScript : IRunCommand
{
    public void Execute(ExecutionResult result)
    {
        AssetDatabase.Refresh();
        result.Log("Asset refresh requested; script reload may reconnect MCP.");
    }
}
