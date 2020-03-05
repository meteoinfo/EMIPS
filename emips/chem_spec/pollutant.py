from ..utils.units import Units, Weight, Area, Period

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