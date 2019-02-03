Set hardware clock to UTC
-------------------------

Some OS like GNU/Linux and MacOS set up the hardware clock to use UTC instead
of local time.  This helps when dealing with daylight saving time, as the real
clock does not need to be updated accordingly.

Windows expects the hardware clock to give "local time" by default.  The reason
is, according to Microsoft, so that users are not confused in BIOS menu
(http://blogs.msdn.com/b/oldnewthing/archive/2004/09/02/224672.aspx).

To enable UTC real-time clock in Windows, put this in a ``.reg`` file::

    Windows Registry Editor Version 5.00

    [HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\TimeZoneInformation]
    "RealTimeIsUniversal"=dword:00000001

Apply this file for example with a command like::

    reg import utc-clock.reg

Or directly set the value with::

    reg add HKLM\SYSTEM\CurrentControlSet\Control\TimeZoneInformation /v RealTimeIsUniversal /t REG_DWORD /d 1

To check the current config, you can use::

    > reg query HKLM\SYSTEM\CurrentControlSet\Control\TimeZoneInformation /v RealTimeIsUniversal

    HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\TimeZoneInformation
        RealTimeIsUniversal    REG_DWORD    0x1
