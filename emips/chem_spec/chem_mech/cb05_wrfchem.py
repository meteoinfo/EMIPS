from ._mechanism import ChemicalMechanism
from ..species import Species, SpeciesEnum
from .retro import RETRO


class CB05_wrfchem(ChemicalMechanism):
    # NMVOC species (15)
    ETOH = Species('ETOH', molar_mass=46)  # Ethanol
    ETHA = Species('ETHA', molar_mass=30)  # Ethane
    PAR = Species('PAR', molar_mass=16)  # Paraffin carbon bond
    NR = Species('NR', molar_mass=16)  # non-reactive class
    ETH = Species('ETH', molar_mass=28)  # Ethene
    OLE = Species('OLE', molar_mass=27)  # Oleftnic carbon bond
    ALDX = Species('ALDX', molar_mass=44)  # Propionaldehyde and higher aldehydes
    ISOP = Species('ISOP', molar_mass=68)  # Isoprene
    TERP = Species('TERP', molar_mass=136)  # Terpene
    TOL = Species('TOL', molar_mass=92)  # Toluene
    XYL = Species('XYL', molar_mass=106)  # Xylene
    FORM = Species('FORM', molar_mass=30)  # Formaldehyde
    ALD2 = Species('ALD2', molar_mass=44)  # Acetaldehyde
    MEOH = Species('MEOH', molar_mass=32)  # Methanol
    IOLE = Species('IOLE', molar_mass=48)  # Internal olefin carbon bond
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
        CB05_wrfchem chemical mechanism
        """
        super(CB05_wrfchem, self).__init__()

        self.name = 'CB05_wrfchem'

    def nmvoc_species(self):
        """
        Get NMVOC (None-Methane VOC) species
        :return: (*list of species*) NMVOC species
        """
        sp_nmvoc = [self.ETOH, self.ETHA, self.PAR, self.NR, self.ETH, self.OLE,
                    self.ALDX, self.ISOP, self.TERP, self.TOL, self.XYL, self.FORM,
                    self.ALD2, self.MEOH, self.IOLE]

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
        if spec == self.ETOH:
            spec_dict[RETRO.Alcohols] = 0.5
        elif spec == self.MEOH:
            spec_dict[RETRO.Alcohols] = 0.5
        elif spec == self.ETHA:
            spec_dict[RETRO.Ethane] = 1.0
        elif spec == self.PAR:
            spec_dict[RETRO.Propane] = 1.5
            spec_dict[RETRO.Butanes] = 4.0
            spec_dict[RETRO.Pentanes] = 5.0
            spec_dict[RETRO.Hexanes_plus_higher_alkanes] = 6.0
            spec_dict[RETRO.Propene] = 1.0
            spec_dict[RETRO.Ethyne] = 1.0
            spec_dict[RETRO.Other_alkenes_and_alkynes] = 3.5
            spec_dict[RETRO.Benzene] = 1.0
            spec_dict[RETRO.Trimethylbenzenes] = 1.0
            spec_dict[RETRO.Other_aromatics] = 2.25
            spec_dict[RETRO.Esters] = 1.0
            spec_dict[RETRO.Ethers] = 2.0
            spec_dict[RETRO.Ketones] = 3.0
            spec_dict[RETRO.Acids] = 0.5
            spec_dict[RETRO.Other_VOC] = 1.0
        elif spec == self.NR:
            spec_dict[RETRO.Propane] = 1.5
            spec_dict[RETRO.Ethyne] = 1.0
            spec_dict[RETRO.Benzene] = 5.0
            spec_dict[RETRO.Esters] = 1.0
            spec_dict[RETRO.Ethers] = 1.0
            spec_dict[RETRO.Chlorinated_hydrocarbons] = 1.0
            spec_dict[RETRO.Acids] = 1.0
            spec_dict[RETRO.Other_VOC] = 1.0
        elif spec == self.ETH:
            spec_dict[RETRO.Ethene] = 1.0
        elif spec == self.OLE:
            spec_dict[RETRO.Propene] = 1.0
            spec_dict[RETRO.Other_alkenes_and_alkynes] = 0.5
        elif spec == self.ALDX:
            spec_dict[RETRO.Other_alkenes_and_alkynes] = 0.75
        elif spec == self.ISOP:
            spec_dict[RETRO.Isoprene] = 1.0
        elif spec == self.TERP:
            spec_dict[RETRO.Terpenes] = 1.0
        elif spec == self.TOL:
            spec_dict[RETRO.Toluene] = 1.0
            spec_dict[RETRO.Other_aromatics] = 0.25
        elif spec == self.XYL:
            spec_dict[RETRO.Xylene] = 1.0
            spec_dict[RETRO.Trimethylbenzenes] = 1.0
            spec_dict[RETRO.Other_aromatics] = 0.75
        elif spec == self.FORM:
            spec_dict[RETRO.Methanal] = 1.0
        elif spec == self.ALD2:
            spec_dict[RETRO.Other_alkanals] = 1.0
        elif spec == self.IOLE:
            spec_dict[RETRO.Other_alkenes_and_alkynes] = 0.75

        return spec_dict
