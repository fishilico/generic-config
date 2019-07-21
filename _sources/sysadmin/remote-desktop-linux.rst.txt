Remote Desktop on Linux
=======================

Most Linux-based systems use X11 or Wayland in order to render the desktop.
In order to connect to a remote Linux system and operate with a graphical user interface, there exist several approaches: VNC, RDP, X11 forwarding over SSH, etc.

X11 principles
--------------

X11 is a specification and a protocol for *X window system* that enables using a graphical user interface.
It relies on a client/server pattern where:

* The server is a physical device with peripherals such as a display, a mouse, a keyboard, etc.
* Each application is a client to the server.

Among applications, some special ones render the window borders, the desktop background, etc.
These are parts of a desktop environment.

On a local system, the X11 server listens on a Unix socket located at ``/tmp/.X11-unix/X0``.
This is referred by client applications as ``:0.0``.
A client knows to which server it talks using the ``$DISPLAY`` environment variable:

.. code-block:: sh

    $ echo $DISPLAY
    :0.0

This variable may also contain an IP address, for remote X11.
For example ``DISPLAY=192.168.1.2:0`` refers to a server running at 192.168.1.2 on TCP port 6000.
The general form of variable ``DISPLAY`` is ``hostname:D.S`` where ``hostname`` is the name of the target host (empty for a local server), ``D`` is the display index and ``S`` is the screen index.
On a remote host, the associated TCP port is computed by: ``6000 + D``.
On the local host, the display index is used to compute the path to the Unix socket: ``"/tmp/.X11-unix/X" + D``

There exists some kind of authentication to a X11 server, using a magic cookie located in ``$HOME/.Xauthority``.
The content of the binary file can be decoded using ``xauth list``::

    $ xauth list
    myhost/unix:0  MIT-MAGIC-COOKIE-1  7a77125b6af11c25a72662e316ab40a0

X11 protocol allows many powerful actions for clients, such as:

* changing the screen resolution (``xrandr`` command)
* getting information about any windows (``xwininfo`` command, such as ``xwininfo -root -tree``)
* getting the PID (process identifier) which owns a window (``xprop _NET_WM_PID``)
* reading all keystrokes (``xinput`` command, such as ``xinput test $KEYBOARD_NUM``)
* reading and writing the clipboard buffers (``xsel`` command)
* taking a screenshot (``import -display :0 -window root screenshot.png`` from ImageMagick)
* etc.


Remote X11
----------

On a trusted network, it is possible to expose a X11 server on a TCP port.
As the communication does not include encryption, this setup is not recommended as-is.
It is nonetheless possible to encapsulate the X11 protocol in a secure tunnel (that provides confidentiality, integrity and authentication), such as a VPN.

OpenSSH also provides an easy way to forward a X11 server over a SSH connection, so that remote applications can run on the local X11 server.
This feature is called *X11 forwarding* and is enabled using a configuration variable (``X11Forwarding yes`` on the SSH server, ``ForwardX11 yes`` on the SSH client) or a command-line switch (``-X`` or ``-Y``).
As X11 clients are powerful, OpenSSH allows specifying whether the remote server is to be fully trusted (``ForwardX11Trusted`` configuration variable, ``-Y`` option) or not (``-X`` option).


Remote Desktop
--------------

Sometimes, there is a need to connect to a remote host that is running a X11 server with applications.
Several VNC and RDP servers create a new X11 server for such remote connection, which is fine in order to isolate each user one from each other.

For example Microsoft documents how to setup xrdp on https://docs.microsoft.com/en-us/azure/virtual-machines/linux/use-remote-desktop:

.. code-block:: sh

    echo xfce4-session >~/.xsession
    sudo service xrdp restart

It is also possible to expose the X11 server as a VNC server using ``x11vnc``, as described in https://undeadly.org/cgi?action=article;sid=20071108214134:

.. code-block:: sh

    # Connect using SSH to the remote host, forwarding VNC port
    # Several websites state that allocating a PTY (-t) for x11vnc makes it faster
    ssh -t -L 5900:localhost:5900 remotehost

    # Start x11vnc on the remote host to expose the first display as a VNC server
    # The user display can also be found using "-find"
    x11vnc -display :0 -auth "$HOME/.Xauthority" -localhost

    # Connect from the local host to the VNC server, reachable through localhost:5900
    vncviewer -depth 8 -encodings hextile localhost:0

If the remote host does not have an X11 server, it is possible to start a virtual one such as Xvfb:

.. code-block:: sh

    # On the remote host
    export DISPLAY=:1
    Xvfb :1 -screen 0 1024x768x16 &
    x11vnc -display :1 -nopw -localhost -xkb

This can be used to run software such as QEMU with a graphical output, or a web browser, etc.
