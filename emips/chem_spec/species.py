from ..utils import Units, Weight, Area, Period

class Species(object):

    def __init__(self, name, units=Units(Weight.KG, Area.M2, Period.SECOND), ratio=1.0):
        """
        Chemical species

        :param name: Species name
        :param units: Species units
        :param ratio: Lump ratio - only used for VOC lump
        """
        self.name = name
        self.units = units
        self.ratio = ratio

    def __str__(self):
        return 'Name: {}}\nUnits: {}\nRatio: {}'.format(self.name, self.units,
                                                        self.ratio)

    __repr__ = __str__

    def __eq__(self, other):
        return self.name == other.name and self.units == other.units