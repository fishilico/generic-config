Configuration tweaks on a Raspberry Pi
======================================

Raspbian installation
---------------------

Download Raspbian image from http://www.raspberrypi.org/downloads.

Each time the SD card is mounted and files modified, ``/etc/fake-hwtime`` or
``/etc/fake-hwclock.data`` needs to be updated with current date and time in
``YYYY-MM-DD HH:MM:SS`` format. Otherwise the system may experience some
timing-related issues (and fails to mount the root filesystem).
This can be done with::

    date '+%Y-%m-%d %H:%M:%S' > /etc/fake-hwclock.data

You may run the system on the SD card in QEMU if you don't have an HDMI screen.
http://xecdesign.com/qemu-emulating-raspberry-pi-the-easy-way/ describes how to
achieve that, by downloading a special kernel of qemu-arm and running:

.. code-block:: sh

    qemu-system-arm -kernel kernel-qemu -cpu arm1176 -m 256 -M versatilepb \
        -no-reboot -serial stdio -append "root=/dev/sda2 panic=1" -hda /dev/sdb

This kernel has been compiled with instructions written on
http://xecdesign.com/compiling-a-kernel/.  It is configured to build a kernel
for an ARM11 (ARMv6) versatile board, which requires a patch to be applied:
http://xecdesign.com/downloads/linux-qemu/linux-arm.patch


Post-install configuration
--------------------------

Like all Debian systems, some files needs updating after the initial setup:

* ``/etc/mailname`` (with the name to be used in mailing)
* ``/etc/sudoers`` (remove ``pi ALL=(ALL) NOPASSWD: ALL``)
* ``/etc/ntp.conf`` (remove ``restrict ::1`` if IPv6 module is not loaded)
* Reconfigure the keyboard: ``keyboard-configuration``
* Change timezone: ``tzselect`` (``TZ='Europe/Paris'; export TZ``)

Moreover, ``/etc/sysctl.conf`` contains Raspberry Pi-specific configuration::

    # rpi tweaks
    vm.swappiness=1
    vm.min_free_kbytes = 8192


Networking
----------

``/etc/network/interfaces`` with a dynamic configuration::

    auto lo
    # Add contents:
    allow-hotplug eth0

    iface lo inet loopback
    iface eth0 inet dhcp

    allow-hotplug wlan0
    iface wlan0 inet manual
    wpa-roam /etc/wpa_supplicant/wpa_supplicant.conf
    iface default inet dhcp

Static configuration may be used with the following lines::

    iface eth0 inet static
        address 192.0.2.2
        netmask 255.255.255.0
        gateway 192.0.2.1


Enable IPv6
-----------

To enable IPv6, use the following commands:

.. code-block:: sh

    modprobe ipv6
    sysctl -w net.ipv6.conf.default.use_tempaddr=2
    sysctl -w net.ipv6.conf.all.use_tempaddr=2

To make these changes persistent, add ``ipv6`` to ``/etc/modules`` and
``net.ipv6.conf.default.use_tempaddr = 2`` to ``/etc/sysctl.conf``.


Some useful system information
------------------------------

Here are the outputs of several commands to retrieve system information on a
Raspberry Pi, model B.

* As some people consider a Serial Number and a MAC address as being sensitive
  information, each potential sensitive hexadecimal byte has been replaced here
  by ``XX``.
* Information about used kernel is not relevant here. So these outputs don't
  include kernel version and kernel pointers have been protected
  (``sysctl -w kernel.kptr_restrict=2``).
* Address space is randomized (ALSR, ``sysctl -w kernel.randomize_va_space=2``)
  so when dumping ``/proc/*/maps``, random parts of addresses have been
  replaced by ``X``.

::

    $ uname -m
    armv6l

    $ cat /proc/cpuinfo
    processor   : 0
    model name  : ARMv6-compatible processor rev 7 (v6l)
    BogoMIPS    : 2.00
    Features    : swp half thumb fastmult vfp edsp java tls
    CPU implementer : 0x41
    CPU architecture: 7
    CPU variant : 0x0
    CPU part    : 0xb76
    CPU revision    : 7

    Hardware    : BCM2708
    Revision    : 000f
    Serial      : 00000000XXXXXXXX

    $ cat /proc/cmdline | fmt -80
    dma.dmachans=0x7f35 bcm2708_fb.fbwidth=656
    bcm2708_fb.fbheight=416 bcm2708.boardrev=0xf bcm2708.serial=0xXXXXXXXX
    smsc95xx.macaddr=B8:27:XX:XX:XX:XX sdhci-bcm2708.emmc_clock_freq=100000000
    vc_mem.mem_base=0x1ec00000 vc_mem.mem_size=0x20000000  dwc_otg.lpm_enable=0
    console=ttyAMA0,115200 kgdboc=ttyAMA0,115200 console=tty1 root=/dev/mmcblk0p2
    rootfstype=ext4 elevator=deadline rootwait

    $ cat /proc/modules
    ipv6 278186 32 - Live 0x00000000
    snd_bcm2835 16304 0 - Live 0x00000000
    snd_pcm 77560 1 snd_bcm2835, Live 0x00000000
    snd_seq 53329 0 - Live 0x00000000
    snd_timer 19998 2 snd_pcm,snd_seq, Live 0x00000000
    snd_seq_device 6438 1 snd_seq, Live 0x00000000
    snd 58447 5 snd_bcm2835,snd_pcm,snd_seq,snd_timer,snd_seq_device, Live 0x00000000
    snd_page_alloc 5145 1 snd_pcm, Live 0x00000000
    leds_gpio 2235 0 - Live 0x00000000
    led_class 3562 1 leds_gpio, Live 0x00000000

    $ gcc -E -v - < /dev/null 2>&1 | grep cc1 | fmt -80
    /usr/lib/gcc/arm-linux-gnueabihf/4.6/cc1 -E -quiet -v -imultilib
    . -imultiarch arm-linux-gnueabihf - -march=armv6 -mfloat-abi=hard -mfpu=vfp

    $ cat /proc/self/maps | tail -n2
    beXXX000-beXXX000 rw-p 00000000 00:00 0          [stack]
    ffff0000-ffff1000 r-xp 00000000 00:00 0          [vectors]

    $ lsusb
    Bus 001 Device 002: ID 0424:9512 Standard Microsystems Corp.
    Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
    Bus 001 Device 003: ID 0424:ec00 Standard Microsystems Corp.

    $ readlink /sys/class/net/eth0
    ../../devices/platform/bcm2708_usb/usb1/1-1/1-1.1/1-1.1:1.0/net/eth0
    $ readlink /sys/devices/platform/bcm2708_usb/usb1/1-1/1-1.1/1-1.1:1.0/driver
    ../../../../../../../bus/usb/drivers/smsc95xx
    $ dmesg | grep eth0 | head -n1 | tail -c+16
    smsc95xx 1-1.1:1.0: eth0: register 'smsc95xx' at usb-bcm2708_usb-1.1, smsc95xx USB 2.0 Ethernet, b8:27:XX:XX:XX:XX

    $ lshw | fmt -80 -s
    raspberrypi
        description: Computer
        width: 32 bits
      *-core
           description: Motherboard
           physical id: 0
         *-memory
              description: System memory
              physical id: 0
              size: 438MiB
         *-cpu
              physical id: 1
              bus info: cpu@0
              size: 700MHz
              capacity: 700MHz
              capabilities: cpufreq
      *-network
           description: Ethernet interface
           physical id: 1
           logical name: eth0
           serial: b8:27:XX:XX:XX:XX
           size: 100Mbit/s
           capacity: 100Mbit/s
           capabilities: ethernet physical tp mii 10bt 10bt-fd 100bt 100bt-fd
           autonegotiation
           configuration: autonegotiation=on broadcast=yes driver=smsc95xx
           driverversion=22-Aug-2005 duplex=full firmware=smsc95xx USB 2.0
           Ethernet ip=192.0.2.42 link=yes multicast=yes port=MII speed=100Mbit/s
