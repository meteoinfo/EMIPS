from ._mechanism import ChemicalMechanism
from ..species import Species

class RADM2(ChemicalMechanism):
    
    def __init__(self):
        """
        RADM2 chemical mechanism
        """
        super(RADM2, self).__init__()

    @property
    def name(self):
        """
        Get chemical mechanism name
        :return: The name
        """
        return 'RADM2'

    @property
    def voc_species(self):
        """
        Get VOC species
        :return:
        """
        sp_list = [Species('ALD'), Species('CSL'), Species('ETH'), Species('HC3'),
                   Species('HC5'), Species('HC8'), Species('HCHO'), Species('ISOP'),
                   Species('KET'), Species('NR'), Species('OL2'), Species('OLE'),
                   Species('OLI'), Species('OLT'), Species('ORA2'), Species('PAR'),
                   Species('TERP'), Species('TOL'), Species('XYL')]

        return sp_list

    def lump(self, spec):
        """
        Lump VOC species.
        :param spec: (*Species*) The species in this chemical mechanism.
        :return: (*list of Species*) The species in pollutant profile to be lumped as
            the chemical mechanism species.
        """
        l_species = []
        if spec.name == 'ALD':
            l_species.append(Species('Other_alkanals'))