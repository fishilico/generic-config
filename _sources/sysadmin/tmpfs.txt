Use tmpfs for some directories
==============================

On my hosts I configure some directories to be tmpfs mountpoint to save disk
writes, which is very important when using SSD drives. Here is how to do so.

``/tmp``
--------

Here is what I usually put in my ``/etc/fstab``::

    # <file system> <dir> <type> <options>            <dump> <pass>
    tmpfs           /tmp  tmpfs  nodev,nosuid,noexec  0      0

``$HOME/.cache``
----------------

Example of ``/etc/fstab`` entry for user's ``.cache`` home subdirectory::

    $USER.cache $HOME/.cache tmpfs defaults,auto,nodev,noexec,nosuid,size=2048M,gid=100,uid=1000,mode=0700 0 0

As ``.cache/pacaur`` is intended to persist accross reboots, this directory can
be set up as a bind-mount::

    $HOME/.cache.pacaur $HOME/.cache/pacaur none bind 0 0

Yaourt build dir on ArchLinux
-----------------------------

To build AUR packaes, yaourt uses ``/tmp/yaourt-tmp-$USER``. To make this
directory a tmpfs mountpoint the time of a build, add the following line to
``/etc/fstab``::

    $USER.yaourt /tmp/yaourt-tmp-$USER tmpfs defaults,user,noauto,nodev,exec,nosuid,gid=$GID,uid=$UID,mode=0700 0 0

Then, create (if needed) and mount ``/tmp/yaourt-tmp-$USER`` before running
yaourt.

Other directories
-----------------

Here are some entries which may be written into ``/etc/fstab``::

    # Web browser downloads
    $HOME/Downloads/tmp tmpfs defaults,auto,nodev,nosuid,exec,gid=$GID,uid=$UID,mode=0700,rootcontext=$(getfattr --only-values -n security.selinux $HOME/Downloads) 0 0

    # makepkg build directory (modify BUILDDIR=/tmp/makepkg-$USER in /etc/makepkg.conf)
    $USER.yaourt /tmp/makepkg-$USER tmpfs defaults,user,noauto,nodev,exec,nosuid,gid=$GID,uid=$UID,mode=0700 0 0
