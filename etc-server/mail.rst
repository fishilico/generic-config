Mail server configuration with Postfix and dovecot
==================================================

This document describes 3 possible configurations:

* Simple server, where a local postfix server is used to send system messages
  (cron, alerts...) to system admins.
* Relay mail server, which is used to relay messages for a domain to real
  mailbox (aliases).
* Mailbox mail server, which is used to receive messages in user mailboxes which
  can then be accessed through IMAP.

Debian provides other configuration templates when installing ``postfix``
package (or through ``dpkg-reconfigure postfix``), like *Satellite system* and
*Internet with smarthost*.


Local mail server
-----------------

Here are config files for a server named ``examplehost`` in domain ``example.com``.

``/etc/postfix/main.cf``:

.. code-block:: sh

    # Some straightforward configuration
    smtpd_banner = $myhostname ESMTP $mail_name
    biff = no
    readme_directory = no
    mailbox_size_limit = 0

    # Appending .domain is the MUA's job.
    append_dot_mydomain = no

    # Uncomment the next line to generate "delayed mail" warnings
    #delay_warning_time = 4h

    # TLS parameters
    smtpd_tls_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem
    smtpd_tls_key_file=/etc/ssl/private/ssl-cert-snakeoil.key
    smtpd_use_tls=yes
    smtpd_tls_session_cache_database = btree:${data_directory}/smtpd_scache
    smtp_tls_session_cache_database = btree:${data_directory}/smtp_scache
    # Exclude some protocols to mitigate SSL attacks
    smtpd_tls_mandatory_protocols=!SSLv2,!SSLv3
    smtp_tls_mandatory_protocols=!SSLv2,!SSLv3
    smtpd_tls_protocols=!SSLv2,!SSLv3
    smtp_tls_protocols=!SSLv2,!SSLv3
    smtpd_tls_exclude_ciphers = aNULL, eNULL, EXPORT, DES, RC4, MD5, PSK, aECDH, EDH-DSS-DES-CBC3-SHA, EDH-RSA-DES-CDC3-SHA, KRB5-DE5, CBC3-SHA
    # The Diffie-Hellman parameters file can be generated with:
    # openssl dhparam -out /etc/postfix/ssl/dh_2048.pem 2048
    smtpd_tls_dh1024_param_file = ${config_directory}/ssl/dh_2048.pem

    # Fully-qualified domain name of the machine
    myhostname = examplehost.example.com

    # The domain associated with the mailing system
    # By default is it $myhostname without the first prefix
    #mydomain = example.com

    # Mail addresses without a domain will use this one
    myorigin = $myhostname

    # Networks for which the host should relay mail
    mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128
    mynetworks_style = host
    mailbox_size_limit = 0

    # Domains for which a local lookup needs to be performed
    # By default, relay_domains = $mydestination so no need to write it down
    mydestination = $myhostname, localhost.$mydomain, localhost

    # Only support local delivery
    default_transport = error: Local delivery only!

    # Define alias databases
    alias_maps = hash:/etc/aliases
    alias_database = hash:/etc/aliases

    # "smarthost" to send messages to
    relayhost =

    # For relaying messages, when submission is enabled
    smtpd_relay_restrictions = permit_mynetworks permit_sasl_authenticated defer_unauth_destination

    # Character which is used to define a local address extension
    recipient_delimiter = +

    # Only listen to the loopback interface
    inet_interfaces = loopback-only
    # If this becomes misconfigured, reject all clients not in mynetworks
    smtpd_client_restrictions = permit_mynetworks, reject

    # Use IPv4 and IPv6
    inet_protocols = all

File ``/etc/postfix/master.cf`` does not need to be changed relatively to the default one:

.. code-block:: sh

    # Postfix master process configuration file.  For details on the format
    # of the file, see the master(5) manual page (command: "man 5 master").
    #
    # Do not forget to execute "postfix reload" after editing this file.
    #
    # ==========================================================================
    # service type  private unpriv  chroot  wakeup  maxproc command + args
    #               (yes)   (yes)   (yes)   (never) (100)
    # ==========================================================================
    smtp      inet  n       -       -       -       -       smtpd
    pickup    fifo  n       -       -       60      1       pickup
    cleanup   unix  n       -       -       -       0       cleanup
    qmgr      fifo  n       -       n       300     1       qmgr
    tlsmgr    unix  -       -       -       1000?   1       tlsmgr
    rewrite   unix  -       -       -       -       -       trivial-rewrite
    bounce    unix  -       -       -       -       0       bounce
    defer     unix  -       -       -       -       0       bounce
    trace     unix  -       -       -       -       0       bounce
    verify    unix  -       -       -       -       1       verify
    flush     unix  n       -       -       1000?   0       flush
    proxymap  unix  -       -       n       -       -       proxymap
    proxywrite unix -       -       n       -       1       proxymap
    smtp      unix  -       -       -       -       -       smtp
    relay     unix  -       -       -       -       -       smtp
    showq     unix  n       -       -       -       -       showq
    error     unix  -       -       -       -       -       error
    retry     unix  -       -       -       -       -       error
    discard   unix  -       -       -       -       -       discard
    local     unix  -       n       n       -       -       local
    virtual   unix  -       n       n       -       -       virtual
    lmtp      unix  -       -       -       -       -       lmtp
    anvil     unix  -       -       -       -       1       anvil
    scache    unix  -       -       -       -       1       scache
    #
    # ====================================================================
    # Interfaces to non-Postfix software. Be sure to examine the manual
    # pages of the non-Postfix software to find out what options it wants.
    #
    # Many of the following services use the Postfix pipe(8) delivery
    # agent.  See the pipe(8) man page for information about ${recipient}
    # and other message envelope options.
    # ====================================================================
    #
    # maildrop. See the Postfix MAILDROP_README file for details.
    # Also specify in main.cf: maildrop_destination_recipient_limit=1
    #
    maildrop  unix  -       n       n       -       -       pipe
      flags=DRhu user=vmail argv=/usr/bin/maildrop -d ${recipient}

Finally ``/etc/aliases`` may contain some aliases so that most messages get
sent to user ``localuser``:

.. code-block:: sh

    # See man 5 aliases for format
    root: localuser
    mailer-daemon: postmaster
    abuse: root
    hostmaster: root
    postmaster: root
    nobody: root
    webmaster: root
    www: root

Run ``newaliases`` every time this file is updated.

To validate the configuration, run ``postfix check``.


Relay-mode configuration
------------------------

This section describes a Postfix configuration for a relay domain, which
transmits e-mails to addresses behind aliases.  To set-up such a server,
it is possible to use the same configuration as the local mail server, with
a modification to ``/etc/postfix/main.cf`` to allow connections from all
network interfaces::

    inet_interfaces = all

The aliases can then be configured in ``/etc/aliases``, or more generally to
the file configured in ``alias_maps`` and ``alias_database`` variables

.. code-block:: console

    $ postconf |grep '^alias_'
    alias_database = hash:/etc/aliases
    alias_maps = hash:/etc/aliases


To send local emails as ``root+hostname@example.com`` instead of
``root@hostname.example.com``, a canonical mapping can be added:

* in ``/etc/postfix/main.cf``::

    canonical_classes = envelope_sender, header_sender, header_recipient
    canonical_maps = regexp:/etc/postfix/canonical.regexp

* in ``/etc/postfix/canonical.regexp``::

    /^([^@]*)@([a-zA-Z0-9]*)\.(example\.com)/ ${1}+${2}@${3}

* and finally compile the mapping with ``postmap /etc/postfix/canonical.regexp``.


To enable SMTPS as STARTTLS over SMTP (TCP port 587), add the following lines to
``/etc/postfix/master.cf``::

    submission inet n       -       -       -       -       smtpd
      -o syslog_name=postfix/submission
      -o smtpd_tls_security_level=encrypt
      -o smtpd_sasl_auth_enable=yes
      -o smtpd_client_restrictions=permit_sasl_authenticated,reject
      -o smtpd_recipient_restrictions=
      -o smtpd_relay_restrictions=permit_sasl_authenticated,reject
      -o milter_macro_daemon_name=ORIGINATING

In this configuration ``smtpd_client_restrictions`` disables
``reject_unauth_destination`` so that relaying over SMTPS works.

On the firewall, TCP ports 25 and 587 need to be opened for SMTP and SMTPS, and
143 and 993 for IMAP (with STARTTLS) and IMAPS.  With iptables, the commands
are::

    iptables -A INPUT -p tcp -m multiport --dports 25,143,587,993 -j ACCEPT
    iptables -A OUTPUT -p tcp -m multiport --sports 25,143,587,993 -j ACCEPT
    ip6tables -A INPUT -p tcp -m multiport --dports 25,143,587,993 -j ACCEPT
    ip6tables -A OUTPUT -p tcp -m multiport --sports 25,143,587,993 -j ACCEPT


Mailbox mail server
-------------------

To setup a mail server with mailboxes, the first step is to setup the relay-mode
configuration, and then add local accounts and configure dovecot to serve the
mailbox of these accounts over IMAP.

To install dovecot on Debian, two packages need to be installed::

    aptitude install dovecot-core dovecot-imapd

Then the default configuration is available through ``doveconf -n`` command.
This can be use as a source of inspiration, but customizations are simpler when
everything lies in a single file.  By default, ``dovecot.conf`` includes every
file matched by glob pattern ``/etc/dovecot/conf.d/*.conf`` and tries to include
``/etc/dovecot/local.conf`` with::

    !include_try local.conf

To fully control the configuration, it is possible to comment
``!include conf.d/*.conf`` and write in ``/etc/dovecot/local.conf``:

.. code-block:: sh

    # Enable and require TLS communication
    ssl = required
    ssl_cert = </etc/ssl/dovecot/dovecot.crt
    # Do not forget to make /etc/ssl/dovecot/dovecot.key only readable by root
    ssl_key = </etc/ssl/dovecot/dovecot.key

    # DH parameters generated with:
    # openssl dhparam -out /usr/share/dovecot/dh.pem 4096
    ssl_dh = </usr/share/dovecot/dh.pem

    # Disable plaintext authentication
    disable_plaintext_auth = yes

    # Authenticate using PAM
    auth_mechanisms = plain
    userdb {
      driver = passwd
    }
    passdb {
      driver = pam
    }

    # Use Maildir
    mail_location = maildir:~/Maildir
    namespace inbox {
      inbox = yes
      #location =
      #prefix =
      separator = /
    }

    # Create a socket to use dovecot authentication in postfix
    service auth {
      unix_listener /var/spool/postfix/private/auth {
        mode = 0660
        user = postfix
        group = postfix
      }
    }


Also configure Postfix to use qmail-style delivery, with this in
``/etc/postfix/main.cf``:

.. code-block:: sh

    # Deliver mails in ~/Maildir/ (the trailing / is required)
    home_mailbox = Maildir/

The dovecot authentication can then be activated in Postfix by updating the
entry for SMTPS service in ``/etc/postfix/master.cf``::

    submission inet n       -       -       -       -       smtpd
      -o syslog_name=postfix/submission
      -o smtpd_tls_wrappermode=no
      -o smtpd_tls_security_level=encrypt
      -o smtpd_sasl_auth_enable=yes
      -o smtpd_recipient_restrictions=permit_mynetworks,permit_sasl_authenticated,reject
      -o milter_macro_daemon_name=ORIGINATING
      -o smtpd_sasl_type=dovecot
      -o smtpd_sasl_path=private/auth

Moreover in Postfix configuration, local delivery is configured with
``local_recipient_maps`` which has a default value which is correct:

.. code-block:: sh

    # postconf local_recipient_maps
    local_recipient_maps = proxy:unix:passwd.byname $alias_maps



Documentation
-------------

Here are some useful links to configure a mail server:

* https://wiki.archlinux.org/index.php/Postfix
* https://wiki.archlinux.org/index.php/Virtual_user_mail_system
* http://wiki2.dovecot.org/QuickConfiguration
* http://wiki2.dovecot.org/MailboxFormat A list of mailbox formats
