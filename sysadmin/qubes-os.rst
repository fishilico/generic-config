Qubes OS setup
==============

Here is some information on Qubes OS, a resonably secure operating system
(according to https://www.qubes-os.org/).

This document was written using Qubes OS R4.0, released in April 2018.
There are some differences with previous versions (Qubes OS 3 and below), which
are not covered.


Useful commands
---------------

When using Qubes OS, some specific commands are quite useful:

* Copy a file from a Qube to ``dom0``:

    .. code-block:: sh

        qvm-run --pass-io $QUBE_NAME 'cat /home/user/path/to/file' > filename

* Copy a file from ``dom0`` to a Qube (it pops into ``/home/user/QubesIncoming/dom0``),
  or from a Qube to another one:

    .. code-block:: sh

        qvm-copy-to-vm $QUBE_NAME filepath

* Xen-specific commands executed from ``dom0``:

    .. code-block:: sh

        # List Xen domains (i.e. virtual machines)
        xl list
        # Read Xen dmesg buffer
        xl dmesg
        # Monitor Xen domains
        xl top
        # Print uptime for all domains
        xl uptime
        # Connect to the console of the sys-firewall (Ctrl+] to exit)
        sudo xl console sys-firewall

        # Find where the "eth0" interface of a Qube is connected:
        $ xl network-list sys-firewall
        Idx BE MAC Addr.         handle state evt-ch   tx-/rx-ring-ref BE-path
        0   0  00:16:3e:5e:6c:00     0     4     -1    -1/-1          /local/domain/1/backend/vif/5/0
        $ xl vm-list | grep ' 1 '  # the "/1/" in the Backend path
        xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx 1 sys-net

* Qubes OS-specific commands executed from ``dom0``:

    .. code-block:: sh

        # List Qubes and various information about them
        qvm-ls
        qvm-ls --format=network
        # List USB devices
        qvm-usb ls
        # Run a command in a Qube and show its output
        qvm-run --pass-io $QUBE_NAME $command
        # Show the properties of a Qube, such as sys-net
        qvm-prefs sys-net


Installation
------------

Here are some notes on what I did when installing Qubes OS.

* Update Qubes OS:

  .. code-block:: sh

      sudo qubes-dom0-update

* By default, ``Ctrl-Shift-P`` pauses all the Qubes. This is the same shortcut
  as the one used by Firefox to open private browsing. To change this shortcut,
  in ``dom0``, go to Menu -> System Tools -> Keyboard -> Application Shortcuts
  and change the shortcut associated with ``qvm-run --pause --all`` from
  ``Ctrl-Shift-P`` to something else, like ``Ctrl-Shift-M``.
  For information, this feature comes from the issue
  https://github.com/QubesOS/qubes-issues/issues/881, which documents the
  following script to configure XFCE shortcuts:

  .. code-block:: sh

      shortcut() {
          for sub in default custom; do
              xfconf-query --channel xfce4-keyboard-shortcuts \
                           --property "/commands/$sub/$1" \
                           --type string --create --set "$2"
          done
      }

      shortcut '<Control><Shift><Alt>p' 'qvm-run --pause --all'
      shortcut '<Control><Alt>Escape'   'qvm-xkill'

* By default, the Inter-VM Copy/Paste shortcuts are ``Ctrl-Shift-C`` and
  ``Ctrl-Shift-V``. They conflict with the terminal clipboard sequences and
  Chrome's Console shortcut. In order to move them to ``Ctrl-Alt-C`` and
  ``Ctrl-Alt-V``, the configuration file ``/etc/qubes/guid.conf`` (for Qubes GUI
  daemon) needs to be modified to::

    global: {
        #secure_copy_sequence = "Ctrl-Shift-c";
        #secure_paste_sequence = "Ctrl-Shift-v";
        secure_copy_sequence = "Ctrl-Alt-c";
        secure_paste_sequence = "Ctrl-Alt-v";
        # NB: The Windows key (if wanted) is Mod4
    }

* The default format of XFCE Clock plugin does not contain the date. The
  following ``strftime`` format displays dates like ``Thu  1 Jan 1970 00:42``::

    %a %e %b %Y %R

* In order to use a USB keyboard, the following command has to be run in
  ``dom0`` (cf. https://www.qubes-os.org/doc/usb/#how-to-use-a-usb-keyboard).
  This will create a ``sys-usb`` Qube if it does not already exist.

  .. code-block:: sh

      sudo qubesctl state.sls qvm.usb-keyboard

* Create an Arch Linux TemplateVM by following the instructions from the
  official documentation:

  - https://www.qubes-os.org/doc/templates/archlinux/
  - https://www.qubes-os.org/doc/building-archlinux-template/

* Create application shortcuts for Firefox private mode and Chromium incognito
  mode by adding some ``.desktop`` files in TemplateVMs
  (documentation: https://www.qubes-os.org/doc/managing-appvm-shortcuts/):

  .. code-block:: ini

      # /usr/share/applications/firefox-private.desktop
      [Desktop Entry]
      Version=1.0
      Name=Firefox Private
      Comment=Open a new Firefox private window
      Exec=/usr/bin/firefox --private-window %u
      Icon=firefox
      Terminal=false
      Type=Application
      MimeType=text/html;text/xml;application/xhtml+xml;application/vnd.mozilla.xul+xml;text/mml;x-scheme-handler/http;x-scheme-handler/https;
      StartupNotify=true
      Categories=Network;WebBrowser;
      Keywords=web;browser;internet;private;

      # /usr/share/applications/chromium-incognito.desktop
      [Desktop Entry]
      Version=1.0
      Name=Chromium Incognito
      Comment=Open a new Chromium incognito window
      Exec=/usr/bin/chromium-browser --incognito %U
      Terminal=false
      X-MultipleArgs=false
      Type=Application
      ; Icon=chromium-browser
      Icon=web-browser
      Categories=Network;WebBrowser;
      MimeType=text/html;text/xml;application/xhtml+xml;x-scheme-handler/http;x-scheme-handler/https;x-scheme-handler/ftp;
      StartupWMClass=Chromium-browser
      StartupNotify=true
      Keywords=web;browser;internet;incognito;


Additional software
-------------------

As the root partition of every AppVM is reset when it boots, additional software
need to be installed in TemplateVMs.

A Fedora template is used for system Qubes (``sys-net``, ``sys-usb``, etc.).
It was ``fedora-26`` for Qubes OS R4.0, ``fedora-29`` for Qubes OS R4.0.1, etc.
Even though this template should be kept as minimal, some software can
nevertheless be useful:

* Generic packages: ``zsh screen tmux htop`` (and maybe change the default shell
  in ``/etc/passwd`` for user ``user`` to ``/usr/bin/zsh``)
* Administrative tools for ``sys-net``: ``bind-utils rfkill traceroute``
* Debugging programs: ``strace tcpdump wireshark wireshark-cli``

For AppVMs, a new template (for example ``fedora-26-with-tools``) may be
created, with additional software:

* Web browsing: ``chromium`` (Firefox is already installed. After installing an
  application, it is possible to add it to the menu through the Qubes Manager)
* File cleaning: ``bleachbit``
* LaTeX compiling: ``latexmk texlive-collection-latex texlive-collection-latexrecommended texlive-xetex texlive-collection-xetex pandoc``

For configuring home-files (``$HOME/bin`` programs and hidden files in
``$HOME``), it is possible to clone a repository like
https://github.com/fishilico/home-files to ``/opt/home-files``, as ``root`` in
a TemplateVM, which makes updating it simpler in AppVMs.
In order to do this, the update proxy needs to be used from the TemplateVM:

.. code-block:: sh

    https_proxy=http://127.0.0.1:8082


Documentation
-------------

* https://www.qubes-os.org/doc/ Qubes OS user documentation
* https://github.com/QubesOS Qubes OS project Github
* https://github.com/QubesOS/qubes-issues/issues Qubes OS issues


RPC Architecture
----------------

qubesd
~~~~~~

In ``dom0``, there is a service written in Python which performs actions on
Qubes: ``qubesd``.
Its architecture is described in https://www.qubes-os.org/doc/admin-api/:

    A central entity in the Qubes Admin API system is a ``qubesd`` daemon, which
    holds information about all domains in the system and mediates all actions
    (like starting and stopping a qube) with ``libvirtd``. The ``qubesd`` daemon
    also manages the ``qubes.xml`` file, which stores all persistent state
    information and dispatches events to extensions. Last but not least,
    ``qubesd`` is responsible for querying the RPC policy for ``qrexec`` daemon.

Package update notification
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When updating a Qube based on Fedora, ``dnf`` may show::

    Notifying dom0 about installed applications

This is due to a Qubes-specific hook in
``/usr/lib/python3.6/site-packages/dnf-plugins/qubes-hooks.py``, which invokes:

.. code-block:: shell

    /usr/lib/qubes/qrexec-client-vm dom0 qubes.NotifyUpdates /bin/echo $UPDATES_COUNT

This RPC call runs ``dom0:/etc/qubes-rpc/qubes.NotifyUpdates``, which contains:

.. code-block:: shell

    #!/bin/sh

    exec /usr/bin/qubesd-query -c /var/run/qubesd.misc.sock --fail \
             "$QREXEC_REMOTE_DOMAIN" qubes.NotifyUpdates dom0 "" >/dev/null 2>&1

This transmits the RPC call to ``qubesd`` daemon.
The policy of this RPC call is written in
``dom0:/etc/qubes-rpc/policy/qubes.NotifyUpdates``::

    $anyvm dom0 allow

The method ``qubes.NotifyUpdates`` is implemented in
``dom0:/usr/lib/python3.5/site-packages/qubes/api/misc.py``:

.. code-block:: python3

        @qubes.api.method('qubes.NotifyUpdates')
        @asyncio.coroutine
        def qubes_notify_updates(self, untrusted_payload):
            '''
            Receive VM notification about updates availability

            Payload contains a single integer - either 0 (no updates) or some
            positive value (some updates).
            '''

            # ...
            # Update features['updates-available']

Qubes database
~~~~~~~~~~~~~~

Each Qube can query its configuration using ``qubesdb-cmd`` and its aliases
(``qubesdb-list``, ``qubesdb-read``, etc):

.. code-block:: shell

    # This is like: qubesdb-cmd -c list /
    $ qubesdb-list /
    default-user
    name
    qubes-base-template
    qubes-block-devices
    qubes-debug-mode
    qubes-gateway
    qubes-ip
    qubes-iptables
    qubes-iptables-error
    qubes-iptables-header
    qubes-keyboard
    qubes-netmask
    qubes-primary-dns
    qubes-secondary-dns
    qubes-service/qubes-update-check
    qubes-timezone
    qubes-usb-devices
    qubes-vm-persistence
    qubes-vm-type
    qubes-vm-updateable
    type

    $ qubesdb-read /default-user
    user

    $ qubesdb-read /name
    untrusted

    $ qubesdb-read /type
    AppVM

Internally, ``qubesdb-cmd`` communicates with ``/var/run/qubes/qubesdb.sock``,
which is created by service ``qubesdb-daemon``
(https://github.com/QubesOS/qubes-core-qubesdb).
This service communicates with ``dom0`` through the XenBus, as seen in its
opened file descriptors::

    /dev/xen/privcmd
    /dev/xen/gntdev
    /dev/xen/evtchn

Nested Virtualization
---------------------

Nested virtualization (the ability to run a hypervisor inside virtual
machines) is not well supported by Xen. Here are some links relevant to this
subject:

* https://github.com/QubesOS/qubes-issues/issues/2887
  Qubes OS issue: There is no information about nested VMs on Qubes on FAQ or DOCs
* https://github.com/QubesOS/qubes-issues/issues/4104
  Qubes OS issue: No virtualization is available in a HVM qube (patches for Xen and Libvirt, 2015-08)
* https://wiki.xenproject.org/wiki/Nested_Virtualization_in_Xen
  Xen Wiki: Nested Virtualization in Xen

Qubes OS 4.0.1 uses Xen 4.8.4 released on 2018-07-12
(https://github.com/xen-project/xen/releases/tag/RELEASE-4.8.4).

In order to enable bits related to the virtualization in the CPUID of a Qube
named ``virtualizer``:

* Create ``/etc/qubes/templates/libvirt/xen/by-name/virtualizer.xml`` in
  ``dom0`` with the following content (to extend
  https://github.com/QubesOS/qubes-core-admin/blob/master/templates/libvirt/xen.xml):

  .. code-block:: xml

      {% extends 'libvirt/xen.xml' %}
      {% block cpu %}
          <cpu mode='host-passthrough'>
              <feature name='vmx' policy='optional'/>
              <feature name='svm' policy='optional'/>
              <!-- disable SMAP inside VM, because of Linux bug -->
              <feature name='smap' policy='disable'/>
          </cpu>
      {% endblock %}
      {% block features %}
          <pae/>
          <acpi/>
          <apic/>
          <viridian/>
          <hap/> <!-- enable Hardware Assisted Paging -->
          <!-- <nestedvm/> -->
      {% endblock %}

* Start the Qube and read the generated configuration:

  .. code-block:: sh

      sudo virsh dumpxml virtualizer
      # or, if you do not like becoming root for this action:
      virsh --connect=xen:/// dumpxml virtualizer

Vagrant in a Qube, using emulation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Without nested virtualization, here are some commands to use Vagrant to emulate
virtual machines in a Qube, from
https://gist.github.com/xahare/0f2078fc8c52e7ddece1e5ba70c6d5fc.

* Add libvirt to the persistent storage of the Qube
  (cf. https://www.qubes-os.org/doc/bind-dirs/):

  .. code-block:: sh

      mkdir -p /rw/config/qubes-bind-dirs.d
      cat << EOF >> /rw/config/qubes-bind-dirs.d/50_user.conf
      binds+=( '/etc/libvirt' )
      binds+=( '/var/lib/libvirt' )
      EOF

* As ``user``, install ``vagrant-libvirt`` plugin:

  .. code-block:: sh

      vagrant plugin install vagrant-libvirt

* As ``user``, configure Vagrant to use libvirt with an emulated CPU:

  .. code-block:: sh

      cat << EOF > ~/.vagrant.d/Vagrantfile
      Vagrant.configure("2") do |config|
        config.vm.provider "libvirt" do |libvirt|
          libvirt.driver = "qemu"
          libvirt.cpu_mode = "custom"
          libvirt.cpu_model = "qemu64"
        end
      end
      EOF

      cat << EOF >> ~/.bashrc
      export LIBVIRT_DEFAULT_URI="qemu:///system"
      export VAGRANT_DEFAULT_PROVIDER=libvirt
      EOF
