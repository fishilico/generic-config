``etc-server/bitlbee/``: BitlBee IRC gateway
===============================================

BitlBee (https://www.bitlbee.org/) is an IRC gateway to other chat networks.
Once installed, it seems good to restrict BitlBee to listen only on the loopback interface.
Modify ``/etc/bitlbee/bitlbee.conf``:

.. literalinclude:: bitlbee.conf
   :language: ini

Then, start BitlBee daemon and connect to the IRC gateway, for example with WeeChat::

    # Configure the server and connect to it
    /server add bitlbee localhost/6667 -autoconnect
    /connect bitlbee

    # Register the account in BitlBee control channel
    register <password>

    # In WeeChat, save the password
    /secure set bitlbee_password <password>
    /set irc.server.bitlbee.command "/msg &bitlbee identify ${sec.data.bitlbee_password}"

Then, in BitlBee control channel (``&bitlbee``), add a Twitter account for example (https://wiki.bitlbee.org/HowtoTwitter)::

    account add twitter <yourusername>

    # Force using commands in order to post a new tweet
    account twitter set commands strict

    # Disable streams (cf. https://wiki.bitlbee.org/HowtoTwitter/StreamDeprecation)
    account twitter set stream off
    
    # Connect to Twitter
    account twitter on

    # Follow an other Twitter account
    add twitter <twitter_username_to_follow>
