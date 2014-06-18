``etc-server/dhcp/dnsmasq.conf``
================================

Full example configuration file for dnsmasq can be downloaded at:
http://thekelleys.org.uk/gitweb/?p=dnsmasq.git;a=blob;f=dnsmasq.conf.example

Here is an example configuration to serve range 10.13.37.100..10.13.37.200 on
interface eth0.  This can be achieved using this command line::

    dnsmasq -kd -i eth0 --dhcp-range=10.13.37.100,10.13.37.200

By the way, here are iptables commands to allow DHCP and DNS server::

    iptables -I INPUT -i eth0 -p udp --sport 68 --dport 67 -j ACCEPT
    iptables -I INPUT -i eth0 -p udp --dport 53 -j ACCEPT
    iptables -I OUTPUT -o eth0 -p udp --sport 67 --dport 68 -j ACCEPT
    iptables -I OUTPUT -o eth0 -p udp --sport 53 -j ACCEPT

Here is ``/etc/dnsmasq.conf`` for a DHCP server (no IPv6, no DNS):
(:download:`Download file<dnsmasq.conf>`)

.. literalinclude:: dnsmasq.conf
   :language: sh
