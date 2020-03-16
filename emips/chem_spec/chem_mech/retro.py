from ..species import Species

class RETRO(object):

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

    def __init__(self):
        pass

    def new_species(self, spec):
        """
        Get a new Species object.
        :param spec: (*Species or str*) The species or species name.
        :return: (*Species*) New Species object.
        """
        if isinstance(spec, Species):
            return Species(spec.name)
        else:
            return Species(spec)