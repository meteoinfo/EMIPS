from ..utils import Units, Weight, Area, Period
from ..utils._base import enum

class Species(object):

    def __init__(self, name, units=Units(Weight.KG, Area.M2, Period.SECOND)):
        """
        Chemical species

        :param name: Species name
        :param units: Species units
        """
        self.name = name
        self.units = units

    def __str__(self):
        return 'Name: {}; Units: {}'.format(self.name, self.units)

    __repr__ = __str__

    def __eq__(self, other):
        return self.name == other.name and self.units == other.units

#Normally used species
SpeciesEnum = enum(PEC = Species("PEC"),
                   CO = Species("CO"),
                   NH3 = Species("NH3"),
                   POA = Species("POA"),
                   SO2 = Species("SO2"),
                   PMC = Species("PMC"),
                   NO = Species("NO"),
                   NO2 = Species("NO2"),
                   SULF = Species("SULF"),
                   PMFINE = Species("PMFINE"),
                   PNO3 = Species("PNO3"),
                   PSO4 = Species("PSO4"))