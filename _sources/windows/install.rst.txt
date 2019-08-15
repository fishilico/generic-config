Installing Windows
==================

Here are some notes about installing Windows 10 Enterprise.

Base installation of Windows 10
-------------------------------

In order to install Windows 10, a disc image (ISO file) can be downloaded from https://www.microsoft.com/en-us/software-download/windows10ISO.

This would install Windows 10 Pro by default.
In order to set up another edition, all that is needed is to provide a matching license key.
Microsoft published a table describing what switches are available between Windows editions: https://docs.microsoft.com/en-us/windows/deployment/upgrade/windows-10-edition-upgrades.
For example, it is possible to switch from Windows 10 Pro to Windows 10 Enterprise using a KMS (Key Management Service) key.
The official Microsoft website documents such keys on https://docs.microsoft.com/en-us/windows-server/get-started/kmsclientkeys.
On this website, Windows 10 Enterprise's KMS key is ``NPPR9-FWDCX-D2C8J-H872K-2YT43``.


Enable the Windows Subsystem for Linux
--------------------------------------

To install WSL (Windows Subsystem for Linux), run this command as Administrator::

    C:\> PowerShell Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux

    Path          :
    Online        : True
    RestartNeeded : True

After this command, the system should be rebooted.

In order to check whether WSL is installed:

.. code-block:: text

    C:\> PowerShell Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux

    FeatureName      : Microsoft-Windows-Subsystem-Linux
    DisplayName      : Windows Subsystem for Linux
    Description      : Provides services and environments for running native user-mode Linux shells
                       and tools on Windows.
    RestartRequired  : Possible
    State            : Enabled
    CustomProperties :
                       ServerComponent\Description : Provides services and environments for running
                       native user-mode Linux shells and tools on Windows.
                       ServerComponent\DisplayName : Windows Subsystem for Linux
                       ServerComponent\Id : 1033
                       ServerComponent\Type : Feature
                       ServerComponent\UniqueName : Microsoft-Windows-Subsystem-Linux
                       ServerComponent\Deploys\Update\Name : Microsoft-Windows-Subsystem-Linux

In order to install Ubuntu, the following PowerShell commands can be used::

    curl -L -o ubuntu-1804.appx https://aka.ms/wsl-ubuntu-1804
    # Or, without using PowerShell aliases:
    # Invoke-WebRequest -Uri https://aka.ms/wsl-ubuntu-1804 -OutFile Ubuntu-1804.appx -UseBasicParsing
    Rename-Item Ubuntu-1804.appx Ubuntu-1804.zip
    Expand-Archive Ubuntu-1804.zip Ubuntu-1804
    cd Ubuntu-1804
    .\ubuntu1804.exe

This last command spawns a shell inside a Ubuntu distribution which is using WSL.

Documentation about WSL:

- https://docs.microsoft.com/en-us/windows/wsl/install-win10
  Generic installation guide
- https://docs.microsoft.com/en-us/windows/wsl/install-on-server
  Installation guide for servers
- https://docs.microsoft.com/en-gb/windows/wsl/release-notes
  Release notes


Software to install
-------------------

Automatic installation
~~~~~~~~~~~~~~~~~~~~~~

In order to ease the installation of software, a package manager such as
`Ninite <https://ninite.com/>`_ or `Chocolatey <https://chocolatey.org/>`_ can be
used (cf. https://chocolatey.org/docs/chocolatey-vs-ninite).
Chocolatey's website gives some installation commands
(https://chocolatey.org/docs/installation#install-with-cmdexe)::

    # For cmd.exe
    @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
    SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"

    # For PowerShell
    Set-ExecutionPolicy Bypass -Scope Process -Force;
    iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

Chocolatey adds itself to ``%PATH%`` environment variable, and this can be
verified in the registry::

    PS C:\> Get-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment' -Name PATH
    # It should ends with C:\ProgramData\chocolatey\bin;

    # Or with cmd.exe:
    reg query "HKLM\System\CurrentControlSet\Control\Session Manager\Environment" /v PATH

Then, to install software::

    choco install notepadplusplus notepadplusplus.commandline vscode -y
    choco install windbg -y

    # Install Sysinternals tools, https://chocolatey.org/packages?q=sysinternals
    choco install procexp procmon autoruns psexec procdump sigcheck dbgview winobj -y
    choco install adexplorer accesschk accessenum -y

    # MSys2 is installed in C:\tools\msys64
    choco install git python3 msys2 -y
    # Add 'PATH="$PATH:/c/Program Files/Git/cmd"' to C:/tools/msys64/home/IEUser/.bashrc
    # Launch MSys with C:/tools/msys64/usr/bin/bash.exe

    # Install Microsoft Visual C++ Runtime and .Net runtime
    choco install vcredist-all dotnet3.5 dotnet4.7 -y

    # Install Microsoft Baseline Security Analyzer
    choco install mbsa -y

    # Install other Desktop software
    choco install chromium filezilla firefox kitty vlc winscp -y
    choco install ldapadmin sql-server-management-studio -y
    choco install windows-sdk-10.0 windowsdriverkit10 visualstudio2019buildtools -y
    choco install dnspy ilspy wireshark -y
    choco install processhacker regshot -y
    # Install the CFF Explorer and Resource Hacker
    choco install explorersuite reshack -y

These commands install the following software:

* Notepad++: https://notepad-plus-plus.org/ (the sha1sums of the downloaded files can be verified)
* Windows Development Kits, debugger (WinDbg...):

  - https://developer.microsoft.com/en-us/windows/hardware/windows-driver-kit
  - Create a shortcut to ``C:\Program Files (x86)\Windows Kits\10\Debuggers\x64``

* Some Sysinternals tools:

  - Process Explorer https://technet.microsoft.com/en-us/sysinternals/processexplorer
  - Process Monitor https://technet.microsoft.com/en-us/sysinternals/processmonitor
  - DebugView https://technet.microsoft.com/en-us/sysinternals/debugview
  - WinObj https://technet.microsoft.com/en-us/sysinternals/winobj
  - AccessEnum https://technet.microsoft.com/en-us/sysinternals/accessenum
  - etc.

* Git: https://git-scm.com/
* Python: https://www.python.org/downloads/windows/

* MSys2 environment: https://www.msys2.org/. Additional software like GCC
  (to compile C programs) can be installed with::

    c:\tools\msys64\usr\bin\bash.exe
    pacman -Sy base-devel mingw-w64-x86_64-toolchain

In the end: reboot! (Remember that we are talking about Windows...)

::

    # "Powershell Restart-Computer" may also work
    shutdown -r -t 0


Debloat Windows
~~~~~~~~~~~~~~~

Windows 10 comes with many features which are better disabled. Here are some
websites describing them:

* https://github.com/W4RH4WK/Debloat-Windows-10
* https://www.01net.com/actualites/comme-windows-10-windows-7-et-8-embarquent-des-mouchards-911343.html

Here are commands that can be issued once Git has been installed, in a
PowerShell administrator console:

.. code-block:: sh

    git clone https://github.com/W4RH4WK/Debloat-Windows-10
    cd Debloat-Windows-10\scripts
    Set-ExecutionPolicy Bypass -Scope Process -Force
    .\block-telemetry.ps1
    .\disable-services.ps1
    # .\disable-windows-defender.ps1
    # .\experimental_unfuckery.ps1 # Uncomment some apps there
    .\fix-privacy-settings.ps1
    .\optimize-user-interface.ps1
    .\optimize-windows-update.ps1
    .\remove-default-apps.ps1
    .\remove-onedrive.ps1


Hyper-V configuration
---------------------

Hyper-V is quite straightforward to use but for network management.
In order to create an internal network which is NAT'ed to the external network, some PowerShell commands are documented on https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/user-guide/setup-nat-network:

.. code-block:: sh

    # Create a new virtual switch
    New-VMSwitch -SwitchName 'Nat4HyperV' -SwitchType Internal

    # Retrieve the index of the new interface, with one of these two commands
    Get-NetAdapter
    $nat_ifindex = (Get-NetAdapter -Name 'vEthernet (Nat4HyperV)').ifIndex

    # Assign a static IP address to the host interface of the new switch
    New-NetIPAddress -IPAddress '10.0.0.1' -PrefixLength 24 -InterfaceIndex $nat_ifindex

    # Create a new NAT (Network Address Translation)
    New-NetNat -Name 'NatOfHyperV' -InternalIPInterfaceAddressPrefix '10.0.0.0/24'

It is then possible to associate the network adapter of Hyper-V virtual machines with internal network ``Nat4HyperV``.


Activation using py-kms
-----------------------

In order to activate Windows in an offline environment, it is possible to install py-kms (https://github.com/SystemRage/py-kms) on a Debian Hyper-V virtual machine:

.. code-block:: sh

    git clone https://github.com/SystemRage/py-kms
    cd py-kms/py3-kms
    python3 server.py -v DEBUG --sqlite

This will launch a KMS (Key Management Service) on TCP port 1688.
The following PowerShell commands configure a Windows system to use it, using SLMGR (the Software License Manager):

.. code-block:: sh

    # In C:\Windows\system32
    cd %WINDIR%\system32

    # /upk for "Uninstall Product Key"
    cscript //Nologo slmgr.vbs /upk

    # /ipk for "Install Product Key", for example for Windows 10 Enterprise
    cscript //Nologo slmgr.vbs /ipk NPPR9-FWDCX-D2C8J-H872K-2YT43

    # /skms to specify the KMS on IP address 192.0.2.42
    cscript //Nologo slmgr.vbs /skms 192.0.2.42:1688

    # /ato to prompt Windows to attempt online activation
    cscript //Nologo slmgr.vbs /ato

    # Display license information and detailed license information
    cscript //Nologo slmgr.vbs /dli
    cscript //Nologo slmgr.vbs /dlv

This creates an entry in database ``py-kms/py3-kms/clients.db`` (table ``clients``).

In order to launch py-kms as a systemd service, a service file can be created:

.. code-block:: sh

    # cf. https://github.com/SystemRage/py-kms/issues/4
    cat > /etc/systemd/system/py-kms.service << EOF
    [Unit]
    Description=py3-kms
    After=network-online.target
    Wants=network-online.target

    [Service]
    Restart=always
    Type=simple
    ExecStart=/usr/bin/python3 /opt/py-kms/py3-kms/server.py -v DEBUG --sqlite
    WorkingDirectory=/opt/py-kms/py3-kms

    [Install]
    WantedBy=multi-user.target
    EOF

    systemctl daemon-reload
    systemctl enable py-kms.service
    systemctl start py-kms.service
