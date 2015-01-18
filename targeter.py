import datetime
import copy
import stations


class Targeter:
    wnd_opportunity = 300
    attack_attempts = 3
    attacked_targets = None
    possible_targets = None
    target_list = None
    targeter_running = None

    def __init__(self, config):
        self.wnd_opportunity = int(config.get("main", "wnd_opportunity"))
        self.attack_attempts = int(config.get("main", "attack_attempts"))
        self.attacked_targets = stations.APs()
        self.possible_targets = stations.APs()
        self.targeter_running = False

    # public
    def set_possible_targets(self, aps):
        self.possible_targets = copy.deepcopy(aps)
        self.create_target_list()

    # private
    def create_target_list(self):
        possible_targets = self.get_relevant_aps()
        possible_targets = possible_targets.get_by_privacy("WPA")
        possible_targets = possible_targets.get_aps_with_associations()
        possible_targets.sort_by_average_power("desc")
        self.target_list = possible_targets

    def get_target_list(self):
        return self.target_list

    # private
    def get_relevant_aps(self):
        aps = stations.APs()
        now = datetime.datetime.now()

        for ap in self.possible_targets:
            delta = now - ap.last_time_seen
            if delta.seconds < self.wnd_opportunity:
                aps.append(ap)

        return aps

    def request_target(self):
        for ap in self.possible_targets:
            attacked_ap = self.attacked_targets.get_by_mac(ap.mac)
            if attacked_ap:
                if attacked_ap.attack_attempts < self.attack_attempts:
                    return ap
                else:
                    continue
            else:
                return ap

        return None






