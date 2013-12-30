WWW server files (``/var/www``)
===============================

.. toctree::
   :maxdepth: 1
   :glob:

   **

This directory contains basic files which are on every web server which are not
really public. This means that the first function of the web server which
serves these files is not to be a cool website but something else, like
monitoring, statistics, file sharing...

Web server configuration
------------------------

If you're using nginx, put these lines into your default vhost::

    root /path/to/www/htdocs;
    error_page 403 /403.html;
    error_page 404 /404.html;
    error_page 500 /500.html;
    error_page 500 502 503 504 /50x.html;
    index index.html
    try_files $uri $uri/ =404;

With Apache, use::

    DocumentRoot "/path/to/www/htdocs"
    ErrorDocument 403 "/403.html"
    ErrorDocument 404 "/404.html"/i
    ErrorDocument 500 "/500.html"
    ErrorDocument 502 "/50x.html"
    ErrorDocument 503 "/50x.html"
    ErrorDocument 504 "/50x.html"
