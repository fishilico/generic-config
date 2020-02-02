WinDbg-kd, Windows Kernel Debugging
===================================

To debug a Windows kernel, here is what is needed:

* WinDbg (for example with VisualStudio Express Edition)

* A kernel booted in debug mode.  For local debugging, the boot can be
  configured with these commands (on Windows<=7, the second one fails but
  WinDbg still supports local kernel debugging)::

    bcdedit /debug on

    # Since Windows 8, otherwise debugging is enabled on serial port COM2
    bcdedit /dbgsettings local

(``bcdedit`` configures the Boot Configuration Database)

It is then possible to run ``windbg -kl`` as administrator to start a Local
Kernel debugging session.

To verify whether local kernel debugging is enabled::

    cd C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\
    kdbgctrl -c

In order to configure kernel debugging on a virtual machine, it is possible to
use network debugging, with a key which consists in 3 words separated with dots::

    bcdedit /dbgsettings NET HOSTIP:172.16.0.1 PORT:50000 KEY:a.b.c.d

    # On the debugger host (breaking happens in nt!DbgBreakPointWithStatus)
    WinDbg -k net:port=52000,key:a.b.c.d,target:DESKTOP-AB01CDE

To load kernel symbols, it is possible to download a Windows Symbol Package
from MSDN, but it is simpler to make WinDbg download them automatically.
This can be done either with an environment variable
(cf. https://support.microsoft.com/en-us/kb/311503)::

    _NT_SYMBOL_PATH=SRV*C:\DebugSymbols*http://msdl.microsoft.com/download/symbols

    # To make it persistent:
    setx _NT_SYMBOL_PATH srv*C:\DebugSymbols*http://msdl.microsoft.com/download/symbols

or with WinDbg commands::

    .sympath SRV*C:\DebugSymbols*http://msdl.microsoft.com/download/symbols
    .reload /f


Usual commands
--------------

* Get help about a command: ``.hh x`` (examine), ``.hh uu`` (unassemble)

* Examine symbols starting with ``NtCreate`` in the kernel: ``x nt!NtCreate*``.

* Display values at an address, with optional argument ``L size``:

  * ``db``: display hexadecimal bytes (128 by default)
  * ``dc``: display DWORD values and their ASCII equivalents (32 by default)
  * ``dd``: display DWORD values (32 by default)
  * ``dp``: display ULONG_PTR values (128 bytes by default)
  * ``dps``: display pointers and symbols (``dp`` with symbols)
  * ``dpp``: like ``dps``, with an extra pointer dereference
  * ``dq``: display ULONG64_PTR values (128 bytes by default)
  * ``du``: display UNICODE characters values (16 2-byte characters by default)
  * ``dw``: display WORD values (64 by default)

  * ``ds /c width addr``: display width characters at addr
  * ``dS /c width addr``: display width unicode characters at addr

* Disassemble the beginning of a function (use ``L2a`` to show 42 instructions)::

    lkd> u nt!KiSystemCall64
    nt!KiSystemCall64:
    fffff800`29f9d040 0f01f8          swapgs
    fffff800`29f9d043 654889242510000000 mov   qword ptr gs:[10h],rsp
    fffff800`29f9d04c 65488b2425a8010000 mov   rsp,qword ptr gs:[1A8h]
    fffff800`29f9d055 6a2b            push    2Bh
    fffff800`29f9d057 65ff342510000000 push    qword ptr gs:[10h]
    fffff800`29f9d05f 4153            push    r11
    fffff800`29f9d061 6a33            push    33h
    fffff800`29f9d063 51              push    rcx

* Display the types of fields of a structure: ``dt nt!_KUSER_SHARED_DATA``


System-related commands
-----------------------

* List modules with names and timestamps: ``lm n t``

* List some information about the kernel: ``!lmi nt``

* Read the PCR (Processor Control Region): ``!pcr``

* Read the PRCB (Processor Control Block): ``!prbc``

* Get information about the current machine: ``!sysinfo machineid``

* Display information about a process and set it to be the current one::

    lkd> !process 0 0 explorer.exe
    PROCESS ffff9702a7995080
        SessionId: 1  Cid: 0bbc    Peb: 0020f000  ParentCid: 0b7c
        DirBase: 3eaf7000  ObjectTable: ffff820ba5bcc8c0  HandleCount: <Data Not Accessible>
        Image: explorer.exe

    lkd> .process /P ffff9702a7995080
    Implicit process is now ffff9702`a7995080

* Read the PEB (Process Environment Block) of the current process::

    lkd> !peb
    PEB at 000000000020f000
        InheritedAddressSpace:    No
        ReadImageFileExecOptions: No
        BeingDebugged:            No
        ImageBaseAddress:         00007ff773fe0000
        Ldr                       00007ffdf0c623a0
        Ldr.Initialized:          Yes
        Ldr.InInitializationOrderModuleList: 0000000000652270 . 000000000b1c7f00
        Ldr.InLoadOrderModuleList:           00000000006523e0 . 000000000b1c7ee0
        Ldr.InMemoryOrderModuleList:         00000000006523f0 . 000000000b1c7ef0
                        Base TimeStamp                     Module
                7ff773fe0000 57a449e4 Aug 05 01:10:12 2016 C:\Windows\Explorer.EXE
                7ffdf0b10000 57a447be Aug 05 01:01:02 2016 C:\Windows\SYSTEM32\ntdll.dll
                7ffdee620000 57a44ac4 Aug 05 01:13:56 2016 C:\Windows\System32\KERNEL32.DLL
                7ffded2a0000 57a447cc Aug 05 01:01:16 2016 C:\Windows\System32\KERNELBASE.dll
                7ffdf0920000 57a44d8f Aug 05 01:25:51 2016 C:\Windows\System32\msvcrt.dll
                7ffdee500000 57a44c17 Aug 05 01:19:35 2016 C:\Windows\System32\OLEAUT32.dll
                7ffdede80000 57a44804 Aug 05 01:02:12 2016 C:\Windows\System32\ucrtbase.dll
                7ffdeefc0000 57a448db Aug 05 01:05:47 2016 C:\Windows\System32\combase.dll
    ...
                7ffde0670000 57a449c1 Aug 05 01:09:37 2016 C:\Windows\SYSTEM32\CHARTV.dll
        SubSystemData:     00007ffdebb40e30
        ProcessHeap:       0000000000650000
        ProcessParameters: 0000000000651a50
        CurrentDirectory:  'C:\Windows\system32\'
        WindowTitle:  'Microsoft.Windows.Explorer'
        ImageFile:    'C:\Windows\Explorer.EXE'
        CommandLine:  'C:\Windows\Explorer.EXE'
        DllPath:      '< Name not readable >'
        Environment:  000000000b0361f0
            ALLUSERSPROFILE=C:\ProgramData
            APPDATA=C:\Users\IEUser\AppData\Roaming
            ChocolateyInstall=C:\ProgramData\chocolatey
            ChocolateyLastPathUpdate=Wed Aug 10 11:06:58 2016
            CommonProgramFiles=C:\Program Files\Common Files
            CommonProgramFiles(x86)=C:\Program Files (x86)\Common Files
            CommonProgramW6432=C:\Program Files\Common Files
            COMPUTERNAME=MSEDGEWIN10
            ComSpec=C:\Windows\system32\cmd.exe
    ...
            PUBLIC=C:\Users\Public
            SESSIONNAME=Console
            SystemDrive=C:
            SystemRoot=C:\Windows
            TEMP=C:\Users\IEUser\AppData\Local\Temp
            TMP=C:\Users\IEUser\AppData\Local\Temp
            USERDOMAIN=MSEDGEWIN10
            USERDOMAIN_ROAMINGPROFILE=MSEDGEWIN10
            USERNAME=IEUser
            USERPROFILE=C:\Users\IEUser
            windir=C:\Windows

* Dump the virtual memory allocations of the current process::

    lkd> !vad
    VAD             level      start      end    commit
    ffff9702a7812b10 ( 8)         200       3ff       145 Private      READWRITE
    ffff9702a7985420 ( 7)         400       40f         0 Mapped       READWRITE          Pagefile-backed section
    ffff9702a798a880 ( 8)         410       416         6 Private      READWRITE
    ffff9702a7982360 ( 6)         420       435         0 Mapped       READONLY           Pagefile-backed section
    ffff9702a7955100 ( 7)         440       4bf        23 Private      READWRITE
    ffff9702a7986010 ( 8)         4c0       4c3         0 Mapped       READONLY           Pagefile-backed section
    ffff9702a7980230 ( 5)         4d0       4d1         0 Mapped       READONLY           Pagefile-backed section
    ffff9702a78fa380 ( 8)         4e0       4e1         2 Private      READWRITE
    ffff9702a798b8c0 ( 7)         4f0       5b0         0 Mapped       READONLY           \Windows\System32\locale.nls
    ffff9702a66adbf0 ( 8)         5c0       5cc        13 Private      READWRITE
    ffff9702a5f53f70 ( 9)         5d0       5d2         3 Private      READWRITE
    ffff9702a8103700 ( 6)         5e0       5e6         0 Mapped       READONLY           \Windows\System32\en-US\explorerframe.dll.mui
    ffff9702a76fe800 ( 8)         5f0       5f1         0 Mapped       READONLY           Pagefile-backed section
    ffff9702a7ecb6c0 ( 9)         600       600         1 Private      READWRITE
    ffff9702a7fa5090 ( 7)         610       613         4 Private      READWRITE
    ffff9702a7ded0a0 ( 9)         620       623         4 Private      READWRITE
    ffff9702a7dee2f0 ( 8)         630       633         4 Private      READWRITE
    ffff9702a7978850 ( 9)         640       641         0 Mapped       READONLY           Pagefile-backed section
    ffff9702a7750880 ( 4)         650       74f       255 Private      READWRITE
    ...

  (Append ``000`` to ``start`` and ``end`` to get real addresses, usable with ``dd``)

* Dump the System Service Table (SSDT): ``dps nt!KiServiceTable L11c``

* Dump system protected processes (cf. http://www.alex-ionescu.com/?p=116)::

    lkd> !for_each_process "
    r? @$t0 = (nt!_EPROCESS*) @#Process;
    .if @@(@$t0->Protection.Level) {
        .printf /D \"%08x <b>[%70msu]</b> level: <b>%02x</b>\\n\",
            @@(@$t0->UniqueProcessId),
            @@(&@$t0->SeAuditProcessCreationInfo.ImageFileName->Name),
            @@(@$t0->Protection.Level)
    }"
    00000004 [                                                                      ] level: 62
    00000148 [                     \Device\HarddiskVolume2\Windows\System32\smss.exe] level: 61
    000001a8 [                    \Device\HarddiskVolume2\Windows\System32\csrss.exe] level: 61
    000001e4 [                  \Device\HarddiskVolume2\Windows\System32\wininit.exe] level: 61
    000001ec [                    \Device\HarddiskVolume2\Windows\System32\csrss.exe] level: 61
    00000268 [                 \Device\HarddiskVolume2\Windows\System32\services.exe] level: 61
    0000037c [    \Device\HarddiskVolume2\Program Files\Windows Defender\MsMpEng.exe] level: 31


x86-specific commands
---------------------

* Dump the Interrupt Descriptor Table, which contains Interrupt Service Routines::

    lkd> !idt

    Dumping IDT: fffff8002b8e4080

    00: fffff80029f9aa00 nt!KiDivideErrorFault
    01: fffff80029f9ab00 nt!KiDebugTrapOrFault
    02: fffff80029f9acc0 nt!KiNmiInterrupt  Stack = 0xFFFFF8002B8FF000
    03: fffff80029f9b040 nt!KiBreakpointTrap
    04: fffff80029f9b140 nt!KiOverflowTrap
    05: fffff80029f9b240 nt!KiBoundFault
    06: fffff80029f9b340 nt!KiInvalidOpcodeFault
    07: fffff80029f9b580 nt!KiNpxNotAvailableFault
    08: fffff80029f9b640 nt!KiDoubleFaultAbort  Stack = 0xFFFFF8002B8FD000
    09: fffff80029f9b700 nt!KiNpxSegmentOverrunAbort
    0a: fffff80029f9b7c0 nt!KiInvalidTssFault
    0b: fffff80029f9b880 nt!KiSegmentNotPresentFault
    0c: fffff80029f9b9c0 nt!KiStackFault
    0d: fffff80029f9bb00 nt!KiGeneralProtectionFault
    0e: fffff80029f9bc00 nt!KiPageFault
    10: fffff80029f9bfc0 nt!KiFloatingErrorFault
    11: fffff80029f9c140 nt!KiAlignmentFault
    12: fffff80029f9c240 nt!KiMcheckAbort   Stack = 0xFFFFF8002B901000
    13: fffff80029f9c8c0 nt!KiXmmException
    1f: fffff80029f964a0 nt!KiApcInterrupt
    20: fffff80029f99fc0 nt!KiSwInterrupt
    29: fffff80029f9ca80 nt!KiRaiseSecurityCheckFailure
    2c: fffff80029f9cb80 nt!KiRaiseAssertion
    2d: fffff80029f9cc80 nt!KiDebugServiceTrap
    2f: fffff80029f96770 nt!KiDpcInterrupt
    30: fffff80029f969a0 nt!KiHvInterrupt
    31: fffff80029f96d10 nt!KiVmbusInterrupt0
    32: fffff80029f97070 nt!KiVmbusInterrupt1
    33: fffff80029f973d0 nt!KiVmbusInterrupt2
    34: fffff80029f97730 nt!KiVmbusInterrupt3
    35: fffff80029e53090 hal!HalpInterruptCmciService (KINTERRUPT fffff80029e53000)
    50: ffffd0017e709bd0 ataport!IdePortInterrupt (KINTERRUPT ffffd0017e709b40)
    60: ffffd0017e709d10 ataport!IdePortInterrupt (KINTERRUPT ffffd0017e709c80)
    80: ffffd0017e709810 i8042prt!I8042MouseInterruptService (KINTERRUPT ffffd0017e709780)
    81: ffffd0017e709590 ndis!ndisMiniportIsr (KINTERRUPT ffffd0017e709500)
    90: ffffd0017e7096d0 i8042prt!I8042KeyboardInterruptService (KINTERRUPT ffffd0017e709640)
    91: ffffd0017e709310 USBPORT!USBPORT_InterruptService (KINTERRUPT ffffd0017e709280)
    a0: ffffd0017e7091d0 serial!SerialCIsrSw (KINTERRUPT ffffd0017e709140)
    b0: ffffd0017e709e50 ACPI!ACPIInterruptServiceRoutine (KINTERRUPT ffffd0017e709dc0)
    b1: ffffd0017e709a90 storport!RaidpAdapterInterruptRoutine (KINTERRUPT ffffd0017e709a00)
                         HDAudBus!HdaController::Isr (KINTERRUPT ffffd0017e7093c0)
    ce: fffff80029e53a90 hal!HalpIommuInterruptRoutine (KINTERRUPT fffff80029e53a00)
    d1: fffff80029e53890 hal!HalpTimerClockInterrupt (KINTERRUPT fffff80029e53800)
    d2: fffff80029e53790 hal!HalpTimerClockIpiRoutine (KINTERRUPT fffff80029e53700)
    d7: fffff80029e53590 hal!HalpInterruptRebootService (KINTERRUPT fffff80029e53500)
    d8: fffff80029e53390 hal!HalpInterruptStubService (KINTERRUPT fffff80029e53300)
    df: fffff80029e53290 hal!HalpInterruptSpuriousService (KINTERRUPT fffff80029e53200)
    e1: fffff80029f97aa0 nt!KiIpiInterrupt
    e2: fffff80029e53490 hal!HalpInterruptLocalErrorService (KINTERRUPT fffff80029e53400)
    e3: fffff80029e53190 hal!HalpInterruptDeferredRecoveryService (KINTERRUPT fffff80029e53100)
    fd: fffff80029e53990 hal!HalpTimerProfileInterrupt (KINTERRUPT fffff80029e53900)
    fe: fffff80029e53690 hal!HalpPerfInterrupt (KINTERRUPT fffff80029e53600)

* Read a MSR register, like STAR (syscall target)::

    lkd> rdmsr c0000082
    msr[c0000082] = fffff800`29f9d040
    kd> u fffff800`29f9d040 L1
    nt!KiSystemCall64:
    fffff800`29f9d040 0f01f8          swapgs

* To get the Kernel Processor Control Region (KPCR), use ``fs_base`` MSR
  (0xc0000100) on x86-32 and ``gs_base`` (0xc0000101) on x86-64::

    lkd> rdmsr c0000101
    msr[c0000101] = ffffd001`aef40000
    lkd> dt nt!_KPCR ffffd001aef40000

* The GDT (Global Descriptor Table) can be read by a remote debugger with
  ``r gdtr`` and the detail of each descriptors can be seen with commands such
  as ``dp @cs``.  When using a local debugger, it is nevertheless possible to
  compile a userland program which shows the result of ``sgdt`` instruction,
  which is not privileged, and then use the pointer in WinDBG with
  ``nt!_KGDTENTRY`` (or ``nt!_KGDTENTRY64``) structure.


NatVis and JavaScript (since Windows 10)
----------------------------------------

Since Windows 10, WinDbg supports NatVis (Native Visualization, which was added
to Visual Studio 2013).

This allows such a syntax to dump a structure such as an ``EPROCESS``::

    lkd> dx *(nt!_EPROCESS**)&nt!PsInitialSystemProcess
    *(nt!_EPROCESS**)&nt!PsInitialSystemProcess                 : 0xffff9c8708c83040 [Type: _EPROCESS *]
        [+0x000] Pcb              [Type: _KPROCESS]
        [+0x2e0] ProcessLock      [Type: _EX_PUSH_LOCK]
        [+0x2e8] UniqueProcessId  : 0x4 [Type: void *]
        [+0x2f0] ActiveProcessLinks [Type: _LIST_ENTRY]
        [+0x300] RundownProtect   [Type: _EX_RUNDOWN_REF]
    ...

NatVis files are in ``C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\Visualizers``
(for example there is ``stl.natvis`` in order to represent types such as
``std::string``, ``std::list``, ``std::map``, etc.)

NatVis commands:

.. code-block:: sh

    # Define variables
    dx @$myVar = "My sttring"
    dx @$myVar
    dx @$myVar.Length

    # Show methods
    dx -v @$myVar

    # Show a variable with 2 levels of recursion
    dx -r2 @$myVar

    # Create an array from memory
    dx @$testArray = (int(*)[10])0x7ffe0010
    dx @$testPointersArray = (int*(**)[10])0x7ffe0010

    # Copy a variable into some memory
    dx *(TYPE*)0x10000 = *@$myNewContent

    # Show the processor blocks
    dx (nt!_KPRCB**)&nt!KiProcessorBlock, [*(int*)&nt!KeNumberProcessors]

    # Enumerate all variables
    dx @$vars

    # Remove a variable
    @$vars.Remove("myVar")

    # Create an anonymous structure
    dx @$myobject = new { Type = 5, Name = "Process Object" }

    # Create a new function (with anonymous function syntax)
    dx @$mul = (num1, num2) => num * num2

    # Load a NatVis file
    .nvload C:\path\to\myfile.natvis

In WinDbg, there are 3 default NatVis variables: ``@$curprocess``,
``@$curthread`` and ``@$cursession``:

.. code-block:: sh

    lkd> dx @$cursession
    @$cursession                 : Local KD
        Processes
        Devices

    lkd> dx @$cursession.Processes
    @$cursession.Processes
        [0x0]            : <Unknown Image>
        [0x4]            : <Unknown Image>
        [0x38]           : <Unknown Image>
        [0x68]           : <Unknown Image>
        [0x1bc]          : smss.exe

With LINQ (Language INtegrated Query) it is possible to process results using
SQL-like functions:

.. code-block:: sh

    # Find processes named smss.exe
    dx @$cursession.Processes.Where(p=>p.Name == "smss.exe")

    # Get the name of the process
    dx @$cursession.Processes.Where(p=>p.Name == "csrss.exe").First()
        .KernelObject.SeAuditProcessCreationInfo.ImageFileName->Name

    # List processes with their protection levels
    dx -g @$cursession.Processes.Where(p=>p.KernelObject.Protection.Level != 0)
        .Select(p => new{name=p.Name, Level=p.KernelObject.Protection.Level})

    # Get the names of handles opened by csrss
    dx -r2 @$cursession.Processes.Where(p=>p.Name=="csrss.exe").Select(
        p => p.Io.Handles.Select(h => h.ObjectName))

In order to build complex structures from data, there are some helpers:

.. code-block:: sh

    dx -r0 @$processList = *(nt!_LIST_ENTRY*)&nt!PsActiveProcessHead
    dx -r0 @$processes = Debugger.Utility.Collections.FromListEntry(
        @$processList, "nt!_EPROCESS", "ActiveProcessLinks")

    dx Debugger.Utility.Control.ExecuteCommand("!filetime 0").First()

Using JavaScript provider:

.. code-block:: sh

    .load jsprovider.dll

    # call initializeScript()
    .scriptload C:\path\to\MyScriptName.js

    # like .scriptload and call invokeScript()
    .scriptrun C:\path\to\MyScriptName.js

    dx Debugger.State.Scripts.MyScriptName.Contents.my_function(args)
    dx @$scripts.MyScriptName.Contents.my_function(args)
    dx @$scriptContents.my_function(args)

    # call uninitializeScript() and unload
    .scriptunload MyScriptName.js

In JavaScript:

* ``host`` is a COM object for the Degugger
* ``host.memory`` represents the target memory (method
  ``readMemoryValues(ptr, size)`` returns an ``ArrayBuffer`` with memory)
* ``host.diagnostics.debugLog("...")`` prints logs
* ``host.typeSystem.marshalAs(variable, "nt", "SOME_TYPE")`` to cast
* ``new host.metadata.valueWithMetadata(myInteger, {PreferredRadix:10})`` to
  print an integer as decimal
* ``host.evaluateExpression(expr)`` or ``host.namespace.Debugger.Utility.Control.ExecuteCommand``
  to run a debugger command (like ``.printf %y`` to convert a pointer to a
  symbol using MASM syntax)

To add new aliases in Javascript:

.. code-block:: c

    function initializeScript()
    {
        return [new host.functionAlias(my_function, "myfct") /*, ... */];
    }
    // In WinDBG:
    //   !myfct arg1, arg2
    //   dx @$myfct(arg1, arg2)


Links
-----

* https://msdn.microsoft.com/en-us/library/windows/hardware/ff551063(v=vs.85).aspx
  Debugging Tools for Windows (WinDbg, KD, CDB, NTSD)
* https://msdn.microsoft.com/en-us/windows/hardware/gg463028
  Download Windows Symbol Packages
* https://msdn.microsoft.com/en-us/library/windows/hardware/ff551891(v=vs.85).aspx
  Debugger Commands - Kernel-Mode Extensions
* http://windbg.info/doc/1-common-cmds.html
  Common WinDbg Commands
* https://github.com/microsoft/WinDbg-Samples
  Sample extensions, scripts, and API uses for WinDbg
