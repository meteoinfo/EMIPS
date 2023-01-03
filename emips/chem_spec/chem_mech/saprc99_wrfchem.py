from ._mechanism import ChemicalMechanism
from ..species import Species, SpeciesEnum
from .retro import RETRO


class SAPRC99_wrfchem(ChemicalMechanism):
    # NMVOC species (23)
    C2H6 = Species('C2H6', molar_mass=30)  # ethane
    C3H8 = Species('C3H8', molar_mass=44)  # propane
    C2H2 = Species('C2H2', molar_mass=26)  # acetylene
    C3H6 = Species('C3H6', molar_mass=42)  # propene
    ALK3 = Species('ALK3', molar_mass=58.61)  # Alkanes kOH between 2.5 x10e3and 5 x 10e3ppm-1 min-1.
    ALK4 = Species('ALK4', molar_mass=77.6)  # Alkanes kOH between 5 x 10e3and 1 x 10e4ppm-1 min-1.
    ALK5 = Species('ALK5', molar_mass=118.89)  # Alkanes kOH greater than 1 x10e4ppm-1 min-1
    ARO1 = Species('ARO1', molar_mass=95.16)  # Aromatics with kOH < 2x10e4ppm-1 min-1
    ARO2 = Species('ARO2', molar_mass=118.72)  # Aromatics with kOH > 2x10e4ppm-1 min-1
    OLE1 = Species('OLE1', molar_mass=72.34)  # Alkenes (other than ethene) with kOH < 7x10e4ppm-1 min-1
    OLE2 = Species('OLE2', molar_mass=75.78)  # Alkenes with kOH > 7x10e4ppm-1 min-1
    TERP = Species('TERP', molar_mass=136.24)  # Terpenes
    # TRP1 = Species('TRP1', molar_mass=136.2)         #Terpenes
    ETHENE = Species('ETHENE', molar_mass=28.05)  # Ethene
    ISOPRENE = Species('ISOPRENE', molar_mass=68.12)  # Isoprene
    HCHO = Species('HCHO', molar_mass=30.03)  # Formaldehyde
    CCHO = Species('CCHO', molar_mass=44.05)  # Acetaldehyde
    RCHO = Species('RCHO', molar_mass=58.08)  # Higher Aldehydes
    ACET = Species('ACET', molar_mass=58.08)  # Acetone
    MEK = Species('MEK', molar_mass=72.11)  # Ketones (<0.73 react)
    MEOH = Species('MEOH', molar_mass=32.04)  # Methanol
    PROD2 = Species('PROD2', molar_mass=116.16)  # Ketones (>0.73 react)
    HCOOH = Species('HCOOH', molar_mass=46.03)  # Formic Acid
    CCO_OH = Species('CCO_OH', molar_mass=60.05)  # Acetic Acid
    CH4 = SpeciesEnum.CH4  # Methane

    # None-VOC species (12)
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
        SARPC99_wrfchem chemical mechanism
        """
        super(SAPRC99_wrfchem, self).__init__()

    @property
    def name(self):
        """
        Get chemical mechanism name
        :return: The name
        """
        return 'SAPRC99_wrfchem'

    def nmvoc_species(self):
        """
        Get NMVOC (None-Methane VOC) species
        :return: (*list of species*) NMVOC species
        """
        sp_nmvoc = [self.C2H6, self.C3H8, self.C2H2, self.C3H6, self.ALK3, self.ALK4,
                    self.ALK5, self.ARO1, self.ARO2, self.OLE1, self.OLE2, self.TERP,
                    self.ETHENE, self.ISOPRENE, self.HCHO, self.CCHO, self.RCHO, self.ACET,
                    self.MEK, self.MEOH, self.PROD2, self.HCOOH, self.CCO_OH]

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
        if spec == self.C2H6:
            spec_dict[RETRO.Ethane] = 1.0
        elif spec == self.C3H8:
            spec_dict[RETRO.Propane] = 1.0
        elif spec == self.C2H2:
            spec_dict[RETRO.Ethyne] = 1.0
        elif spec == self.C3H6:
            spec_dict[RETRO.Propene] = 1.0
        elif spec == self.ALK3:
            spec_dict[RETRO.Alcohols] = 0.5
            spec_dict[RETRO.Butanes] = 1.0
            spec_dict[RETRO.Chlorinated_hydrocarbons] = 0.5
            spec_dict[RETRO.Other_VOC] = 0.3
            spec_dict[RETRO.Esters] = 0.5
        elif spec == self.ALK4:
            spec_dict[RETRO.Pentanes] = 1.0
            spec_dict[RETRO.Hexanes_plus_higher_alkanes] = 0.5
            spec_dict[RETRO.Other_VOC] = 0.3
            spec_dict[RETRO.Esters] = 0.5
            spec_dict[RETRO.Chlorinated_hydrocarbons] = 0.5
        elif spec == self.ALK5:
            spec_dict[RETRO.Hexanes_plus_higher_alkanes] = 0.5
            spec_dict[RETRO.Ethers] = 1.0
            spec_dict[RETRO.Other_VOC] = 0.3
        elif spec == self.ARO1:
            spec_dict[RETRO.Benzene] = 1.0
            spec_dict[RETRO.Toluene] = 1.0
        elif spec == self.ARO2:
            spec_dict[RETRO.Xylene] = 1.0
            spec_dict[RETRO.Trimethylbenzenes] = 1.0
            spec_dict[RETRO.Other_aromatics] = 1.0
        elif spec == self.OLE1:
            spec_dict[RETRO.Other_alkenes_and_alkynes] = 0.5
        elif spec == self.OLE2:
            spec_dict[RETRO.Other_alkenes_and_alkynes] = 0.5
        elif spec == self.TERP:
            spec_dict[RETRO.Terpenes] = 1.0
        elif spec == self.ETHENE:
            spec_dict[RETRO.Ethene] = 1.0
        elif spec == self.ISOPRENE:
            spec_dict[RETRO.Isoprene] = 1.0
        elif spec == self.HCHO:
            spec_dict[RETRO.Methanal] = 1.0
        elif spec == self.CCHO:
            spec_dict[RETRO.Other_alkanals] = 0.5
        elif spec == self.RCHO:
            spec_dict[RETRO.Other_alkanals] = 0.5
        elif spec == self.ACET:
            spec_dict[RETRO.Ketones] = 0.5
        elif spec == self.MEK:
            spec_dict[RETRO.Ketones] = 0.3
        elif spec == self.MEOH:
            spec_dict[RETRO.Alcohols] = 0.5
        elif spec == self.PROD2:
            spec_dict[RETRO.Ketones] = 0.2
        elif spec == self.HCOOH:
            spec_dict[RETRO.Acids] = 0.5
        elif spec == self.CCO_OH:
            spec_dict[RETRO.Acids] = 0.5

        return spec_dict
