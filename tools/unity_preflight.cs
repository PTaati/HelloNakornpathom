using UnityEngine;
using UnityEditor;
using UnityEngine.SceneManagement;
internal class CommandScript : IRunCommand
{
    public void Execute(ExecutionResult result)
    {
        result.Log("Project: " + Application.dataPath + " Unity: " + Application.unityVersion);
        result.Log("Playing: " + EditorApplication.isPlaying + " Compiling: " + EditorApplication.isCompiling);
        result.Log("WebGL support: " + BuildPipeline.IsBuildTargetSupported(BuildTargetGroup.WebGL, BuildTarget.WebGL));
        for (int i=0;i<SceneManager.sceneCount;i++) {
            var s=SceneManager.GetSceneAt(i);
            result.Log("Scene: " + s.path + " dirty=" + s.isDirty + " roots=" + s.rootCount);
        }
    }
}
