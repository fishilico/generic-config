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
