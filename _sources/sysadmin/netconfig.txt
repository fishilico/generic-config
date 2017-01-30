Network configuration
=====================

This short document is a quick reference to some commands you would like to
know when you're connecting to a network and asking "What's the conf, here?"
If there is a kind of "automatic configuration" taking place, you may want to
know what information the network is giving you. In the other case, you need to
know how to set up a manual configuration by hand.


IPv4 configuration
------------------
Automatic IPv4 configuration is quite straightforward: run a DHCP client! For
example, to discover a DHCP server on ``eth0`` interface::

    dhclient eth0
    # or
    dhcpcd eth0

Static IPv4 configuration can be achieved thanks to ``ip`` command::

    ip addr add 192.168.0.42/24 dev eth0
    ip route add default via 192.168.0.1 dev eth0

This presupposes that you know what IP address your gateway uses. Without this
knowledge, you need to sniff and/or scan the network to find it.


IPv6 configuration
------------------
Automatic IPv6 configuration is more straightforward than IPv4: it is done by
the kernel and you have nothing to do! Sometimes you may want to ignore the
automatic configuration. This command disables it on ``eth0``::

    sysctl -w sys.net.ipv6.conf.accept_ra=0

Automatic configuration works because when a host sends a Router Solicitation
message (ICMPv6 type 133), the gateways answer with a Router Advertisement
(ICMPv6 type 134) containing information similar to DHCP. To send a RS by hand,
install ``ndisc6`` package and run::

    rdisc6 eth0

Like with IPv4, static IPv6 can be configured with ``ip`` command::

    ip addr add 2001:db8::42/64 dev eth0
    ip -6 route add default via 2001:db8::1 dev eth0

However, unlike IPv4, there is a smart way to find the gateway: multicast. More
precisely, IPv6 defines ``ff02::2`` as being a multicast address for all
routers on a link (a Linux machine answers as a router when
``sys.net.ipv6.conf.forwarding`` is 1). If your gateway answers to ping request,
you can run this command to get its IPv6 address::

    ping6 -c1 ff02::2%eth0

The result would look like::

    PING ff02::2%eth0(ff02::2) 56 data bytes
    64 bytes from fe80::4242:42ff:fe42:4242: icmp_seq=1 ttl=64 time=0.420 ms

In such case, you may configure your default route with this link-local address
(in ``fe80::/64``)::

    ip -6 route add default via fe80::4242:42ff:fe42:4242 dev eth0


DNS configuration
-----------------
In automatic configurations, the IP addresses of the local DNS servers and the
search domains are found in DHCP headers and RA options. If you use a software
like NetworkManager or resolvconf or wicd, this information is directly written
in ``/etc/resolv.conf``.

In manual configuration, edit this file with lines like these::

    # resolver1.opendns.com and resolver2.opendns.com
    nameserver 208.67.222.222
    nameserver 208.67.220.220
    domain example.com
    search example.com


Broadcast ping
--------------
To discover pingable hosts on your network, send an Echo Request (ping) to
every host. In IPv4 this broadcasts an ICMP type 8 message::

    ping -b 255.255.255.255 -I eth0

In IPv6 this multicasts an ICMPv6 type 128 message to all nodes::

    ping6 ff02::1%eth0

After such command, you may list every link-layer addresses of your neighbors by
issuing::

    ip neigh show


Link-layer ping
---------------
When the network don't give your host an IP address, you need to find an unused
one. In IPv4 you can test whether an IP address is free or used by sending ARP
requests (what doesn't require an IPv4 address to be configured, unlike
``ping``)::

    arping 192.168.0.42 -I eth0

In IPv6, ARP requests are replaced with Neighbor Solicitation (ICMPv6 type 135
messages)::

    ndisc6 2001:db8::42 eth0
