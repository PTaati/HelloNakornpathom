internal class CommandScript:IRunCommand {
 public void Execute(ExecutionResult result){HNP.Editor.HnpWorldBuilder.Build();result.Log("World Web build completed");}
}
