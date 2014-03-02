Kernel Network Console (netconsole module)
==========================================

To debug hosts when a display is not available, or in other circumstances, it's
possible to set up a network console so that kernel messages go through the
network to a destination host which can display these messages. Let's say the
source host (which sends messages) has an ethernet interface ``eth0`` which is
linked to the destination host (which receives messages).
The addresses of each interface is as follows:

+-------------+-----------------------+-------------------------------+------+
|    Host     |      MAC address      |    Link-local IPv6 address    | Port |
+=============+=======================+===============================+======+
|   Source    | ``00:00:00:00:00:01`` | ``fe80::0200:00ff:fe00:0001`` | 6665 |
+-------------+-----------------------+-------------------------------+------+
| Destination | ``00:00:00:00:00:02`` | ``fe80::0200:00ff:fe00:0002`` | 6666 |
+-------------+-----------------------+-------------------------------+------+

The configuration of netconsole module is documented like this::

    netconsole=[src-port]@[src-ip]/[<dev>],[tgt-port]@<tgt-ip>/[tgt-macaddr]

where:

* ``src-port`` source for UDP packets (defaults to 6665)
* ``src-ip`` source IP to use (interface address)
* ``dev network`` interface (eth0)
* ``tgt-port`` port for logging agent (6666)
* ``tgt-ip`` IP address for logging agent
* ``tgt-macaddr`` ethernet MAC address for logging agent (broadcast)

Hence in the previous scenario, the configuration line is::

    netconsole=6665@fe80::0200:00ff:fe00:0001/eth0,6666@fe80::0200:00ff:fe00:0002/00:00:00:00:00:02

This line can be set as-is either on boot::

    linux loglevel=5 netconsole=...

or when loading the module::

    modprobe netconsole netconsole=...

Once the source host is configured, you would normally set up something which
is listening for incomming messags on the destination host. For example with
``socat`` by doing so::

    socat UDP6-RECV:6666 -

To test the communication between the 2 hosts, you may send a raw UDP packet::

    echo test | socat - 'UDP6:[fe80::0200:00ff:fe00:0002]:6666,sourceport=6665'

and if this worked, trigger a kernel message on the source host::

    echo h > /proc/sysrq-trigger


Dynamic configuration
---------------------

To dynamicaly change netconsole's settings, you need to mount the kernel config
filesystem::

    modprobe configfs
    mount none -t configfs /sys/kernel/config
    # /sys/kernel/config/netconsole would exist if netconsole module is loaded
    mkdir /sys/kernel/config/netconsole/target

Now, ``/sys/kernel/config/netconsole/target`` would contain some files.
To configure this new netconsole target, you need to write the values to each
file before writing 1 to ``enabled``::

    cd /sys/kernel/config/netconsole/target
    echo eth0 > dev_name
    echo fe80::0200:00ff:fe00:0001 > local_ip
    echo 6665 > local_port
    echo fe80::0200:00ff:fe00:0002 > remote_ip
    echo 00:00:00:00:00:02 > remote_mac
    echo 6666 > remote_port
    echo 1 > enabled


Firewall configuration
----------------------

Here are the iptables rules to add to the firewall to accept the communication.

Source host::

    iptables -A OUTPUT -p udp -m udp --sport 6665 --dport 6666 -j ACCEPT
    ip6tables -A OUTPUT -p udp -m udp --sport 6665 --dport 6666 -j ACCEPT

Destination host::

    # You would add some specific filtering:
    # * by interface: -i eth0
    # * by MAC address: -m mac --mac-source 00:00:00:00:00:01
    # * by source IP address: -s fe80::0200:00ff:fe00:0001
    iptables -A INPUT -p udp -m udp --sport 6665 --dport 6666 -j ACCEPT
    ip6tables -A INPUT -p udp -m udp --sport 6665 --dport 6666 -j ACCEPT


Documentation links
-------------------

* https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/tree/Documentation/networking/netconsole.txt
  Linux Documentation
* https://wiki.archlinux.org/index.php/Netconsole
  ArchLinux wiki
* https://wiki.ubuntu.com/Kernel/Netconsole
  Ubuntu wiki
