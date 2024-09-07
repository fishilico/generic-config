SQLite
======

Introduction
------------

SQLite is a database engine that directly uses a file, for example named ``db.sqlite``.
There is therefore no need to authenticate the database users in order for them to access the data: everything is managed by the access control of the file itself.
More precisely, when modifying the database, the directory that stores the database file needs also to be writable by the engine, in order to create and remove a journal file.

SQLite can be used by applications to store settings, user information, messages, etc.
Its engine is also used by projects such as `OSQuery <https://osquery.io/>`_ in order to benefit from a SQL interpreter.


Basic commands
--------------

In order to dump the content of a database file named ``db.sqlite`` from the command line:

.. code-block:: sh

    sqlite3 < /dev/null -bail -batch -cmd .dump db.sqlite

From the interactive prompt given by ``sqlite3``, it is possible to run SQL statements as well as special SQLite commands, prefixed with a dot.

.. code-block:: sh

    # Show available commands and some help
    .help

    # Show the version
    .version
    SELECT SQLITE_VERSION();

    # Quit
    .exit

    # List tables from the database
    .tables
    # Dump the schema of every table of the database
    .schema

    # List tables and dump the schema, for tables which names start with "user"
    .tables user%
    .schema user%

    # Change the output mode of SELECT statement (default one is pretty):
    # * Each cell in a new line
    .mode line
    # * Comma-separated values
    .mode csv
    # * Fixed-wicth columns
    .mode column
    .width 10 20 50 50 5
    # * Pretty tables (the default one in OSQuery)
    .mode pretty
    # * Pipe-separated values (the default one in SQLite)
    .mode list


SQL statements
--------------

SQLite supports standard SQL statements: ``SELECT``, ``INSERT INTO``, ``UPDATE``, ``DELETE``, etc.

Several ``SELECT`` statements can be merged together using:

* ``UNION ALL`` to concatenate the results ;
* ``UNION`` to concatenate the results, removing the duplicated rows ;
* ``INTERSECT`` to only keep the rows in common ;
* ``EXCEPT`` to exclude some rows.

It is also possible to join tables (``LEFT JOIN``, ``INNER JOIN``, etc.) using conditions expressed as:

.. code-block:: sql

    SELECT * FROM users LEFT JOIN user_groups ON users.uid = user_groups.uid;
    SELECT * FROM users LEFT JOIN user_groups USING (uid);

When performing a ``SELECT`` statement, it is possible to group some rows with a common value using ``GROUP BY column``.
In order to filter results before grouping, it is possible to use a ``WHERE condition`` clause.
To filter results after grouping, the clause to use is ``HAVING condition``.

The filters may use ``LIKE`` to match cells according to a pattern.
The pattern can use ``_`` as a wildcard for a single character and ``%`` as a wildcard for multiple characters.
In order to escape ``_``, engines such as MSSQL use a syntax like ``[_]``, but SQLite uses something else:

.. code-block:: sql

    SELECT * FROM objects WHERE name LIKE 'prefix\_%' ESCAPE '\';

To print timestamps as a human-readable date, there exists a function, ``DATETIME``.
For example:

.. code-block:: sql

    SELECT DATETIME(users.last_update_time, 'unixepoch') FROM users;

Schema table
------------

According to the `documentation <https://www.sqlite.org/schematab.html>`_, every SQLite database contains a single "schema table" named ``sqlite_master`` that stores the schema for that database.

.. code-block:: sql

    sqlite> .schema sqlite_master
    CREATE TABLE sqlite_master (
      type text,
      name text,
      tbl_name text,
      rootpage integer,
      sql text
    );

To understand its content in actual database, let's create a new table in an empty database.

.. code-block:: sql

    DROP TABLE IF EXISTS `users`;
    CREATE TABLE IF NOT EXISTS `users` (
      `uid` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
      `name` TEXT NOT NULL,
      `email` VARCHAR(255)  UNIQUE NOT NULL,
      `password` VARCHAR(110) NOT NULL,
      `admin` TINYINT(1) NOT NULL DEFAULT '0',
      `created` DATETIME NOT NULL
    );

After executing these statements, the schema table contains the ``CREATE TABLE`` statement and other objects:

.. code-block:: text

    sqlite> SELECT * FROM sqlite_master;
    table|users|users|2|CREATE TABLE `users` (
      `uid` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
      `name` TEXT NOT NULL,
      `email` VARCHAR(255)  UNIQUE NOT NULL,
      `password` VARCHAR(110) NOT NULL,
      `admin` TINYINT(1) NOT NULL DEFAULT '0',
      `created` DATETIME NOT NULL
    )
    index|sqlite_autoindex_users_1|users|3|
    table|sqlite_sequence|sqlite_sequence|4|CREATE TABLE sqlite_sequence(name,seq)

From a SQL injection vulnerability, this table can be obtained using queries such as:

.. code-block:: sql

    -- Concatenate all fields and select the 1st entry (using COALESCE to support NULL values)
    SELECT type||';'||name||';'||tbl_name||';'||rootpage||';'||COALESCE(sql,'') FROM sqlite_master
        LIMIT 0,1;

    -- Concatenate all fields of all rows
    SELECT GROUP_CONCAT(type||';'||name||';'||tbl_name||';'||rootpage||';'||COALESCE(sql,''),'^')
        FROM sqlite_master;

To exfiltrate the characters of such a string, functions ``HEX``, ``SUBSTR`` and ``LENGTH`` (documented in `Built-In Scalar SQL Functions <https://sqlite.org/lang_corefunc.html>`_) can be used.
For example:

.. code-block:: sql

    sqlite> SELECT HEX('hello');
    68656C6C6F
    sqlite> SELECT LENGTH(HEX('hello'));
    10
    sqlite> SELECT SUBSTR(HEX('hello'),1,1)='6';
    1
    sqlite> SELECT SUBSTR(HEX('hello'),1,1)>'9';
    0
