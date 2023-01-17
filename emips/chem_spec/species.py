from ..utils import Units, Weight, Area, Period
from mipylib.enum import Enum


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
        s = 'Name: {}; Units: {}'.format(self.name, self.units)
        if self.molar_mass is not None:
            s = s + '; Molar mass: {}'.format(self.molar_mass)
        return s

    __repr__ = __str__

    def __eq__(self, other):
        return self.name == other.name and self.units == other.units


# Normally used species
class SpeciesEnum(Enum):
    PEC = Species("PEC")
    CO = Species("CO", molar_mass=28)
    CH4 = Species("CH4", molar_mass=16)
    NH3 = Species("NH3", molar_mass=17)
    POA = Species("POA")
    SO2 = Species("SO2", molar_mass=64)
    PMC = Species("PMC")
    NO = Species("NO", molar_mass=30)
    NO2 = Species("NO2", molar_mass=46)
    SULF = Species("SULF")
    PMFINE = Species("PMFINE")
    PNO3 = Species("PNO3")
    PSO4 = Species("PSO4")

    def __str__(self):
        if self.value.molar_mass is None:
            return "{} ({})".format(self.name, self.value.units)
        else:
            return "{} ({}) ({})".format(self.name, self.value.units, self.value.molar_mass)

    def __repr__(self):
        return self.__str__()

    @property
    def units(self):
        return self.value.units

    @property
    def molar_mass(self):
        return self.value.molar_mass

    @classmethod
    def all_species(cls):
        """
        Get all species
        :return: (*list of species*) All species
        """
        species = [cls.PEC, cls.CO, cls.CH4, cls.NH3, cls.POA, cls.SO2, cls.PMC,
                   cls.NO, cls.NO2, cls.SULF, cls.PMFINE, cls.PNO3, cls.PSO4]
        return species

    @classmethod
    def species(cls, name):
        """
        Get species from name
        :param name: (*str*) Species name
        :return: The species
        """
        species = cls.all_species()
        for spec in species:
            if spec.name == name:
                return spec
        return Species(name)
