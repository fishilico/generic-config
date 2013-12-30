Linux NAT router
================

This document presents some commands to configure a Linux NAT router in an IPv4
network. *NAT* means Network Address Translation and has been designed to
provide Internet connectivity when there is only a limited number of addresses
assigned to a network.

Network architecture
--------------------

For the sake of clarity, this document uses following interface names and
network addresses::

                   +--------------------------------+
                   |             Linux              |      Private Network
    Internet ------| eth0        Router        eth1 |----- (Wifi, VPN...)
                   | 192.0.2.42          10.13.37.1 |       10.13.37.0/24
                   +--------------------------------+             |
                                                                  |
                                                             +---------+
                                                             | Private |
                                                             |  Host   |
                                                             +---------+

Hosts connected to the private network don't have public IPv4 addresses and are
configured to connect to the Internet via a router sitting at ``10.13.37.1``.

To configure the router so that the private host gets access to the Internet,
you need to issue following commands on the Linux router:

* Configure the firewall to do NAT::

    # If the public address (192.0.2.42) is static, use this command
    iptables -t nat -A POSTROUTING -s 10.13.37.0/24 -o eth0 -j SNAT --to-source 192.0.2.42

    # Otherwise if the public address is dynamic, use this command
    iptables -t nat -A POSTROUTING -s 10.13.37.0/24 -o eth0 -j MASQUERADE

* Configure the firewall to allow packet forwarding::

    iptables -A FORWARD -s 10.13.37.0/24 -i eth1 -o eth0 -j ACCEPT
    iptables -A FORWARD -d 10.13.37.0/24 -i eth0 -o eth1 -j ACCEPT

* Enable packet forwarding via sysctl (``sysctl -w`` writes to ``/proc/sys/...``)::

    sysctl -w net.ipv4.conf.eth0.forwarding=1
    sysctl -w net.ipv4.conf.eth1.forwarding=1

    # Previous entries may not exists in old kernels. In such case, use:
    # sysctl -w net.ipv4.ip_forward=1
    # ... which acts like: sysctl -w net.ipv4.conf.all.forwarding=1


Persistent configuration
------------------------

You may create following files to write your configuration in a way it is kept
across rebooting.

``/etc/iptables/iptables.rules`` (please adapt this path according to your Linux
distribution)::

    *filter
    :INPUT DROP [0:0]
    :FORWARD DROP [0:0]
    :OUTPUT DROP [0:0]
    # (... INPUT and OUTPUT filters ...)
    -A FORWARD -s 10.13.37.0/24 -i eth1 -o eth0 -j ACCEPT
    -A FORWARD -d 10.13.37.0/24 -i eth0 -o eth1 -j ACCEPT
    COMMIT

    *nat
    :PREROUTING ACCEPT [0:0]
    :POSTROUTING ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    -A POSTROUTING -s 10.13.37.0/24 -o eth0 -j SNAT --to-source 192.0.2.42
    COMMIT


``/etc/sysctl.d/ip_forward.conf`` (or ``/etc/sysctl.conf`` on old systems)::

    net.ipv4.conf.eth0.forwarding=1
    net.ipv4.conf.eth1.forwarding=1
