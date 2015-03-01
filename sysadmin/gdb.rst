GDB, The GNU Project Debugger
=============================

When debugging an application or investigating a crash, several tools exist to
understand what's going on:

* ``strace`` to list system calls,
* ``ltrace`` to list calls to functions in shared libraries,
* ``valgrind`` to track memory usage and find out memory leaks and access to
  uninitialized data,
* ``gdb`` to debug the application.

This document presents how ``gdb`` can be used to debug a program.  It is not a
complete introduction to ``gdb`` and it is not focused on development issues.
It is written in a mindset of a system admin facing an application crashing or
having serious bugs.  These dysfunctions can be caused by a harmful
configuration, by a component missing or by a code issue.  ``gdb`` can be used
to gather data such as stack trace and memory dumps.  Such data can be used when
reporting bugs, to help developers investigate further, and it can also be used
to get precise information about the environment context (allocated memory,
global variables...).


Starting GDB
------------

To load a program into ``gdb``, the command is::

    gdb program

The program is not started but symbols are read, which allows doing things such
as defining breakpoints, loading shared libraries, customizing the interface...

It is possible to debug a running process knowing its PID (eg. 1234)::

    gdb -p 1234

Moreover, to launch a text user interface (TUI), one can run::

    gdb -tui -quiet program


Basic commands
--------------

Once ``gdb`` is started, it prints a few lines and presents a prompt with
"``(gdb)``".  The commands which are mandatory to know then are:

* ``quit`` or ``q``: exit ``gdb``.
* ``help`` or ``h``: get help.
* ``run arg1 arg2 arg3`` or ``r``: launch the program with the specified
  command-line arguments.
* ``breakpoint main`` or ``b``: set up a breakpoint on function ``main()``.
* ``clear main`` or ``cl``: remove the breakpoint on function ``main()``.
* ``delete 1`` or ``d``: remove the first breakpoint.
* ``watch variable`` or ``wa``: set up a watchpoint on a variable.
* ``catch syscall``: set up a catchpoint for any syscall
* ``continue`` or ``c``: continue execution after it being interrupted.
* ``step`` or ``s``: step program until a different line of code.
* ``next`` or ``n``: like ``step``, but step over subroutines.
* ``stepi`` or ``si``: step one instruction.
* ``nexti`` or ``ni``: like ``stepi`` but step over subroutines.

``step``, ``next``, ``stepi`` and ``nexti`` takes an optional integer parameter
which specifies how many times to repeat the command.

* ``layout split``: change layout to a 3-windows layout, code, asm and command.
  Other possible layout are ``src``, ``asm`` and ``regs``.

To iterate through layouts, use ``layout next`` (or ``la n``) and press enter
several times.  Pressing enter with an empty prompt repeats the last command.

To switch between TUI (with layouts) and CLI (only command line), the default
key binding is ``Ctrl-X A`` (``^Xa``, ``^XA`` or ``^X^A``).


Analysis commands
-----------------

Once a program is interrupted, either because of a breakpoint, a segmentation
fault, an interrupt signal (Ctrl-C) or other trapped signals, it is possible to
analysis the execution context of a program.

Call frame:

* ``backtrace`` or ``bt``: show the stack trace (list of function calls).
* ``frame 0`` or ``f 0``: select a frame in the stack trace.
* ``info frame`` or ``i f``: show information about current frame.
  (A frame ID can be added).

Display variables and expressions:

* ``print $rsp`` or ``p``: print an expression, which is here the x86_64 stack
  pointer, but can be a symbol (to a global variable) or a complex expression.
  It can even call functions from the currently-being-debugged program!
* ``p/x $r12``: print the value of register 12 in hexadecimal format.
* ``p *(char***)&__libc_argv``: retrieve the value of ``argv``.
* ``output`` or ``ou``: like ``print`` without value history nor newline.

Memory:

* ``x/256xb $rsp``: dump 256 bytes from the stack in hexadecimal format.
* ``x/60xw $rsp``: dump 60 32-bit words from the stack.
* ``x/30xg $rsp``: dump 30 64-bit words from the stack.
* ``x/42i main``: show the 42 first asm instructions of function ``main``.
* ``x/10s **(char***)&environ``: show 10 environment variables.
* ``x/hs $rsi``: show an wide-character string from rsi.
* ``disassemble`` or ``disas``: show asm instructions around the current one.
  (an address or a symbol can be given).
* ``list`` or ``l``: show code lines around the current one.
* ``list -`` or ``l -``: show code lines before the current one.
* ``dump memory text.bin 0x400000 0x401000``: write memory content to a file.
  The two hexadecimal arguments define a [start, stop) range.

General information:

* ``info registers`` or ``i reg``: show the values of current registers.
* ``info proc mappings`` or ``i proc m``: show the memory mapping.
* ``info locals`` or ``i lo``: show the values of local variables.


Remote debug
------------

It is possible debug a program through a network connection using ``target``
command in ``gdb``.  Even if it is quite crazy to do such a thing for an usual
application, it comes handy when debugging an emulated program (with QEmu),
a Windows program on a Linux host (with Wine), or an embedded system (with a
real wire).

For example, to debug an application running with wine, it is possible to do::

    $ winedbg --gdb --no-start cmd.exe
    0022:0023: create process 'C:\windows\system32\cmd.exe'/0x110760 @0x7ece8b70 (0<0>)
    0022:0023: create thread I @0x7ece8b70
    target remote localhost:12345

    $ gdb -quiet
    (gdb) target remote localhost:12345
    Remote debugging using localhost:47152
    0x7b85d4b0 in ?? ()
    (gdb) c
    Continuing.

``target`` can also be used to load a core dump and other things.


Using core dumps
----------------

When a program crashes, Linux can dump its execution context to a file.  This
file is called a "core dump" and it is possible to run gdb to analyze it using:

    gdb program corefile

To generate such a core dump, the "core resource limit" needs to be non-zero
and ``kernel.core_pattern`` needs to be configured.  By default, these values
are::

    $ ulimit -c
    0
    $ sysctl kernel.core_pattern
    kernel.core_pattern = core

Here is an example to dump core of "sleep":

.. code-block:: sh

    sudo sysctl -w kernel.core_pattern=%e.core
    ulimit -c unlimited
    sleep 3600 &
    kill -SEGV $!

The shell would print something like::

    [1]  + segmentation fault (core dumped)  sleep 3600

and the current directory now contains a file named ``sleep.core.1234`` with
1234 being the PID of the sleep process.  To launch ``gdb`` on the coredump,
the command is:

.. code-block:: sh

    gdb $(which sleep) sleep.core.1234

and it prints lines such as::

    Core was generated by `sleep 3600'.
    Program terminated with signal SIGSEGV, Segmentation fault.
    #0  0x00007fe5073c89d0 in __nanosleep_nocancel () from /usr/lib/libc.so.6

Systemd uses a specific system to store core dump in the journal.  To use this
system, you need to configure ``kernel.core_pattern`` with::

    |/usr/lib/systemd/systemd-coredump %p %u %g %s %t %e

Once this is done, core dumps are available through ``coredumpctl`` command,
which provides an easy way to launch ``gdb`` on the dumps.


Debug options for compilation
-----------------------------

To compile a C program with debug symbols, the compiler command line is::

    gcc -g -ggdb -fvar-tracking-assignments

The variable tracker is documented on GCC wiki:
https://gcc.gnu.org/wiki/Var_Tracking_Assignments

To build an Archlinux package with debug symbols, the ``debug`` option needs to
be enabled in ``/etc/makepkg.conf`` or in the used ``PKGBUILD``.  Moreover, if
the ``strip`` option is also given, the usual package contains compiled binaries
without debug symbols and a second package (with ``-debug`` suffix) is built,
which installs files in ``/usr/lib/debug/`` with debug information.  More
information is given in the ``PKGBUILD`` manpage.

To build a Debian package with debug symbols, the following commands can be
used:

.. code-block:: sh

    export DEB_BUILD_OPTIONS="nostrip noopt"
    debuild -uc -us

When the debug symbols are separated from a binary, the build ID is used to
keep a relationship between the stripped binary and the debug symbols.  This ID
is created at build time and is available in section ``.note.gnu.build-id`` (or
``NOTE`` entry in the program header)::

    $ LANG=C readelf --notes /bin/sh |grep Build
    Build ID: ab8308edd4619fdf3c578408bee0b123b41f8553

    $ readelf --program-headers /usr/bin/sh |grep -A1 NOTE
      NOTE           0x0000000000000254 0x0000000000400254 0x0000000000400254
                     0x0000000000000044 0x0000000000000044  R      4

    $ LANG=C objdump -s -j .note.gnu.build-id /bin/sh |tail -n +4
    Contents of section .note.gnu.build-id:
     400274 04000000 14000000 03000000 474e5500  ............GNU.
     400284 ab8308ed d4619fdf 3c578408 bee0b123  .....a..<W.....#
     400294 b41f8553                             ...S

Here, debug information may be found in
``/usr/lib/debug/.build_id/ab/8308edd4619fdf3c578408bee0b123b41f8553.debug``,
if this file is installed.


Documentations
--------------

Zenk Security made a useful Quick Reference PDF for gdb:
https://repo.zenk-security.com/Reversing%20.%20cracking/GDB%20QUICK%20REFERENCE.pdf

More information about core dumps and ``kernel.core_pattern`` format can be
found in the "core" man page: http://man7.org/linux/man-pages/man5/core.5.html

To debug Linux kernel, it is recommended to first decompress the kernel image
(like ``vmlinuz``) to an uncompressed ELF image (``vmlinux``).  The kernel
sources contain a script which exactly does this:
https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/tree/scripts/extract-vmlinux.
As ``vmlinux`` is likely to be stripped, the ``System.map`` file is needed to
find the symbols.  Nevertheless a developer-oriented distribution may choose to
provide the decompressed unstripped ``vmlinux`` file in
``/usr/lib/modules/$(uname -r)/build/vmlinux``.
