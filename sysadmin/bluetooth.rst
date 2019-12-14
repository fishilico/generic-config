Bluetooth on Linux
==================

Introduction
------------

Bluetooth is a protocol that can be used to communicate between two devices that are paired together.
It can be used to connect wireless devices (keyboard, mouse, sound speaker, etc.), to transmit files (with OBEX, for Object Exchange) and even to share Internet connectivity (using BNEP, the Bluetooth Network Encapsulation Protocol, which uses a L2CAP channel to transmit IP packets).
The protocol has been developed since at least 1989 and Bluetooth has been standardised as IEEE 802.15.1.
It operates in UHF radio waves, between 2.400 and 2.485 GHz.
More information can be found on its Wikipedia page: https://en.wikipedia.org/wiki/Bluetooth

On Linux, several steps need to be performed in order to use Bluetooth:

* Install the packages that provide Bluetooth service and programs: ``bluez`` and ``bluez-utils``
* Unblock the radio interface, if it has been blocked:

  .. code-block:: sh

      rfkill unblock bluetooth

* Start the service:

  .. code-block:: sh

      systemctl start bluetooth.service

* Start a ``bluetoothctl`` CLI and power the device on by issuing ``power on``.

It is possible to record the Bluetooth communications using the monitor, ``btmon -w file.bt``.
This command produces BTSnoop files that can be opened for example in Wireshark.


Connecting an Android phone to a laptop using Bluetooth
-------------------------------------------------------

Here is a trace on a laptop that get paired with an Android phone via Bluetooth (``[bluetooth]#`` is the user prompt):

.. code-block:: sh

    $ bluetoothctl
    [CHG] Controller 01:23:45:67:89:AB Pairable: yes

    [bluetooth]# power on
    [CHG] Controller 01:23:45:67:89:AB Class: 0x0000010c
    Changing power on succeeded
    [CHG] Controller 01:23:45:67:89:AB Powered: yes

    [bluetooth]# scan on
    [NEW] Device 55:44:33:22:11:00 AndroidPhone

    [bluetooth]# devices
    Device 55:44:33:22:11:00 AndroidPhone

    [bluetooth]# pair 55:44:33:22:11:00
    Attempting to pair with 55:44:33:22:11:00
    [CHG] Device 55:44:33:22:11:00 Connected: yes
    Request confirmation
    [agent] Confirm passkey 123123 (yes/no): yes
    [CHG] Device 55:44:33:22:11:00 Modalias: bluetooth:v0075p0100d0201
    [CHG] Device 55:44:33:22:11:00 UUIDs: 00001105-0000-1000-8000-00805f9b34fb
    [CHG] Device 55:44:33:22:11:00 UUIDs: 0000110a-0000-1000-8000-00805f9b34fb
    [CHG] Device 55:44:33:22:11:00 UUIDs: 0000110c-0000-1000-8000-00805f9b34fb
    [CHG] Device 55:44:33:22:11:00 UUIDs: 0000110e-0000-1000-8000-00805f9b34fb
    [CHG] Device 55:44:33:22:11:00 UUIDs: 00001112-0000-1000-8000-00805f9b34fb
    [CHG] Device 55:44:33:22:11:00 UUIDs: 00001115-0000-1000-8000-00805f9b34fb
    [CHG] Device 55:44:33:22:11:00 UUIDs: 00001116-0000-1000-8000-00805f9b34fb
    [CHG] Device 55:44:33:22:11:00 UUIDs: 0000111f-0000-1000-8000-00805f9b34fb
    [CHG] Device 55:44:33:22:11:00 UUIDs: 0000112d-0000-1000-8000-00805f9b34fb
    [CHG] Device 55:44:33:22:11:00 UUIDs: 0000112f-0000-1000-8000-00805f9b34fb
    [CHG] Device 55:44:33:22:11:00 UUIDs: 00001132-0000-1000-8000-00805f9b34fb
    [CHG] Device 55:44:33:22:11:00 UUIDs: 00001200-0000-1000-8000-00805f9b34fb
    [CHG] Device 55:44:33:22:11:00 UUIDs: 00001800-0000-1000-8000-00805f9b34fb
    [CHG] Device 55:44:33:22:11:00 UUIDs: 00001801-0000-1000-8000-00805f9b34fb
    [CHG] Device 55:44:33:22:11:00 UUIDs: a23d00bc-217c-123b-9c00-fc44577136ee
    [CHG] Device 55:44:33:22:11:00 ServicesResolved: yes
    [CHG] Device 55:44:33:22:11:00 Paired: yes
    Pairing successful
    [CHG] Device 55:44:33:22:11:00 ServicesResolved: no
    [CHG] Device 55:44:33:22:11:00 Connected: no

    [bluetooth]# info 55:44:33:22:11:00
    Device 55:44:33:22:11:00 (public)
        Name: AndroidPhone
        Alias: AndroidPhone
        Class: 0x005a020c
        Icon: phone
        Paired: yes
        Trusted: no
        Blocked: no
        Connected: no
        LegacyPairing: no
        UUID: OBEX Object Push          (00001105-0000-1000-8000-00805f9b34fb)
        UUID: Audio Source              (0000110a-0000-1000-8000-00805f9b34fb)
        UUID: A/V Remote Control Target (0000110c-0000-1000-8000-00805f9b34fb)
        UUID: A/V Remote Control        (0000110e-0000-1000-8000-00805f9b34fb)
        UUID: Headset AG                (00001112-0000-1000-8000-00805f9b34fb)
        UUID: PANU                      (00001115-0000-1000-8000-00805f9b34fb)
        UUID: NAP                       (00001116-0000-1000-8000-00805f9b34fb)
        UUID: Handsfree Audio Gateway   (0000111f-0000-1000-8000-00805f9b34fb)
        UUID: SIM Access                (0000112d-0000-1000-8000-00805f9b34fb)
        UUID: Phonebook Access Server   (0000112f-0000-1000-8000-00805f9b34fb)
        UUID: Message Access Server     (00001132-0000-1000-8000-00805f9b34fb)
        UUID: PnP Information           (00001200-0000-1000-8000-00805f9b34fb)
        UUID: Generic Access Profile    (00001800-0000-1000-8000-00805f9b34fb)
        UUID: Generic Attribute Profile (00001801-0000-1000-8000-00805f9b34fb)
        UUID: Vendor specific           (a23d00bc-217c-123b-9c00-fc44577136ee)
        Modalias: bluetooth:v0075p0100d0201

The information about the peering (for example encryption and signature keys for messages) can be extracted from ``/var/lib/bluetooth/01:23:45:67:89:AB/55:44:33:22:11:00/info``.

When using NetworkManager, a Bluetooth interface can be configured in order to use the phone Internet connection wirelessly.
This produces a BNEP interface (Bluetooth Network Encapsulation Protocol) named for example ``bnep0``, where a DHCP client can be used in order to get the IPv4 network configuration.
This can cause the following message to appear in ``bluetoothctl``::

    Authorize service
    [agent] Authorize service 0000000f-0000-1000-8000-00805f9b34fb (yes/no): yes
    [AndroidPhone]#

This UUID matches the BNEP service and is needed in order to exchange data.
Such an UUID can be searched in bluez header files such as https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/lib/uuid.h?h=5.51
