from .pollutant import Pollutant
from .species import Species

class SpeciesProfile(object):

    def __init__(self, pollutant, species, sf, dv, mf):
        """
        Species profile

        :param pollutant: (*Pollutant*) The pollutant
        :param species: (*Species*) The species
        :param sf: (*float*) Split factor
        :param dv: (*float*) Divisor
        :param mf: (*float*) Mass fraction
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
        return SpeciesProfile(pollutant, species, float(data[3]), float(data[4]), float(data[5]))
