PHP Configuration Customization
================================

Here are some tips & tricks to configure a php.ini file.

Common important configuration options
--------------------------------------

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
----------------------------------

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
