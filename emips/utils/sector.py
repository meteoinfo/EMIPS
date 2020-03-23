from ._base import enum

__all__ = ['Sector', 'SectorEnum']

class Sector(object):

    def __init__(self, name):
        """
        Sector class
        :param name: (*str*) Sector name.
        """
        self.name = name

    def __str__(self):
        return self.name

    __repr__ = __str__

#Normally used sectors
SectorEnum = enum(ENERGY = Sector("energy"),
               INDUSTRY = Sector("industry"),
               RESIDENTIAL = Sector("residential"),
               SHIPS = Sector("ships"),
               TRANSPORT = Sector("transport"),
               AIR = Sector("air"),
               BIOMASS = Sector("biomass"),
               WASTE_TREATMENT = Sector("waste_treatment"),
               AGRICULTURE = Sector("agriculture"))
