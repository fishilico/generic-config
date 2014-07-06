Traffic shaping
===============

This is not a complete guide which explains how to shape traffic but a list
of not-so-intuitive commands related to traffic shaping.

Documentation:

* http://linux-ip.net/articles/Traffic-Control-HOWTO/
* http://lartc.org/wondershaper/ (scripts to do QoS on ADSL)
* https://www.kernel.org/doc/Documentation/cgroups/net_cls.txt (filter with cgroup)

First, to dump current traffic shaping rules on interface ``eth0``, use the
following command (``tc`` means "Traffic Controller")::

    tc -s qdisc show dev eth0

By default it will display something like::

    qdisc pfifo_fast 0: root refcnt 2 bands 3 priomap  1 2 2 2 1 2 0 0 1 1 1 1 1 1 1 1
     Sent 42000 bytes 1337 pkt (dropped 0, overlimits 0 requeues 0) 
     backlog 0b 0p requeues 0 

At any time, to restore this default configuration (and remove all rules), run::

    tc qdisc del dev eth0 root


Egress shaping (limiting outbound traffic)
------------------------------------------

This command attachs a TBF (Token Bucket Filter) to ``eth0`` which :

* limit the maxium rate to 1 Mbits/s,
* define a peakrate at 2 Mbits/s,
* use a 10 KB buffer,
* limit the latency caused by the TBF to at most 70ms

::

    tc qdisc add dev eth0 root tbf rate 1mbit peakrate 2mbit burst 10kb latency 70ms minburst 1540


Delay
-----

This command applies a delay of 500ms on each outbound packets::

    tc qdisc add dev eth0 root netem delay 500ms

With this, ``tc qdisc show dev eth0`` shows::

    qdisc netem 8001: root refcnt 2 limit 1000 delay 500.0ms


HTTP server outbound traffic shaping
------------------------------------

When running an HTTP server on TCP port 80, it is possible to throttle the
outbound traffic with ``tc``::

    tc qdisc add dev eth0 root handle 1:0 htb default 10
    tc class add dev eth0 parent 1:0 classid 1:10 htb rate 512kbps ceil 768kbps prio 0
    tc filter add dev eth0 parent 1:0 protocol ip match ip sport 80 0xffff flowid 1:10

Here are some commands to get a similar behavior of the last ``tc filter``
command with ``iptables`` power::

    iptables -A OUTPUT -t mangle -o eth0 -p tcp --sport 80 -j MARK --set-mark 10
    ip6tables -A OUTPUT -t mangle -o eth0 -p tcp --sport 80 -j MARK --set-mark 10
    tc filter add dev eth0 parent 1:0 prio 0 protocol ip handle 10 fw flowid 1:10


To show active rules::

    # tc -s -d class show dev eth0
    class htb 1:10 root prio 0 quantum 51200 rate 4096Kbit ceil 6144Kbit burst 1599b/1 mpu 0b overhead 0b cburst 1598b/1 mpu 0b overhead 0b level 0 
     Sent 42000 bytes 1337 pkt (dropped 0, overlimits 0 requeues 0) 
     rate 400bit 0pps backlog 0b 0p requeues 0 
     lended: 1337 borrowed: 0 giants: 0
     tokens: 44738 ctokens: 29819

    # tc filter show dev eth0
    filter parent 1: protocol ip pref 49152 fw


Make downloads slow
-------------------

In order to slow down downloads to prevent them from filling ISP's buffers, you
can attach a filter in ingress mode which drops too fast packets::

    tc qdisc add dev eth0 handle ffff: ingress
    tc filter add dev eth0 parent ffff: protocol ip prio 50 u32 \
        match ip src 0.0.0.0/0 police rate 800kbit burst 10k drop flowid :1

After that, statistics commands display this::

    # tc qdisc show dev eth0
    qdisc pfifo_fast 0: dev eth0 root refcnt 2 bands 3 priomap  1 2 2 2 1 2 0 0 1 1 1 1 1 1 1 1
    qdisc ingress ffff: dev eth0 parent ffff:fff1 ----------------

    # tc filter show dev eth0 parent ffff:
    filter protocol ip pref 50 u32 
    filter protocol ip pref 50 u32 fh 800: ht divisor 1 
    filter protocol ip pref 50 u32 fh 800::800 order 2048 key ht 800 bkt 0 flowid :1 
      match 00000000/00000000 at 12
            action order 0:  police 0x1 rate 800Kbit burst 10Kb mtu 2Kb action drop overhead 0b 
    ref 1 bind 1

To delete everything related to inbound packets policy on ``eth0``, use::

    tc qdisc del dev eth0 ingress
