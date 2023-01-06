from ._mechanism import ChemicalMechanism
from ..species import Species, SpeciesEnum
from .retro import RETRO


class RADM2(ChemicalMechanism):
    # NMVOC species (19)
    ALD = Species('ALD', molar_mass=44)  # Acetaldehyde and higher aldehydes
    CSL = Species('CSL', molar_mass=108)  # Counter species for cresol reaction
    ETH = Species('ETH', molar_mass=30)  # Ethane
    HC3 = Species('HC3', molar_mass=44)  # Alkanes w/ 2.7x10-13 > kOH < 3.4x10-12
    HC5 = Species('HC5', molar_mass=72)  # Alkanes w/ 3.4x10-12 > kOH < 6.8x10-12
    HC8 = Species('HC8', molar_mass=114)  # Alkanes w/ kOH > 6.8x10-12
    HCHO = Species('HCHO', molar_mass=30)  # Formaldehyde
    ISOP = Species('ISOP', molar_mass=68)  # Isoprene
    KET = Species('KET', molar_mass=72)  # Ketones
    NR = Species('NR', molar_mass=100)  # non-reactive class (molar mass: 45-150)
    OL2 = Species('OL2', molar_mass=28)  # Ethene
    OLE = Species('OLE', molar_mass=27)  # double-bonded carbon atoms
    OLI = Species('OLI', molar_mass=56)  # Internal olefins
    OLT = Species('OLT', molar_mass=42)  # Terminal olefins
    ORA2 = Species('ORA2', molar_mass=60)  # Acetic and higher acids
    PAR = Species('PAR', molar_mass=14)  # single-bonds carbon atoms
    TERP = Species('TERP', molar_mass=136)  # Monoterpenes
    TOL = Species('TOL', molar_mass=92)  # Toluene and less reactive aromatics
    XYL = Species('XYL', molar_mass=106)  # Xylene and more reactive aromatics
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
        RADM2 chemical mechanism
        """
        super(RADM2, self).__init__()

        self.name = 'RADM2'

    def nmvoc_species(self):
        """
        Get NMVOC (None-Methane VOC) species
        :return: (*list of species*) NMVOC species
        """
        sp_nmvoc = [self.ALD, self.CSL, self.ETH, self.HC3, self.HC5, self.HC8,
                    self.HCHO, self.ISOP, self.KET, self.NR, self.OL2, self.OLE,
                    self.OLI, self.OLT, self.ORA2, self.PAR, self.TERP, self.TOL,
                    self.XYL]

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
        sp_all.extend([self.NH3, self.SO2, self.SULF, self.PEC, self.PMFINE, self.PNO3, self.POA,
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

    def lump_RETRO(self, spec, biomass=False):
        """
        Lump a species from RETRO species.
        :param spec: (*Species*) The species in this chemical mechanism.
        :return: (*dict of Species and ratios*) The species in pollutant profile to be lumped as
            the chemical mechanism species.
        """
        spec_dict = {}
        if biomass is False:
            if spec == self.ALD:
                spec_dict[RETRO.Other_alkanals] = 1.0
            elif spec == self.CSL:
                spec_dict[RETRO.Esters] = 1.0
                spec_dict[RETRO.Ethers] = 1.0
            elif spec == self.ETH:
                spec_dict[RETRO.Ethane] = 1.0
            elif spec == self.HC3:
                spec_dict[RETRO.Propane] = 1.0
            elif spec == self.HC5:
                spec_dict[RETRO.Butanes] = 1.0
                spec_dict[RETRO.Pentanes] = 1.0
            elif spec == self.HC8:
                spec_dict[RETRO.Hexanes_plus_higher_alkanes] = 1.0
                spec_dict[RETRO.Other_VOC] = 1.0
            elif spec == self.HCHO:
                spec_dict[RETRO.Methanal] = 1.0
            elif spec == self.ISOP:
                spec_dict[RETRO.Isoprene] = 1.0
            elif spec == self.KET:
                spec_dict[RETRO.Ketones] = 1.0
            elif spec == self.OL2:
                spec_dict[RETRO.Ethene] = 1.0
            elif spec == self.OLI:
                spec_dict[RETRO.Propene] = 1.0
            elif spec == self.OLT:
                spec_dict[RETRO.Ethyne] = 1.0
                spec_dict[RETRO.Other_alkenes_and_alkynes] = 1.0
            elif spec == self.TERP:
                spec_dict[RETRO.Terpenes] = 1.0
            elif spec == self.TOL:
                spec_dict[RETRO.Toluene] = 1.0
                spec_dict[RETRO.Benzene] = 1.0
            elif spec == self.XYL:
                spec_dict[RETRO.Xylene] = 1.0
                spec_dict[RETRO.Trimethylbenzenes] = 1.0
                spec_dict[RETRO.Other_aromatics] = 1.0
            elif spec == self.ORA2:
                spec_dict[RETRO.Acids] = 1.0
                spec_dict[RETRO.Alcohols] = 1.0
        else:
            if spec == self.ALD:
                spec_dict[RETRO.C2H4O] = 1.0
            elif spec == self.CSL:
                spec_dict[RETRO.C2H6S] = 1.0
            elif spec == self.ETH:
                spec_dict[RETRO.C2H6] = 1.0
            elif spec == self.HC3:
                spec_dict[RETRO.C2H2] = 1.0
                spec_dict[RETRO.C2H5OH] = 1.0
                spec_dict[RETRO.C3H8] = 1.0
                spec_dict[RETRO.CH3OH] = 1.0
            elif spec == self.HC8:
                spec_dict[RETRO.Higher_Alkanes] = 1.0
            elif spec == self.HCHO:
                spec_dict[RETRO.CH2O] = 1.0
            elif spec == self.ISOP:
                spec_dict[RETRO.C5H8] = 1.0
            elif spec == self.KET:
                spec_dict[RETRO.CH3COCHO] = 1.0
                # spec_dict[RETRO.C3H6O] = 1.0
                # spec_dict[RETRO.MEK] = 1.0
            elif spec == self.OL2:
                spec_dict[RETRO.C2H4] = 1.0
            elif spec == self.OLI:
                spec_dict[RETRO.C3H6] = 1.0
            elif spec == self.OLT:
                spec_dict[RETRO.Higher_Alkenes] = 1.0
            elif spec == self.TERP:
                spec_dict[RETRO.C10H16] = 1.0
            elif spec == self.TOL:
                spec_dict[RETRO.C6H6] = 1.0
                spec_dict[RETRO.C7H8] = 1.0
                # spec_dict[RETRO.Toluene_lump] = 1.0
            elif spec == self.XYL:
                spec_dict[RETRO.C8H10] = 1.0
            elif spec == self.ORA2:
                spec_dict[RETRO.CH3COOH] = 1.0
                spec_dict[RETRO.HCOOH] = 1.0

        return spec_dict
