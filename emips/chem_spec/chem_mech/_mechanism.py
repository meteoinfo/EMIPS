from ..species import Species
from abc import ABCMeta, abstractmethod


class ChemicalMechanism(object):

    __metaclass__ = ABCMeta

    def __init__(self):
        """
        Chemical mechanism.
        """
        self.name = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    @abstractmethod
    def nmvoc_species(self):
        """
        Get NMVOC (None-Methane VOC) species
        :return: (*list of species*) NMVOC species
        """
        return []

    @abstractmethod
    def voc_species(self):
        """
        Get VOC species
        :return:
        """
        return []

    @abstractmethod
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

    @abstractmethod
    def lump_RETRO(self, spec, biomass=False):
        """
        Lump a species from RETRO species.
        :param spec: (*Species*) The species in this chemical mechanism.
        :param biomass: (*bool*) Whether is biomass section. Default is `False`.
        :return: (*dict of Species and ratios*) The species in pollutant profile to be lumped as
            the chemical mechanism species.
        """
        pass
