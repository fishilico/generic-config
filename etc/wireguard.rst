``etc/wireguard/``: WireGuard VPN
=================================

Installation
------------

Installing WireGuard is quite simple.
It is documented on several places:

* For Arch Linux: https://wiki.archlinux.org/index.php/WireGuard

  .. code-block:: sh

      pacman -S wireguard-dkms wireguard-tools

* For Debian: https://www.linode.com/docs/networking/vpn/set-up-wireguard-vpn-on-debian/

  .. code-block:: sh

      # Add unstable repository with a low priority (the default one is 500)
      echo "deb http://deb.debian.org/debian/ unstable main" > /etc/apt/sources.list.d/unstable-wireguard.list
      printf 'Package: *\nPin: release a=unstable\nPin-Priority: 150\n' > /etc/apt/preferences.d/limit-unstable
      apt-get update && apt-get install wireguard-dkms wireguard-tools

* For Fedora: https://www.wireguard.com/install/

  .. code-block:: sh

      dnf copr enable jdoss/wireguard
      dnf install wireguard-dkms wireguard-tools


Configuration
-------------

In order to generate the private key of a host, as ``root``:

.. code-block:: sh

    cd /etc/wireguard
    (umask 277 && wg genkey | tee privatekey | wg pubkey > publickey)

An optional pre-shared key can also be generated:

.. code-block:: sh

    (umask 277 && wg genpsk > /etc/wireguard/psk)

In order to configure an interface for the server:

.. code-block:: sh

    ip link add dev wg0 type wireguard
    ip addr add 10.0.0.1/32 dev wg0
    ip addr add fd12:3456:789a::1/128 dev wg0
    wg set wg0 listen-port 51820 private-key /etc/wireguard/privatekey
    wg set wg0 peer ${CLIENT_PUBKEY} persistent-keepalive 25 \
        preshared-key /etc/wireguard/psk \
        allowed-ips 10.0.0.2/32,fd12:3456:789a::2/128
    ip link set wg0 up

    # Save the configuration
    (umask 077 && wg showconf wg0 > /etc/wireguard/wg0.conf)

    # In order to restore the configuration:
    wg setconf wg0 /etc/wireguard/wg0.conf

The configuration file for interface ``wg0``, ``/etc/wireguard/wg0.conf``, can also be directly written like this:

.. code-block:: ini

    [Interface]
    Address = 10.0.0.1/32, fd12:3456:789a::1/128
    ListenPort = 51820
    PrivateKey = <Private Key>
    SaveConfig = true

    [Peer]
    PublicKey = <Client public key>
    PresharedKey = <Pre-Shared Key>
    AllowedIPs = 10.0.0.2/32,fd12:3456:789a::2/128
    PersistentKeepalive = 25

On the client, the configuration is similar, and the server is configured with an additional ``endpoint`` parameter:

.. code-block:: sh

    wg set wg0 peer ${SERVER_PUBKEY} persistent-keepalive 25 \
        allowed-ips 10.0.0.1/32 endpoint ${SERVER_ADDR}:51820
    # In the configuration file: Endpoint = ${SERVER_ADDR}:51820

If the VPN endpoint is allowed to route packets to the external network interface ``eth0``, this firewall configuration needs to be applied on the server:

.. code-block:: sh

    iptables -A FORWARD -i wg0 -o eth0 -j ACCEPT
    iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
    ip6tables -A FORWARD -i wg0 -o eth0 -j ACCEPT
    ip6tables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

Then, in order to start WireGuard, run as ``root``:

.. code-block:: sh

    wg-quick up wg0
    systemctl enable wg-quick@wg0

    # To shut down an interface:
    wg-quick down wg0

To display WireGuard status:

.. code-block:: sh

    wg
    wg show


Disabling NetworkManager
------------------------

In order to disable NetworkManager for the interface, write into ``/etc/NetworkManager/conf.d/unmanaged.conf``:

.. code-block:: ini

    [keyfile]
    unmanaged-devices=interface-name:wg0


Listening on a DNS port used by a DNS server
--------------------------------------------

WireGuard listens on all available IP addresses (and it is designed like this according to https://lists.zx2c4.com/pipermail/wireguard/2019-March/003938.html).
If another service is bound to the loopback on the port configured by WireGuard, starting interface ``wg0`` fails, with the following kernel logs:

    wireguard: wg0: Could not create IPv4 socket
    A link change request failed with some changes committed already.
    Interface wg0 may have been left with an inconsistent configuration, please check.

This occurs for example when trying to listen to 192.0.2.42:53 (UDP) while a DNS resolver is running on 127.0.0.1:53.
A possible workaround can use a firewall to solve this issue:

* Configure WireGuard to listen on another port (eg. UDP 5353, which is used for multicast DNS)
* Redirect port 53 to 5353 for incoming traffic:

  .. code-block:: sh

      # Allow incoming connections
      nft add rule inet filter input 'udp dport {53, 5353} counter accept comment "accept WireGuard on DNS ports"'
      nft add rule inet filter output 'udp sport {53, 5353} counter accept comment "accept WireGuard on DNS ports"'

      # Load NAT module
      nft add table nat
      nft add chain nat prerouting '{ type nat hook prerouting priority 0 ; }'
      nft add chain nat postrouting '{ type nat hook postrouting priority 100 ; }'

      # Redirect module has been available since Linux Kernel 3.19.
      nft add rule nat prerouting ip daddr 192.0.2.42 udp dport 53 counter redirect to 5353

* Here is an example configuration file for nftables firewall:

  .. code-block:: text

      table inet filter {
          chain input {
              type filter hook input priority 0; policy accept;
              # ...
              udp dport 53 counter accept comment "accept WireGuard on DNS port"
              udp dport 5353 counter accept comment "accept WireGuard on mDNS port"
              # ...
          }
          chain output {
              type filter hook output priority 0; policy accept;
              # ...
              udp sport 53 counter accept comment "accept WireGuard on DNS port"
              udp sport 5353 counter accept comment "accept WireGuard on mDNS port"
          }
      }
      table nat {
          chain prerouting {
              type nat hook prerouting priority 0; policy accept;
              ip daddr 192.0.2.42 udp dport 53 counter redirect to 5353 comment "WireGuard redirect"
          }
          chain postrouting {
              type nat hook postrouting priority 100; policy accept;
          }
      }
