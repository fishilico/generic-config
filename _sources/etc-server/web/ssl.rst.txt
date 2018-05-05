SSL configuration on a web server
=================================

Many websites describe how to correctly set up a SSL/TLS web server with a
secure configuration. Here is a list of some that I've found:

* http://hynek.me/articles/hardening-your-web-servers-ssl-ciphers/
* https://wiki.mozilla.org/Security/Server_Side_TLS
* https://bettercrypto.org/ (with a paper which advices a configuration)

Here are example configurations for ssl.example.com host with a certificate
signed by StartSSL (https://www.startssl.com/) or Let's encrypt
(https://letsencrypt.org/) or AlwaysOnSSL (https://alwaysonssl.com/).

Apache::

    <IfModule mod_ssl.c>
    <VirtualHost *:443>
        ServerName ssl.example.com
        SSLEngine on
        SSLCertificateFile /etc/ssl/ssl.example.com.crt
        SSLCertificateKeyFile /etc/ssl/ssl.example.com.key
        SSLCertificateChainFile /etc/ssl/intermediate.pem
        SSLCACertificateFile /etc/ssl/certs
        SSLProtocol ALL -SSLv2 -SSLv3
        SSLHonorCipherOrder On
        SSLCipherSuite ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA:ECDHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA;
        SSLCompression Off

        # Enable this if your want HSTS (recommended, but be careful)
        # Header add Strict-Transport-Security "max-age=15768000"

        # OCSP Stapling, only in httpd 2.3.3 and later
        SSLUseStapling On
        SSLStaplingResponderTimeout 5
        SSLStaplingReturnResponderErrors off
        SSLStaplingCache shmcb:/var/run/ocsp(128000)
    </VirtualHost>
    </IfModule>

Nginx::

    server {
        listen 443;
        server_name ssl.example.com;
        ssl on;
        # certs sent to the client in SERVER HELLO are concatenated
        ssl_certificate /etc/ssl/ssl.example.com_and_intermediates.pem;
        ssl_certificate_key /etc/ssl/ssl.example.com.key;
        ssl_dhparam /etc/ssl/dhparam.pem;
        ssl_session_timeout 10m;
        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA:ECDHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA;
        ssl_prefer_server_ciphers on;
        ssl_session_cache shared:SSL:10m;

        # Enable this if your want HSTS (recommended, but be careful)
        # add_header Strict-Transport-Security max-age=15768000;

        # OCSP Stapling
        # fetch OCSP records from URL in ssl_certificate and cache them
        ssl_stapling on;
        ssl_stapling_verify on;
        # verify chain of trust of OCSP response using Root CA and Intermediate certs
        ssl_trusted_certificate /path/to/root_CA_cert_plus_intermediates;
        # IP address of the DNS resolver to be used to obtain the IP address of
        # the OCSP responder
        resolver 127.0.0.1;
    }

To generate the Diffie-Hellman parameters for DHE ciphersuites, use::

    openssl dhparam -out /etc/ssl/dhparam.pem 4096


Testing configuration
---------------------

Here are several commands to be used to check a running HTTPS web server.

Establish an TLS (or SSL) connection::

    openssl s_client -connect ssl.example.com:443 -servername ssl.example.com -showcerts

Use a web service, like Qualys' SSL Server Test:
https://www.ssllabs.com/ssltest/

This web page helps displays what your browser supports:
https://www.ssllabs.com/ssltest/viewMyClient.html


Using Let's Encrypt
-------------------

The official Let's Encrypt client (https://github.com/letsencrypt/letsencrypt)
needs to run as root on the server which will use the certificate.  Thankfully
there exists other ways of signing certificates:

* https://github.com/diafygi/letsencrypt-nosudo Let's Encrypt Without Sudo
* https://gethttpsforfree.com/ Get HTTPS for free! (web interface to Let's Encrypt)

These methods rely on some openssl commands to use an account key.

* To create an account key and print the associated public key::

    openssl genrsa 4096 > account.key
    openssl rsa -in account.key -pubout

* To sign what needs to be signed::

    echo -n 'Content' | openssl dgst -sha256 -hex -sign account.key

To generate a Certificate Signing Request (CSR) for a domain with X509v3
Subject Alternative Name (SAN), these commands can be used::

    openssl genrsa 4096 > ssl.example.com.key
    openssl req -new -sha256 -key ssl.example.com.key -subj "/" \
        -reqexts SAN -config <(cat /etc/ssl/openssl.cnf
        <(printf "[SAN]\nsubjectAltName=DNS:example.com,DNS:ssl.example.com"))

On some systems the OpenSSL configuration file lie elsewhere, for example in
``/etc/pki/tls/openssl.cnf`` or in ``/System/Library/OpenSSL/openssl.cnf``
(Mac OS).

In order to validate the ownership of a domain, a generated file needs to be
served over HTTP (not HTTPS), which may for example give::

    $ curl http://ssl.example.com/.well-known/acme-challenge/abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQ
    abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQ.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefg

To do this on a live (production system), a possible way consists in serving
/.well-known/acme-challenge from a specific directory, where an administrator
will put the needed files.  With nginx, a configuration can be::

    server {
        listen 127.0.0.1:80;
        listen [::1]:80;
        server_name ssl.example.com;

        # Let's encrypt
        location /.well-known/acme-challenge {
            alias /var/acme-challenge/ssl.example.com;
        }
        location / {
            rewrite ^(.*) https://ssl.example.com$1 permanent;
        }
    }

Then an admin can put the files needed for Let's Encrypt to verify domain
ownership in directory ``/var/acme-challenge/ssl.example.com/``.
