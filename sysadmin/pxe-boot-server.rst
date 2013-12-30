Configure a server to handle network boot (PXE)
===============================================

*PXE* (Pre-Execution Environment) is a way to boot a computer which can't boot
from a physical drive (CD, DVD, USB). The computer gets an IP address from the
network using DHCP and then download a PXE image from a TFTP (Trivial File
Transfer Protocol) server. On Linux, Dnsmasq does all the networking stuff and
Syslinux provides a PXE image. The LiveCD of any GNU/Linux distribution contains
configuration files for Syslinux and a compressed file system which can be used
by network boot.

Example
-------

1- Configure the PXE server network (IP address, DNS...) and make it up and
running.

2- Uncompress or mount an ISO image of an Ubuntu LiveCD to ``/tmp/iso``.
This may work too with other distributions, but this example has only been
tested with Ubuntu.

3- Prepare a TFTP directory:

.. code-block:: sh

    mkdir -p /srv/tftpboot
    cp -a /tmp/iso/isolinux/* /srv/tftpboot/
    mkdir /srv/tftpboot/pxelinux.cfg
    mv /srv/tftpboot/isolinux.cfg /srv/tftpboot/pxelinux.cfg/default

    cp -r /tmp/iso/casper /src/tftpboot

    # This requires Syslinux to be installed
    cp /usr/lib/syslinux/pxelinux.0 /srv/tftpboot

4- Configure DNSMasq to be both a DHCP server and a TFTP one. To do so, edit
``/etc/dnsmasq.conf``::

    # Uncomment following line if you want to restrict to one interface
    #interface=eth0
    dhcp-range=192.168.0.50,192.168.0.150,12h
    dhcp-boot=pxelinux.0
    enable-tftp
    tftp-root=/srv/tftpboot

5- (Re)Start Dnsmasq service and enjoy your PXE server !


Debian network installation
---------------------------

Debian provides files on its FTP mirrors which can be used to set up a PXE
server to boot Debian netinstall.

* 32-bit version:
  ftp://ftp.debian.org/debian/dists/stable/main/installer-i386/current/images/netboot/debian-installer/i386/
* 64-bit version:
  ftp://ftp.debian.org/debian/dists/stable/main/installer-amd64/current/images/netboot/debian-installer/amd64/

On this FTP, only ``initrd.gz``, ``linux`` and ``pxelinux.0`` are really useful.
``pxelinux.cfg/default`` can be rewritten in a much simpler version::

    DEFAULT linux
    LABEL linux
        kernel linux
        append vga=normal initrd=initrd.gz --
    TIMEOUT 0
