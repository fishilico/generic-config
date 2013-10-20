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

First, create ``/etc/systemd/system/timer-daily.timer``::

    [Unit]
    Description=Daily Timer

    [Timer]
    OnBootSec=10min
    OnUnitActiveSec=1d
    Unit=timer-daily.target

    [Install]
    WantedBy=basic.target

and ``/etc/systemd/system/timer-daily.target``::

    [Unit]
    Description=Daily Timer Target
    StopWhenUnneeded=yes

You may also create ``timer-hourly`` and ``timer-weekly`` files with 1h and 1w
durations, and also with different ``OnBootSec`` values.

Then, add some events in ``/etc/systemd/system/timer-daily.target.wants``.

- Logrotate::

    # /etc/systemd/system/timer-daily.target.wants/logrotate.service
    [Unit]
    Description=Rotate Logs

    [Service]
    Nice=19
    IOSchedulingClass=2
    IOSchedulingPriority=7
    ExecStart=/usr/bin/logrotate /etc/logrotate.conf

- Update man-db::

    # /etc/systemd/system/timer-daily.target.wants/man-db-update.service
    [Unit]
    Description=Update man-db

    [Service]
    Nice=19
    IOSchedulingClass=2
    IOSchedulingPriority=7
    ExecStart=/usr/bin/mandb --quiet

- Update mlocate database::

    # /etc/systemd/system/timer-daily.target.wants/mlocate-update.service
    [Unit]
    Description=Update mlocate database

    [Service]
    Nice=19
    IOSchedulingClass=2
    IOSchedulingPriority=7
    ExecStart=/usr/bin/updatedb

- Verify integrity of password and group files::

    # /etc/systemd/system/timer-daily.target.wants/verify-shadow.service
    [Unit]
    Description=Verify integrity of password and group files

    [Service]
    Type=oneshot
    ExecStart=/usr/bin/pwck -r
    ExecStart=/usr/bin/grpck -r

Finally, start the timer::

    systemctl enable timer-daily.timer && systemctl start timer-daily.timer
