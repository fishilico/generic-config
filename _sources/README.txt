Generic Configuration README
============================

.. image:: https://circleci.com/gh/fishilico/generic-config.png?style=shield
  :target: https://circleci.com/gh/fishilico/generic-config

https://fishilico.github.io/generic-config/

Overview
--------
This project aims to give a quick technical perspective of the configuration
files I need to modify to get a system which fits my needs.

Disclaimer
----------
*This project is NOT intended to be a tutorial or a reference for anyone else*.
There is absolutely **NO WARRANTY** for the content of this project to give you
a safe and usable configuration. Please consider this files as a cheat-set or as
last resort documentation if you really don't know how to configure a software.

History
-------
Every time I install a new Linux machine there are config files that need to be
edited. For example, on a server it's a good idea to disable remote root login
after an administrator account has been created. Another example is given by a
desktop host which may need a basic firewall (just for this host not to be
open to the four winds), which rules should I put?

At first I've written some text files and memos to keep things. However, system
administration of a few personal hosts (servers and desktop workstations) is
really hard when you don't have a way to keep configuration "in sync with your
mind".

Soon another problem came. One of my friends who was new to IPv6 wanted to know
what ip6tables rules I was using in the firewall of my server. I gave him a
kind of "anonymous file" with rules which were not specific to my server and he
found out that there were some problems with IPv6 fragmentation. So I needed to
add some rules and to update the firewall of every hosts I had.

So I've started my `Generic Configuration` project to create a place where I
could write down the non-specific files I can show to my friends and to other
people. So when you are reading the files I've written, please keep in mind that
no host in this world can run with only the things I describe but need some
slight customization from sysadmins.

Finally, I use a version control system (Git) to ease the way people can
contribute to this project. So if you find a bug and fill an issue or a pull
request to help me improve this project, what would be really nice!

Structure
---------

This project is organized in folders by field:

- ``etc``: common files in ``/etc`` folder which are in every host
- ``etc-desktop``: desktop-specific configuration of some ``/etc`` files
- ``etc-server``: config files of services which can be found on a server
- ``sysadmin``: some thoughts and tips&tricks about system administration
- ``www``: content of ``/var/www`` on a web server without specific purpose
