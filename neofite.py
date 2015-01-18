__author__ = 'parallax'
import config
import Scanner
import targeter
import Logger


class neofite:
    config = None
    scanner = None
    targeter = None
    logger = None

    def __init__(self, config):
        self.logger = Logger.Logger()
        self.config = config
        if not self.config.validate():
            exit()

        self.scanner = Scanner.Scanner(self.config, self.logger)
        if not self.scanner.validate():
           exit()

        self.targeter = targeter.Targeter(self.config)

    def is_scanner_running(self):
        if self.scanner.scanner_starting:
            return True
        if self.scanner.airodump_thread_hnd and self.scanner.airodump_thread_hnd.isAlive():
            return True
        return False

    def start_scanner(self):
        if self.is_scanner_running():
            self.logger.error("scanner already running")
            return False

        self.scanner.scanner_starting = True
        self.scanner.remove_previous_csv()
        self.scanner.enable_monitor_mode(self.scanner.listen_interface)
        self.scanner.start_airodump()
        self.scanner.scanner_starting = False
        return True

    def stop_scanner(self):
        if not self.is_scanner_running():
            self.logger.error("Scanner not running")
            return False

        self.scanner.stop_airodump()
        self.scanner.disable_monitoring()
        return True

    def get_potential_targets(self):
        if not self.is_scanner_running():
            self.logger.error("Scanner not running")
            return False

        stations = self.scanner.get_detected_stations()
        if len(stations.aps) == 0:
            return False

        return stations.aps

    def get_selected_targets(self):
        if not self.is_scanner_running():
            self.logger.error("Scanner not running")

        stations = self.scanner.get_detected_stations()
        self.targeter.set_possible_targets(stations.aps)

        selected_targets = self.targeter.get_target_list()

        if len(selected_targets) == 0:
            return False

        return selected_targets





