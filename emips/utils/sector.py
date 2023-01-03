from mipylib.enum import Enum

__all__ = ['Sector', 'SectorEnum']


class Sector(object):

    def __init__(self, name, scc):
        """
        Sector class
        :param name: (*str*) Sector name.
        :param scc: (*str*) Source classification code of sector.
        """
        self.name = name
        self.scc = scc

    def __str__(self):
        re = 'Sector: {}; SCC: {}'.format(self.name, self.scc)
        return re

    __repr__ = __str__


# Normally used sectors
class SectorEnum(Enum):
    ENERGY = Sector("energy", '10100101')
    INDUSTRY = Sector("industry", "30100101")
    RESIDENTIAL = Sector("residential", "2104001000")
    SHIPS = Sector("ships", "2280000000")
    TRANSPORT = Sector("transport", "2294000000")
    AIR = Sector("air", "2275000000")
    BIOMASS = Sector("biomass", "2810001000")
    WASTE_TREATMENT = Sector("waste_treatment", "50100101")
    AGRICULTURE = Sector("agriculture", "28050000")
