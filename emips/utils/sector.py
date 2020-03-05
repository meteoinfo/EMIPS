from ._base import enum

__all__ = ['Sector', 'SectorName']

SectorName = enum(ENERGY = "energy",
              INDUSTRY = "industry",
              RESIDENTIAL = "residential",
              SHIPS = "ships",
              TRANSPORT = "transport",
              AIR = "air",
              BIOMASS = "biomass",
              WASTE_TREATMENT = "waste_treatment",
              AGRICULTURE = "agriculture")

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
