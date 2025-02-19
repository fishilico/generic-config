Wireshark: analyzing HTTPS traffic
==================================

HTTPS packets can be decrypted using the server private key when non-Perfect Forward Secrecy cipher suites are used.
In most cases nowadays, this will not work.
Instead, the master secret needs to be recorded, for example using ``SSLKEYLOGFILE``:

- In Curl: https://everything.curl.dev/usingcurl/tls/sslkeylogfile
- In Firefox: https://firefox-source-docs.mozilla.org/security/nss/legacy/key_log_format/index.html
- In Chrome: option ``--ssl-key-log-file``
- In Python: https://sslkeylog.readthedocs.io/en/latest/
- Wireshark documentation: https://wiki.wireshark.org/TLS#using-the-pre-master-secret

For example:

.. code-block:: sh

    # Capture network traffic
    tshark -ni any -w capture.pcapng

    # Perform a request to a HTTPS website, for example with curl
    SSLKEYLOGFILE=keylogfile.txt curl https://wiki.wireshark.org/

    # Merge the secrets in the Decryption Secrets Block part of the capture file
    editcap --inject-secrets tls,keylogfile.txt capture.pcapng capture-with-secrets.pcapng

    # It is also possible to live-capture with the keylogfile
    # Option -V -O http displays packet details for (decrypted) HTTP
    # Option -x displays hexadecimal data
    tshark -ni any -f 'tcp port 443' -o tls.keylog_file:keylogfile.txt -V -O http -x

The keylogfile then looks like (for TLS 1.3):

.. code-block:: text

    SERVER_HANDSHAKE_TRAFFIC_SECRET f3cac18f4b5042390a8929a1bef9e5d543a214d3a163a8649843457e91a95265
        5d06ef1d3074b3ce830fddece3000e81028467c30bcd35eeee0ef867f8d22c4a1ab08db4172ac1235faab04b10e6c1e5
    EXPORTER_SECRET f3cac18f4b5042390a8929a1bef9e5d543a214d3a163a8649843457e91a95265
        dc27c85675113c4c1b2b0187cb1e2d6615b9039f66fa69e16822ccea989fb45049303113e184f266e672b1e867c03201
    SERVER_TRAFFIC_SECRET_0 f3cac18f4b5042390a8929a1bef9e5d543a214d3a163a8649843457e91a95265
        2930b243f1dab9c62dd96439355ebd22a689d3eca9e8acce9fcaad00b3ca7206ccba5258501696f774527398e8dabc49
    CLIENT_HANDSHAKE_TRAFFIC_SECRET f3cac18f4b5042390a8929a1bef9e5d543a214d3a163a8649843457e91a95265
        7ed9a53c1b24b70bcd0474ccd85323f14eeb27871d7e68c51c33ab884e3c7bd29bdb749290d564da2dc0aad212c88a65
    CLIENT_TRAFFIC_SECRET_0 f3cac18f4b5042390a8929a1bef9e5d543a214d3a163a8649843457e91a95265
        42e9ee4316095ea838daefef1cfdc2587d0fe4369d77dfed0182c2c476cfe54bd86541b3b4b488e908a7f8cf1fe2c436

For TLS 1.2 (for example using ``curl --tlsv1.2 --tls-max 1.2``):

.. code-block:: text

    CLIENT_RANDOM 0e42bf17cf0d1b3140b29b44cddedf29db7abcb5ab01f91259987678e5ce9d57
        a9e4f9da3afa588934f984c457bb6fe99a9f77e3e9dd6796c7596d683790f46ba532a1a2e308c52a81ebc03e652f1bae
