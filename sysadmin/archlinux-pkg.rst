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
have a ``PKGBUILD`` (and additionnal files such as patches) in a directory,
to build and install the package you just need to issue::

    makepkg -si

``-s`` option means *install missing dependencies using pacman*.
``-i`` option means *install the package after it is built*.

You should customize your ``/etc/makepkg.conf`` file before launching the build,
for example to set up the packager name::

    PACKAGER="Myself <root@localhost>"

For more information read the wiki! Here are some links:

- https://wiki.archlinux.org/index.php/Arch_Build_System
- https://wiki.archlinux.org/index.php/AUR
- https://wiki.archlinux.org/index.php/makepkg
- https://wiki.archlinux.org/index.php/Official_Repositories
- https://wiki.archlinux.org/index.php/Pacman_Tips
- https://wiki.archlinux.org/index.php/PKGBUILD
- https://wiki.archlinux.org/index.php/Yaourt


Yaourt
------

``yaourt`` (Yet AnOther User Repository Tool) ease the installation of packages
from the AUR. Its interface is similar to ``pacman`` but it can download, build
and install user packages too, using ``makepkg`` and ``pacman``.

``yaourt`` includes ``-G`` option (``--getpkgbuild``) to get a ``PKGBUILD`` file
for a specified package.


Debug build
-----------

To build packages with debug symbols, you need to change ``OPTIONS`` variable
in ``/etc/makepkg.conf``. Here is the default configuration::

    OPTIONS=(strip docs !libtool !staticlibs emptydirs zipman purge !upx !debug)

You just need to add and remove some bangs following your needs::

    OPTIONS=(!strip docs !libtool !staticlibs emptydirs zipman purge !upx debug)
