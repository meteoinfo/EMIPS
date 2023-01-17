from ..utils.units import Units, Weight, Area, Period
from mipylib.enum import Enum


class Pollutant(object):

    def __init__(self, name, units=Units(Weight.KG, Area.M2, Period.SECOND)):
        """
        Chemical pollutant

        :param name: Pollutant name
        :param units: Pollutant units
        """
        self.name = name
        self.units = units

    def __str__(self):
        return 'Name: %s\nUnits: %s' % (self.name, self.units)

    __repr__ = __str__

    def __eq__(self, other):
        return self.name == other.name and self.units == other.units


# Normally used pollutants
class PollutantEnum(Enum):
    BC = Pollutant("BC")
    CO = Pollutant("CO")
    NH3 = Pollutant("NH3")
    NOx = Pollutant("NOx")
    OC = Pollutant("OC")
    PM2_5 = Pollutant("PM2_5")
    SO2 = Pollutant("SO2")
    PM10 = Pollutant("PM10")
    PMcoarse = Pollutant("PMcoarse")
    PM10more = Pollutant("PM10more")
    CH4 = Pollutant("CH4")
    NMVOC = Pollutant("NMVOC")
    VOC = Pollutant("VOC")

    def __str__(self):
        return "{} ({})".format(self.name, self.value.units)

    def __repr__(self):
        return self.__str__()

    @classmethod
    def of(cls, name, units=None):
        """
        Create a PollutantEnum.
        :param name: (*str*) The name.
        :param units: (*Units*) The units.
        :return: PollutantEnum.
        """
        pollutant = PollutantEnum[name]
        if units is not None:
            pollutant.units = units

        return pollutant

    @property
    def units(self):
        return self.value.units

    @units.setter
    def units(self, value):
        self.value.units = value

    @property
    def is_VOC(self):
        if self in [PollutantEnum.NMVOC, PollutantEnum.VOC]:
            return True
        else:
            return False
