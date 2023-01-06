from ..species import Species


class ChemicalMechanism(object):

    def __init__(self):
        """
        Chemical mechanism.
        """
        self.name = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def nmvoc_species(self):
        """
        Get NMVOC (None-Methane VOC) species
        :return: (*list of species*) NMVOC species
        """
        return []

    def voc_species(self):
        """
        Get VOC species
        :return:
        """
        return []

    def all_species(self):
        """
        Get all species
        :return: (*list of species*) All species
        """
        return []

    def species(self, name):
        """
        Get species by name
        :param name: (*str*) Species name
        :return: Species
        """
        species = self.all_species()
        for spec in species:
            if spec.name == name:
                return spec
        return Species(name)
