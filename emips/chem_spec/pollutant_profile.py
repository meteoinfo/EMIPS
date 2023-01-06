from .pollutant import Pollutant, PollutantEnum


class PollutantProfile(object):

    def __init__(self, pollutant, species_profiles=[]):
        """
        Pollutant profile

        :param pollutant: (*Pollutant*) The pollutant
        :param species_profiles: (*list of SpeciesProfile*) The species profiles
        """
        if isinstance(pollutant, basestring):
            pollutant = Pollutant(pollutant)
        elif isinstance(pollutant, PollutantEnum):
            pollutant = pollutant.value

        self.pollutant = pollutant
        self.species_profiles = []
        self.species_profiles.extend(species_profiles)

    def __str__(self):
        r = 'Pollutant: {}'.format(self.pollutant.name)
        for prof_item in self.species_profiles:
            r += "\n\t{}".format(prof_item)
        return r

    __repr__ = __str__

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.species_profiles[item]
        else:
            for spec_prof in self.species_profiles:
                if spec_prof.species.name == item:
                    return spec_prof
            raise ValueError("Not a valid key: {}".format(item))

    def append(self, spec_prof):
        """
        Append a species profile
        :param spec_prof: (*SpeciesProfile*) The species profile
        """
        self.species_profiles.append(spec_prof)

    def get_species(self):
        """
        Get species
        :return: The species
        """
        specs = []
        for spec_prof in self.species_profiles:
            specs.append(spec_prof.species)
        return specs
