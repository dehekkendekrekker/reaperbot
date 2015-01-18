__author__ = 'parallax'
import logging


class Logger:
    def __init__(self):
        logging.basicConfig(filename="/var/log/reaperbot.log", level=logging.DEBUG)

    def notice(self, message):
        logging.info("[+] " + message)

    def error(self, message):
        logging.error("[!] " + message)