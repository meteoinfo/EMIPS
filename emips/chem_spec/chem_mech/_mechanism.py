
class ChemicalMechanism(object):

    def __init__(self):
        """
        Chemical mechanism.
        """
        pass

    @property
    def name(self):
        """
        Get chemical mechanism name
        :return: The name
        """
        return None

    @classmethod
    def voc_species(cls):
        """
        Get VOC species
        :return:
        """
        pass

    @classmethod
    def species(cls, name):
        """
        Get species by name
        :param name: (*str*) Species name
        :return: Species
        """
        pass