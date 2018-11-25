Generic Configuration README
============================

.. image:: https://circleci.com/gh/fishilico/generic-config.png?style=shield
  :target: https://circleci.com/gh/fishilico/generic-config

https://fishilico.github.io/generic-config/

Overview
--------
This project aims to give a quick technical perspective of the configuration
files I need to modify to get a system which fits my needs in terms of security
and usability.

Disclaimer
----------
*This project is NOT intended to be a tutorial or a reference for anyone else*.
There is absolutely **NO WARRANTY** for the content of this project to give you
a safe and usable configuration. Please consider this files as a cheat-sheet or
as some kind of last resort documentation to be looking for when you really do
not know how to configure a piece of software.

History
-------
Whenever I install a new Linux machine there are config files that need to be
edited. For example, on a server it's a good idea to disable remote ``root``
login after an administrator account has been created. Another example happens
when a desktop computer needs a basic firewall (only to prevent for this
computer from being open to the four winds): which rules should I configure?

At first I've written some text files and memos to keep track of these things.
However, system administration of a few personal hosts (servers and desktop
workstations) becomes really hard when you have not got a way to keep
configuration "in sync with your mind".

Another issue occured several years ago. One of my friends who was new to IPv6
wanted to know what rules I was using in the ``ip6tables`` firewall of my
server. I gave him a kind of "anonymized file" with rules which were not
specific to my server and he found out that there were some problems with IPv6
fragmentation. Therefore I needed to add some rules and to update the firewall
of every host I had.

So I've started my `Generic Configuration` project to create a place where I
could write down the non-specific files I can show to my friends and to other
people. In order to promote getting feedback from my notes, I made this project
public, with a Git tree hosted by GitHub. Nowadays the HTML pages are hosted by
GitHub Pages, and a
`Circle-Ci job <https://circleci.com/gh/fishilico/generic-config>`_ has been
configured to rebuild the pages everytime branch ``master`` is updated.

When you are reading the files I've written, please keep in mind that no host
in the world would run with only the things I describe, as they most likely
require some slight customization from their sysadmins.

Finally, I use a version control system (Git) to ease the way people can
contribute to this project. So if you find a bug and fill an issue or a pull
request to help me improve this project, what would be really nice! The project
is located on https://github.com/fishilico/generic-config.

Structure
---------

This project is organized in folders by field:

- `<etc/>`_: common files in ``/etc`` folder which are in every host
- `<etc-desktop/>`_: desktop-specific configuration of some ``/etc`` files
- `<etc-server/>`_: config files of services which can be found on a server
- `<sysadmin/>`_: some thoughts and tips&tricks about system administration
- `<windows/>`_: content related to using Microsoft Windows systems
- `<www/>`_: content of ``/var/www`` on a web server without specific purpose

License
-------
This project is licensed under
`Creative Commons Attribution Share Alike 4.0 International <https://creativecommons.org/licenses/by-sa/4.0/legalcode>`_
(`CC-BY-SA-4.0 <https://spdx.org/licenses/CC-BY-SA-4.0.html>`_).
