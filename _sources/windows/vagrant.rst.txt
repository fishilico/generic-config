Windows Virtual Machine with Vagrant
====================================

Microsoft provides free Windows Vircual Machines (which expire after 90 days) on
https://developer.microsoft.com/en-us/microsoft-edge/.
Among the available VM are Vagrant machines. Here are instructions to setup
a Windows VM through Vagrant using Libvirt and QEmu-KVM as backend.


Create a Libvirt box
--------------------

* Download a ZIP from https://developer.microsoft.com/en-us/microsoft-edge/tools/vms/, like
  https://az792536.vo.msecnd.net/vms/VMBuild_20180425/Vagrant/MSEdge/MSEdge.Win10.Vagrant.zip

  - Or pull the Vagrant image from https://app.vagrantup.com/Microsoft/boxes/EdgeOnWindows10

* Extract the box from the ZIP (it is named for example ``MSEdge - Win10.box``)::

    unzip MSEdge.Win10.Vagrant.zip

* Import the VirtualBox-Vagrant box and mutate it to use provider ``libvirt``::

    vagrant plugin install vagrant-mutate
    vagrant box add windows/win10-edge 'MSEdge - Win10.box'
    vagrant mutate windows/win10-edge libvirt
    vagrant box remove --provider virtualbox windows/win10-edge

  The mutate command will use ``qemu-img convert -p -S 16k -o compat=1.1 -O qcow2 ...``
  to convert the virtual box disk to a QEmu-compatible one.

* Initialize a new Vagrant box in the current directory::

    vagrant init windows/win10-edge

* Configure the box by adding the following lines to ``Vagrantfile`` before the
  final ``end``::

    # Configure remote access
    config.ssh.username = "IEUser"
    config.ssh.password = "Passw0rd!"

    # Use 2 CPU and 4GB of RAM
    config.vm.provider :libvirt do |v|
      v.cpus = 2
      v.memory = 4096
    end

* Start the new box::

    vagrant up --provider libvirt --no-destroy-on-error

This command will fail and the console on the virtual machine will display:

.. code-block:: text

    Booting from Hard disk...
    No bootable device.

This is because the virtual machine needs to boot in UEFI mode and the network
drivers are missing. For the network issue, the next section provides a way to
fix the issue. For UEFI boot, Libvirt needs to be configured to support this
boot mode. For Arch Linux, this is documented in
https://wiki.archlinux.org/index.php/libvirt#UEFI_Support. Here are some
instructions:

* Install package ``ovmf``.
* Add the following statements to ``/etc/libvirt/qemu.conf``::

    nvram = [
        "/usr/share/ovmf/x64/OVMF_CODE.fd:/usr/share/ovmf/x64/OVMF_VARS.fd"
    ]

* Restart ``libvirtd`` (for example with ``systemctl restart libvirtd``).
* Run ``virsh edit windows_default`` (replacing ``windows_default`` with the
  name of the domain) and insert a ``<loader>`` tag into the ``<os>`` one.
  It should looks like:

  .. code-block:: xml

      <os>
        <type arch='x86_64' machine='pc-i440fx-3.0'>hvm</type>
        <loader readonly='yes' secure='no' type='rom'>/usr/share/ovmf/x64/OVMF_CODE.fd</loader>
        <boot dev='hd'/>
      </os>


First configuration
-------------------

By default the virtual machine won't be able to use the virtual network card as
it lacks the VirtIO network drivers. The suitable drivers are provided by Redhat
in a ``virtio-win`` package:
https://docs.fedoraproject.org/en-US/quick-docs/creating-windows-virtual-machines-using-virtio-drivers/

* Download the floppy disk of the drivers, https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/latest-virtio/virtio-win_amd64.vfd
* Power the virtual machine off and add the floppy drive to the VM   with
  ``virt-manager`` (GUI) or ``virsh edit windows_default`` (CLI)::

    <disk type='file' device='floppy'>
      <driver name='qemu' type='raw'/>
      <source file='/path/to/virtio-win_amd64.vfd'/>
      <target dev='fda'/>
      <readonly/>
      <address type='drive' controller='0' bus='0' target='0' unit='0'/>
    </disk>

* Then power the machine on (through Libvirt), open the Explorer (``Win`` +
  ``E``), go to directory ``A:\amd64\Win10\`` and install all ``.inf`` files.
  There are 3 drivers:

  - ``netkvm.inf`` for the Virtio Ethernet Adapter,
  - ``vioscsi.inf`` for the VirtIO SCSI pass-through controller,
  - ``viostor.inf`` for the VirtIO SCSI controller.

These commands install a French keyboard layout::

    PowerShell Set-WinUserLanguageList fr-FR,en-US
    PowerShell Get-WinUserLanguageList

Remote access
-------------

RDP connection
~~~~~~~~~~~~~~

In order to use the graphical interface, Vagrant supports using RDP (Remote
Desktop Protocol), using ``freerdp`` (``rdesktop`` can also be used if CredSSP
is disabled on the Windows virtual machine).
Before being able to connect, the RDP server needs to be started and the
firewall opened::

    PS C:\> Set-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections" -Value 0
    PS C:\> Enable-NetFirewallRule -DisplayGroup "Remote Desktop"

Then, one of these command should work (from a shell on the host):

.. code-block:: sh

    vagrant rdp
    xfreerdp /u:IEUser '/p:Passw0rd!' "/v:$(vagrant ssh-config | sed -n 's/ *HostName *//p'):3389"


Using WinRM
~~~~~~~~~~~

In order to use WinRM to connect to the machine, add the following information
to the ``Vagrantfile``::

    # Use Windows Remote Management protocol (WinRM)
    config.vm.communicator = "winrm"
    config.winrm.username = "IEUser"
    config.winrm.password = "Passw0rd!"

In a command-line prompt (eg. in ``vagrant ssh``), run::

    powershell -Command Enable-PSRemoting

If this commands fails with::

    WinRM is already set up to receive requests on this computer.
    Set-WSManQuickConfig : <f:WSManFault xmlns:f="http://schemas.microsoft.com/wbem/wsman/1/wsmanfault"
    Code="2150859113" Machine="localhost"><f:Message><f:ProviderFault provider="Config provider"
    path="%systemroot%\system32\WsmSvc.dll"><f:WSManFault
    xmlns:f="http://schemas.microsoft.com/wbem/wsman/1/wsmanfault" Code="2150859113"
    Machine="MSEDGEWIN10"><f:Message>WinRM firewall exception will not work since one of the network
    connection types on this machine is set to Public. Change the network connection type to either
    Domain or Private and try again. </f:Message></f:WSManFault></f:ProviderFault></f:Message>
    </f:WSManFault>
    At line:116 char:17
    +                 Set-WSManQuickConfig -force
    +                 ~~~~~~~~~~~~~~~~~~~~~~~~~~~
        + CategoryInfo          : InvalidOperation: (:) [Set-WSManQuickConfig], InvalidOperationException
        + FullyQualifiedErrorId : WsManError,Microsoft.WSMan.Management.SetWSManQuickConfigCommand

You need to change the network to a Private network. Here are some PowerShell
commands to perform this (cf. http://www.hurryupandwait.io/blog/fixing-winrm-firewall-exception-rule-not-working-when-internet-connection-type-is-set-to-public)::

    $networkListManager = [Activator]::CreateInstance([Type]::GetTypeFromCLSID([Guid]"{DCB00C01-570F-4A9B-8D69-199FDBA5723B}"))
    $connections = $networkListManager.GetNetworkConnections()

    # Set network location to Private for all networks
    $connections | % {$_.GetNetwork().SetCategory(1)}


Otherwise the output is::

    WinRM is already set up to receive requests on this computer.
    WinRM has been updated for remote management.
    WinRM firewall exception enabled.
    Configured LocalAccountTokenFilterPolicy to grant administrative rights remotely to local users.

Then::

    $ vagrant plugin install vagrant-winrm
    $ vagrant winrm -s cmd -c ipconfig

    Windows IP Configuration


    Ethernet adapter Ethernet 2:

       Connection-specific DNS Suffix  . :
       Link-local IPv6 Address . . . . . : fe80::40eb:b9c3:babb:31b5%4
       IPv4 Address. . . . . . . . . . . : 192.168.121.241
       Subnet Mask . . . . . . . . . . . : 255.255.255.0
       Default Gateway . . . . . . . . . : 192.168.121.1

    Tunnel adapter isatap.{8C624652-4727-4A10-9CC3-DC0C7E0177FB}:

       Media State . . . . . . . . . . . : Media disconnected
       Connection-specific DNS Suffix  . :

    Tunnel adapter Teredo Tunneling Pseudo-Interface:

       Connection-specific DNS Suffix  . :
       IPv6 Address. . . . . . . . . . . : 2001:0:9d38:6ab8:248d:f1e:b27a:31df
       Link-local IPv6 Address . . . . . : fe80::248d:f1e:b27a:31df%3
       Default Gateway . . . . . . . . . : ::

The Windows version can be gathered using this PowerShell command::

    PS C:\> systeminfo | Select-String "^OS Name","^OS Version"

    OS Name:                   Microsoft Windows 10 Enterprise Evaluation
    OS Version:                10.0.17134 N/A Build 17134

Or with::

    PS C:\> [System.Environment]::OSVersion

    Platform ServicePack Version      VersionString
    -------- ----------- -------      -------------
     Win32NT             10.0.17134.0 Microsoft Windows NT 10.0.17134.0


Install Windows OpenSSH server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since Windows 10 Fall Creators Update (1709 or 10.0.16299), Microsoft provides
OpenSSH client (installed by default) and server (installed on demand)::

    PS C:\> Get-WindowsCapability -Online | ? Name -like 'OpenSSH*'
    Name  : OpenSSH.Client~~~~0.0.1.0
    State : Installed

    Name  : OpenSSH.Server~~~~0.0.1.0
    State : NotPresent

These capabilities are available in the graphical interface in
"Settings/Apps/Apps & features/Manage optional features".
In order to install OpenSSH server, the following command can also be used::

    PS C:\> Add-WindowsCapability -Online -Name "OpenSSH.Server~~~~0.0.1.0"

If the install fails with error code ``0x80070002``, the issue was likely caused
by Windows Update service (e.g. it is not running, there are pending updates,
etc.). If this happens, check the state of Windows Update, reboot and try again.

OpenSSH server files are installed in ``C:\Windows\System32\OpenSSH`` (the
server is ``sshd.exe`` and the default configuration ``sshd_config_default``).

In order to use it, the firewall needs to be configured, if it is not already::

    PS C:\> Get-NetFirewallRule -DisplayName ssh
    Name                  : {4C9D3CE5-D9ED-42F1-95A3-1FEB069DBF34}
    DisplayName           : ssh
    Description           :
    DisplayGroup          :
    Group                 :
    Enabled               : True
    Profile               : Any
    Platform              : {}
    Direction             : Inbound
    Action                : Allow
    EdgeTraversalPolicy   : Block
    LooseSourceMapping    : False
    LocalOnlyMapping      : False
    Owner                 :
    PrimaryStatus         : OK
    Status                : The rule was parsed successfully from the store. (65536)
    EnforcementStatus     : NotApplicable
    PolicyStoreSource     : PersistentStore
    PolicyStoreSourceType : Local

    # If the above rule is not returned:
    PS C:\> New-NetFirewallRule -Protocol TCP -LocalPort 22 -Direction Inbound -Action Allow -DisplayName ssh

There are some services related to SSH (add ``| Format-list *`` to list more properties)::

    PS C:\> Get-Service | ? Name -like '*ssh*'
    Status   Name               DisplayName
    ------   ----               -----------
    Running  OpenSSHd           OpenSSH Server
    Stopped  ssh-agent          OpenSSH Authentication Agent
    Stopped  sshd               OpenSSH SSH Server

``OpenSSHd`` is the server provided by Cygwin, installed on Vagrant images by
Microsoft in ``C:\Program Files\OpenSSH\usr\sbin\sshd.exe`` (it comes from
https://www.mls-software.com/opensshd.html).
In order to switch to the native OpenSSH server (``sshd``)::

    PS C:\> Stop-Service -Name OpenSSHd
    PS C:\> Start-Service -Name sshd
    PS C:\> Set-Service -Name OpenSSHd -StartupType Disabled  # (or Manual)
    PS C:\> Set-Service -Name sshd -StartupType Automatic

    # Verify with: Get-Service | ? Name -like '*ssh*' | Format-List Status,StartType,Name,DisplayName

After the switch, the SSH prompt given by Vagrant becomes a real ``cmd.exe``::

    $ vagrant ssh
    IEUser@192.168.121.61's password:
    Microsoft Windows [Version 10.0.17134.345]
    (c) 2018 Microsoft Corporation. All rights reserved.

    ieuser@MSEDGEWIN10 C:\Users\IEUser>

In order to change the number of columns (ie. the line width)::

    C:\> mode con cols=80
    C:\> mode
    Status for device COM1:
    -----------------------
        Baud:            1200
        Parity:          None
        Data Bits:       7
        Stop Bits:       1
        Timeout:         OFF
        XON/XOFF:        OFF
        CTS handshaking: OFF
        DSR handshaking: OFF
        DSR sensitivity: OFF
        DTR circuit:     ON
        RTS circuit:     ON


    Status for device CON:
    ----------------------
        Lines:          9999
        Columns:        80
        Keyboard rate:  31
        Keyboard delay: 1
        Code page:      437

In order to authenticate with an RSA key generated by vagrant, the public key
needs to be written to ``C:\Users\IEUser\.ssh\authorized_keys``.
This public key can be provisioned with::

    $ ssh-keygen -y -f .vagrant/machines/default/libvirt/private_key | \
        ssh IEUser@$VMIP PowerShell "Read-Host > .ssh/authorized_keys"


Enable the Windows Subsystem for Linux
--------------------------------------

To install WSL (Windows Subsystem for Linux), run this command as Administrator::

    C:\> PowerShell Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux

    Path          :
    Online        : True
    RestartNeeded : True

After this command, the system automatically reboots.

In order to check whether WSL is installed::

    C:\> PowerShell Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux

    FeatureName      : Microsoft-Windows-Subsystem-Linux
    DisplayName      : Windows Subsystem for Linux
    Description      : Provides services and environments for running native user-mode Linux shells and tools on Windows.
    RestartRequired  : Possible
    State            : Enabled
    CustomProperties :
                       ServerComponent\Description : Provides services and environments for running native user-mode Linux
                       shells and tools on Windows.
                       ServerComponent\DisplayName : Windows Subsystem for Linux
                       ServerComponent\Id : 1033
                       ServerComponent\Type : Feature
                       ServerComponent\UniqueName : Microsoft-Windows-Subsystem-Linux
                       ServerComponent\Deploys\Update\Name : Microsoft-Windows-Subsystem-Linux

In order to install Ubuntu, the following PowerShell commands can be used::

    curl -L -o ubuntu-1804.appx https://aka.ms/wsl-ubuntu-1804
    # Or: Invoke-WebRequest -Uri https://aka.ms/wsl-ubuntu-1804 -OutFile Ubuntu-1804.appx -UseBasicParsing
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
    @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
    # For PowerShell
    Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

Chocolatey adds itself to ``%PATH%`` environment variable, and this can be
verified in the registry::

    PS C:\> Get-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment' -Name PATH
    # It should ends with C:\ProgramData\chocolatey\bin;

    # Or with cmd.exe:
    reg query "HKLM\System\CurrentControlSet\Control\Session Manager\Environment" /v PATH

Then, to install software::

    choco install notepadplusplus notepadplusplus.commandline -y
    choco install windbg -y
    # https://chocolatey.org/packages?q=sysinternals
    choco install procexp procmon autoruns psexec procdump adexplorer sigcheck dbgview winobj accesschk accessenum -y

    # MSys2 is installed in C:\tools\msys64
    choco install git python3 msys2 -y
    # Add 'PATH="$PATH:/c/Program Files/Git/cmd"' to C:/tools/msys64/home/IEUser/.bashrc
    # Launch MSys with C:/tools/msys64/usr/bin/bash.exe

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
PowerShell administrator console::

    git clone https://github.com/W4RH4WK/Debloat-Windows-10
    cd Debloat-Windows-10\scripts
    .\block-telemetry.ps1
    .\disable-services.ps1
    # .\disable-windows-defender.ps1
    # .\experimental_unfuckery.ps1 # Uncomment some apps there
    .\fix-privacy-settings.ps1
    .\optimize-user-interface.ps1
    .\optimize-windows-update.ps1
    .\remove-default-apps.ps1
    .\remove-onedrive.ps1
