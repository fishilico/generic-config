Git Web
=======

To configure Git Web on a server, you need to install ``git`` and ``gitweb``
packages. With Apache, the configuration is already included within ``gitweb``
package. With Nginx, you need FastCGI (``fcgiwrap`` package on Debian) and some
configuration in an host file.

Let's suppose you host Git repositories in ``/home/git`` on your server.
You would like to setup a web server (Apache or Nginx) to be able to use ``git``
over HTTP and to browse your repositories using the Git Web interface.

Documentation:

* https://www.kernel.org/pub/software/scm/git/docs/git-http-backend.html
* https://wiki.archlinux.org/index.php/gitweb (ArchLinux)

Gitweb configuration
--------------------

Here is an example of ``/home/git/gitweb.conf``::

    # path to git projects (<project>.git)
    $projectroot = "/home/git";

    # directory to use for temp files
    $git_temp = "/tmp";

    # target of the home link on top of all pages
    #$home_link = $my_uri || "/";

    # html text to include at home page
    #$home_text = "indextext.html";

    # file with project list; by default, simply scan the projectroot dir.
    #$projects_list = $projectroot;

    # stylesheet to use
    #@stylesheets = ("static/gitweb.css");

    # javascript code for gitweb
    #$javascript = "static/gitweb.js";

    # logo to use
    #$logo = "static/git-logo.png";
    #$logo_url = "http://localhost/git";
    #$logo_label = "Localhost Git Repositories";

    # the 'favicon'
    #$favicon = "static/git-favicon.png";

    # git-diff-tree(1) options to use for generated patches
    #@diff_opts = ("-M");
    @diff_opts = ();

    # This prevents gitweb to show hidden repositories
    #$export_ok = "git-daemon-export-ok";
    #$strict_export = 1;

    # This lets it make the URLs you see in the header
    #@git_base_url_list = ( 'git://localhost/git' );

    # Features: syntax highlighting and blame view
    $feature{'highlight'}{'default'} = [1];
    $feature{'blame'}{'default'} = [1];


Apache configuration
--------------------
::

    <VirtualHost *:80>
        ServerName localhost

        SetEnv GIT_PROJECT_ROOT /home/git
        SetEnv GIT_HTTP_EXPORT_ALL

        AliasMatch ^/git/(.*/objects/[0-9a-f]{2}/[0-9a-f]{38})$          /home/git/$1
        AliasMatch ^/git/(.*/objects/pack/pack-[0-9a-f]{40}.(pack|idx))$ /home/git/$1
        # Remove git-receive-pack in next line to forbid push to this server
        ScriptAliasMatch \
                "(?x)^/git/(.*/(HEAD | \
                                info/refs | \
                                objects/info/[^/]+ | \
                                git-(upload|receive)-pack))$" \
                /usr/libexec/git-core/git-http-backend/$1

        ScriptAlias /git/ /usr/share/gitweb/gitweb.cgi/
        Alias /git /usr/share/gitweb
        <Directory "/usr/share/gitweb/">
            AddHandler cgi-script .cgi
            DirectoryIndex gitweb.cgi
            Options +ExecCGI

            AllowOverride None
            Order allow,deny
            Allow from all

            SetEnv GITWEB_CONFIG /home/git/gitweb.conf
        </Directory>
    </VirtualHost>


Nginx configuration
-------------------
::

    server {
        listen 80 default_server;
        listen [::]:80 default_server ipv6only=on;
        #root /var/www/...;
        # Server name is used in the title of GitWeb pages
        server_name localhost;

        location / {
            try_files $uri $uri/ /index.html;
        }

        # Git over HTTP
        location ~ ^/git/.*\.git/objects/([0-9a-f]+/[0-9a-f]+|pack/pack-[0-9a-f]+.(pack|idx))$ {
            root /home/git;
        }
        # Remove git-receive-pack in next line to forbid push to this server
        location ~ ^/git/(.*\.git/(HEAD|info/refs|objects/info/.*|git-(upload|receive)-pack))$ {
            rewrite ^/git(/.*)$ $1 break;
            fastcgi_pass unix:/var/run/fcgiwrap.socket;
            fastcgi_param SCRIPT_FILENAME     /usr/lib/git-core/git-http-backend;
            fastcgi_param PATH_INFO           $uri;
            fastcgi_param GIT_PROJECT_ROOT    /home/git;
            fastcgi_param GIT_HTTP_EXPORT_ALL "";
            include fastcgi_params;
        }

        # Git web
        location /git/static/ {
            alias /usr/share/gitweb/static/;
        }
        location /git/ {
            fastcgi_pass unix:/var/run/fcgiwrap.socket;
            fastcgi_param SCRIPT_FILENAME     /usr/share/gitweb/gitweb.cgi;
            fastcgi_param PATH_INFO           $uri/git;
            fastcgi_param GITWEB_CONFIG       /home/git/gitweb.conf;
            fastcgi_param GIT_HTTP_EXPORT_ALL "";
            include fastcgi_params;
        }
    }


Tips & Tricks
-------------

* Gitweb is written in Perl so to use FastCGI you need to install
  ``libcgi-fast-perl``. On Debian::

    apt-get install libcgi-fast-perl

* To color files with syntax highlighting, you need to install ``highlight``
  program. On Debian::

    apt-get install highlight
