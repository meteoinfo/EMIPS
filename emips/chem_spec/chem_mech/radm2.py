from ._mechanism import ChemicalMechanism
from ..species import Species
from .retro import RETRO

class RADM2(ChemicalMechanism):

    ALD = Species('ALD')    #Acetaldehyde and higher aldehydes
    CSL = Species('CSL')    #Counter species for cresol reaction
    ETH = Species('ETH')    #Ethane
    HC3 = Species('HC3')    #Alkanes w/ 2.7x10-13 > kOH < 3.4x10-12
    HC5 = Species('HC5')    #Alkanes w/ 3.4x10-12 > kOH < 6.8x10-12
    HC8 = Species('HC8')    #Alkanes w/ kOH > 6.8x10-12
    HCHO = Species('HCHO')  #Formaldehyde
    ISOP = Species('ISOP')  #Isoprene
    KET = Species('KET')    #Ketones
    NR = Species('NR')      #non-reactive class
    OL2 = Species('OL2')    #Ethene
    OLE = Species('OLE')    #double-bonded carbon atoms
    OLI = Species('OLI')    #Internal olefins
    OLT = Species('OLT')    #Terminal olefins
    ORA2 = Species('ORA2')  #Acetic and higher acids
    PAR = Species('PAR')    #single-bonds carbon atoms
    TERP = Species('TERP')  #Monoterpenes
    TOL = Species('TOL')    #Toluene and less reactive aromatics
    XYL = Species('XYL')    #Xylene and more reactive aromatics
    
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

    @classmethod
    def voc_species(cls):
        """
        Get VOC species
        :return:
        """
        sp_list = [cls.ALD, cls.CSL, cls.ETH, cls.HC3, cls.HC5, cls.HC8,
                   cls.HCHO, cls.ISOP, cls.KET, cls.NR, cls.OL2, cls.OLE,
                   cls.OLI, cls.OLT, cls.ORA2, cls.PAR, cls.TERP, cls.TOL,
                   cls.XYL]

        return sp_list

    @classmethod
    def lump_RETRO(cls, spec):
        """
        Lump a species from RETRO species.
        :param spec: (*Species*) The species in this chemical mechanism.
        :return: (*dict of Species and ratios*) The species in pollutant profile to be lumped as
            the chemical mechanism species.
        """
        spec_dict = {}
        if spec == cls.ALD:
            spec_dict[RETRO.Other_alkanals] = 1.0
        elif spec == cls.CSL:
            spec_dict[RETRO.Esters] = 1.0
            spec_dict[RETRO.Ethers] = 1.0
        elif spec == cls.ETH:
            spec_dict[RETRO.Ethane] = 1.0
        elif spec == cls.HC3:
            spec_dict[RETRO.Propane] = 1.0
        elif spec == cls.HC5:
            spec_dict[RETRO.Butanes] = 1.0
            spec_dict[RETRO.Pentanes] = 1.0
        elif spec == cls.HC8:
            spec_dict[RETRO.Hexanes_plus_higher_alkanes] = 1.0
            spec_dict[RETRO.Other_VOC] = 1.0
        elif spec == cls.HCHO:
            spec_dict[RETRO.Methanal] = 1.0
        elif spec == cls.ISOP:
            spec_dict[RETRO.Isoprene] = 1.0
        elif spec == cls.KET:
            spec_dict[RETRO.Ketones] = 1.0
        elif spec == cls.OL2:
            spec_dict[RETRO.Ethene] = 1.0
        elif spec == cls.OLI:
            spec_dict[RETRO.Propene] = 1.0
        elif spec == cls.OLT:
            spec_dict[RETRO.Ethyne] = 1.0
            spec_dict[RETRO.Other_alkenes_and_alkynes] = 1.0
        elif spec == cls.TERP:
            spec_dict[RETRO.Terpenes] = 1.0
        elif spec == cls.TOL:
            spec_dict[RETRO.Toluene] = 1.0
            spec_dict[RETRO.Benzene] = 1.0
        elif spec == cls.XYL:
            spec_dict[RETRO.Xylene] = 1.0
            spec_dict[RETRO.Trimethylbenzenes] = 1.0
            spec_dict[RETRO.Other_aromatics] = 1.0
        elif spec == cls.ORA2:
            spec_dict[RETRO.Acids] = 1.0
            spec_dict[RETRO.Alcohols] = 1.0

        return spec_dict