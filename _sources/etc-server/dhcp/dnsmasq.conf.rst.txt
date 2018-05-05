``etc-server/dhcp/dnsmasq.conf`` and doc
========================================

Full example configuration file for dnsmasq can be downloaded at:
http://thekelleys.org.uk/gitweb/?p=dnsmasq.git;a=blob;f=dnsmasq.conf.example

The following command spawns a DHCP server on interface ``eth0`` which gives IP
addresses in range 10.13.37.100..10.13.37.200 and tells its clients to use
192.168.1.1 as primary DNS server::

    dnsmasq -kd -i eth0 --dhcp-range=10.13.37.100,10.13.37.200 --dhcp-option=6,192.168.1.1

By the way, here are iptables commands to open UDP ports for DHCP and DNS server::

    iptables -I INPUT -i eth0 -p udp --sport 68 --dport 67 -j ACCEPT
    iptables -I OUTPUT -o eth0 -p udp --sport 67 --dport 68 -j ACCEPT
    iptables -I INPUT -i eth0 -p udp --dport 53 -j ACCEPT
    iptables -I OUTPUT -o eth0 -p udp --sport 53 -j ACCEPT

Here is ``/etc/dnsmasq.conf`` for a DHCP server (no IPv6, no DNS):
(:download:`Download file<dnsmasq.conf>`)

.. literalinclude:: dnsmasq.conf
   :language: sh
