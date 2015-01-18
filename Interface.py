__author__ = 'parallax'

class Interface:
    name = None
    type = None
    power = None

    def __init__(self, name, power):
        self.name = name
        self.power = power

    def __str__(self):
        return self.name + "\t" + self.power