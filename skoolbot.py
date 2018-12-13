#!/usr/bin/env python3

#-----------------------------
# skoolbot 0.1
# written by ahriman
# ahriman@falte.red
# https://falte.red
#-----------------------------

import socket
import ssl
import time
import requests
import os
import signal
import sys
import subprocess

# just defining some basic vars.
# pretty self explanatory.
# the last var is the quit command to be used in-channel
server = "irc.tilde.chat"
port = "6697"
use_ssl = "yes"
channel = "#institute"
nickname = "skoolbot"
nickservpass = ""
adminname = "ahriman"
exitcmd = "die, devil bird!"
exitrsp = "SQUAWWWK"
ownermail = "ahriman@falte.red"

# "to TLS or not to TLS, that is the question" --Shakesbeer
# seriously, who doesn't use TLS?
if use_ssl == "yes":
    ircsockraw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ircsock = ssl.wrap_socket(ircsockraw, ssl_version=ssl.PROTOCOL_TLSv1)
else:
    ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# actually bring up the connection and request the bot's nick
ircsock.connect((server, int(port)))
ircsock.send(bytes("USER "+ nickname +" "+ nickname +" "+ nickname +" "+ nickname +"\n", "UTF-8"))
ircsock.send(bytes("NICK "+ nickname +"\n", "UTF-8"))

# this is the function to join channels
# it loops until the server sends the nick list
# and prints what the server sends us to stdout
# so we know we joined successfully
def jchan(chan):
    ircsock.send(bytes("JOIN "+ channel +"\n", "UTF-8"))
    ircmsg = " "
    while ircmsg.find("End of /NAMES list.") == -1:
        ircmsg = ircsock.recv(2048).decode("UTF-8")
        ircmsg = ircmsg.strip("\n\r")
        print(ircmsg)

# identify with nickserv
def identify():
    ircsock.send(bytes("PRIVMSG nickserv :identify "+ nickservpass +"\n", "UTF-8"))

# keep the connection alive
# PING? PONG! etc
# irc is fucking weird
def ping():
    ircsock.send(bytes("PONG :pingis\n", "UTF-8"))

# this lets the bot communicate with [target]
# user, channel, whatever
def sendmsg(msg, target=channel):
    ircsock.send(bytes("PRIVMSG "+ target +" :"+ msg +"\n", "UTF-8"))

# check connected users
def checkconns():
    connusers = str(subprocess.check_output("who -q; exit 0", stderr=subprocess.STDOUT,shell=True).decode()).splitlines()
    ircsock.send(bytes("PRIVMSG "+ channel +" :Connected users: ", "UTF-8"))
    i = 1
    for users in connusers:
        if "#" not in users:
            ircsock.send(bytes(str(i) +"_"+ users +" ", "UTF-8"))
            i = i + 1
    ircsock.send(bytes("\n", "UTF-8"))

# now for the meat
def main():

# wait for the connection to come up,
# then identify with nickserv,
# then wait for the response and join the channel
    time.sleep(3)
    identify()
    time.sleep(1)

    jchan(channel)

# so we've connected, set the nick, and joined the channel. for multiple channels, repeat the above jchan() function with different channel names. I'm only doing one. Because I feel like it.
# now we're going to set the rest of the meat to an infinite loop. It's connected, now keep looping to respond to commands and ping-pongs and whatever else this bot does in its puny bot life
    while 1:

# when receiving SIGINT / ^C from the command line, die gracefully
        def signal_handler(sig, frame):
            print("\n\n\nCaught ^C, exiting...\n\n")
            ircsock.close()
            sys.exit(0)
        signal.signal(signal.SIGINT, signal_handler)

        ircmsg = ircsock.recv(2048).decode("UTF-8")
        ircmsg = ircmsg.strip("\n\r")
# parse received data in the channel by user and content. helps us look for commands
        if ircmsg.find("PRIVMSG") != -1:
            name = ircmsg.split('!',1)[0][1:]
            message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]

# make sure it's coming from a valid nick (16chars or less).
# use this skeleton to add more commands/responses.
            if len(name) < 17:
# say hi
                if message.find('hola ' + nickname) != -1:
                    sendmsg("Que pasa, "+ name +"?!")
                if message[:5].find('!yell') != -1:
                    target = message.split(' ', 1)[1]
                    if target.find(' ') != -1:
                        message = target.split(' ', 1)[1]
                        target = target.split(' ')[0]
                    else:
                        target = name
                        message = "The message should be in the format of !yell [target] [message]"
                    sendmsg(message, target)

# this implements the manpage reference
# luckily the openbsd team made it stupid easy for me
                if message[:5].find('!man') != -1:
                    target = message.split(' ', 1)[1]
                    if target.find(' ') != -1:
                        message = target.split(' ', 1)[1]
                        target = target.split(' ')[0]
                    sendmsg("https://man.openbsd.org/"+ target)

# toot to the ~institute mastodon account
                if message[:5].find('!toot') != -1:
                    target = message.split(' ', 1)[1]
                    if target.find(' ') != -1:
                        message = target.split(' ', 1)[1]
                        target = target.split(' ')[0]
                        os.system("./toot.py \""+ target +" "+ message +"\"")
                        sendmsg("Successfully tooted: "+ target +" "+ message)

# the help command
                if message[:5].find('!help') != -1:
                    sendmsg("Useage: !botlist - Required info for tilde.chat bots. !man [term] - Returns link to OpenBSD man pages. !toot [message] - Toots to ~institute mastodon account. !uptime - Returns uptime and load averages of ~institute. !load - Displays information on BSD load measurements. !users - Displays currently connected users.")

                if message[:5].find('!load') != -1:
                    sendmsg("Run !uptime - Caveat: https://undeadly.org/cgi?action=article;sid=20090715034920")
# this is the exit command. change the exitcmd and exitrsp vars above to change
# the command and what the bot's last words will be
                if name.lower() == adminname.lower() and message.rstrip().lower() == exitcmd:
                    sendmsg(exitrsp)
                    ircsock.send(bytes("QUIT \n", "UTF-8"))
                    ircsock.close()
                    print("\n\n\nRECEIVED EXIT CMD WITHIN IRC\n\n")
                    sys.exit(0)
                    return
                if message == "!uptime":
                    uptime = str(subprocess.check_output(['uptime']).decode())
                    sendmsg(uptime)

# the !botlist command is required on tilde.chat
# in case your bot is misbehaving
                if message == "!botlist":
                    sendmsg("Owned by "+ ownermail +". I'm a fragile work-in-progress, please don't hurt me!")

# respond with connected users
                if message == "!users":
                    checkconns()

# tells the bot to register if you want
                if name.lower() == adminname.lower() and message == "!register":
                    ircsock.send(bytes("PRIVMSG nickserv :register "+ nickservpass +" "+ ownermail +"\n", "UTF-8"))
                    while ircmsg.find("register") != -1:
                        ircmsg = ircsock.recv(2048).decode("UTF-8")
                        ircmsg = ircmsg.strip("\n\r")
                        print(ircmsg)

# PING? PONG!!!
        if ircmsg.find("PING :") != -1:
            ping()

main()
