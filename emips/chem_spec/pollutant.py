from ..utils.units import Units, Weight, Area, Period
from ..utils._base import enum

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

#Normally used pollutants
PollutantEnum = enum(BC = Pollutant("BC"),
                     CO = Pollutant("CO"),
                     NH3 = Pollutant("NH3"),
                     NOx = Pollutant("NOx"),
                     OC = Pollutant("OC"),
                     PM25 = Pollutant("PM25"),
                     SO2 = Pollutant("SO2"),
                     PMcoarse = Pollutant("PMcoarse"),
                     PM10more = Pollutant("PM10more"),
                     CH4 = Pollutant("CH4"),
                     NMVOC = Pollutant("NMVOC"),
                     VOC = Pollutant("VOC"))