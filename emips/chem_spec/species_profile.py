from .pollutant import Pollutant, PollutantEnum
from .species import Species, SpeciesEnum


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
        elif isinstance(pollutant, PollutantEnum):
            self.pollutant = pollutant.value
        else:
            self.pollutant = pollutant

        if isinstance(species, basestring):
            self.species = Species(species)
        elif isinstance(species, SpeciesEnum):
            self.species = species.value
        else:
            self.species = species

        self.split_factor = sf
        self.divisor = dv
        self.mass_fraction = mf

    def __str__(self):
        r = "{}: split_factor={}, divisor={}, mass_fraction={}".format(self.species.name, self.split_factor,
                                                                       self.divisor, self.mass_fraction)
        return r

    __repr__ = __str__

    @classmethod
    def read_string(cls, line, mechanism=None):
        """
        Read pollutant profile item from string line
        :param line: (*str*) The string line
        :param mechanism: (*ChemicalMechanism*) Chemical mechanism
        :return: Pollutant profile item
        """
        data = line.split()
        pollutant = Pollutant(data[1])
        if mechanism is None:
			if data[2] == 'NO':
				species = Species(data[2], molar_mass=30)
			elif data[2] == 'NO2':
				species = Species(data[2], molar_mass=46)
			else:
				species = Species(data[2])
        else:
            species = mechanism.species(data[2])
        return SpeciesProfile(pollutant, species, float(data[3]), float(data[4]), float(data[5]))
