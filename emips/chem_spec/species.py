from ..utils import Units, Weight, Area, Period

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
        return 'Name: %s\nUnits: %s' % (self.name, self.units)

    __repr__ = __str__

    def __eq__(self, other):
        return self.name == other.name and self.units == other.units