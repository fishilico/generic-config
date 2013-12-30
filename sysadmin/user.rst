User management on Linux
========================

Add a new user
--------------

Command:

.. code-block:: sh

    useradd LOGIN

Options::

    -c, --comment "Comment"
    -m, --create-home
    -u, --uid UID

Add an existing user to groups
------------------------------

Example:

.. code-block:: sh

    usermod -a -G sudo,adm user
