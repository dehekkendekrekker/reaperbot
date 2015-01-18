__author__ = 'parallax'

import sys
from twisted.words.protocols import irc
from twisted.internet import protocol, reactor


class ReaperBot(irc.IRCClient):
    def __init__(self):
        self.channel = None
        self.message = None
        self.auth_key = "1337"
        self.authenticated = False
        self.master = ""

    def _get_nickname(self):
        return self.factory.nickname

    nickname = property(_get_nickname)

    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as %s." % (self.nickname,)

    def joined(self, channel):
        print "Joined %s." % (channel,)

    def privmsg(self, user, channel, msg):
        # Set the global properies for easy reference later on
        self.user = user
        self.channel = channel
        self.message = msg

        # Received message from something else than a user? Do nothing
        if not user:
            return

        # Start looking for an auth command. It's the only command that is handled without authentication
        command = msg.split(" ", 1)[0]
        if command == "auth":
            self.handle_auth()
            return

        # Any commands after this line require an authenticated master
        if not self.authenticated or user != self.master:
            return

        if command == "help":
            self.display_help()
            return


        self.msg(channel, "That's so interesting master, tell me more")

    # Handles the authentication of a user.
    # Only one user can be authenticated, and is therefor able to issue commands
    def handle_auth(self):
        operand = self.message.split(" ", 1)[1]
        if operand == self.auth_key:
            self.authenticated = True
            self.master = self.user
            print self.user + " is now master"
            self.msg(self.channel, "ack")
        return

    def display_help(self):
        self.msg(self.channel, "The following commands are possible:")
        self.msg(self.channel, "status   | Displays the status of the sniffer, targeter and attacker")
        return



class BotFactory(protocol.ClientFactory):
    protocol = ReaperBot

    def __init__(self, channel, nickname='reaperbot'):
        self.channel = channel
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason,)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)


if __name__ == "__main__":
    chan = sys.argv[1]
    reactor.connectTCP('irc.oftc.net', 6667, BotFactory('#' + chan))
    reactor.run()