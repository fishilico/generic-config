QEmu-KVM notes
==============

This document contains some useful command lines to use QEmu to work with
virtual images.

Simple QEmu invocation commands
-------------------------------

The most simple QEmu usage consists in running a disk image or a liveCD/liveUSB
in a virtual machine, with a NAT network.  Here are some commands:

.. code-block:: sh

    # Run a LiveCD
    qemu-system-x86_64 -cdrom livecd.iso -boot d

    # Run a disk image with KVM acceleration, 1GB memory and 4 cores
    qemu-system-x86_64 -enable-kvm -m 1024M -cpu host -smp cores=4 disk-image.img

    # Run a kernel with a cow images and output its console on the current tty
    qemu-system-x86_64 -nographic \
        -drive file=image.qcow2,if=virtio \
        -kernel vmlinuz -initrd initrd.img \
        -append "root=/dev/vda1 console=ttyS0,16550A earlyprint=serial,ttyS0,16550A"

    # Boot in UEFI mode with a Tianocore UEFI firmware (from https://github.com/tianocore/edk2)
    qemu-system-x86_64 -bios /usr/share/ovmf/ovmf_x64.bin ...

    # Run a kernel with an initrd (made with "find . -print | cpio -o -Hcrc | gzip > ../initrd.img"
    # for example) on a KVM CPU, maybe booted from the network
    # (source https://lkml.org/lkml/2014/9/2/11)
    # By the way, to extract initrd images: "cat ../initrd.img | cpio -id"
    qemu-system-x86_64 -enable-kvm -cpu kvm64 -m 320 -smp 2 \
        -kernel vmlinux -initrd initrd.img \
        -net nic,vlan=1,model=e1000 -net user,vlan=1 -boot order=nc \
        -no-reboot -watchdog i6300esb -rtc base=localtime \
        -serial stdio -display none -monitor null \
        -append " \
            earlyprintk=ttyS0,115200 console=ttyS0,115200 console=tty0 \
            panic=-1 oops=panic vga=normal \
            load_ramdisk=2 prompt_ramdisk=0 root=/dev/ram0 rw"

    # Run an ARM kernel in a Versatile QEmu machine with a Raspberry-Pi-like CPU
    # (source http://web.archive.org/web/20150512213356/http://xecdesign.com/qemu-emulating-raspberry-pi-the-easy-way/)
    qemu-system-arm \
        -kernel kernel-qemu \
        -cpu arm1176 -m 256 \
        -machine versatilepb \
        -chardev socket,id=monitor,path=$(pwd)/monitor.sock,server,nowait \
        -monitor chardev:monitor \
        -hda rpiarch.qcow2 \
        -net nic -net user,hostname=raspberrypi \
        -serial pty -nographic -no-reboot \
        -append "root=/dev/sda rw rootfstype=ext4 panic=0 earlyprint=serial,ttyAMA0,38400 loglevel=7 console=ttyAMA0,38400 kgdboc=ttyAMA0,38400"

    # Run a MIPS kernel
    # (source https://doar-e.github.io/blog/2014/10/11/taiming-a-wild-nanomite-protected-mips-binary-with-symbolic-execution-no-such-crackme/)
    qemu-system-mipsel -M malta -kernel vmlinux-malta -hda root.qcow2 \
        -nographic -append "root=/dev/sda1 console=tty0"

Networking
----------

It is possible to run a virtual machine which only exposes some TCP ports
through local TCP redirections using the "user network" with options:

.. code-block:: sh

    # Redirect local host 2222 (on host) to guest SSH port (legacy parameters)
    -net nic -net user,hostname=myvm -redir tcp:2222::22

    # Or, more complex (recent parameters)
    -net nic,model=virtio,macaddr=52:54:00:12:34:56 -net user,hostfwd=tcp:127.0.0.1:2222-:22

To run a virtual machine with a tap interface which is bridged to a ``br0``
interface (created for example with ``brctl addbr br0``), here are commands
which can be used:

.. code-block:: sh

    # Old command: tunctl -u "$(id -nu)" -t tap_vm
    sudo ip tuntap add dev tap_vm mode tap user "$(id -nu)"
    trap "ip tuntap del dev tap_vm mode tap" EXIT HUP INT QUIT TERM
    sudo ip link set tap_vm up promisc on
    sudo brctl addif br0 tap_vm

The result of these commands can be checked with ``ip`` and ``brctl`` commands:

.. code-block:: sh

    $ ip link show tap_vm
    4: tap_vm: <NO-CARRIER,BROADCAST,MULTICAST,PROMISC,UP> mtu 1500 qdisc fq_codel
    master br0 state DOWN mode DEFAULT group default qlen 500
    link/ether 3a:d9:20:17:d3:c0 brd ff:ff:ff:ff:ff:ff

    $ brctl show br0
    bridge name bridge id               STP enabled     interfaces
    br0         8000.be2f28151bed       no              tap_vm

To add this new virtual interface to a QEmu virtual machine, these command-line
arguments can be used:

.. code-block:: sh

    -net nic,macaddr=$MAC -net tap,ifname=tap_vm,script=no,downscript=no

where ``$MAC`` is the MAC address to use, for example generated with:

.. code-block:: sh

     MAC=$(printf '52:54:%02x:%02x:%02x:%02x' $((RANDOM & 0xff)) $((RANDOM & 0xff)) \
        $((RANDOM & 0xff)) $((RANDOM & 0xff)))

Another possible choice of arguments is:

.. code-block:: sh

    -device virtio-net,netdev=tap,mac=$MAC
    -netdev type=tap,ifname=tap_vm,script=no,downscript=no,id=tap

QCow2 format and virtual disk usage
-----------------------------------

QEmu can use the QCow2 format for disks to efficiently store the data of virtual
disks (documentation: https://en.wikibooks.org/wiki/QEMU/Images).

To create a 10G disk image, the following command can be used:

.. code-block:: sh

    qemu-img create -f qcow2 virtual_disk.qcow2 10G

The resulting file weights 193KB and will expand once the disk image begins to
be filled with data.

The QCow2 images can not be directly mounted and an indirection layer needs to
be used to use such disks in a live system.  For example a kernel module can be
used, by issuing the following commands as root:

.. code-block:: sh

    modprobe nbd max_part=8
    qemu-nbd -c /dev/nbd0 virtual_disk.qcow2
    mount /dev/nbd0p1 /mnt
    ...
    umount /mnt
    qemu-nbd -d /dev/nbd0

This can be used to use the files stored on the virtual disk.  Another use when
the virtual disk is the root partition of a systemd-based system is to be able
to launch the system in a container, with:

.. code-block:: sh

    systemd-nspawn -D /mnt

NFS configuration
-----------------

To share files between a virtual machine and the host, it is possible to set
up and Network Filesystem (NFS) share.  Here is a sample configuration to share
``/srv/nfs/ro`` read-only and ``/srv/nfs/user-rw`` read-write, with writing
creating files for user 1000 group 100 on the host.  The virtual machine is
supposed to get an IP address in the 10.0.0.0/24 range, with the host having the
address 10.0.0.1.

On the host:

* Install ``nfs-utils`` package or something similar.
* Make sure ``/srv/nfs`` is accessible to everyone (if this directory is
  chmod-ed ``o-x``, NFS denies the access to the clients).
* Add in ``/etc/exports``:

.. code-block:: text

    /srv/nfs/ro 10.0.0.0/24(ro,sync)
    /srv/nfs/user-rw 10.0.0.0/24(rw,no_subtree_check,sync,anonuid=1000,anongid=100)

* Reload the currenlty exported entries:

.. code-block:: sh

    exportfs -arv

* Start the NFS services:

.. code-block:: sh

    systemctl start rpcbind.service nfs-server.service

* Open the ports in the firewall configuration:

.. code-block:: sh

    iptables -A INPUT -i br0 -p tcp -m multiport --dports 111,2049,20048,49367 -j ACCEPT
    iptables -A INPUT -i br0 -p udp -m multiport --dports 111,745,2049,20048,57797 -j ACCEPT

On the virtual machine:

* Install ``nfs-utils`` package or something similar.
* Check that the exported directory are accessible:

.. code-block:: sh

    showmount -e 10.0.0.1

* Mount the directories by hand:

.. code-block:: sh

    mount -t nfs 10.0.0.1:/srv/nfs/ro /mnt/ro -o ro
    mount -t nfs 10.0.0.1:/srv/nfs/user-rw /mnt/rw

* Here is the ``/etc/fstab`` configuration to automatically mount:

.. code-block:: text

    10.0.0.1:/srv/nfs/ro /mnt/ro nfs auto,ro,_netdev 0 0
    10.0.0.1:/srv/nfs/user-rw /mnt/rw nfs auto,rw,_netdev 0 0

9p shared directory
-------------------

Another way of sharing files between a guest and the host which is simpler than
NFS in its configuration is 9p.

This QEmu parameter shares the content of ``/var/vmsh`` on the host with the
guest:

.. code-block:: sh

    -virtfs local,id=fs0,mount_tag=vmsh,security_model=none,path=/var/vmsh

or:

.. code-block:: sh

    -fsdev local,id=fs0,security_model=none,path=/var/vmsh
    -device virtio-9p-pci,fsdev=fs0,mount_tag=vmsh

On the guest, ``/etc/fstab`` may contain the following line to mount the shared
directory on ``/mnt/vmsh``:

.. code-block:: text

    vmsh /mnt/vmsh 9p auto,trans=virtio,version=9p2000.L,_netdev 0 0

Interaction based on Unix sockets
---------------------------------

QEmu virtual machines are usually used either in graphical mode, with a QEmu
windown, or in console mode (``-nographic`` option), with a serial console
redirected to the standard input/output. A third alternative consists in using
Unix sockets to communicate with the guest. This can be achieved with two QEmu
options:

.. code-block:: sh

    -monitor unix:monitor.sock,server,nowait
    -serial unix:console.sock,server,nowait

If the guest machine runs Linux, the virtual serial port will be available
through device ``ttyS0``.  It can be used as a console with early kernel
messages with these kernel command line parameters:

.. code-block:: sh

    console=ttyS0,38400n8 earlyprint=serial,ttyS0,38400n8

If the guest machine runs systemd, it is possible to automatically spawn a
login shell on the serial port with the following command:

.. code-block:: sh

    systemctl enable serial-getty@ttyS0.service

Then it is possible to:

* connect to QEmu monitor console for example with:

.. code-block:: sh

    # Use cfmakeraw to make TAB work and isig=1 to allow using Ctrl+C
    socat STDIO,cfmakeraw,isig=1 UNIX:monitor.sock

    # socat<1.7.3.0 does not support cfmakeraw. Use raw instead
    socat STDIO,raw,echo=0,isig=1 UNIX:monitor.sock

* connect to QEmu guest console for example with:

.. code-block:: sh

    socat STDIO,cfmakeraw UNIX:console.sock

    # or, with socat<1.7.3.0
    socat STDIO,raw,echo=0 UNIX:console.sock

Other QEmu options
------------------

Here are some options which may be useful when invoking QEmu:

* ``-cpu kvm64``: use KVM virtual CPU, not the one of the host.
* ``-machine accel=kvm``: use KVM for acceleration.
* ``-rtc base=localtime``: use localtime for the emulated hardware clock.
* ``-nographic -serial stdio -display none -monitor null``: output the console
  of the guest on the standard output of the terminal which is used to launch
  QEmu.
* ``-chardev stdio,id=stdio,mux=on -device virtio-serial -device virtserialport,chardev=stdio,name=qemu.stdio``:
  Create a virtual device in the guest, ``/dev/virtio-ports/qemu.stdio``, which
  can be used to read and write messages to the input and output stream of the
  QEmu process.
* ``-chardev stdio,id=stdio,mux=on,signal=off -device virtio-serial-pci -device virtconsole,chardev=stdio -mon chardev=stdio``:
  Multiplex the console and the monitor on stdio (``Ctrl-A h`` for help)

QEmu-static chroot
------------------

To run programs from a foreign CPU architecture without building a virtual
machine, it is possible to setup a chroot environment with QEmu emulation.

For this, the ``qemu-user-static`` binaries are needed
(https://packages.debian.org/sid/qemu-user-static).  Then ``binfmt`` needs to
be configured so that Linux launches these programs when trying to execute
binaries for foreign architectures.

For example, for ARM ELF binaries, this can be done by writing this in
``/etc/binfmt.d/qemu-arm.conf``, on one line:

.. code-block:: text

    :arm:M::\x7fELF\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x28\x00:
    \xff\xff\xff\xff\xff\xff\xff\x00\xff\xff\xff\xff\xff\xff\xff\xff\xfe\xff\xff\xff:
    /usr/bin/qemu-arm-static:C

or by writting this directly into ``/proc/sys/fs/binfmt_misc/register``.  If
this succeeds, ``/proc/sys/fs/binfmt_misc/arm`` file would have been created
with the following content:

.. code-block:: text

    enabled
    interpreter /usr/bin/qemu-arm-static
    flags: OC
    offset 0
    magic 7f454c4601010100000000000000000002002800
    mask ffffffffffffff00fffffffffffffffffeffffff

Once this is configured, an ARM QEmu-static chroot can be built by:

* creating a base chroot (with ``debootstrap`` for Debian, ``pacstrap`` for
  Arch Linux), and
* copying ``/usr/bin/qemu-arm-static`` in the ``/usr/bin`` directory of the
  chroot.

On debian, there also exists command ``qemu-debootstrap``:

.. code-block:: sh

    apt-get install qemu qemu-user-static qemu-utils binfmt-support debootstrap

    # arm64 for ARMv8
    qemu-debootstrap --arch=arm64 sid /opt/arm64/ http://ftp.debian.org/debian

    # armhf for ARMv7 (hardware floating-point)
    qemu-debootstrap --arch=armhf sid /opt/armhf/ http://ftp.debian.org/debian

    # armel for ARMv4 (software floating-point, Little Endian)
    qemu-debootstrap --arch=armel sid /opt/armel/ http://ftp.debian.org/debian


This allows using usual programs but some have some issues running with
``qemu-user-static``, like ``strace`` because the ``ptrace`` syscall is not
implemented.  Nevertheless ``qemu-user-static`` has an option to show the
system calls which are emulated, so a simple work-around consists in creating
a ``strace`` shell script for example in ``/usr/local/bin`` in the chroot with:

.. code-block:: sh

    #!/bin/sh
    exec qemu-arm-static -strace "$@"

Libvirt integration
-------------------

Libvirt can be used to managed virtual machines. Some commands:

.. code-block:: sh

    # List all known virtual machines (domains)
    # This command may need to be run as root
    virsh list --all

    # Edit the XML configuration of a domain
    virsh edit <domain>

    # Start a domain
    virsh start <domain>

virt-manager can also be used as a graphical interface to interact with virtual
machines (by default in ``qemu://system`` connection).

When starting, libvirt sets up a network bridge, ``virbr0``, with an associated
dnsmasq process to attribute IP addresses. This default network is configured
with ``virsh net-edit default``. It looks like:

.. code-block:: xml

    <network>
      <name>default</name>
      <uuid>bb24f0ba-754c-4f00-b16b-5e7dbb35807e</uuid>
      <forward mode='nat'/>
      <bridge name='virbr0' stp='on' delay='0'/>
      <mac address='52:54:00:12:34:56'/>
      <ip address='192.168.122.1' netmask='255.255.255.0'>
        <dhcp>
          <range start='192.168.122.2' end='192.168.122.254'/>
          <!-- Static IP addresses -->
          <host mac='52:54:00:11:22:33' name='vm1' ip='192.168.122.11'/>
        </dhcp>
      </ip>
    </network>

The generated dnsmasq configuration is in ``/var/lib/libvirt/dnsmasq/default.conf``.

Web links
---------

Here are some links to online articles and documentation relevant with QEmu:

* http://wiki.qemu.org/Testing QEmu testing images
* https://wiki.archlinux.org/index.php/QEMU ArchLinux wiki entry
* http://debian-handbook.info/browse/stable/sect.virtualization.html
    Virtualization -- The Debian Administrator's Handbook

* https://blog.nelhage.com/2013/12/lightweight-linux-kernel-development-with-kvm/
* http://blog.oddbit.com/2014/07/21/tracking-down-a-kernel-bug-wit/
* https://www.berrange.com/posts/2011/06/07/what-benefits-does-libvirt-offer-to-developers-targetting-qemukvm/
  (This article explains what libvirt does)

* https://wiki.debian.org/QemuUserEmulation
  How to setup and use QEMU user emulation in a "transparent" fashion
* https://github.com/ixty/xarch_shellcode/blob/master/README.md
  Build portable, architecture independant shellcode from C code

A quick glance at Docker
------------------------

Docker is known for being able to run containers. It is also good for spawning
short-lived well-controlled environment like a fresh Ubuntu Precise (12.04 LTS)
install:

.. code-block:: sh

    docker run -t -i ubuntu:12.04 /bin/bash

To list images:

.. code-block:: sh

    docker images

To list containers:

.. code-block:: sh

    docker ps -l
