Windows Virtual Machine with Vagrant
====================================

Microsoft provides free Windows VM (which expire after 90 days) on
https://developer.microsoft.com/en-us/microsoft-edge/ .
Among the available VM are Vagrant machines. Here are instructions to setup
a Windows VM through Vagrant using Libvirt and QEmu-KVM as backend.

Create a libvirt box
--------------------

* Download a ZIP from https://developer.microsoft.com/en-us/microsoft-edge/tools/vms/, like
  https://az792536.vo.msecnd.net/vms/VMBuild_20180425/Vagrant/MSEdge/MSEdge.Win10.Vagrant.zip

  - Or pull the Vagrant image from https://app.vagrantup.com/Microsoft/boxes/EdgeOnWindows10

* Extract the box from the ZIP (it is named for example ``MSEdge - Win10.box``)::

    unzip MSEdge.Win10.Vagrant.zip

* Import the VirtualBox-Vagrant box and mutate it to use libvirt::

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

It will fail, because it needs to boot in UEFI mode and because the network
drivers are missing. For the network issue, the next section provides a way to
fix the issue. For UEFI boot, libvirt needs to be configured to support this
boot mode. For Arch Linux, this is documented in
https://wiki.archlinux.org/index.php/libvirt#UEFI_Support :

* Install package ``ovmf``.
* Add the following statements to ``/etc/libvirt/qemu.conf``::

    nvram = [
        "/usr/share/ovmf/x64/OVMF_CODE.fd:/usr/share/ovmf/x64/OVMF_VARS.fd"
    ]

* Restart libvirtd.
* Run ``virsh edit windows_default`` (replacing ``windows_default`` with the
  name of the domain) and insert a ``<loader>`` tag into the ``<os>`` one.
  It should looks like::

      <os>
        <type arch='x86_64' machine='pc-i440fx-3.0'>hvm</type>
        <loader readonly='yes' secure='no' type='rom'>/usr/share/ovmf/x64/OVMF_CODE.fd</loader
        <boot dev='hd'/>
      </os>



First configuration
-------------------

By default the virtual machine won't be able to use the virtual network card as
it lacks the VirtIO network drivers. The suitable drivers are provided by Redhat
in a ``virtio-win`` package:
https://docs.fedoraproject.org/en-US/quick-docs/creating-windows-virtual-machines-using-virtio-drivers/

* Download the floppy disk of the drivers, https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/latest-virtio/virtio-win_amd64.vfd
* Poweroff the virtual machine and add the floppy drive to the Virtual Machine,
  with virt-manager or ``virsh edit windows_default``::

    <disk type='file' device='floppy'>
      <driver name='qemu' type='raw'/>
      <source file='/path/to/virtio-win_amd64.vfd'/>
      <target dev='fda'/>
      <readonly/>
      <address type='drive' controller='0' bus='0' target='0' unit='0'/>
    </disk>

* Then power on the machine again through libvirt, open the Explorer (Win+E), go
  to directory ``A:\amd64\Win10\`` and install all ``.inf`` files. There are 3
  drivers:

  - ``netkvm.inf`` for the Virtio Ethernet Adapter,
  - ``vioscsi.inf`` for the VirtIO SCSI pass-through controller,
  - ``viostor.inf`` for the VirtIO SCSI controller.

Software to install
-------------------

Here is a list of software which can be useful in a Windows virtual machine:

* Notepad++: https://notepad-plus-plus.org/ (the sha1sums of the downloaded files can be verified)
* Windows Development Kits, debugger (WinDbg...):

  - https://developer.microsoft.com/en-us/windows/hardware/windows-driver-kit
  - Create a shortcut to ``C:\Program Files (x86)\Windows Kits\10\Debuggers\x64``

* msys2 environment: https://www.msys2.org/ , and install some software::

    PATH="/cygdrive/c/msys64/usr/bin:$PATH"
    pacman -Syu
    pacman -Sy git mingw-w64-x86_64-toolchain

* Python: https://www.python.org/downloads/windows/

* Some Sysinternals tools:

  - Process Explorer https://technet.microsoft.com/en-us/sysinternals/processexplorer
  - Process Monitor https://technet.microsoft.com/en-us/sysinternals/processmonitor
  - DebugView https://technet.microsoft.com/en-us/sysinternals/debugview
  - WinObj https://technet.microsoft.com/en-us/sysinternals/winobj
  - AccessEnum https://technet.microsoft.com/en-us/sysinternals/accessenum

Using WinRM
-----------

In order to use WinRM to connect to the machine, add the following information
to the ``Vagrantfile``::

    # Use Windows Remote Management protocol (WinRM)
    config.vm.communicator = "winrm"
    config.winrm.username = "IEUser"
    config.winrm.password = "Passw0rd!"

In a command-line prompt (eg. in ``vagrant ssh``) run::

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

Ensable the Windows Subsystem for Linux
---------------------------------------

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
