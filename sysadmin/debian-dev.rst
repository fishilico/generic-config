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


Package a Python library for Debian
-----------------------------------

Relevant Debian wiki articles:

* https://wiki.debian.org/IntroDebianPackaging
* https://wiki.debian.org/Python/Packaging
* https://wiki.debian.org/Python/LibraryStyleGuide

In this section, let's suppose you have a Python library which is packaged with
``distutils``, ``setuptools``, ``distribute`` or whatever. This library provides
a ``setup.py`` file which can be used to install it on the system.

Debian wiki documents command line tools such as ``py2dsc``. This tool is a
shortcut for some of the initial steps but this section will focus on lower
level tools which help understanding how Debian packaging work.

For the sake of clarity, let's say you're working on library ``mylibrary``
version ``0.0.1``.

The starting point of every Debian package is the *original files archive*. This
archive is the one that may be downloaded from the websites which provide a
`download link`. For example, if your library is on PyPI, you would download
https://pypi.python.org/packages/source/m/mylibrary/mylibrary-0.0.1.tar.gz.
This file should be put in the parent directory of the folder where `mylibrary``
lies, and named ``mylibrary_0.0.1.orig.tar.gz`` (name, underscore, version).
``setup.py`` can be used to create this file::

    python setup.py sdist
    cp dist/mylibrary-0.0.1.tar.gz ../mylibrary_0.0.1.orig.tar.gz

Side note: if you're the author of the library, the command to upload it to
PyPI is::

    python setup.py sdist register upload

Once you have a proper original files archive the next step is to create a
``debian`` directory in the current directory. There are two ways to achieve
this:

* Invoke magic from ``python-stdeb`` package::

    python setup.py --command-packages=stdeb.command debianize

* Read Debian's packaging documentation and create files by hand.
  To create/update ``debian/changelog`` file, you may use for example::

    dch --create -v 0.0.1-1 --package mylibrary

When you feel the package is almost ready, you need to test building the package
without running tests nor signing the package nor its changelog::

    DEB_BUILD_OPTIONS=nocheck debuild -uc -us

Usually ``lintian`` will get angry and print error messages because it's really
hard to follow Debian packaging rules the first time. This is where the
packaging takes time, as you need to edit files in ``debian`` folder to fix the
issues reported by ``lintian``.

Often the ``clean`` function of the package doesn't remove the ``.egg-info``
folder which is created by ``setup.py build``. This is an issue because
``debuild`` finds out that ``mylibrary.egg-info`` doesn't exist in the original
files and so treats it as a `Debian-specific patch`. To prevent this behavior,
you need to add that to ``debian/clean``::

    mylibrary.egg-info/*

Once ``lintian`` has no more things to say, you should build the final package
and sign it with your GPG key::

    debuild

Your parent directory now contains the following files (here on a 64-bits
system):

* ``mylibrary_0.0.1-1_all.deb``
* ``mylibrary_0.0.1-1_amd64.build``
* ``mylibrary_0.0.1-1_amd64.changes``
* ``mylibrary_0.0.1-1.debian.tar.gz``
* ``mylibrary_0.0.1-1.dsc``
* ``mylibrary_0.0.1.orig.tar.gz``

Now you would directly install the package using ``dpkg -i`` or upload it to
a Debian package repository or wherever you like.
