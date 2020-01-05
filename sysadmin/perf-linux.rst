Using perf on Linux
===================

Introduction
------------

``perf`` is a tool to analyze the performance of applications and of the kernel, on  Linux-based systems.
It relies on syscall ``perf_event_open`` (http://man7.org/linux/man-pages/man2/perf_event_open.2.html) to access performance monitoring facilities provided by the kernel.
These facilities consist in:

* tracepoints (probes) in the kernel, the C library (glibc), some interpreters, etc.
* processor counters from the PMU (Performance Instrumentation Unit), like Intel PMC (Performance Monitoring Counter), replaced by Intel PCM (Processor Counter Monitor), or PIC (Performance Instrumentation Counter)
* hardware-assisted tracing, like Intel PT (Processor Tracing)

The access of the performance events system by unprivileged users is configured through sysctl ``kernel.perf_event_paranoid`` (file ``/proc/sys/kernel/perf_event_paranoid``).
The value of this setting is documented on https://www.kernel.org/doc/Documentation/sysctl/kernel.txt:

* ``-1``: Allow use of (almost) all events by all users.
  Ignore ``mlock`` limit after ``perf_event_mlock_kb`` without ``CAP_IPC_LOCK``
* ``>= 0``: Disallow ``ftrace`` function tracepoint by users without ``CAP_SYS_ADMIN``.
  Disallow raw tracepoint access by users without ``CAP_SYS_ADMIN``
* ``>= 1``: Disallow CPU event access by users without ``CAP_SYS_ADMIN``
* ``>= 2``: Disallow kernel profiling by users without ``CAP_SYS_ADMIN``


Usage
-----

The tool named ``perf`` works with subcommands (``stat``, ``record``, ``report``...).

.. code-block:: sh

    # Enumerate all symbolic event types
    perf list

    # Look for events related to KVM hypervisor
    perf list 'kvm:*'

In order to collect several statistics about a command:

.. code-block:: sh

    perf stat $COMMAND

Example with ``uname``:

.. code-block:: text

    # perf stat uname
    Linux

     Performance counter stats for 'uname':

                  0.50 msec task-clock                #    0.551 CPUs utilized
                     0      context-switches          #    0.000 K/sec
                     0      cpu-migrations            #    0.000 K/sec
                    67      page-faults               #    0.133 M/sec
             1,837,945      cycles                    #    3.656 GHz
             1,266,497      instructions              #    0.69  insn per cycle
               284,608      branches                  #  566.071 M/sec
                 8,956      branch-misses             #    3.15% of all branches

           0.000911814 seconds time elapsed

           0.001001000 seconds user
           0.000000000 seconds sys

In order to record a trace of a command:

.. code-block:: sh

    perf record $COMMAND

    # --branch-any: enable taken branch stack sampling
    # --call-graph=dwarf: enable call-graph (stack chain/backtrace) recording with DWARF information
    perf record --branch-any --call-graph=dwarf $COMMAND

    # Record a running process during 30 seconds
    # -a = --all-cpus: system-wide collection from all CPUs
    # -g (like --call-graph=fp): enable call-graph (stack chain/backtrace) recording
    # -p = --pid: record events on existing process ID (comma separated list)
    timeout 30s perf record -a -g -p $(pidof $MYPROCESS)

This creates a file named ``perf.data``, that can be analyzed with other subcommands.

.. code-block:: sh

    # Show perf.data in an ncurses browser (TUI) if possible
    perf report

    # Dump the raw trace in ASCII
    perf report -D
    perf report --dump-raw-trace

    # Display the trace output
    perf script

    # Show perf.data as:
    # * a text report
    # * with a column for sample count
    # * with call stacks
    # * with data coalesced and percentages
    perf report --stdio -n -g folded

    # List fields of header if the record was done with option -a
    perf script --header -F comm,pid,tid,cpu,time,event,ip,sym,dso

The trace can also be analyzed with a GUI such as https://github.com/KDAB/hotspot.

When Intel PT (Processor Tracing) is available on the CPU, the following commands can be used to trace a program (from https://lkml.org/lkml/2019/11/27/160):

.. code-block:: sh

    perf record -e '{intel_pt//,cpu/mem_inst_retired.all_loads,aux-sample-size=8192/pp}:u' $COMMAND
    perf script -F +brstackinsn --xed --itrace=i1usl100

More recent versions of ``perf`` introduced an equivalent of ``strace`` without using the ``ptrace`` syscall:

.. code-block:: sh

    perf trace --call-graph=dwarf $COMMAND

    # Or, with perf record:
    perf record -e 'raw_syscalls:*' $COMMAND

    # Trace with "augmented syscalls" (in order to see string parameters, for example)
    perf trace -e /usr/lib/perf/examples/bpf/augmented_raw_syscalls.c $COMMAND


Flame Graphs
------------

Using https://github.com/brendangregg/FlameGraph, it is very simple to produce a flamegraph out of a trace.
This can be useful for example to find in a program what functions take much time and need to be better optimized.

.. code-block:: sh

    # Record stack samples at 99 Hertz during 60 seconds
    # (both userspace and kernel-space stacks, all processes)
    perf record -F 99 -a -g -- sleep 60

    # Fold the stacks into a text file
    perf script | ./stackcollapse-perf.pl --all > out.folded

    # Filter on names of processes, functions... and create a flamegraph
    grep my_application < out.folded | ./flamegraph.pl --color=java > graph.svg

Another project enables producing flamegraphs for Rust projects: https://github.com/ferrous-systems/flamegraph


Documentation
-------------

* https://perf.wiki.kernel.org/index.php/Tutorial
  perf Wiki - Tutorial
* http://www.brendangregg.com/perf.html
  Linux perf Examples, documentation, links, and more!
* http://www.brendangregg.com/flamegraphs.html
  Flame Graphs
* https://github.com/brendangregg/perf-tools
  perf-tools GitHub project
* https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/tools/perf/Documentation/perf-record.txt
  perf-record man page
* https://alexandrnikitin.github.io/blog/transparent-hugepages-measuring-the-performance-impact/
  Transparent Hugepages: measuring the performance impact
* https://twitter.com/b0rk/status/945900285460926464
  perf cheat sheet by ulia Evans
