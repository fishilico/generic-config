Windows Virtual Machine with Vagrant
====================================

Microsoft provides free Windows VM (which expire after 90 days) on
https://developer.microsoft.com/en-us/microsoft-edge/ .
Among the available VM are Vagrant machines. Here are instructions to setup
a Windows VM through Vagrant using Libvirt and QEmu-KVM as backend.

Create a libvirt box
--------------------

* Download a ZIP from https://developer.microsoft.com/en-us/microsoft-edge/tools/vms/, like
  https://az792536.vo.msecnd.net/vms/VMBuild_20160810/Vagrant/MSEdge/MSEdge.Win10_RS1.Vagrant.zip

* Extract the box from the ZIP (it is named for example ``dev-msedge.box``::

    unzip MSEdge.Win10_RS1.Vagrant.zip

* Import the VirtualBox-Vagrant box and mutate it to use libvirt::

    vagrant plugin install vagrant-mutate
    vagrant box add windows/win10-edge dev-msedge.box
    vagrant mutate windows/win10-edge libvirt
    vagrant box remove --provider virtualbox windows/win10-edge

  The mutate command will use ``qemu-img convert -p -S 16k -o compat=1.1 -O qcow2 ...``
  to convert the virtual box disk to a QEmu-compatible one.

* Initialize a new Vagrant box in the current directory::

    vagrant init windows/win10-edge

* Configure the box by adding the following lines to ``Vagrantfile`` before the final ``end``::

    # Configure remote access
    config.ssh.username = "IEUser"
    config.ssh.password = "Passw0rd!"

    # Use 2GB of memory
    config.vm.provider :libvirt do |v|
      v.memory = 2048
    end

* Start the new box::

    vagrant up --provider libvirt --no-destroy-on-error

First configuration
-------------------

By default the virtual machine won't be able to use the virtual network card as
it lacks the VirtIO network drivers. The suitable drivers are provided by Redhat
in a ``virtio-win`` package: https://fedoraproject.org/wiki/Windows_Virtio_Drivers.

* Download the floppy disk of the drivers, https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/latest-virtio/virtio-win_amd64.vfd
* Poweroff the virtual machine and add the floppy drive to the Virtual Machine,
  with virt-manager or ``virsh edit windows_default``::

    <disk type='file' device='floppy'>
        <source file='/path/to/virtio-win_amd64.vfd'/>
        <target dev='fda'/>
    </disk>

* Then power the machine on again through Libvirt, open the Explorer (Win+E), go
  to ``A:\amd64\Win10\`` directory and install all ``.inf`` files. There are 3
  drivers:

  - ``netkvm.inf`` for the Virtio Ethernet Adapter,
  - ``vioscsi.inf`` for the VirtIO SCSI pass-through controller,
  - ``viostor.inf`` for the VirtIO SCSI controller.

Software to install
-------------------

Here is a list of software which can be useful in a Windows virtual machine:

* Notepad++: https://notepad-plus-plus.org/ (the sha1sums of the downloaded files can be verified)
* Windows Development Kits, debugger (WinDbg)...: https://developer.microsoft.com/en-us/windows/hardware/windows-driver-kit

    - Create a shortcut to ``C:\Program Files (x86)\Windows Kits\10\Debuggers\x64``

* msys2 environment: https://msys2.github.io/ , and install some software::

    PATH="/cygdrive/c/msys64/usr/bin:$PATH"
    pacman -Syu
    pacman -Sy git mingw-w64-x86_64-toolchain

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

    # Use Windows Remote Management protocol
    config.vm.communicator = "winrm"
    config.winrm.username = "IEUser"
    config.winrm.password = "Passw0rd!"

In a command-line prompt (eg. in ``vagrant ssh``) run::

    powershell -Command Enable-PSRemoting

If this commands fails with::

    WinRM is already set up to receive requests on this computer.
    Set-WSManQuickConfig : <f:WSManFault xmlns:f="http://schemas.microsoft.com/wbem/wsman/1/wsmanfault" Code="2150859113" 
    Machine="localhost"><f:Message><f:ProviderFault provider="Config provider" 
    path="%systemroot%\system32\WsmSvc.dll"><f:WSManFault xmlns:f="http://schemas.microsoft.com/wbem/wsman/1/wsmanfault" 
    Code="2150859113" Machine="MSEDGEWIN10"><f:Message>WinRM firewall exception will not work since one of the network 
    connection types on this machine is set to Public. Change the network connection type to either Domain or Private and 
    try again. </f:Message></f:WSManFault></f:ProviderFault></f:Message></f:WSManFault>
    At line:116 char:17
    +                 Set-WSManQuickConfig -force
    +                 ~~~~~~~~~~~~~~~~~~~~~~~~~~~
        + CategoryInfo          : InvalidOperation: (:) [Set-WSManQuickConfig], InvalidOperationException
        + FullyQualifiedErrorId : WsManError,Microsoft.WSMan.Management.SetWSManQuickConfigCommand

You need to change the network to a Private network (cf. for example
http://www.hurryupandwait.io/blog/fixing-winrm-firewall-exception-rule-not-working-when-internet-connection-type-is-set-to-public).
Otherwise the output is::

    WinRM is already set up to receive requests on this computer.
    WinRM is already set up for remote management on this computer.

Then::

    $ vagrant install vagrant-winrm
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

