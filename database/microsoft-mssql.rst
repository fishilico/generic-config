Microsoft SQL Server
====================

MSSQL queries
-------------

Show the version of the database:

.. code-block:: mysql

    SELECT @@version
    GO

List available databases:

.. code-block:: mysql

    SELECT name FROM sys.Databases;
    SELECT * FROM master..sysdatabases;

List available tables from a database:

.. code-block:: mysql

    USE msdb;
    SELECT name FROM sys.Tables

    SELECT name FROM sysobjects WHERE xtype='U';

List columns of a table:

.. code-block:: mysql

    SELECT syscolumns.* FROM syscolumns
      JOIN sysobjects ON syscolumn.id=sysobjects.id
      WHERE sysobjects.name='my_table'

Enumerate users (type "``U``" is for ``WINDOWS_LOGIN``, like ``NT AUTHORITY\SYSTEM`` account, and "``S``" is for ``SQL_LOGIN``, like ``sa`` account):

.. code-block:: mysql

    SELECT principal_id, sid, name, type, type_desc, credential_id, owning_principal_id
      FROM master.sys.server_principals

    -- With passwords (John The Ripper format "mssql")
    SELECT name, password FROM sysxlogins;
    -- since MSSQL 2005 (JtR format "mssql05", after adding "0x" prefix to hashes):
    SELECT name, password_hash FROM sys.sql_logins;

Run system commands:

.. code-block:: mysql

    EXEC master.dbo.sp_configure 'show advanced options', 1
    RECONFIGURE
    EXEC master.dbo.sp_configure 'xp_cmdshell', 1
    RECONFIGURE
    GO

    xp_cmdshell "whoami"
    GO


Docker container on Linux
-------------------------

In order to use a MSSQL server on a development workstation, a Docker image can be used.
Microsoft provides an image for both Linux and Windows environments.
This is documented on https://docs.microsoft.com/en-us/sql/linux/quickstart-install-connect-docker?view=sql-server-2017&pivots=cs1-bash and the building scripts are published on https://github.com/Microsoft/mssql-docker.

Steps on Linux:

* Enable Docker overlay2 storage driver (cf. https://docs.docker.com/storage/storagedriver/overlayfs-driver/#configure-docker-with-the-overlay-or-overlay2-storage-driver).
  Write this in ``/etc/docker/daemon.json``:

.. code-block:: json

    {
      "storage-driver": "overlay2"
    }

* Pull Microsoft Docker image (cf. https://hub.docker.com/_/microsoft-mssql-server):

.. code-block:: sh

    docker pull mcr.microsoft.com/mssql/server:2017-latest

* Run a server:

.. code-block:: sh

    docker run -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=yourStrong(!)Password' -p 127.0.0.1:1433:1433 --name mssql -d mcr.microsoft.com/mssql/server:2017-latest

* Run SQL commands on the server (if ``-Q`` option is not used, an interactive prompt appears and the user needs to enter ``GO`` in order to launch queries and ``QUIT`` to exit):

.. code-block:: sh

    docker exec -it mssql /bin/bash
    /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "$SA_PASSWORD" -Q 'SELECT @@SERVERNAME'

On Windows, the Docker images is available on https://hub.docker.com/r/microsoft/mssql-server-windows-developer/
