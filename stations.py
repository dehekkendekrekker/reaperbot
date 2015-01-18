#!/usr/bin/python
import csv
import json
from datetime import datetime


class Station:
    def __init__(self):
        self.mac = ""
        self.first_time_seen = ""
        self.last_time_seen = ""
        self.power = 0
        self.nr_packets = 0


class APClients(list):
    def sort_by_power(self, direction):
        if direction == "asc":
            self.sort(key=lambda x: x.sorting_lambda(), reverse=False)
        else:
            self.sort(key=lambda x: x.sorting_lambda(), reverse=True)


class AP(Station):
    def __init__(self):
        Station.__init__(self)

        self.channel = 0
        self.speed = ""
        self.privacy = ""
        self.authentication = ""
        self.nr_beacons = 0
        self.nr_iv = 0
        self.lan_ip = 0
        self.id_length = 0
        self.essid = ""
        self.key = ""
        self.handshake_captured = False
        self.attack_attempts = 0
        self.associations = APClients()

    def get_avg_power(self):
        if self.associations:
            return (self.power + self.associations[0].power) / 2
        else:
            return self.power

    def toList(self):
        data = {'bssid': self.mac,
                'essid': self.essid,
                'avg_power': str(self.get_avg_power()),
                'nr_associations': str(len(self.associations))}

        return data


class APClient(Station):
    def __init__(self):
        Station.__init__(self)

        self.association_bssid = ""
        self.probed_essids = ""

    def sorting_lambda(self):
        if self.power > -5:
            return -100
        else:
            return self.power


class APs(list):
    def get_by_mac(self, mac):
        for ap in self:
            if ap.mac == mac:
                return ap
        return None

    def sort_by_power(self, direction):
        if direction == "asc":
            self.sort(key=lambda x: x.power, reverse=False)
        else:
            self.sort(key=lambda x: x.power, reverse=True)

    def sort_by_average_power(self, direction):
        if direction == "asc":
            self.sort(key=lambda x: x.get_avg_power(), reverse=False)
        else:
            self.sort(key=lambda x: x.get_avg_power(), reverse=True)
        return self

    def get_by_privacy(self, privacy):
        aps = APs()
        for ap in self:
            if privacy.upper() == "WPA":
                if ap.privacy in ["WPA", "WPA2WPA", "WPA2"]:
                    aps.append(ap)
        return aps

    def get_aps_with_associations(self):
        aps = APs()
        for ap in self:
            if len(ap.associations) > 0:
                aps.append(ap)
        return aps

    def toList(self):
        data = list()
        for station in self:
            data.append(station.toList())

        return data

    def __str__(self):
        result = list()
        for ap in self:
            result.append(ap.mac + "\t" + ap.essid + "\t" + str(ap.power) + "\t" + str(len(ap.associations)))
        if len(result) > 0:
            return "\n".join(result)
        else:
            return None



class Stations:
    def __init__(self):
        self.aps = APs()
        self.apcs = APClients()




def create_valid_ap(row):
    try:
        ap = AP()
        ap.mac = row[0].strip()
        ap.first_time_seen = datetime.strptime(row[1].strip(), "%Y-%m-%d %H:%M:%S")  # date
        ap.last_time_seen = datetime.strptime(row[2].strip(), "%Y-%m-%d %H:%M:%S")  # date
        ap.channel = int(row[3].strip())  # int
        ap.speed = int(row[4].strip())  # int
        ap.privacy = row[5].strip()
        ap.cipher = row[6].strip()
        ap.authentication = row[7].strip()
        ap.power = int(row[8].strip())  # int
        ap.nr_beacons = int(row[9].strip())  # int
        ap.nr_iv = int(row[10].strip())  # int
        ap.lan_ip = row[11].strip()
        ap.id_length = row[12].strip()
        ap.essid = row[13].strip()
        ap.key = row[14].strip()

        if ap.power == -1 or ap.channel == -1:
            return None
        else:
            return ap
    except IndexError:
        return None


def create_valid_apc(row):
    apc = APClient()
    apc.mac = row[0].strip()
    apc.first_time_seen = datetime.strptime(row[1].strip(), "%Y-%m-%d %H:%M:%S")  # date
    apc.last_time_seen = datetime.strptime(row[2].strip(), "%Y-%m-%d %H:%M:%S")  # date
    apc.power = int(row[3].strip())  # int
    apc.nr_packets = int(row[4].strip())  # int
    apc.association_bssid = row[5].strip()
    apc.probed_essids = row[6].strip()

    if apc.power == -1:
        return None

    return apc


def process_associations(stations):
    for apc in stations.apcs:
        ap = stations.aps.get_by_mac(apc.association_bssid)
        if ap:
            ap.associations.append(apc)
            ap.associations.sort_by_power("desc")


def load_stations_from_csv(filename):
    stations = Stations()

    state = "undetermined"
    header_skipped = False

    """ Load CSV file"""
    with open(filename, 'rb') as csvfile:
        linereader = csv.reader(csvfile, delimiter=',')
        for row in linereader:
            if state == "undetermined":
                if not row:
                    state = "ap"
                    header_skipped = False
                    continue

            if state == "ap":
                if not row:
                    state = "apc"
                    header_skipped = False
                    continue
                elif not header_skipped:
                    header_skipped = True
                    continue
                else:
                    try:
                        ap = create_valid_ap(row)
                        if ap:
                            stations.aps.append(ap)
                    except ValueError:
                        None

            if state == "apc":
                if not row:
                    state = "undetermined"
                    header_skipped = False
                    continue
                elif not header_skipped:
                    header_skipped = True
                    continue
                else:
                    try:
                        apc = create_valid_apc(row)
                        if apc:
                            stations.apcs.append(apc)
                    except ValueError:
                       None

    return stations


def load_stations(filename):
    stations = load_stations_from_csv(filename)
    process_associations(stations)
    stations.aps.sort_by_power("desc")

    return stations




