MySQL tips and tricks
=====================

Here are some useful reference for MySQL command line.  This file does not
contain anything related to server configuration

The official documentation is available at: http://dev.mysql.com/doc/


Basic commands
--------------

The basic MySQL commands are:

* ``SHOW DATABASES`` to list available databases,
* ``USE database`` to tell the MySQL client to use a specific database,
* ``SHOW TABLES`` to list tables in the current database,
* ``DESCRIBE table`` to get a list of fields of a given table, and
* ``SELECT * FROM table LIMIT 10`` to get 10 rows from the given table.

Once a database is selected, standard SQL queries are possible.


Account management
------------------

To create a new MySQL user and give her a special database, which is useful for
example when creating a new website, three commands are needed:

.. code-block:: mysql

    CREATE USER 'newsite'@'localhost' IDENTIFIED BY 'a-random-password';
    CREATE DATABASE newsite DEFAULT CHARACTER SET 'utf8';
    GRANT SELECT, INSERT, DELETE, UPDATE, CREATE, DROP, INDEX, ALTER, CREATE TEMPORARY TABLES ON newsite.* TO 'newsite'@'localhost';
    FLUSH PRIVILEGES;

The following command changes the password assiociated to the user:

.. code-block:: mysql

    SET PASSWORD FOR 'newsite'@'localhost' = PASSWORD('an other random password!');

To list all users, you need SELECT access to ``mysql`` database:

.. code-block:: mysql

    SELECT User, Host FROM mysql.user;

The permissions of a specific user can be seen with ``SHOW GRANTS``.  Here is
an example::

    mysql> SHOW GRANTS FOR root@localhost;
    +---------------------------------------------------------------------------------------------------------------+
    | Grants for root@localhost                                                                                     |
    +---------------------------------------------------------------------------------------------------------------+
    | GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' IDENTIFIED BY PASSWORD '*Hashed password' WITH GRANT OPTION |
    | GRANT PROXY ON ''@'' TO 'root'@'localhost' WITH GRANT OPTION                                                  |
    +---------------------------------------------------------------------------------------------------------------+


Shell connection
----------------

To connect to a database when being in a shell, use the ``mysql`` command:

.. code-block:: sh

    mysql -H server -u user -p database

This command asks for the password of user and then connects and use the
specified database.

To give the password directly on the command line, do not put a space between
``-p`` and the password:

.. code-block:: sh

    mysql -u user "-p$PASSWORD" database

It is also possible to put login information in a hidden file in your home
folder, in ``~/.my.cnf``.  Such file looks like this::

    [mysql]
    user=mysqluser
    password=password-for-mysqluser
    database=mydb

To dump a database, the command is ``mysqldump``.  Here are some examples:

.. code-block:: sh

    mysqldump --lock-tables database mytable
    mysqldump --single-transaction --add-drop-table database_with_innoDB

List of permissions
-------------------

This table lists the available permissions, used by ``GRANT``:

+------------+-----------------------------+------------------------+
|    Data    |          Structure          |     Administration     |
+============+=============================+========================+
| ``SELECT`` | ``CREATE``                  | ``GRANT``              |
+------------+-----------------------------+------------------------+
| ``INSERT`` | ``ALTER``                   | ``SUPER``              |
+------------+-----------------------------+------------------------+
| ``UPDATE`` | ``INDEX``                   | ``PROCESS``            |
+------------+-----------------------------+------------------------+
| ``DELETE`` | ``DROP``                    | ``RELOAD``             |
+------------+-----------------------------+------------------------+
| ``FILE``   | ``CREATE TEMPORARY TABLES`` | ``SHUTDOWN``           |
+------------+-----------------------------+------------------------+
|            | ``SHOW VIEW``               | ``SHOW DATABASES``     |
|            +-----------------------------+------------------------+
|            | ``CREATE ROUTINE``          | ``LOCK TABLES``        |
|            +-----------------------------+------------------------+
|            | ``ALTER ROUTINE``           | ``REFERENCES``         |
|            +-----------------------------+------------------------+
|            | ``EXECUTE``                 | ``REPLICATION CLIENT`` |
|            +-----------------------------+------------------------+
|            | ``CREATE VIEW``             | ``REPLICATION SLAVE``  |
|            +-----------------------------+------------------------+
|            | ``EVENT``                   | ``CREATE USER``        |
|            +-----------------------------+------------------------+
|            | ``TRIGGER``                 |                        |
+------------+-----------------------------+------------------------+



MySQL query examples
--------------------

These queries create an empty account table with some fields:

.. code-block:: mysql

    DROP TABLE IF EXISTS `account`;
    CREATE TABLE IF NOT EXISTS `account` (
      `uid` int(11) NOT NULL AUTO_INCREMENT,
      `hruid` varchar(255) CHARACTER SET ascii NOT NULL,
      `name` tinytext CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
      `email` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
      `admin` tinyint(1) NOT NULL DEFAULT '0',
      `birthday` datetime NOT NULL,
      PRIMARY KEY (`uid`),
      UNIQUE KEY `hruid` (`hruid`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;


When the user is allowed to interact with the filesystem:

.. code-block:: mysql

    -- Read a file from the filesystem
    SELECT LOAD_FILE('/etc/hosts');

    -- Write a file that does not exist
    SELECT 'Hello, world!' INTO OUTFILE '/tmp/my_hello.txt';


SQL injection queries
---------------------

When a SQL injection vulnerability hits an application and makes it possible to
run arbitrary ``SELECT`` queries, here are some queries that can be used in
order to gather information about the database.

* Which version is the server running?

    .. code-block:: mysql

        SELECT version();
        SELECT @@version;

* What are the available tables?

    .. code-block:: mysql

        SELECT CONCAT(IF(TABLE_CATALOG,TABLE_CATALOG,''),':',
                      TABLE_SCHEMA,'.',TABLE_NAME)
               FROM information_schema.TABLES;

* What are the columns in the tables?

    .. code-block:: mysql

        SELECT CONCAT(IF(TABLE_CATALOG,TABLE_CATALOG,''),':',
                      TABLE_SCHEMA,'.',TABLE_NAME,'.',
                      COLUMN_NAME,'(',DATA_TYPE,', ',COLUMN_TYPE,')')
               FROM information_schema.COLUMNS;

* What are the privileges visible from the current user?

    .. code-block:: mysql

        SELECT CONCAT(GRANTEE,'=',IF(TABLE_CATALOG,TABLE_CATALOG,''),',',
                      PRIVILEGE_TYPE,IF(IS_GRANTABLE,'_grantable',''))
               FROM information_schema.USER_PRIVILEGES;
        SELECT CONCAT(GRANTEE,'=',IF(TABLE_CATALOG,TABLE_CATALOG,''),':',
                      TABLE_SCHEMA,',',
                      PRIVILEGE_TYPE,IF(IS_GRANTABLE,'_grantable',''))
               FROM information_schema.SCHEMA_PRIVILEGES;
        SELECT CONCAT(GRANTEE,'=',IF(TABLE_CATALOG,TABLE_CATALOG,''),':',
                      TABLE_SCHEMA,'.',TABLE_NAME,',',
                      PRIVILEGE_TYPE,IF(IS_GRANTABLE,'_grantable',''))
               FROM information_schema.TABLE_PRIVILEGES;
        SELECT CONCAT(GRANTEE,'=',IF(TABLE_CATALOG,TABLE_CATALOG,''),':',
                      TABLE_SCHEMA,'.',TABLE_NAME,'.',COLUMN_NAME,',',
                      PRIVILEGE_TYPE,IF(IS_GRANTABLE,'_grantable',''))
               FROM information_schema.COLUMN_PRIVILEGES;

* Who gave the grants and when?

    .. code-block:: mysql

        SELECT CONCAT(User,'@',Host,':',Db,'.',Table_name,':',Grantor,' ',
                      Timestamp,' ',Table_priv,' ',Column_priv)
               FROM mysql.tables_priv;

* What are the password hashes?

    .. code-block:: mysql

        SELECT CONCAT(User,'@',Host,':',Password,
                      ' (grant=',Grant_priv,',super=',Super_priv,')')
               FROM mysql.user;
