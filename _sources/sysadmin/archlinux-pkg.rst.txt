Notes about Arch Linux packages
===============================

Here are some notes about Arch Linux packages.

Building packages
-----------------

Arch Linux packages can be found in two main places: official repositories and
Arch User Repository (AUR). Official repositories are managed throw the Arch
Build System (ABS). Users interact with them thanks to ``pacman``. AUR is
managed by users and only contain sources, not binary packages.

To build a package, you need to install ``base-devel`` and use ``makepkg``.
The main component of a package is the ``PKGBUILD`` description file, which
describes where to download sources and how to compile binary files. Once you
have a ``PKGBUILD`` (and additional files such as patches) in a directory,
to build and install the package you just need to issue::

    makepkg -si

``-s`` option means *install missing dependencies using pacman*.
``-i`` option means *install the package after it is built*.

You should customize your ``/etc/makepkg.conf`` file before launching the build,
for example to set up the packager name:

.. code-block:: sh

    PACKAGER="Myself <root@localhost>"

It is also possible to enable parallel build and to use a temporary build directory

.. code-block:: sh

    cat >> /etc/makepkg.conf << EOF
    MAKEFLAGS="-j4"  # According to $(nproc)
    BUILDDIR=/tmp/makepkg
    EOF
    cat >> /etc/fstab << EOF
    makepkg /tmp/makepkg tmpfs defaults,auto,nodev,nosuid,exec,gid=100,uid=1000,mode=0700 0 0
    EOF

For more information read the wiki! Here are some links:

- https://wiki.archlinux.org/index.php/Arch_Build_System
- https://wiki.archlinux.org/index.php/AUR
- https://wiki.archlinux.org/index.php/makepkg
- https://wiki.archlinux.org/index.php/Official_Repositories
- https://wiki.archlinux.org/index.php/Pacman_Tips
- https://wiki.archlinux.org/index.php/PKGBUILD
- https://wiki.archlinux.org/index.php/Yaourt


Yaourt, pacaur and trizen
-------------------------

``yaourt`` (Yet AnOther User Repository Tool), ``pacaur`` and ``trizen`` ease the
installation of packages from the AUR. Their interfaces are similar to
``pacman`` but they can download, build and install user packages too, wrapping
both ``makepkg`` and ``pacman``.

``yaourt`` includes ``-G`` option (``--getpkgbuild``) to get a ``PKGBUILD`` file
for a specified package.

``pacaur`` main advantage lies in keeping the downloaded PKGBUILD and their git
history in a directory, ``$HOME/.cache/pacaur/``, which allows tracking changes
when upgrading AUR packages.

``trizen`` is a more recent one and can replace ``pacaur``.


Debug build
-----------

To build packages with debug symbols, you need to change ``OPTIONS`` variable
in ``/etc/makepkg.conf``. Here is the default configuration::

    OPTIONS=(strip docs !libtool !staticlibs emptydirs zipman purge !upx !debug)

You just need to add and remove some bangs following your needs::

    OPTIONS=(!strip docs !libtool !staticlibs emptydirs zipman purge !upx debug)
