systemd configuration
=====================

Even if systemd works well with the default configuration, it needs to be
configured on some system so that logs don't fill the disk, ...

Logging: syslog and journald
----------------------------

On most of my systems I'm using syslog-ng to manage my log files. This
interfaces quite well with journald as the only thing you need to do to make it
work is to use these sources in ``/etc/syslog-ng/syslog-ng.conf``::

    source src {
      unix-dgram("/run/systemd/journal/syslog");
      internal();
      file("/proc/kmsg");
    };

Once this is done, you no longer need persistent storage to /var/log/journal.
Instead of deleting this directory or making it a tmpfs, the right way to
disable persistent storage is to set this into ``/etc/systemd/journald.conf``::

    Storage=volatile
    ForwardToSyslog=yes
    ForwardToKMsg=no
    ForwardToConsole=no

More information can be found in the man page:
http://www.freedesktop.org/software/systemd/man/journald.conf.html

If you use persistent storage, you may want to rotate logs every 3 months for
example. This option in ``/etc/systemd/journald.conf`` tells journald to do
this::

    MaxRetentionSec=3month


Write journal on tty
--------------------

On a workstation, it can be quite convenient to read the journal directly from
ttys above 7 (tty1-6 being consoles and tty7 the X Window session, for example).

With syslog-ng, the configuration is quite straightforward::

    source src { system(); };
    destination d_tty9 { file("/dev/tty9" owner(-1) group(-1) perm(-1)); };
    destination d_tty10 { file("/dev/tty10" owner(-1) group(-1) perm(-1)); };
    destination d_tty11 { file("/dev/tty11" owner(-1) group(-1) perm(-1)); };
    destination console_all { file("/dev/tty12" owner(-1) group(-1) perm(-1)); };
    filter f_authpriv { facility(auth, authpriv); };
    filter f_daemon { facility(daemon); };
    filter f_kernel { facility(kern); };
    log { source(src); filter(f_authpriv); destination(d_tty9); };
    log { source(src); filter(f_daemon); destination(d_tty10); };
    log { source(src); filter(f_kernel); destination(d_tty11); };
    log { source(src); destination(console_all); };

With journald, the only "natively" available feature is logging to a tty, with
something like this in ``/etc/systemd/journald.conf``::

    ForwardToConsole=yes
    TTYPath=/dev/tty12
    MaxLevelConsole=info

The other filters can be implemented with services.  Here are some files.

``/etc/systemd/system/journal@.service``::

    [Unit]
    Description=Show journal on %I
    After=systemd-journald.service
    ConditionPathExists=/dev/%I

    [Service]
    Type=idle
    StandardOutput=tty
    TTYPath=/dev/%I
    TTYReset=yes
    TTYVHangup=yes

    [Install]
    WantedBy=multi-user.target

``/etc/systemd/system/journal@tty9.service``::

    .include /etc/systemd/system/journal@.service

    [Unit]
    Description=Show journal on %I (auth)

    [Service]
    # Facilities: 4 = LOG_AUTH, 10 = LOG_AUTHPRIV
    ExecStart=/usr/bin/journalctl -b -n50 SYSLOG_FACILITY=4 SYSLOG_FACILITY=10

``/etc/systemd/system/journal@tty10.service``::

    .include /etc/systemd/system/journal@.service

    [Unit]
    Description=Show journal on %I (daemon)

    [Service]
    # Facility codes:
    #   2 = LOG_MAIL
    #   3 = LOG_DAEMON
    #   5 = LOG_SYSLOG
    #   6 = LOG_LPR
    #   7 = LOG_NEWS
    #   8 = LOG_UUCP
    #   9 = LOG_CRON
    #  11 = LOG_FTP
    #
    # Not selected:
    #   0 = LOG_KERN
    #   1 = LOG_USER
    #   4 = LOG_AUTH
    #  10 = LOG_AUTHPRIV
    #  16..23 = LOG_LOCAL0..7
    #
    # Source: /usr/include/sys/syslog.h
    #   in glibc: https://sourceware.org/git/?p=glibc.git;a=blob;f=misc/sys/syslog.h;hb=HEAD
    ExecStart=/usr/bin/journalctl -b -n50 \
        SYSLOG_FACILITY=2 SYSLOG_FACILITY=3 SYSLOG_FACILITY=5 SYSLOG_FACILITY=6 \
        SYSLOG_FACILITY=7 SYSLOG_FACILITY=8 SYSLOG_FACILITY=9 SYSLOG_FACILITY=11

``/etc/systemd/system/journal@tty11.service``::

    .include /etc/systemd/system/journal@.service

    [Unit]
    Description=Show journal on %I (kernel)

    [Service]
    # --dmesg implies -b and _TRANSPORT=kernel
    ExecStart=/usr/bin/journalctl -b -f -n 50 --dmesg

    ``/etc/systemd/system/journal@tty12.service``::

    .include /etc/systemd/system/journal@.service

    [Unit]
    Description=Show journal on %I (everything)

    [Service]
    ExecStart=/usr/bin/journalctl -b -f -n 50

With such commands, it is also possible to pipe ``journalctl`` output to
``ccze`` (if installed) to colorize the logs.


Configure timers (and remove cron)
----------------------------------

systemd doesn't rely on a cron daemon to run periodic tasks but uses its own
system with calendar time events. ArchLinux provides on its wiki some config
files to replace common cron scripts:
https://wiki.archlinux.org/index.php/Systemd/cron_functionality

Since April 2014 the timers are included and enabled by default, with timer
files in ``/usr/lib/systemd/system`` and symlinks in
``/usr/lib/systemd/system/multi-user.target.wants/``. To disable some timers
which do many disk writes, an overriding unit needs to be created.

``/etc/systemd/system/disabled-timer.service``::

    [Unit]
    Description=Unit to be able to disable timers

    [Service]
    Type=oneshot
    ExecStart=/usr/bin/true


``/etc/systemd/system/updatedb.timer``::

    [Unit]
    Description=Disabled locate database update

    [Timer]
    #OnCalendar=daily
    #Persistent=true
    #OnBootSec=10min
    #OnUnitActiveSec=1d
    OnCalendar=monthly
    Unit=disabled-timer.service

Another way may consist in masking the service units, but it did not work well
back in spring 2014::

    $ systemctl mask updatedb
    Created symlink from /etc/systemd/system/updatedb.service to /dev/null.

Automatically create a bridge interface
---------------------------------------

To automatically create a bridge interface which can be used for example to
bridge together several virtual machines, here is a systemd-networkd
configuration.

``/etc/systemd/network/VMBridge.netdev``::

    [NetDev]
    Name=br0
    Kind=bridge

``/etc/systemd/network/br0.network``::

    [Match]
    Name=br0

    [Address]
    Address=198.51.100.0/24
