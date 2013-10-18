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
