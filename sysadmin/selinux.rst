Some notes about my SELinux installation
========================================

This document doesn't document how to install SELinux. If you want to install
it, please read one of these websites:

* https://wiki.debian.org/SELinux
* https://wiki.gentoo.org/wiki/SELinux/Tutorials (an excellent tutorial for Gentoo)
* https://fedoraproject.org/wiki/SELinux

To develop the SELinux policy, here are the relevant git repositories:

* https://github.com/TresysTechnology/refpolicy/commits/master (Reference Policy)
* https://github.com/TresysTechnology/refpolicy-contrib/commits/master
  (refpol contrib modules)
* http://git.overlays.gentoo.org/gitweb/?p=proj/hardened-refpolicy.git;a=summary
  (Gentoo)
* https://github.com/selinux-policy/selinux-policy/tree/rawhide-base (Fedora)
* http://anonscm.debian.org/cgit/selinux/refpolicy.git/log/ (Debian)

And here is some documentation related with writing the policy:

* http://oss.tresys.com/docs/refpolicy/api/ (reference policy API)
* http://www.selinuxproject.org/page/ObjectClassesPerms
  (SELinux Object Classes and Permissions Reference)
* https://wiki.gentoo.org/wiki/Project:SELinux/Development (Gentoo doc)
* http://wiki.gentoo.org/wiki/Project:SELinux/CodingStyle
  (Gentoo coding style for SELinux)

And while listing websites, here are some more:

* https://people.redhat.com/sgrubb/audit/visualize/index.html
  (Audit Data Visualization)
* https://github.com/SELinuxProject/selinux
  (SELinux userland libraries and tools repository)
* http://www.freetechbooks.com/the-selinux-notebook-the-foundations-t785.html
  (The SELinux Notebook - The Foundations)

The present document will focus on some pitfalls I've encountered since
installing SELinux on systems running Debian or ArchLinux.


Install a strict policy
-----------------------

On Debian by default a targeted policy is installed, daemons are confined but
not users. To make users confined, you need to remove the unconfined module.
To do this:

.. code-block:: sh

    # Set up staff accounts
    semanage login -a -s staff_u userlogin

    # Confine other users
    semanage login -m -s user_u -r s0 __default__

    # Map root to root instead of unconfined_u
    semanage login -m -s root root

    # Remove the unconfined module
    semodule -r unconfined


Use ``run_init`` as root without a password
-------------------------------------------

``run_init`` command (to manage services) authenticates the real user with PAM
before making a transition to ``system_u:system_r:init_t`` context. The default
configuration tell PAM to ask for a password to authenticate but this may be
annoying on non-critical systems where root needs to restart services.
To disable the password prompt for root, add this at the beginning of
``/etc/pam.d/run_init``::

    auth       sufficient   pam_rootok.so

Moreover make sure that you allow ``run_init_t`` to use ``pam_rootok.so``::

    allow run_init_t self:passwd rootok;


Fix ``/tmp`` labeling
---------------------

If ``mount`` shows::

    tmpfs on /tmp type tmpfs (rw,nosuid,nodev,relatime,rootcontext=system_u:object_r:file_t:s0,seclabel)

... or if ``ls -Zd /tmp`` shows::

    system_u:object_r:file_t:SystemLow /tmp

... ``/tmp`` is incorrectly labeled ``file_t`` instead of ``tmp_t``.

To fix the label, you need to restore the context of the ``/tmp`` folder of the
root filesystem to ``system_u:object_r:tmp_t:s0``::

    mount --bind / /mnt
    setfiles -r /mnt /etc/selinux/default/contexts/files/file_contexts /mnt
    umount /mnt

It is also possible to use such a line in ``/etc/fstab``::

    tmpfs /tmp tmpfs nodev,nosuid,rootcontext=system_u:object_r:tmp_t:s0 0 0


Configure SELinux booleans
--------------------------

Here are some booleans I use is almost all my SELinux systems:

.. code-block:: sh

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

Fix labels for files in ``/home``
---------------------------------

By default, files under ``/home`` are labeled as user home directories. On some
system, ``/home`` is on the largest disk partition and there are other things,
like database files (instead of ``/var/lib/...`` folders) or Git repositories.
For such folders, you must a command like this to specify the real file context
to use::

    semanage fcontext -a -t httpd_sys_content_t "/home/git(/.*)?"


Generate interface file for ``audit2allow -R``
----------------------------------------------

``audit2allow -R`` needs ``/var/lib/sepolgen/interface_info``, which is created
by ``sepolgen-ifgen``. However, as the ``-p`` parameter of this command is
buggy, your interface files need to be located in the ``default`` policy, ie.
in ``/usr/share/selinux/default/include`` directory. For example, add a symlink
``/usr/share/selinux/default`` to your policy directory:

.. code-block:: sh

    . /etc/selinux/config
    cd /usr/share/selinux && ln -s $SELINUXTYPE default
    sepolgen-ifgen


Activate some SELinux modules
-----------------------------

To reload modules, go to ``/usr/share/selinux/$(policyname)`` and run::

    semodule --verbose -b base.pp -s $(basename $(pwd)) -n -i module1.pp -i ...


Allow ``staff_u`` to read ``/root`` when running ``sudo``
---------------------------------------------------------

By default ``/etc/selinux/default/modules/active/file_contexts.homedirs``
defines ``/root`` to be labeled ``root:object_r:user_home_t``, which ``staff_u``
can't access (there is a constraint for it). To solve this issue, change the
constraint or (much sumpler) change the user associated to ``root``::

    chcon -u staff_u /root -R

Alternatively it is possible to consider root as an usual staff user::

    semanage login -m -s staff_u root


Export local configuration done with ``semanage``
-------------------------------------------------

To export all local changes done with ``semanage``, there is an option:

    semanage -o

To import exported data back to the local configuration:

    semanage -i


Bugs still present in October 2014
----------------------------------

In ArchLinux, ``/sys`` is not labelled correctly on boot. It needs to be labeled
by systemd using ``tmpfiles.d`` configuration. Therefore you need to add this in
``/etc/tmpfiles.d/sysfs.conf``::

    Z /sys/devices/system/cpu/online 0444 root root

For further information, please read:

* https://bugzilla.redhat.com/show_bug.cgi?id=767355
* http://www.spinics.net/lists/selinux/msg11684.html
