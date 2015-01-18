import ConfigParser
import os
import sys


def error(message):
    sys.stderr.write("[!] " + message + "\n")


def notice(message):
    sys.stdout.write("[+] " + message + "\n")


class Config(ConfigParser.ConfigParser):
    display = None
    logger = None
    listen_dump_file = "reaperbot_dmp"
    tmp_dir = None


    def __init__(self, filename, logger):
        ConfigParser.ConfigParser.__init__(self)
        self.read(filename)
        self.logger = logger

    # --- IRC RELATED CONFIG ---
    def get_host(self):
        return self.get("main", "host")

    def get_port(self):
        return int(self.get("main", "port"))

    def get_channel(self):
        return self.get("main", "channel")

    def get_handle(self):
        return self.get("main", "handle")

    def confirm_root(self):
        if not os.getuid() == 0:
            self.logger.error("reaperbot must be run as root")
            return False
        else:
            return True

    def get_dump_file_full_path(self):
        return self.tmp_dir + "/" + self.listen_dump_file + "-01.csv"


    def validate(self):
        if not self.confirm_root():
            return False

        result = True

        if not self.has_option("main", "tmp_dir") or not self.get("main", "tmp_dir"):
            self.logger.error("tmp dir not set")
            result = False

        if self.has_option("main", "tmp_dir") and not os.path.isdir(self.get("main", "tmp_dir")):
            self.logger.error("tmp dir is not a dir")
            result = False

        if not self.has_option("main", "listen_interface") or not self.get("main", "listen_interface"):
            self.logger.error("listen_interface not set")
            result = False
        # if not self.has_option("main", "attack_interface"):
        # print "attack_interface not set")
        # result = False
        if not self.has_option("main", "wnd_opportunity") or not self.get("main", "wnd_opportunity"):
            self.logger.error("wnd_opportunity not set, should be seconds")
            result = False
        if not self.has_option("main", "attack_attempts") or not self.get("main", "attack_attempts"):
            self.logger.error("attack_attempts not set, should be number")
            result = False

        if not result:
            self.logger.error("One or more config settings aren't correct, check /etc/reaperbot/config")

        if result:
            self.tmp_dir = self.get("main", "tmp_dir")

        return result
