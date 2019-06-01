Some VBScript commands
======================

VBScript is a light version of Microsoft's programming language Visual Basic.
It can be used in ASP (Active Server Pages) between tags ``<%`` and ``%>``, or run as a standalone script using a file ending with ``.vbs`` and interpreter ``wscript.exe``.

Special variables
-----------------

When launching a script:

* ``WScript.ScriptFullName`` contains the path of the script
* ``WScript.Arguments(0)`` contains the first argument of the invocation

Launch a process
----------------

.. code-block:: sh

    Dim objShell, strCommand
    Set objShell = CreateObject("Wscript.Shell")

    ' Show string concatenation and use Chr(), even though this is a trivial example
    strCommand = "cmd /c" & Chr(32) & "echo Hello"

    ' Syntax: objShell.Run (strCommand, [intWindowStyle], [bWaitOnReturn])
    objShell.Run strCommand, 0, true

    Set objShell = Nothing
