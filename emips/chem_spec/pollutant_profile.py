from .pollutant import Pollutant
from .species import Species

class PollutantProfileItem(object):

    def __init__(self, pollutant, species, sf, dv, mf):
        """
        Pollutant profile item

        :param pollutant The pollutant
        :param species: The species
        :param sf: Split factor
        :param dv: Divisor
        :param mf: Mass fraction
        """
        if isinstance(pollutant, basestring):
            self.pollutant = Pollutant(pollutant)
        else:
            self.pollutant = pollutant
        if isinstance(species, basestring):
            self.species = Species(species)
        else:
            self.species = species
        self.split_factor = sf
        self.divisor = dv
        self.mass_fraction = mf

    def __str__(self):
        r = "{}: split_factor={}, divisor={}, mass_fraction={}".format(self.species.name, self.split_factor,
            self.divisor, self.mass_fraction)
        return r

    __repr__ =  __str__

    @classmethod
    def read_string(cls, line):
        """
        Read pollutant profile item from string line
        :param line: The string line
        :return: Pollutant profile item
        """
        data = line.split()
        pollutant = Pollutant(data[1])
        species = Species(data[2])
        return PollutantProfileItem(pollutant, species, float(data[3]), float(data[4]), float(data[5]))

class PollutantProfile(list):

    def __init__(self, pollutant, prof_items=[]):
        """
        Pollutant profile
        :param prof_items: The pollutant profile items
        """
        list.__init__([])
        if isinstance(pollutant, basestring):
            pollutant = Pollutant(pollutant)
        self.pollutant = pollutant
        self.extend(prof_items)

    def __str__(self):
        r = 'Pollutant: {}'.format(self.pollutant.name)
        for prof_item in self:
            r += "\n\t{}".format(prof_item)
        return r

    __repr__ = __str__