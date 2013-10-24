Some notes about my SELinux installation
========================================

This document doesn't document how to install SELinux. If you want to install
it, please read one of these websites:

- https://wiki.debian.org/SELinux
- https://wiki.gentoo.org/wiki/SELinux/Tutorials
- https://fedoraproject.org/wiki/SELinux

Other websites useful to be bookmarked:

- http://oss.tresys.com/docs/refpolicy/api/ (reference policy API)
- http://oss.tresys.com/projects/refpolicy/log/ (git log)
- https://wiki.gentoo.org/wiki/Project:SELinux/Development
- http://www.selinuxproject.org/page/ObjectClassesPerms
- http://git.overlays.gentoo.org/gitweb/?p=proj/hardened-refpolicy.git;a=summary


Install a strict policy
-----------------------

On Debian by default a targeted policy is installed, daemons are confined but
not users. To make users confined, you need to remove the unconfined module.
To do this:

- Set up staff accounts::

    semanage login -a -s staff_u userlogin

- Confine users::

    semanage login -m -s user_u -r s0 __default__

- Map ``root`` to ``root`` instead of ``unconfined_u``::

    semanage login -m -s root root

- Remove the ``unconfined`` module::

    semodule -r unconfined


Fix ``/tmp`` labeling
---------------------

If ``mount`` shows::

    tmpfs on /tmp type tmpfs (rw,nosuid,nodev,relatime,rootcontext=system_u:object_r:file_t:s0,seclabel)

... or if ``ls -Zd /tmp`` shows::

    system_u:object_r:file_t:SystemLow /tmp

... the filesystem is incorrectly labeled.

To fix this bug, you need to restore the context of the ``/tmp`` folder of the
root filesystem to ``system_u:object_r:tmpfs_t:s0``::

    mount --bind / /mnt
    setfiles -r /mnt /etc/selinux/default/contexts/files/file_contexts /mnt
    umount /mnt

Also make sure your ``/etc/fstab`` contains this line::

    tmpfs /tmp tmpfs nodev,nosuid,rootcontext=system_u:object_r:tmp_t:s0 0 0


Configure SELinux booleans
--------------------------

Here are some booleans I use is almost all my SELinux system::

    # Allow users to send ping
    setsebool -P user_ping on

    # Enable reading of urandom for all domains
    setsebool -P global_ssp on

    # Use CGI with nginx (eg. for gitweb)
    setsebool -P httpd_enable_cgi on
    setsebool -P nginx_enable_http_server on

    # Make GPG agent to work
    setsebool -P gpg_agent_env_file on

    # Disable NX memory protection for some applications (eg. Firefox)
    setsebool -P allow_execmem on

    # Print logs on some tty (like tty12)
    setsebool -P logging_syslogd_use_tty on

Fix labels for files in /home
-----------------------------

By default, files under ``/home`` are labeled as user home directories. On some
system, ``/home`` is on the largest disk partition and there are other things,
like database files (instead of ``/var/lib/...`` folders) or Git repositories.
For such folders, you must a command like this to specify the real file context
to use::

    semanage fcontext -a -t httpd_sys_content_t "/home/git(/.*)?"


Activate some SELinux modules
-----------------------------

To reload modules, go to ``/usr/share/selinux/$(policyname)`` and run::

    semodule --verbose -b base.pp -s $(basename $(pwd)) -n -i module1.pp -i ...

Here are the modules from the Reference policy which are active on my Debian desktop system:

    accountsd
    apache
    application
    apt
    authlogin
    avahi
    clock
    consolekit
    cron
    dbus
    devicekit
    dhcp
    dmidecode
    dnsmasq
    dpkg
    fstools
    ftp
    getty
    git
    gpg
    gpm
    hddtemp
    hostname
    hotplug
    inetd
    init
    iptables
    kerberos
    lda
    libraries
    loadkeys
    locallogin
    logging
    logrotate
    lpd
    lvm
    miscfiles
    modutils
    mount
    mozilla
    mpd
    mplayer
    mta
    netlabel
    netutils
    networkmanager
    ntp
    policykit
    postfix
    postgresql
    ptchown
    pulseaudio
    pythonsupport
    radvd
    remotelogin
    rsync
    rtkit
    screen
    selinuxutil
    setrans
    ssh
    staff
    storage
    sudo
    sysadm
    sysnetwork
    systemd
    timidity
    tzdata
    udev
    unprivuser
    usbmodules
    usbmuxd
    userdomain
    usermanage
    vbetool
    wireshark
    wm
    xscreensaver
    xserver


Allow ``staff_u`` to read ``/root`` when running ``sudo``
---------------------------------------------------------

By default ``/etc/selinux/default/modules/active/file_contexts.homedirs``
defines ``/root`` to be labeled ``root:object_r:user_home_t``, which ``staff_u``
can't access (there is a constraint for it). To solve this issue, change the
constraint or (much sumpler) change the user associated to ``root``::

    chcon -u staff_u /root -R


Bugs still present in September 2013
------------------------------------

In ArchLinux, ``/sys`` is not labelled correctly on boot. It needs to be labeled
by systemd using ``tmpfiles.d`` configuration. Therefore you need to add this in
``/etc/tmpfiles.d/sysfs.conf``::

    Z /sys/devices/system/cpu/online 0444 root root

For further information, please read:

- https://bugzilla.redhat.com/show_bug.cgi?id=767355
- http://www.spinics.net/lists/selinux/msg11684.html
