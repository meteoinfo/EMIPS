from ..species import Species


class RETRO(object):
    ########################
    # Anthropogenic emission
    ########################
    Alcohols = Species('Alcohols')
    Ethane = Species('Ethane')
    Propane = Species('Propane')
    Butanes = Species('Butanes')
    Pentanes = Species('Pentanes')
    Hexanes_plus_higher_alkanes = Species('Hexanes_plus_higher_alkanes')
    Ethene = Species('Ethene')
    Propene = Species('Propene')
    Ethyne = Species('Ethyne')
    Isoprene = Species('Isoprene')
    Terpenes = Species('Terpenes')
    Other_alkenes_and_alkynes = Species('Other_alkenes_and_alkynes')
    Benzene = Species('Benzene')
    Toluene = Species('Toluene')
    Xylene = Species('Xylene')
    Trimethylbenzenes = Species('Trimethylbenzenes')
    Other_aromatics = Species('Other_aromatics')
    Esters = Species('Esters')
    Ethers = Species('Ethers')
    Chlorinated_hydrocarbons = Species('Chlorinated_hydrocarbons')
    Methanal = Species('Methanal')
    Other_alkanals = Species('Other_alkanals')
    Ketones = Species('Ketones')
    Acids = Species('Acids')
    Other_VOC = Species('Other_VOC')
    #################
    # Biomass burning#
    #################
    C2H2 = Species('C2H2')
    C2H4 = Species('C2H4')
    C2H4O = Species('C2H4O')
    C2H5OH = Species('C2H5OH')
    C2H6 = Species('C2H6')
    C2H6S = Species('C2H6S')
    C3H6 = Species('C3H6')
    C3H6O = Species('C3H6O')
    C3H8 = Species('C3H8')
    C5H8 = Species('C5H8')
    C6H6 = Species('C6H6')
    C7H8 = Species('C7H8')
    C8H10 = Species('C8H10')
    C10H16 = Species('C10H16')
    CH2O = Species('CH2O')
    CH3COCHO = Species('CH3COCHO')
    CH3COOH = Species('CH3COOH')
    CH3OH = Species('CH3OH')
    HCOOH = Species('HCOOH')
    Higher_Alkanes = Species('Higher_Alkanes')
    Higher_Alkenes = Species('Higher_Alkenes')
    MEK = Species('MEK')
    NMHC = Species('NMHC')
    Toluene_lump = Species('Toluene_lump')

    def __init__(self):
        pass

    @classmethod
    def new_species(cls, spec):
        """
        Get a new Species object.
        :param spec: (*Species or str*) The species or species name.
        :return: (*Species*) New Species object.
        """
        if isinstance(spec, Species):
            return Species(spec.name)
        else:
            return Species(spec)
