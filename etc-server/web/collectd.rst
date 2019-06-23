Collectd
========

Collectd is a daemon to collect system statistics in RRD (Round-Robin Database)
files. It is basically a backend daemon and several front-end exist to navigate through the data.

* Web site: https://collectd.org/
* Plugins: https://collectd.org/wiki/index.php/Table_of_Plugins
* Front-ends: https://collectd.org/wiki/index.php/List_of_front-ends


Installation
------------

Collectd is packaged for some Linux distribution. In Debian, this command
installs collectd with the default configuration::

    apt-get install collectd

The configuration is done in ``/etc/collectd/collectd.conf``. It is quite
straightforward and the wiki helps understanding the few tricky fields
(https://collectd.org/wiki/index.php/Table_of_Plugins).

Here is a basic configuration::

    LoadPlugin syslog
    <Plugin syslog>
        LogLevel info
    </Plugin>

    LoadPlugin cpu
    LoadPlugin df
    LoadPlugin disk
    LoadPlugin interface
    #LoadPlugin irq
    LoadPlugin load
    LoadPlugin memory
    LoadPlugin rrdtool
    #LoadPlugin sensors
    LoadPlugin swap

    <Plugin df>
        Device "rootfs"
        # MountPoint "/home"
        FSType "cgroup"
        FSType "devtmpfs"
        FSType "tmpfs"
        IgnoreSelected true
        ReportByDevice false
        ReportReserved true
        ReportInodes true
    </Plugin>
    <Plugin interface>
        # Don't collect statistitics about loopback interface
        Interface "lo"
        IgnoreSelected true
    </Plugin>
    <Plugin rrdtool>
        DataDir "/var/lib/collectd/rrd/"
    </Plugin>

Network setup
-------------

To centralise collected data on a server, you need to use the network plugin
(https://collectd.org/wiki/index.php/Plugin:Network). If your collectd daemon
is recent enough, you may use authenticated and encrypted communication channels
using a password.

On the server, the configuration looks like this in ``collectd.conf``::

    <Plugin network>
        # Server IP and UDP port to listen to
        <Listen "10.0.0.1" "25826">
            SecurityLevel Sign
            # This file contains for each user with password "secret":
            #     user: secret
            AuthFile "/etc/collectd/passwd"
            Interface "eth0"
        </Listen>
        MaxPacketSize 1024
    </Plugin>

On each client, ``collectd.conf`` may contain::

    <Plugin network>
        <Server "10.0.0.1" "25826">
            SecurityLevel Encrypt
            Username "user"
            Password "secret"
            Interface "eth0"
        </Server>
        TimeToLive "128"
    </Plugin>


Collection3 front-end
---------------------

Collectd package often provides front-end examples among which is Collection3.
This front-end is a web front-end written as a CGI script in Perl.
By default it will look for RRD files in ``/var/lib/collectd/rrd`` but this
can be changed by editing ``etc/collection.conf`` which contains by default::

    DataDir "/var/lib/collectd/rrd"

Collection3 needs some Perl modules:

* ``Config::General``
* ``Regexp::Common``
* ``HTML::Entities``
* ``RRDs``

On a Debian server, this command installs the needed modules::

    apt-get install lib{config-general,regexp-common,html-parser,rrds}-perl

Apache virtual host configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    <VirtualHost *:80>
        Alias /collection3/ /usr/share/doc/collectd-core/examples/collection3/
        ScriptAlias /collection3/bin/ /usr/share/doc/collectd-core/examples/collection3/bin/
        <Directory /usr/share/doc/collectd-core/examples/collection3/>
            AddHandler cgi-script .cgi
            DirectoryIndex bin/index.cgi
            Options +ExecCGI
            Order Allow,Deny
            Allow from all
        </Directory>
    </VirtualHost>

Nginx server configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    server {
        listen 80 default_server;
        location /collection3 {
            alias /usr/share/doc/collectd-core/examples/collection3;
            location ~ ^/collection3/bin/.+\.cgi$ {
                include fastcgi_params;
                fastcgi_pass unix:/var/run/fcgiwrap.socket;
            }
            location /collection3/share {
                try_files $uri $uri/ =404;
            }
            location /collection3 {
                return 301 /collection3/bin/index.cgi;
            }
        }
    }

Lighttpd server configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    # Note: if the config already enables mod_alias, you must remove it from
    # the next line
    server.modules += ( "mod_alias" "mod_cgi" )
    alias.url += ( "/collection3" => "/usr/share/doc/collectd-core/examples/collection3/" )
    $HTTP["url"] =~ "^/collection3" {
        cgi.assign = ( ".cgi" => "/usr/bin/perl" )
    }
    index-file.names += ( "bin/index.cgi" )


Collectd Graph Panel front-end
------------------------------

CGP (Collectd Graph Panel) is a better front-end than Collection3. It is
written in PHP. To install it, you just need to download latest release from
https://github.com/pommi/CGP/releases in a folder and to configure your web
server accordingly.

Official website: http://pommi.nethuis.nl/category/cgp/

To enable ``jsrrdgraph`` (to have Javascript-rendered graphs in which you can
navigate with your mouse), you just need to enable the ``canvas`` mode. This
is done by creating ``conf/config.local.php`` with::

    <?php
    $CONFIG['graph_type'] = 'canvas';

    // Here are some other useful options
    $CONFIG['graph_type'] = 'hybrid';
    $CONFIG['rrd_fetch_method'] = 'async';
    $CONFIG['overview'] = array('load', 'memory', 'swap', 'sensors', 'df', 'interface');
    $CONFIG['time_range']['default'] = 7200; // 2 hours
