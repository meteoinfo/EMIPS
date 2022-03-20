from ._mechanism import ChemicalMechanism
from ..species import Species, SpeciesEnum
from .retro import RETRO

class MOZART_wrfchem(ChemicalMechanism):

    #NMVOC species (22)
    BIGALK = Species('BIGALK', molar_mass=72)      #Lumped alkanes C > 3
    BIGENE = Species('BIGENE', molar_mass=56)      #Lumped alkenes C > 3
    C2H4 = Species('C2H4', molar_mass=28)          #Ethene
    C2H5OH = Species('C2H5OH', molar_mass=46)      #Ethanol
    C2H6 = Species('C2H6', molar_mass=30)          #Ethane
    C3H6 = Species('C3H6', molar_mass=42)          #Propene
    C3H8 = Species('C3H8', molar_mass=44)          #Propane
    CH2O = Species('CH2O', molar_mass=30)          #Methanal
    CH3CHO = Species('CH3CHO', molar_mass=44)      #Acetaldehyde
    CH3COCH3 = Species('CH3COCH3', molar_mass=58)  #Acetone
    CH3OH = Species('CH3OH', molar_mass=32)        #Methanol
    MEK = Species('MEK', molar_mass=72)    		   #Methyl ethyl ketone
    TOLUENE = Species('TOLUENE', molar_mass=92)    #Lumped aromatics
    BENZENE = Species('BENZENE', molar_mass=78)    #Benzene
    XYLENE = Species('XYLENE', molar_mass=106)     #Xylene
    ISOP = Species('ISOP', molar_mass=68)    	   #Isoprene
    APIN = Species('APIN', molar_mass=136)    	   #Terpenes
    C2H2 = Species('C2H2', molar_mass=26)    	   #Ethyne
    MGLY = Species('MGLY', molar_mass=72)    	   #Methylglyoxal
    MVK = Species('MVK', molar_mass=70)    		   #Methyl Vinyl Ketone and unsaturated ketones
    GCOOH = Species('GCOOH', molar_mass=46)        #HCOOH
    CRESOL = Species('CRESOL', molar_mass=108)     #Cresol
    CH4 = SpeciesEnum.CH4                          #Methane

    #None-VOC species (12)
    CO = SpeciesEnum.CO
    NO = SpeciesEnum.NO
    NO2 = SpeciesEnum.NO2
    NH3 = SpeciesEnum.NH3
    SO2 = SpeciesEnum.SO2
    SULF = SpeciesEnum.SULF
    PEC = SpeciesEnum.PEC
    PMFINE = SpeciesEnum.PMFINE
    PNO3 = SpeciesEnum.PNO3
    POA = SpeciesEnum.POA
    PSO4 = SpeciesEnum.PSO4
    PMC = SpeciesEnum.PMC
    
    def __init__(self):
        """
        MOZART_wrfchem chemical mechanism
        """
        super(MOZART_wrfchem, self).__init__()

    @property
    def name(self):
        """
        Get chemical mechanism name
        :return: The name
        """
        return 'MOZART_wrfchem'

    def nmvoc_species(self):
        """
        Get NMVOC (None-Methane VOC) species
        :return: (*list of species*) NMVOC species
        """
        sp_nmvoc = [self.BIGALK, self.BIGENE, self.C2H4, self.C2H5OH, self.C2H6, self.C3H6,
                   self.C3H8, self.CH2O, self.CH3CHO, self.CH3COCH3, self.CH3OH, self.MEK,
                   self.TOLUENE, self.BENZENE, self.XYLENE, self.ISOP, self.APIN, self.C2H2,
				   self.MGLY, self.MVK, self.GCOOH, self.CRESOL]

        return sp_nmvoc

    def voc_species(self):
        """
        Get VOC species
        :return: (*list of species*) VOC species
        """
        sp_voc = self.nmvoc_species()
        sp_voc.insert(1, self.CH4)

        return sp_voc

    def all_species(self):
        """
        Get all species
        :return: (*list of species*) All species
        """
        sp_all = [self.CO, self.NO, self.NO2]
        sp_all.extend(self.voc_species())
        sp_all.extend([self.NH3, self.SO2, self.SULF, self.PEC, self.PMFINE, self.PNO3, self.POA, \
                      self.PSO4,self.PMC])
        return sp_all

    def species(self, name):
        """
        Get species from name
        :param name: (*str*) Species name
        :return: The species
        """
        species = self.all_species()
        for spec in species:
            if spec.name == name:
                return spec
        return Species(name)

    def lump_RETRO(self, spec):
        """
        Lump a species from RETRO species.
        :param spec: (*Species*) The species in this chemical mechanism.
        :return: (*dict of Species and ratios*) The species in pollutant profile to be lumped as
            the chemical mechanism species.
        """
        spec_dict = {}
        if spec == self.BIGALK:
            spec_dict[RETRO.Butanes] = 1.0
            spec_dict[RETRO.Pentanes] = 1.0
            spec_dict[RETRO.Hexanes_plus_higher_alkanes] = 1.0
        elif spec == self.BIGENE:
			spec_dict[RETRO.Other_alkenes_and_alkynes] = 1.0
        elif spec == self.C2H4:
        	spec_dict[RETRO.Ethene] = 1.0
        elif spec == self.C2H5OH:
        	spec_dict[RETRO.Alcohols] = 0.5
        elif spec == self.C2H6:
        	spec_dict[RETRO.Ethane] = 1.0
        elif spec == self.C3H6:
        	spec_dict[RETRO.Propene] = 1.0
        elif spec == self.C3H8:
        	spec_dict[RETRO.Propane] = 1.0
        elif spec == self.CH2O:
        	spec_dict[RETRO.Methanal] = 1.0
        elif spec == self.CH3CHO:
        	spec_dict[RETRO.Other_alkanals] = 1.0
        elif spec == self.CH3COCH3:
        	spec_dict[RETRO.Ketones] = 0.5
        elif spec == self.CH3OH:
        	spec_dict[RETRO.Alcohols] = 0.5
        elif spec == self.MEK:
        	spec_dict[RETRO.Ketones] = 0.5
        elif spec == self.TOLUENE:
        	spec_dict[RETRO.Toluene] = 1.0
        	spec_dict[RETRO.Other_aromatics] = 0.25
        elif spec == self.BENZENE:
        	spec_dict[RETRO.Benzene] = 1.0
        elif spec == self.XYLENE:
        	spec_dict[RETRO.Xylene] = 1.0
        	spec_dict[RETRO.Trimethylbenzenes] = 1.0
        	spec_dict[RETRO.Other_aromatics] = 0.75
        elif spec == self.ISOP:
        	spec_dict[RETRO.Isoprene] = 1.0
        elif spec == self.APIN:
        	spec_dict[RETRO.Terpenes] = 1.0
        elif spec == self.C2H2:
        	spec_dict[RETRO.Ethyne] = 1.0
        elif spec == self.MGLY:
        	spec_dict[RETRO.Other_VOC] = 1.0
        #elif spec == self.MVK:
        elif spec == self.GCOOH:
        	spec_dict[RETRO.Acids] = 1.0
        elif spec == self.CRESOL:
            spec_dict[RETRO.Esters] = 1.0
            spec_dict[RETRO.Ethers] = 1.0

        return spec_dict
