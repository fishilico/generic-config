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
