Installing a Linux system
=========================

This document aims at providing the main steps in installing a Linux system.
When installing a specific Linux distribution, the documentation available on the distribution's wiki often provides very detailed steps:

* Arch Linux's installation guide: https://wiki.archlinux.org/index.php/installation_guide
* Gentoo's Handbook: https://wiki.gentoo.org/wiki/Handbook:AMD64#Installing_Gentoo

Booting a live media to a live system
-------------------------------------

The first steps of installing a Linux system consist in booting on a Linux system provided as a CD-ROM image (``.iso`` file) or as a live USB key image.
Such live media can also be created with tools such as:

* Fedora's Livemedia-creator (with Anaconda): https://fedoraproject.org/wiki/Livemedia-creator-_How_to_create_and_use_a_Live_CD
* UNetbootin: https://unetbootin.github.io/

Once booted using the live media, the keyboard layout needs to be configured:

.. code-block:: sh

    # Enumerate the available console keymaps, provided by:
    # * package kbd on Arch Linux
    # * package console-data on Debian
    ls /usr/share/kbd/keymaps/**/*.map.gz

    # Load a French keymap using loadkeys from:
    # * package kbd on Arch Linux
    # * package kbd on Debian
    loadkeys fr-latin9

For UEFI-based system, it is possible to verify that the live media has been booted in UEFI mode by enumerating the UEFI variables:

.. code-block:: sh

    ls /sys/firmware/efi/efivars

Then, it is possible to configure the network interfaces.
This greatly depends upon the network environment of the installed system.
Here are some commands to perform this:

.. code-block:: sh

    # Using DHCP
    dhclient eth0

    # Add an static IPv4 address for Ethernet interface eth0 and configure the DNS resolver
    ip addr add 192.168.0.2/24 dev eth0
    ip route add default via 192.168.0.1
    echo 'nameserver 192.168.0.1' >> /etc/resolv.conf

    # Check the connectivity with GitHub
    curl -v https://github.com

    # Enable time synchronization, on systemd-based distribution
    timedatectl set-ntp true


Partitioning the disks
----------------------

Once a live system is booted, the disks can be partitioned.
There does not exist a generic configuration that works for every possible computer: some could use software RAID with much swap, others do not need swap at all, etc.

One major differences between systems is the way a system boot:

* Legacy systems use BIOS with a MBR partition table.
  ``/boot`` can be split in its own partition but this is not mandatory.
* Newer systems use UEFI with a GPT partition table.
  This requires a ``EFI system partition`` which is nowadays the ``/boot`` partition.
  Allocating 400 MB for such a partition should be more than enough.

When installing GRUB boot manager on a UEFI system, an other dedicated partition needs to be created.
Allocating 200 MB to it should be enough.

Here are useful commands for this step:

.. code-block:: sh

    # Enumerate the available disks and partitions
    fdisk -l
    lsblk
    ls -l /sys/class/block
    ls -l /dev/disk/by-path

    # Create partitions on /dev/sda in an interactive way
    fdisk /dev/sda

    # Format the EFI system partition as FAT32
    mkfs.fat -F32 /dev/sda1

    # Format a partition as ext4
    mkfs.ext4 /dev/sda2

    # Format a partition as Swap
    mkswap /dev/sda2 && swapon /dev/sda2

    # Create an encrypted LUKS partition
    cryptsetup -v --cipher aes-xts-plain64 --key-size 512 luksFormat /dev/sda2
    cryptsetup open /dev/sda2 system
    mkfs.ext4 /dev/mapper/system

    # Rescan LVM partitions after a change has been made
    # (Physical Volumes, Volume Groups and Logical Volumes)
    vgchange --available y
    pvscan
    vgscan
    lvscan

    # Mount the partitions on /mnt
    mount /dev/mapper/system /mnt
    mount /dev/sda1 /mnt/boot

Some documentation:

* https://help.ubuntu.com/community/ResizeEncryptedPartitions


Installing a base system
------------------------

Once the disks are ready, bootstrapping a system is often achieved using one command specific to the distribution.

* Arch Linux use ``pacstrap``:

  .. code-block:: sh

      pacstrap /mnt base

* Debian-based system use ``debootstrap``:

  .. code-block:: sh

      debootstrap --arch amd64 stable /mnt

Once this is done, it is possible to ``chroot`` into the bootstrapped system.
Before that, the special directories need to be bind-mounted to the live system:

.. code-block:: sh

    mount --bind /dev /mnt/dev
    mount --bind /proc /mnt/proc
    mount --bind /sys /mnt/sys
    chroot /mnt

Arch Linux provides some helper scripts to minimize the number of commands to type:

.. code-block:: sh

    genfstab -U /mnt >> /mnt/etc/fstab
    arch-chroot /mnt


Configuring the base system before the first boot
-------------------------------------------------

Once chrooted into the newly-installed system while still being on the live system, a few things need to be configured.

.. code-block:: sh

    # Set the console keyboard layout at boot (French keymap is sometimes named fr-pc)
    echo 'KEYMAP=fr-latin9' > /etc/vconsole.conf

    # Configure the timezone
    ln -sf "/usr/share/zoneinfo/${TIMEZONE:-UTC}" /etc/localtime

    # Generate /etc/adjtime
    hwclock --systohc

    # Enable locales in /etc/locale.gen and generate then
    sed -i 's/^#\(en_GB.UTF-8 UTF-8\)/\1/' /etc/locale.gen
    ${EDITOR:-vim} /etc/locale.gen
    locale-gen
    echo 'LANG=en_GB.UTF-8' > /etc/locale.conf

    # Configure the hostname in /etc/hostname and /etc/hosts
    echo 'my-new-hostname' > /etc/hostname
    echo '127.0.1.1 my-new-hostname' > /etc/hosts

    # Set the root password
    passwd

    # Create a new user in group adm and with /home/user as $HOME
    # Options: -m to create home, -N no user group -G for admin groups
    useradd -mN -G adm,wheel user
    passwd user

    # Install a bootloader
    if $USING_GRUB ; then
        grub-mkconfig -o /boot/grub/grub.cfg
        grub-install /dev/sda
    fi
    if $USING_UEFI ; then
        cat >> /boot/loader/entries/00-arch-linux-hardened.conf
    title Arch Linux Hardened kernel
    linux /vmlinuz-linux-hardened
    initrd /intel-ucode.img
    initrd /initramfs-linux-hardened.img
    options root=UUID=...
    EOF

        # Install the systemd-boot EFI boot manager
        bootctl install
    fi

    # Install the needed firmware, for example for the network interface controller
    apt-get -y install firmware-linux-free  # on Debian
    pacman -S --noconfirm linux-firmware  # on Arch Linux

If the main system partition is encrypted, the initramfs needs to be regenerated.
The hooks need to be modified accordingly in ``/etc/mkinitcpio.conf``:

.. code-block:: sh

    # Initial line:
    #HOOKS=(base udev autodetect modconf block filesystems keyboard fsck)
    # New line:
    HOOKS=(base udev autodetect modconf block keymap keyboard encrypt filesystems fsck)

And run ``mkinitcpio -p linux``.
The kernel boot command line also needs to be adjusted to include information about the encrypted partition::

    root=UUID=xxxxxxxx-...-xxxxxxxxxxxx cryptdevice=/dev/disk/by-uuid/xxxxxxxx-...-xxxxxxxxxxxx:system

While at it, here are some other useful options::

    verbose loglevel=6 kaslr intel_iommu=on audit=1 security=selinux selinux=1

On a local system, it is a good idea to ensure that the USB-HID kernel modules (that handle the keyboard) are always loaded.
Otherwise, a USB keyboard cannot be used to enter the disk encryption passphrase upon boot...
It is also nice to ensure that the module for FAT filesystems is loaded, in order to be able to plug USB sticks even after disabling the module loading on the system.

.. code-block:: sh

    echo 'MODULES=(hid-generic vfat)' >> /etc/mkinitcpio.conf

If the system is remotely available through SSH, enable the server:

.. code-block:: sh

    # On Debian-based systems
    systemctl enable ssh
    # On Arch Linux
    systemctl enable sshd

If the system is a remote one and has an encrypted disk partition, remote unlocking can be achieved by embedding a Dropbear SSH server in the initramfs.
Such a configuration is detailed on https://wiki.archlinux.org/index.php/Dm-crypt/Specialties.


The last installation step
--------------------------

Finally, exit the chroot, unmount the system disks and reboot the system.
With this, the base system is installed and it is possible to install software, use them, etc.
A list of useful packages for some distributions is available on https://github.com/fishilico/shared/tree/master/machines/base_install.

It is also recommended to configure OpenSSH, sudo, sysctl, iptables, XScreenSaver, etc.
https://fishilico.github.io/generic-config/ provides some help in this regard.

On Debian-based systems, `<debian.rst>`_ (:doc:`debian`) provides also some advices.

On Arch Linux systems, `<archlinux-pkg.rst>`_ (:doc:`archlinux-pkg`) has some too.
Also, please add ``ILoveCandy`` in section ``[options]`` in ``/etc/pacman.conf`` ;)
