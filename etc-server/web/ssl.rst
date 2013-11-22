SSL configuration on an Apache server
=====================================

Many websites describe how to correctly set up a SSL/TLS web server with a
secure configuration. Here is a list of some that I've found:

* http://hynek.me/articles/hardening-your-web-servers-ssl-ciphers/
* https://wiki.mozilla.org/Security/Server_Side_TLS

Here are example configurations for ssl.example.com host with a certificate
signed by StartSSL.

Apache::

    <IfModule mod_ssl.c>
    <VirtualHost *:443>
        ServerName ssl.example.com
        SSLEngine on
        SSLCertificateFile /etc/ssl/ssl.example.com.crt
        SSLCertificateKeyFile /etc/ssl/ssl.example.com.key
        SSLCertificateChainFile /etc/ssl/startssl-sub.class1.server.ca.pem
        SSLCACertificateFile /etc/ssl/certs
        SSLProtocol ALL -SSLv2
        SSLHonorCipherOrder On
        SSLCipherSuite ECDHE-RSA-AES128-SHA256:AES128-GCM-SHA256:RC4:HIGH:!MD5:!aNULL:!EDH
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
        ssl_certificate /etc/nginx/ssl/ssl.example.com_and_intermediates.pem;
        ssl_certificate_key /etc/nginx/ssl/ssl.example.com.key;
        ssl_dhparam /etc/nginx/ssl/dhparam.pem;
        ssl_session_timeout 5m;
        ssl_protocols SSLv3 TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers ECDHE-RSA-AES128-SHA256:AES128-GCM-SHA256:RC4:HIGH:!MD5:!aNULL:!EDH;
        ssl_prefer_server_ciphers on;
        ssl_session_cache shared:SSL:50m;

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

    openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048


Testing configuration
---------------------

Here are several commands to be used to check a running HTTPS webserver.

Establish an TLS (or SSL) connection::

    openssl s_client -connect ssl.example.com:443 -servername ssl.example.com -showcerts

Use a web service, like Qualys’s SSL Server Test:
https://www.ssllabs.com/ssltest/

This web page helps displays what your browser supports:
https://www.ssllabs.com/ssltest/viewMyClient.html
