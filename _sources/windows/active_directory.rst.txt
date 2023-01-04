Active Directory by Microsoft
=============================

Network discovery
-----------------

An Active Directory ("AD") is a technology from Microsoft which aims to ease the management of organizations through a centralized authentication ("SSO" for Single Sign-On), an inventory of users and machines, a way to apply configurations, etc.
This uses several protocols:

* Kerberos (`RFC 4120 <https://tools.ietf.org/html/rfc4120>`_, TCP port 88) for authentication ;
* LDAP (Lightweight Directory Access Protocol, `RFC 4511 <https://tools.ietf.org/html/rfc4511>`_, TCP ports 389 for LDAP and 636 for LDAPS) to access properties of the directory (user names, group memberships, etc.) ;
* DNS (Domain Name System, UDP and TCP port 53) to allow clients to discover the servers which host the AD, the *Domain Controllers* (DC) ;
* MS-RPC and SMB (Server Message Block Protocol, TCP port 445) to share configuration files and programs (such as Group Policy Objects, GPO) with clients ;
* etc.

On a network which uses an AD, the machines are usually configured such that their DNS resolver is a domain controller and the DNS search suffix is the name of the AD domain.
Such a configuration can be easily discovered, for example through DHCP.

A way to discover the Domain Controllers of a specific domain, such as ``contoso.com`` (the example company of Microsoft, cf. https://en.wikipedia.org/wiki/Contoso) consists in issuing DNS requests with type ``SRV`` to:

* ``_kerberos._tcp.contoso.com`` (enumerate the servers which provide the Kerberos protocol, TCP and UDP 88)
* ``_kerberos._udp.contoso.com``
* ``_kpasswd._tcp.contoso.com`` (for Kerberos password change servers, TCP and UDP 464)
* ``_kpasswd._udp.contoso.com``
* ``_ldap._tcp.contoso.com``  (for LDAP, TCP 389)
* ``_ldaps._tcp.contoso.com`` (for LDAPS, TCP 636)
* ``_gc._tcp.contoso.com`` (for Global Catalog, LDAP for the entire forest, TCP 3268 for LDAP and 3269 for LDAPS)

A DNS response to a ``SRV`` request contains a priority number (0), a weight number (100), a TCP (or UDP) port number and a host name that can be resolved to an IPv4 or an IPv6 (type ``A`` or ``AAAA`` records).

There also exists a specific DNS zone for "Microsoft Domain Controller Server", ``_msdcs.contoso.com``:

* ``_ldap._tcp.dc._msdcs.contoso.com`` ("DC" means "Domain Controller")
* ``_ldap._tcp.gc._msdcs.contoso.com`` ("GC" means "Global Catalog")
* ``_ldap._tcp.pdc._msdcs.contoso.com`` ("PDC" means "Primary Domain Controller", which is usually unique per domain)
* ``_kerberos._tcp.dc._msdcs.contoso.com``
* ``A`` and ``AAAA`` requests to ``gc._msdcs.contoso.com`` also resolves to IP addresses of DC.


Kerberos configuration
----------------------

In order to authenticate to an AD using an account through Kerberos protocol, ``kinit`` can be used (from package ``krb5``).
Its configuration lies in ``/etc/krb5.conf`` and looks like:

.. code-block:: ini

    [libdefaults]
        default_realm = CONTOSO.COM
        dns_lookup_realm = false
        dns_lookup_kdc = true
        forwardable = true

    [realms]
    # use "kdc = ..." if realm admins haven't put SRV records into DNS
        ATHENA.MIT.EDU = {
            admin_server = kerberos.mit.edu
        }
        CONTOSO.COM = {
            kdc = 192.168.0.1:88
            kdc_tcp_ports = 88
            admin_server = 192.168.0.1
            default_domain = CONTOSO.COM

            # For smartcard authentication
            pkinit_anchors = FILE:/etc/ssl/contoso.com/ca.crt
            pkinit_kdc_hostname = dc1.contoso.com
            pkinit_kdc_hostname = dc2.contoso.com
            pkinit_cert_match = <SUBJECT>CN=mylogin.*
            pkinit_identities = PKCS11:/usr/lib/pkcs11/opensc-pkcs11.so
        }

    [domain_realm]
        .contoso.com = CONTOSO.COM
        contoso.com = CONTOSO.COM

    [logging]
    #    kdc = CONSOLE
    #    default = FILE:/tmp/krb5log.log
    #    kdc = FILE:/tmp/krb5log.log
    #    admin_server = FILE:/tmp/krb5admin.log

``kinit`` stores Kerberos tickets in ``/tmp/krb5cc_${UID}`` where ``UID`` is the user identifier.
This can be overridden using variable ``$KRB5CCNAME``.
The tickets can then be used for example with:

.. code-block:: sh

    # From samba
    smbclient -k //machine.contoso.com/IPC$
    rpclient -k machine.contoso.com
    # ... and issue "getusername"

    # From impacket
    wmiexec.py -k -no-pass contoso.com/mylogin@machine.contoso.com


LDAP queries
------------

In order to query an AD using ``ldapsearch``, several parameters need to be found:

* The connection string (protocol, host name, TCP port) to the LDAP or LDAPS server, like ``ldaps://dc1.contoso.com``.
* A user account, with a login and the associated password, like ``mylogin`` and ``P@ssw0rd!``.
* The base DN (Distinguished Name) of the directory, which can be derived from the domain name of the AD using ``DC=`` components, like ``DC=contoso,DC=com``.

  - ``DC`` means Domain Component (for the domain name)
  - ``OU`` means Organizational Unit (like folders)
  - ``CN`` means Common Name (designation of objects)

With all these parameters, a LDAP search command looks like:

.. code-block:: sh

    # -N to not use reverse DNS to canonicalize the SASL host name
    # -H connection string (LDAP URI)
    # -D login ("bind DN") and -w password, or -W to prompt for the password
    #    or -y to specify a password file
    #    or -Y GSSAPI to use Kerberos (with SASL, requires package cyrus-sasl-gssapi)
    # -x to use simple authentication instead of SASL
    # -LLL to disable printing LDIF version and comments
    # -b search base
    # -v -o ldif-wrap=no to prevent wrapping the output
    ldapsearch \
        -N \
        -H ldaps://dc1.contoso.com \
        -D mylogin@contoso.com \
        -w 'P@ssw0rd!' \
        -xLLL \
        -b DC=contoso,DC=com \
        -v -o ldif-wrap=no \
        $FILTER $ATTRIBUTES

The LDAP filter is a LDAP query on attributes:

* ``*`` and ``(objectClass=*)`` request every available objects and their attributes
* ``(cn=mylogin)`` requests the attributes of the object which Common Name matches "mylogin"
* ``(cn=*_admin)`` requests the attributes of the object which Common Name ends with "_admin"
* ``(objectCategory=Person)`` requests the attributes of all objects in category "Person"
* ``(displayName=*needle*)`` requests the attributes of the object which display name contains "needle"
* ``(memberOf=CN=Administration,OU=User Groups,OU=Company Groups,DC=contoso,DC=com)`` requests the member of a group
* ``(&(cn=*a*)(cn=*b*))`` matches objects with a Common Name containing both "a" and "b"
* ``(|(cn=*a*)(cn=*b*))`` matches objects with a Common Name containing either "a" or "b"
* ``(&(objectClass=user)(memberOf:1.2.840.113556.1.4.1941:=CN=Domain Admins,OU=Users,DC=contoso,DC=com)`` requests the nested member of a group (with ``LDAP_MATCHING_RULE_IN_CHAIN`` Microsoft extension)
* For paging: ``-E pr=1000/noprompt``

To ignore certificate issues, this environment variable can be used: ``LDAPTLS_REQCERT=never``.

In order to find out the search base, the scope of the search can be modified using option ``-s base``:

.. code-block:: sh

    # Look in the result for "namingContexts", "defaultNamingContext", etc.
    ldapsearch -H ldaps://dc1.contoso.com -xLLL -b '' -s base

    # ... or specify the attribute that is printed
    ldapsearch -H ldaps://dc1.contoso.com -xLLL -b '' -s base namingContexts

User accounts have several interesting attributes:

* ``objectClass``: ``person``, ``organizationalPerson``, ``user`` (and ``top``)
* ``distinguishedName``: full DN for the object
* ``sAMAccountName``: user name in SAM (Security Account Manager)
* ``userPrincipalName``: like an email address
* ``memberOf``: group memberships
* ``badPwdCount``: failed login attempts count
* ``pwdLastSet``: timestamp and the last password change (convertible to a date through ``LANG=C date --date="@$(( (TS/10000000)-11676009600))"``)
* ``logonCount``: connection count
* ``lastLogon`` and ``lastLogoff``: connection timestamps
* ``adminCount``: 1 when a given object has had its ACLs changed to a more secure value by the system because it was a member of one of the administrative groups

Groups have:

* ``objectClass``: ``group``
* ``member``: group members
* ``memberOf``: group memberships

Computers have:

* ``objectClass``: ``computer`` (and ``top``, ``person``, ``organizationalPerson``, ``user``)
* ``name``: NetBIOS name
* ``dNSHostName``: DNS FQDN
* ``operatingSystem``
* ``operatingSystemVersion``
* ``lastLogonTimestamp``
* ``servicePrincipalName``: SPN, ie. services such as TERMSRV, HTTP, MSSQL, etc.
  The Kerberos ticket for the service (TGS) is encrypted using the NTLM password hash of the account (Impacket provides `GetUserSPNs.py <https://github.com/SecureAuthCorp/impacket/blob/impacket_0_9_20/examples/GetUserSPNs.py>`_ for Kerberoasting attack, when an SPN is attached to a user instead of a computer).

GPO have:

* ``objectClass``: ``groupPolicyContainer``, ``container`` (and ``top``)
* ``displayName``
* ``gPCFileSysPath``: path to ``\\contoso.com\sysvol\contoso.com\Policies\...``

DNS zones are in several trees, the variable in ``${...}`` coming from a base query (``ldapsearch -b '' -s base``):

* ``CN=MicrosoftDNS,CN=System,${defaultNamingContext}``
* ``CN=MicrosoftDNS,DC=DomainDnsZones,${defaultNamingContext}`` (eg. ``ldapsearch -N -H ldaps://dc1.contoso.com -xLLL -b 'CN=MicrosoftDNS,DC=DomainDnsZones,DC=contoso,DC=com' -v -o ldif-wrap=no``)
* ``CN=MicrosoftDNS,DC=ForestDnsZones,${rootDomainNamingContext}``

DNS zones and DNS nodes objects have:

* ``objectClass``: ``dnsZone`` or ``dnsNode``
* ``dc``: "Domain Component", the Fully-Qualified Domain Name (FQDN) for the object (optional)
* ``distinguishedName`` for DNS zones: full DN for the object (eg. ``DC=example.org,CN=MicrosoftDNS,DC=DomainDnsZones,DC=contoso,DC=com``)
* ``dn`` for DNS nodes: full DN for the object
* ``objectCategory``: ``CN=Dns-Zone,CN=Schema,CN=Configuration,DC=contoso,DC=com`` or ``CN=Dns-Node,...``
* ``dnsRecord``: encoded DNS records for a DNS node


Resources
---------

* https://syscall.eu/blog/2018/09/03/ldapsearch_ad_tls/
  Active Directory searches from Linux

* https://speakerdeck.com/ropnop/fun-with-ldap-kerberos-and-msrpc-in-ad-environments
  Fun with LDAP, Kerberos (and MSRPC) in AD Environments

* https://github.com/dirkjanm/adidnsdump/blob/master/adidnsdump/dnsdump.py
  Tool to interact with ADIDNS over LDAP (query the DNS zones and nodes through LDAP)

* https://www.synacktiv.com/ressources/delegation_kerberos_biere_secu_toulouse.pdf
  Non-constrained Kerberos Delegation.
  Search of machine accounts with flag ``TRUSTED_FOR_DELEGATION``:

  .. code-block:: sh

      $ ldapsearch -H ldap://DC.VICTIM.LAN -b DC=VICTIM,DC=LAN \
        -D VICTIM\\user -w P@ssw0rd '(&(objectClass=computer) \
        (userAccountControl:1.2.840.113556.1.4.803:=524288))' \
        sAMAccountName

      dn: CN=CLIENT1SHARE,OU=Share,DC=VICTIM.LAN
      sAMAccountName: CLIENT1SHARE$
