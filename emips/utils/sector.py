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
    ENERGY = Sector("ENERGY", '10100101')
    INDUSTRY = Sector("INDUSTRY", "30100101")
    RESIDENTIAL = Sector("RESIDENTIAL", "2104001000")
    SHIPS = Sector("SHIPS", "2280000000")
    TRANSPORT = Sector("TRANSPORT", "2294000000")
    AIR = Sector("AIR", "2275000000")
    BIOMASS = Sector("BIOMASS", "2810001000")
    WASTE_TREATMENT = Sector("WASTE_TREATMENT", "50100101")
    AGRICULTURE = Sector("AGRICULTURE", "28050000")

    @classmethod
    def of(cls, name, scc=None):
        """
        Create a SectorEnum.
        :param name: (*str*) The sector name.
        :param scc: (*str*) The SCC.
        :return: The SectorEnum.
        """
        sector = SectorEnum[name.upper()]
        if scc is not None:
            if isinstance(scc, int):
                scc = str(scc)
            sector.scc = scc

        return sector

    @property
    def scc(self):
        return self.value.scc

    @scc.setter
    def scc(self, value):
        self.value.scc = value

    def __str__(self):
        return "{} ({})".format(self.name, self.value.scc)

    def __repr__(self):
        return self.__str__()
