import curses
from collections import deque



class TargetWindow:
    target_aps = None
    target_display_limit = 10
    prio_x = 1
    bssid_x = 6
    avg_power_x = 27
    nr_associations_x = 38
    essid_x = 51

    def __init__(self):
        self.target_wnd = curses.newwin(15, 70, 0, 0)
        self.target_wnd.border(0)
        self.target_wnd.box()

    def draw_headers(self):
        self.target_wnd.addstr(0, 2, " Targets ", curses.COLOR_GREEN)
        self.target_wnd.addstr(1, self.prio_x, "Prio")
        self.target_wnd.addstr(1, self.bssid_x, "BSSID")
        self.target_wnd.addstr(1, self.avg_power_x, "Avg. Power")
        self.target_wnd.addstr(1, self.nr_associations_x, "# clients")
        self.target_wnd.addstr(1, self.essid_x, "ESSID")

    def draw_targets(self):
        prio = 1
        y = 2
        for ap in self.target_aps:
            if prio <= self.target_display_limit:
                self.target_wnd.addstr(y, self.prio_x, str(prio))
                self.target_wnd.addstr(y, self.bssid_x, ap.mac)
                self.target_wnd.addstr(y, self.avg_power_x, str(ap.get_avg_power()))
                self.target_wnd.addstr(y, self.nr_associations_x, str(len(ap.associations)))
                self.target_wnd.addstr(y, self.essid_x, ap.essid)
                y += 1
            else:
                remaining = len(self.target_aps) - self.target_display_limit
                self.target_wnd.addstr(y + 1, self.bssid_x, str(remaining) + " More ..")

            prio += 1


    def draw(self):
        self.target_wnd.erase()
        self.target_wnd.box()
        self.draw_headers()
        if self.target_aps:
            self.draw_targets()
        self.target_wnd.noutrefresh()

class StatusWindow:
    status_wnd = None
    wnd_width = None
    wnd_height = None

    max_items = 13
    items = None

    def __init__(self, height, width, y, x):
        self.wnd_width = width
        self.wnd_height = height
        self.status_wnd = curses.newwin(self.wnd_height, self.wnd_width, y, x)
        self.status_wnd.border(0)
        self.status_wnd.box()

        #init list
        self.items = list()
        self.max_items = self.wnd_height - 2

    def draw_headers(self):
        self.status_wnd.addstr(0, 2, " Status ", curses.COLOR_GREEN)

    def draw_messages(self):
        y = 1
        items = deque(self.items, self.max_items)
        for item in items:
            self.status_wnd.addstr(y, 2, item)
            y += 1


    def draw(self):
        self.status_wnd.box()
        self.draw_headers()
        self.draw_messages()
        self.status_wnd.noutrefresh()





class Dispay():
    screen = None
    target_wnd = None
    status_wnd = None

    def __init__(self, screen):
        self.screen = screen
        self.target_wnd = TargetWindow()
        self.status_wnd = StatusWindow(15, 70, 15, 0)
        self.update()

    def add_status_message(self, message):
        self.status_wnd.items.append(message)

    def set_target_aps(self, aps):
        self.target_wnd.target_aps = aps


    def update(self):
        self.target_wnd.draw()
        self.status_wnd.draw()
        self.screen.refresh()

    def wait_for_quit(self):
        self.add_status_message("Press 'q' to exit")
        self.update()
        while True:
            if self.screen.getkey() == 'q':
                break
















