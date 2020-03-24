from ..utils import Units, Weight, Area, Period
from ..utils._base import enum

class Species(object):

    def __init__(self, name, units=Units(Weight.KG, Area.M2, Period.SECOND),
                 molar_mass=None):
        """
        Chemical species

        :param name: (*str*) Species name
        :param units: (*Units*) Species units
        :param molar_mass: (*float*) Molar mass
        """
        self.name = name
        self.units = units
        self.molar_mass = molar_mass

    def __str__(self):
        return 'Name: {}; Units: {}'.format(self.name, self.units)

    __repr__ = __str__

    def __eq__(self, other):
        return self.name == other.name and self.units == other.units

#Normally used species
SpeciesEnum = enum(PEC = Species("PEC"),
                   CO = Species("CO", molar_mass=28),
                   CH4 = Species("CH4", molar_mass=16),
                   NH3 = Species("NH3", molar_mass=17),
                   POA = Species("POA"),
                   SO2 = Species("SO2", molar_mass=64),
                   PMC = Species("PMC"),
                   NO = Species("NO", molar_mass=30),
                   NO2 = Species("NO2", molar_mass=46),
                   SULF = Species("SULF"),
                   PMFINE = Species("PMFINE"),
                   PNO3 = Species("PNO3"),
                   PSO4 = Species("PSO4"))