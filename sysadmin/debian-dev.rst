Build a development environment for Debian
==========================================

Here is a memo about how some development activities can be done in Debian.


Compile a Debian package in debug mode
--------------------------------------

Sometimes a program crashes and you need to reinstall it to be able to debug it.
With debug symbols, you may attach a process with gdb and then follow the
execution with commands such as ``layout src`` and ``layout split`` instead of
``layout regs`` and ``layout asm``. There are several ways to get a program
built with debug symbols in Debian. For the rest of this section, let's state
that the program you want to debug is in a package which name is ``foo``.

First, there is occasionally a debug package for ``foo``, named ``foo-dbg`` or
something like that. In such case, you have a clean solution and nothing to do
more than to replace a package.

For most of the cases, such package doesn't exist and you need to recompile
package ``foo`` by adding some options to ``debuild``. This can be done in a
clean temporary directory by issuing the following commands::

    sudo apt-get build foo
    apt-get source foo
    cd foo-*/
    export DEB_BUILD_OPTIONS="nostrip noopt"
    debuild -uc -us
    sudo dpkg -i ../foo_*.deb

Theses commands first install all the necessary build dependency and extract
the Debian-patched version of ``foo`` in a ``foo-version`` directory. Running
``debuild`` into this directory is enough to build a ``foo_version_arch.deb``
file in the main folder, the options are here to tweak the compiling process
(disable stripping symbols from executable files and disable optimization) and
the build process (don't sign any produced files). Instead of calling debuild,
calling ``dpkg-buildpackage -rfakeroot`` may work, as some documents suggest.


Set up your own Debian repository
---------------------------------

You may want to install some package you compiled in several systems or to make
this package publicly available. This can be achieved thanks to ``reprepro``,
which is a simple tool to maintain a repository tree. To do that, let's assume
you want a package tree in ``/var/packages/debian``.

First, create ``/var/packages/debian/conf/distributions`` with something like::

    Origin: My Repository
    Label: My Repository
    Suite: unstable
    Codename: sid
    Architectures: i386 amd64 source
    Components: main
    Description: My APT repositories
    DebOverride: override.sid
    DscOverride: override.sid
    SignWith: 12345678

(``SignWith`` is an optional line which identifies a PGP key which is used to
sign the package tree)

Then create ``/var/packages/debian/conf/options``::

    verbose
    ask-passphrase
    basedir /var/packages/debian

And create ``/var/packages/debian/conf/override.sid``, which can be empty but
may also contains lines which override package descriptions such as::

    my-package Priority optional
    my-package Section net

Then you can add ``.deb`` files with::

    reprepro includedeb sid /path/to/mypackage.deb

and source, changes and deb files all at once with::

    reprepro include sid /path/to/mypackage.dsc

To serve this repo with a web server, you may want to exclude ``conf/`` and
``db/`` directories from direct browsing to protect your specific configuration.

Finally, you need to add at least the first line in the
``/etc/apt/sources.list`` of each host which uses this new APT repository::

    deb http://my-host.tld/debian sid main
    deb-src http://my-host.tld/debian sid main

And also use ``apt-key add`` to add the GPG public key of the repository to your
GPG keychain.

More detail in the Debian official wiki:
https://wiki.debian.org/SettingUpSignedAptRepositoryWithReprepro
