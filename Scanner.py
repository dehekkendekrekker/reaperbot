# Executing, communicating with, killing processes
from subprocess import Popen, call, PIPE
import os
import threading
import stations


DN = open(os.devnull, 'w')




class Scanner:
    logger = None
    scanner_starting = False
    listen_interface = None
    listen_monitor_interface = None
    listen_dump_file = None
    tmp_dir = None
    airodump_thread_hnd = None

    def __init__(self, config, logger):
        self.logger = logger
        self.tmp_dir = config.tmp_dir
        self.wireless_interfaces = list()
        self.listen_interface = config.get("main", "listen_interface")
        self.listen_dump_file = config.listen_dump_file
        self.airodump_thread_hnd = None
        self.scanner_starting = False

    def enable_monitor_mode(self, iface):
        self.logger.notice("Taking down [" + iface + "]")
        call(['ifconfig', iface, 'down'])

        self.logger.notice("Enabling monitor mode on [" + iface + "]")
        monitors_pre = self.enumerate_monitor_wireless_interfaces()
        call(['airmon-ng', 'start', iface], stdout=PIPE, stderr=DN)
        monitors_post = self.enumerate_monitor_wireless_interfaces()

        result = list(set(monitors_post) - set(monitors_pre))

        if len(result) > 1:
            self.logger.error("Too many monitors after enabling monitor!")
            return False

        if len(result) == 0:
            self.logger.error("Error enabling monitor")
            return False

        self.listen_monitor_interface = result[0]
        self.logger.notice("Initialised monitor [" + self.listen_monitor_interface + "] for listening")
        file = open("/tmp/liface", "w")
        file.write(self.listen_monitor_interface)

    def airodump_thread(self):
        path = self.tmp_dir + '/' + self.listen_dump_file
        dumpname = path + "-01.csv"
        self.logger.notice('dumping to ' + dumpname)
        call(['airodump-ng', '-i', self.listen_monitor_interface, '-w', path, '--output-format', 'csv'], stdout=DN, stderr=DN)

    def start_airodump(self):
        self.logger.notice("Starting airodump")
        self.airodump_thread_hnd = threading.Thread(target=self.airodump_thread)
        self.airodump_thread_hnd.daemon = False
        self.airodump_thread_hnd.start()

    def stop_airodump(self):
        proc = Popen(['pidof', 'airodump-ng'], stdout=PIPE, stderr=DN)
        pids = proc.communicate()[0]
        if len(pids) == 0:
            self.logger.error("airodump not running, can't stop")
            return False

        self.logger.notice("Killing airodump processes")
        call(['kill', pids], stdout=PIPE, stderr=DN)

    def disable_monitoring(self):
        file = open("/tmp/liface", "r")
        monitor = file.read()
        self.logger.notice("Stopping monitor [" + monitor + "]")
        call(['airmon-ng', 'stop', monitor], stdout=DN, stderr=DN)

    def validate(self):
        """ Check executables """
        result = True
        for file in ["airmon-ng", "aircrack-ng", "iwconfig"]:
            if not self.exec_exists(file):
                self.logger.error("could not find " + file)
                result = False

        if not result:
            self.logger.error("not all nescessary executables are installed")
            return result

        """ Check interfaces """
        interfaces = self.enumerate_non_monitor_wireless_interfaces()

        if not self.listen_interface in interfaces:
            self.logger.error("" + self.listen_interface + " is not a WLAN interface")
            result = False
            # # @ todo add support for attack interface

        return result

    def enumerate_non_monitor_wireless_interfaces(self):
        ifaces = list()
        proc = Popen(['iwconfig'], stdout=PIPE, stderr=DN)

        for line in proc.communicate()[0].split('\n'):
            if len(line) == 0: continue
            if ord(line[0]) != 32:  # Doesn't start with space
                iface = line[:line.find(' ')]

                if line.find('IEEE') != -1 and line.find('Mode:Monitor') == -1:
                    ifaces.append(iface)
        return ifaces

    def enumerate_monitor_wireless_interfaces(self):
        ifaces = list()
        proc = Popen(['iwconfig'], stdout=PIPE, stderr=DN)

        for line in proc.communicate()[0].split('\n'):
            if len(line) == 0: continue
            if ord(line[0]) != 32:  # Doesn't start with space
                iface = line[:line.find(' ')]
                if line.find('mon') != -1:
                    ifaces.append(iface)
        return ifaces

    def exec_exists(self, program):
        """
            Uses 'which' (linux command) to check if a program is installed.
        """

        proc = Popen(['which', program], stdout=PIPE, stderr=PIPE)
        txt = proc.communicate()
        if txt[0].strip() == '' and txt[1].strip() == '':
            return False
        if txt[0].strip() != '' and txt[1].strip() == '':
            return True

        return not (txt[1].strip() == '' or txt[1].find('no %s in' % program) != -1)

    def remove_previous_csv(self):
        extensions = ["-01.csv", "-01.ivs"]

        self.logger.notice("Removing previous dumpfiles")
        for extension in extensions:
            fullpath = self.tmp_dir + "/" + self.listen_dump_file + extension
            if os.path.isfile(fullpath):
                os.remove(fullpath)

    def get_detected_stations(self):
        path = self.tmp_dir + '/' + self.listen_dump_file + "-01.csv"
        return stations.load_stations(path)
