Some information of Debian systems
==================================

This document describes some configuration customizations and other sysadmin
tasks I do when I set up a Debian host.


Debian post-installation commands
---------------------------------

``dpkg-reconfigure locales``
    Reconfigure locales, for example to ``en_US en_US.UTF-8 fr_FR.UTF-8 fr_FR@euro``.
    Keep in mind SSH preserve locale accross the connection so a single UTF-8
    locale is not enough.

``cd /usr/bin && sudo ln -s python python2``
    For scripts which require python2 command.

``update-rc.d $SERVICE remove`` or ``sysv-rc-conf``
    Remove some uneeded services from boot. Opposite operation is ``defaults``.


APT configuration
-----------------

This configuration doesn't install recommended packages by default.

``/etc/apt/apt.conf``::

    APT::Install-Recommends "0";
    APT::Install-Suggests "0";

To configure an HTTP proxy, you need to add one more line::

    Acquire::http::Proxy "http://proxy.example.com:8080/";

``/etc/apt/sources.list`` file depends on your location::

    # Here is this file for a Debian Unstable in the US.
    deb http://http.us.debian.org/debian/     sid main contrib non-free
    deb-src http://http.us.debian.org/debian/ sid main contrib non-free

    # And here for a Debian Squeeze server in Germany
    deb http://ftp.de.debian.org/debian          squeeze main contrib non-free
    deb http://ftp.de.debian.org/debian-security squeeze/updates main contrib non-free

You may install ``debsums`` package to check the integrity of the installed
files. There is a cron job with ``debsums`` which is configured by
``/etc/default/debsums``::

    # Set this to never to disable the checksum verification or
    # one of "daily", "weekly", "monthly" to enable it
    CRON_CHECK=never

Apticron is a program which automatically downloads the new updates (without
installing them) and send mails about them. By default, it is configured to run
every day. To change this to a weekly-based period, you need to edit
``/etc/cron.d/apticron``::

    # Sunday, 0:41
    41 0 * * 0 root if test -x /usr/sbin/apticron; then /usr/sbin/apticron --cron; else true; fi


Apache commands
---------------

``a2dismod status``
    Disable the status module.

``a2dissite default``
    Disable the default site, you need to write your own site file and enable it.


Postfix configuration
---------------------

To send system messages by email, it is a good idea to have a mail server on an
host which is configured as an "Internet Site". On a Debian host Postfix seems
to be a good choice and is easy to install, configure and manage.

Reload aliases after any change in ``/etc/aliases``::

    postaliases /etc/aliases || newaliases
    postfix reload

``/etc/aliases`` example::

    root: root@example.com
    postmaster: root
    abuse: root
    user: root
    web: web@example.com
    www: web

The name of the mail system is written down in ``/etc/mailname``.
