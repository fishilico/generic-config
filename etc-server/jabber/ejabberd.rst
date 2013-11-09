ejabberd configuration
======================

Here is how ejabberd can be installed and configured on a Debian system.

First install the package::

    apt-get install ejabberd

``debconf`` asks for several things:

- a domain name, like ``example.com``
- an account to administrate the server, let's call it ``admin``

Then, the configuration file (``/etc/ejabberd/ejabberd.cfg``) looks like::

    %% Options which are set by Debconf and managed by ucf

    %% Admin user
    {acl, admin, {user, "admin", "example.com"}}.

    %% Hostname
    {hosts, ["example.com"]}.


By default, ejabberd listens on 3 TCP ports::

    {listen,
     [
      {5222, ejabberd_c2s, [
        {access, c2s},
        {shaper, c2s_shaper},
        {max_stanza_size, 65536},
        %%zlib,
        starttls, {certfile, "/etc/ejabberd/ejabberd.pem"}
        ]},
      {5269, ejabberd_s2s_in, [
        {shaper, s2s_shaper},
        {max_stanza_size, 131072}
        ]},
      {5280, ejabberd_http, [
        %%{request_handlers,
        %% [
        %%  {["pub", "archive"], mod_http_fileserver}
        %% ]},
        %%captcha,
        http_bind,
        http_poll,
        web_admin
        ]}
     ]}.
    {s2s_use_starttls, true}.
    {s2s_certfile, "/etc/ejabberd/ejabberd.pem"}.

This enable web administration on an HTTP server running on port 5280. Use an
URL such as to access to administration http://example.com:5280/admin/. Note
that this is note secure (no HTTPS) so you may want to set-up a front-end to
access to this server (reverse proxy, VPN, firewall, ...).

To add a new user, you just need to run::

    ejabberdctl register mynewuser example.com 'UserPassword'


DNS configuration
-----------------
Here is how a DNS zone may be configured::

    ;service.proto.name          class rr   pri weight port target
    _jabber._tcp.example.com.      IN  SRV  10    0    5269 jabber.example.com.
    _xmpp-server._tcp.example.com. IN  SRV  10    0    5269 jabber.example.com.
    _xmpp-client._tcp.example.com. IN  SRV  10    0    5222 jabber.example.com.

    jabber IN A 10.22.33.44


Bitlbee configutation
---------------------
Bitlbee can be used to interact with jabber through an IRC server.
Here are some useful commands from http://wiki.bitlbee.org/quickstart::

    account add jabber bitlbee@example.com UserPassword
    account jabber on

In ``account list``, this new account is associated with an ID (like 0). Once
you know this ID, you may run::

    add 0 myuser@example.com


Source
------
http://wiki.linuxwall.info/doku.php/en:ressources:articles:ejabberd
