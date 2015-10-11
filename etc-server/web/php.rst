PHP Configuration Customization
================================

Here are some tips & tricks to configure a php.ini file.

``php.ini`` configuration
-------------------------

Common important configuration options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here are some options I use in both development and production environments::

    ; Decides whether PHP may expose the fact that it is installed on the server
    ; (e.g. by adding its signature to the Web server header).  It is no security
    ; threat in any way, but it makes it possible to determine whether you use PHP
    ; on your server or not.
    ; http://php.net/expose-php
    ;;expose_php = On
    expose_php = Off

    include_path = ".:/usr/share/pear:/usr/share/php"

    ; Whether to allow the treatment of URLs (like http:// or ftp://) as files.
    ; http://php.net/allow-url-fopen
    ;;allow_url_fopen = On
    allow_url_fopen = Off

    ; Whether to allow include/require to open URLs (like http:// or ftp://) as files.
    ; http://php.net/allow-url-include
    allow_url_include = Off

    [Date]
    ; Defines the default timezone used by the date functions
    ; http://php.net/date.timezone
    ;date.timezone =
    date.timezone = "Europe/Paris"

Development vs. Production options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here are the options which are likely to be different in dev and in prod::

    ; open_basedir, if set, limits all file operations to the defined directory
    ; and below.  This directive makes most sense if used in a per-directory
    ; or per-virtualhost web server configuration file. This directive is
    ; *NOT* affected by whether Safe Mode is turned On or Off.
    ; http://php.net/open-basedir
    ; Production value:
    open_basedir = /srv/http/:/tmp/:/usr/share/pear/:/usr/share/webapps/
    ; Development value:
    open_basedir = /srv/http/:/tmp/:/usr/share/pear/:/usr/share/php/:/dev/urandom:/media/:/home:/usr/bin/phpunit

    ; This directive informs PHP of which errors, warnings and notices you would like
    ; it to take action for. The recommended way of setting values for this
    ; directive is through the use of the error level constants and bitwise
    ; operators. The error level constants are below here for convenience as well as
    ; some common settings and their meanings.
    ; By default, PHP is set to take action on all errors, notices and warnings EXCEPT
    ; those related to E_NOTICE and E_STRICT, which together cover best practices and
    ; recommended coding standards in PHP. For performance reasons, this is the
    ; recommend error reporting setting. Your production server shouldn't be wasting
    ; resources complaining about best practices and coding standards. That's what
    ; development servers and development settings are for.
    ; Note: The php.ini-development file has this setting as E_ALL. This
    ; means it pretty much reports everything which is exactly what you want during
    ; development and early testing.
    ;
    ; Error Level Constants:
    ; E_ALL             - All errors and warnings (includes E_STRICT as of PHP 5.4.0)
    ; E_ERROR           - fatal run-time errors
    ; E_RECOVERABLE_ERROR  - almost fatal run-time errors
    ; E_WARNING         - run-time warnings (non-fatal errors)
    ; E_PARSE           - compile-time parse errors
    ; E_NOTICE          - run-time notices (these are warnings which often result
    ;                     from a bug in your code, but it's possible that it was
    ;                     intentional (e.g., using an uninitialized variable and
    ;                     relying on the fact it's automatically initialized to an
    ;                     empty string)
    ; E_STRICT          - run-time notices, enable to have PHP suggest changes
    ;                     to your code which will ensure the best interoperability
    ;                     and forward compatibility of your code
    ; E_CORE_ERROR      - fatal errors that occur during PHP's initial startup
    ; E_CORE_WARNING    - warnings (non-fatal errors) that occur during PHP's
    ;                     initial startup
    ; E_COMPILE_ERROR   - fatal compile-time errors
    ; E_COMPILE_WARNING - compile-time warnings (non-fatal errors)
    ; E_USER_ERROR      - user-generated error message
    ; E_USER_WARNING    - user-generated warning message
    ; E_USER_NOTICE     - user-generated notice message
    ; E_DEPRECATED      - warn about code that will not work in future versions
    ;                     of PHP
    ; E_USER_DEPRECATED - user-generated deprecation warnings
    ;
    ; Common Values:
    ;   E_ALL (Show all errors, warnings and notices including coding standards.)
    ;   E_ALL & ~E_NOTICE  (Show all errors, except for notices)
    ;   E_ALL & ~E_NOTICE & ~E_STRICT  (Show all errors, except for notices and coding standards warnings.)
    ;   E_COMPILE_ERROR|E_RECOVERABLE_ERROR|E_ERROR|E_CORE_ERROR  (Show only errors)
    ; Default Value: E_ALL & ~E_NOTICE & ~E_STRICT & ~E_DEPRECATED
    ; Development Value: E_ALL
    ; Production Value: E_ALL & ~E_DEPRECATED & ~E_STRICT
    ; http://php.net/error-reporting
    ;;error_reporting = E_ALL & ~E_DEPRECATED & ~E_STRICT
    error_reporting = E_ALL | E_STRICT

    ; This directive controls whether or not and where PHP will output errors,
    ; notices and warnings too. Error output is very useful during development, but
    ; it could be very dangerous in production environments. Depending on the code
    ; which is triggering the error, sensitive information could potentially leak
    ; out of your application such as database usernames and passwords or worse.
    ; It's recommended that errors be logged on production servers rather than
    ; having the errors sent to STDOUT.
    ; Possible Values:
    ;   Off = Do not display any errors
    ;   stderr = Display errors to STDERR (affects only CGI/CLI binaries!)
    ;   On or stdout = Display errors to STDOUT
    ; Default Value: On
    ; Development Value: On
    ; Production Value: Off
    ; http://php.net/display-errors
    ;;display_errors = Off
    display_errors = On

    ; The display of errors which occur during PHP's startup sequence are handled
    ; separately from display_errors. PHP's default behavior is to suppress those
    ; errors from clients. Turning the display of startup errors on can be useful in
    ; debugging configuration problems. But, it's strongly recommended that you
    ; leave this setting off on production servers.
    ; Default Value: Off
    ; Development Value: On
    ; Production Value: Off
    ; http://php.net/display-startup-errors
    ;;display_startup_errors = Off
    display_startup_errors = On

PHP size limits
~~~~~~~~~~~~~~~

In some configurations it may be needed to raise the limits on memory resource
usage.  Here are some relevant options in ``php.ini``::

    ; Maximum amount of memory a script may consume (128MB)
    ; http://php.net/memory-limit
    ;memory_limit = 128M
    memory_limit = 1G

    ; Maximum size of POST data that PHP will accept.
    ; Its value may be 0 to disable the limit. It is ignored if POST data reading
    ; is disabled through enable_post_data_reading.
    ; http://php.net/post-max-size
    ;post_max_size = 8M
    post_max_size = 2G

    ; Maximum allowed size for uploaded files.
    ; http://php.net/upload-max-filesize
    ;upload_max_filesize = 2M
    upload_max_filesize = 2G

Extensions list
---------------

Here are some extensions to enable for most common-purpose websites:

- ``curl``
- ``gd``
- ``gettext``
- ``iconv``
- ``mcrypt``
- ``mysqli``
- ``mysql``
- ``pdo_mysql``
- ``pdo_pgsql``
- ``pdo_sqlite``
- ``pgsql``
- ``sqlite3``

Apache configuration
--------------------

Apache has a module to run PHP. On Debian its installation is simple::

    apt-get install libapache2-mod-php5
    a2enmod php5

This will automatically load ``/usr/lib/apache2/modules/libphp5.so`` and
configure Apache so that ``.php`` files (and other extensions) are handled to
PHP module for execution.

To disable the PHP engine for some folders, use ``php_admin_value`` directive
in ``<Directory>`` sections. For example this disables PHP in home directories::

    <IfModule mod_userdir.c>
        <Directory /home/*/public_html>
            php_admin_value engine Off
        </Directory>
    </IfModule>

Rewrite module
~~~~~~~~~~~~~~

To have nicer URLs, many websites setup a hook to call ``index.php`` with a part of the path in its parameter. In Apache, this behavior is achieved thanks to the rewrite module. To enable this module on Debian, run::

    a2enmod rewrite

Then ensure that you have this directive in your virtual host configuration, to
allow ``.htaccess`` files::

    AllowOverride All

Finally, put a ``.htaccess`` file where you want to split the path and write
lines such as these ones in it::

    <IfModule mod_rewrite.c>
        RewriteEngine on
        RewriteBase /path/to/current/directory
        # Only rewrite non-existing files and directories
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule ^(.*)$ index.php?path=$1 [L,QSA]
    </IfModule>

Module doc: https://httpd.apache.org/docs/current/mod/mod_rewrite.html


Nginx configuration
-------------------

Nginx doesn't use PHP as a module so you have to run another daemon which
provides a CGI-like gateway. For example, you may use ``php5-fpm`` daemon,
which installation is trivial on Debian::

    apt-get install php5-fpm
    update-rc.d php5-fpm defaults

This daemon creates an Unix socket in ``/var/run/php5-fpm.sock``.
Use something like this to connect nginx to php5-fpm::

    server {
        listen 80;
        listen [::]:80;

        root /var/www/localhost/htdocs;
        location ~ ^(.+?\.php)(/.*)?$ {
            try_files $1 =404;
            include fastcgi_params;
            fastcgi_param SCRIPT_FILENAME $document_root$1;
            fastcgi_param PATH_INFO $2;
            fastcgi_pass unix:/var/run/php5-fpm.sock;
        }
    }

Indeed all the mandatory paramaters for fastcgi interface are already defined
in ``/etc/nginx/fastcgi_params``::

    fastcgi_param   QUERY_STRING            $query_string;
    fastcgi_param   REQUEST_METHOD          $request_method;
    fastcgi_param   CONTENT_TYPE            $content_type;
    fastcgi_param   CONTENT_LENGTH          $content_length;

    fastcgi_param   SCRIPT_FILENAME         $request_filename;
    fastcgi_param   SCRIPT_NAME             $fastcgi_script_name;
    fastcgi_param   REQUEST_URI             $request_uri;
    fastcgi_param   DOCUMENT_URI            $document_uri;
    fastcgi_param   DOCUMENT_ROOT           $document_root;
    fastcgi_param   SERVER_PROTOCOL         $server_protocol;

    fastcgi_param   GATEWAY_INTERFACE       CGI/1.1;
    fastcgi_param   SERVER_SOFTWARE         nginx/$nginx_version;

    fastcgi_param   REMOTE_ADDR             $remote_addr;
    fastcgi_param   REMOTE_PORT             $remote_port;
    fastcgi_param   SERVER_ADDR             $server_addr;
    fastcgi_param   SERVER_PORT             $server_port;
    fastcgi_param   SERVER_NAME             $server_name;

    fastcgi_param   HTTPS                   $https;

    # PHP only, required if PHP was built with --enable-force-cgi-redirect
    fastcgi_param   REDIRECT_STATUS         200;

PHP can also be enabled only in a specific subdirectory of a location::

    server {
        [...]
        # The trailing slash makes nginx redirect "/subdir" to "/subdir/"
        location /subdir/ {
            alias /var/www/localhost/htdocs/specialPHPdir/;
            location ~ ^(/subdir)(.+?\.php)(/.*)?$ {
                try_files $2 =404;
                include fastcgi_params;
                fastcgi_param SCRIPT_FILENAME $document_root$2;
                fastcgi_param SCRIPT_NAME $1$2;
                fastcgi_param PATH_INFO $3;
                fastcgi_param DOCUMENT_URI $1$2;
                fastcgi_pass unix:/var/run/php5-fpm.sock;
            }
        }
    }


Rewrite directive
~~~~~~~~~~~~~~~~~

Nginx provides an HTTP rewrite module to change URIs dynamically. This directive
sets up pseudo subdirectories in ``/path`` URI which are handled by ``page.php``
script::

    rewrite ^/path(/.*)$ /page.php$1 last;

Module doc: http://nginx.org/en/docs/http/ngx_http_rewrite_module.html


Lighttpd configuration
----------------------

Like Nginx, Lighttpd can use PHP through a CGI or FastCGI application like
PHP-FPM.  Here are some documentation links:

* http://redmine.lighttpd.net/projects/lighttpd/wiki/Docs_ConfigurationOptions#mod_fastcgi-fastcgi
* https://wiki.archlinux.org/index.php/lighttpd#Using_php-fpm

And here is what ``/etc/lighttpd/lighttpd.conf`` looks like, once it is linked
with PHP-FPM::

    server.modules += ( "mod_fastcgi" )
    index-file.names += ( "index.php" )
    fastcgi.server += (
        ".php" => ("localhost" => (
            "socket" => "/var/run/php5-fpm.sock",
            "broken-scriptfilename" => "enable"
        ))
    )
    alias.url += ( "/my-php-pages" => "/srv/http/my-php-pages" )
