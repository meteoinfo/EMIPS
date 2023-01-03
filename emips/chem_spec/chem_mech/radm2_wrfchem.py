from ._mechanism import ChemicalMechanism
from ..species import Species, SpeciesEnum
from .retro import RETRO


class RADM2_wrfchem(ChemicalMechanism):
    # NMVOC species (17)
    ALD = Species('ALD', molar_mass=44)  # Acetaldehyde and higher aldehydes
    CSL = Species('CSL', molar_mass=108)  # Counter species for cresol reaction
    ETH = Species('ETH', molar_mass=30)  # Ethane
    HC3 = Species('HC3', molar_mass=44)  # Alkanes w/ 2.7x10-13 > kOH < 3.4x10-12
    HC5 = Species('HC5', molar_mass=72)  # Alkanes w/ 3.4x10-12 > kOH < 6.8x10-12
    HC8 = Species('HC8', molar_mass=114)  # Alkanes w/ kOH > 6.8x10-12
    HCHO = Species('HCHO', molar_mass=30)  # Formaldehyde
    ISO = Species('ISO', molar_mass=68)  # Isoprene
    KET = Species('KET', molar_mass=72)  # Ketones
    OL2 = Species('OL2', molar_mass=28)  # Ethene
    OLI = Species('OLI', molar_mass=56)  # Internal olefins
    OLT = Species('OLT', molar_mass=42)  # Terminal olefins
    ORA1 = Species('ORA1', molar_mass=46)  # Acetic and higher acids
    ORA2 = Species('ORA2', molar_mass=60)  # Acetic and higher acids
    TOL = Species('TOL', molar_mass=92)  # Toluene and less reactive aromatics
    XYL = Species('XYL', molar_mass=106)  # Xylene and more reactive aromatics
    CH3CL = Species('CH3CL', molar_mass=50.5)  # CH3CL
    CH4 = SpeciesEnum.CH4  # Methane

    # None-VOC species
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
        RADM2_wrfchem chemical mechanism
        """
        super(RADM2_wrfchem, self).__init__()

    @property
    def name(self):
        """
        Get chemical mechanism name
        :return: The name
        """
        return 'RADM2_wrfchem'

    def nmvoc_species(self):
        """
        Get NMVOC (None-Methane VOC) species
        :return: (*list of species*) NMVOC species
        """
        sp_nmvoc = [self.ALD, self.CSL, self.ETH, self.HC3, self.HC5, self.HC8,
                    self.HCHO, self.ISO, self.KET, self.OL2, self.OLI, self.OLT,
                    self.ORA1, self.ORA2, self.TOL, self.XYL, self.CH3CL]

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
                       self.PSO4, self.PMC])
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
        if spec == self.ALD:
            spec_dict[RETRO.Other_alkanals] = 1.0
        elif spec == self.CSL:
            spec_dict[RETRO.Other_VOC] = 1.0
        elif spec == self.ETH:
            spec_dict[RETRO.Ethane] = 1.0
        elif spec == self.HC3:
            spec_dict[RETRO.Propane] = 1.0
            spec_dict[RETRO.Butanes] = 1.0
            spec_dict[RETRO.Ethyne] = 0.4
            spec_dict[RETRO.Alcohols] = 0.95
            spec_dict[RETRO.Esters] = 0.69
        elif spec == self.HC5:
            spec_dict[RETRO.Alcohols] = 0.05
            spec_dict[RETRO.Hexanes_plus_higher_alkanes] = 0.43
            spec_dict[RETRO.Pentanes] = 1.0
            spec_dict[RETRO.Esters] = 0.31
        elif spec == self.HC8:
            spec_dict[RETRO.Hexanes_plus_higher_alkanes] = 0.57
            spec_dict[RETRO.Other_aromatics] = 1.0
            spec_dict[RETRO.Ethers] = 1.0
        elif spec == self.HCHO:
            spec_dict[RETRO.Methanal] = 1.0
        elif spec == self.ISO:
            spec_dict[RETRO.Isoprene] = 1.0
        elif spec == self.KET:
            spec_dict[RETRO.Ketones] = 1.0
        elif spec == self.OL2:
            spec_dict[RETRO.Ethene] = 1.0
        elif spec == self.OLI:
            spec_dict[RETRO.Other_alkenes_and_alkynes] = 1.0
            spec_dict[RETRO.Terpenes] = 1.0
        elif spec == self.OLT:
            spec_dict[RETRO.Propene] = 1.0
        elif spec == self.TOL:
            spec_dict[RETRO.Toluene] = 1.0
            spec_dict[RETRO.Benzene] = 0.293
        elif spec == self.XYL:
            spec_dict[RETRO.Xylene] = 1.0
            spec_dict[RETRO.Trimethylbenzenes] = 1.0
            spec_dict[RETRO.Other_aromatics] = 1.0
        elif spec == self.ORA1:
            spec_dict[RETRO.Acids] = 0.44
        elif spec == self.ORA2:
            spec_dict[RETRO.Acids] = 0.56
        elif spec == self.CH3CL:
            spec_dict[RETRO.Chlorinated_hydrocarbons] = 1.0

        return spec_dict
