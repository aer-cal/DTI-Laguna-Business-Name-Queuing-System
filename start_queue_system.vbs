Dim shell
Dim fso
Dim repoRoot
Dim batPath

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

repoRoot = fso.GetParentFolderName(WScript.ScriptFullName)
batPath = Chr(34) & repoRoot & "\run.bat" & Chr(34)

shell.Run batPath, 0, False
