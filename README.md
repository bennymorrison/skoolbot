# skoolbot

A hackish IRC bot

This project is very new. As in just put together on 2018 December 08 "NEW"..

Useage:

!man [term]     -   Returns the corresponding OpenBSD manpage link

!toot [message] -   Toots to the Mastodon account specified in toot.json

!uptime         -   Responds with the uptime and load averages

!users          -   Lists currently active users

This is going to be designed around tilde.institute but I'm sure anyone could use this for any projects, hence the BSD license.

The code is very easy to decipher. Once you read it, and read the comments, you'll see how to extend it and add your own commands/responses. Despite the use of raw sockets instead of abtracting away the IRC protocol, it's not unwieldly at all.

skoolbot uses SSL to connect to the IRC server specified in the variables at the top of the file. In the unlikely event that your IRC server does not support SSL, it's very simple to change.

Take it, borrow it, use it to build other things. Have fun.
