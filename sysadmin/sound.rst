Sound Configuration
===================

Here are some notes about how I setup sound on my desktop systems.


MPD and PulseAudio
------------------

MPD (Music Player Daemon) is a system daemon which plays music from files,
playlists... It needs to interact with PulseAudio to get the sound out (using
ALSA) to enable multiplexing several audio output streams (like the ones which
are played by the Desktop Environment to signal important events to the user).

As it is discouraged to run PulseAudio as a system daemon, I use the standard
setup which spawns one PulseAudio server per logged user. However to allow
multiplexing MPD needs to use the same server as my user. Hence on my system
MPD is running with my user ID.

ArchLinux' MPD wiki article give some tips to set up such configuration.
First, configure these two files:

``/etc/systemd/system/mpd-MYUSER.service``::

    .include /usr/lib/systemd/system/mpd.service

    [Unit]
    Description=Music Player Daemon (running as MYUSER)

    [Service]
    User=MYUSER
    PAMName=system-local-login

``/etc/mpd.conf``::

    music_directory "/home/public/music"
    playlist_directory "/var/lib/mpd/playlists"
    db_file "/var/lib/mpd/mpd.db"
    pid_file "/var/lib/mpd/mpd.pid"
    state_file "/var/lib/mpd/mpdstate"

    user "MYUSER"
    audio_output {
        type            "pulse"
        name            "MPD Pulse Output"
    }

Then disable the system-wide MPD service and enable the new one:

.. code-block:: sh

    systemctl disable mpd
    systemctl stop mpd
    systemctl start mpd-MYUSER
    systemctl enable mpd-MYUSER

Documentation:
https://wiki.archlinux.org/index.php/MPD/Tips_and_Tricks#MPD_and_PulseAudio
(This wiki also describe the setup with a local TCP socket)


Network
-------

Streaming audio stream over the network is quite easy with PulseAudio. Let's
suppose host ``192.0.2.42`` wants to send its audio output to a PulseAudio
server running on host ``192.0.2.1``.

First setup the listener (``192.0.2.1``) to accept connections from the sender
(``192.0.2.42``). ``/etc/pulse/default.pa``::

    load-module module-native-protocol-tcp auth-ip-acl=127.0.0.1;192.0.2.42

Then configure the sender to send its audio output. ``/etc/pulse/default.pa``::

    load-module module-rtp-send destination=192.0.2.1 port=16001
