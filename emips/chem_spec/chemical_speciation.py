from .species_reference import SpeciesReferenceItem, SpeciesReference
from .species_profile import SpeciesProfile
from .pollutant_profile import PollutantProfile
from .pollutant import Pollutant
import mipylib.numeric as np

__all__ = ['get_pollutant_profile', 'read_file', 'speciation', 'get_model_species_wrf']

def get_pollutant_profile(poll_profiles, pollutant):
    """
    Get pollutant profile from pollutant profile list by pollutant name.
    :param poll_profiles: (*list*) The pollutant profile list.
    :param pollutant: (*string or Pollutant*) The pollutant name.
    :return: (*PollutantProfile*) Pollutant profile.
    """
    if isinstance(pollutant, basestring):
        pollutant = Pollutant(pollutant)
    for profile in poll_profiles:
        if profile.pollutant.name.upper() == pollutant.name.upper():
            return profile
    return None

def read_file(ref_fn, profile_fn, scc):
    """
    Read pollutant profiles from reference and profile files
    :param ref_fn: The reference file
    :param profile_fn: The profile file
    :param scc: Source classification code
    :return: Pollutant profiles
    """
    #Read reference file
    spec_ref = SpeciesReference()
    n = len(scc)
    ref_f = open(ref_fn)
    for line in ref_f:
        line = line.strip()
        if len(line) < n:
            continue
        data = line.split()
        if data[0] == scc:
            ref_item = SpeciesReferenceItem.read_string(line)
            spec_ref.append(ref_item)
    ref_f.flush()
    ref_f.close()

    #Read profile file
    pollutant_profiles = []
    profile_f = open(profile_fn)
    poll_names = []
    for line in profile_f:
        line = line.strip()
        if not line:
            continue
        if line[0] == "#":
            continue
        data = line.split()
        profile_id = data[0]
        poll_name = data[1]
        if spec_ref.contains(profile_id, poll_name):
            ppi = SpeciesProfile.read_string(line)
            if poll_name in poll_names:
                poll_profile = get_pollutant_profile(pollutant_profiles, poll_name)
                poll_profile.append(ppi)
            else:
                poll_profile = PollutantProfile(poll_name)
                poll_profile.append(ppi)
                pollutant_profiles.append(poll_profile)
                poll_names.append(poll_name)
    profile_f.flush()
    profile_f.close()
    return pollutant_profiles

def speciation(data, pollutant_profile):
    """
    Chemical speciation.
    :param data: (*array*) Pollutant data array.
    :param pollutant_profile: (*PollutantProfile*) The pollutant profile.
    :return: (*array*) Species data array.
    """
    shape = list(data.shape)
    n = len(pollutant_profile)
    shape.insert(0, n)
    s_data = np.zeros(shape)
    for i in range(n):
        s_data[i] = data * pollutant_profile[i].mass_fraction
    return s_data

def get_model_species_wrf(mechanism_name):
    """
    Get species in wrf-chem in different chemical mechanism.
    (E_PM10: saprc99, cb05 E_PM_10: radm2, mozart)
    :param mechanism_name: (*string*) The name of chemical mechanism.
    :return: (*list*) All species(out_species) and aerosols(out_species_aer) under chemical mechanisms.
    """
    mechanism_name = mechanism_name.lower()
    if mechanism_name == 'cb05':
        ##########################################
        #------CB05, emiss_opt=15, (52, 15)------#
        ##########################################
        out_species = ['E_ACET', 'E_PAR', 'E_ALK3', 'E_ALK4', 'E_ALK5', 'E_TOL', 'E_XYL', 'E_BALD', 
                       'E_ALD2', 'E_CCOOH', 'E_CO', 'E_CRES', 'E_ETH', 'E_ETHA', 'E_GLY', 'E_FORM', 
                       'E_HCOOH', 'E_IPROD', 'E_ISOP', 'E_MACR', 'E_MEK', 'E_MEOH', 'E_MEO2', 'E_ETOH', 
                       'E_MGLY', 'E_NH3', 'E_HCL', 'E_NO', 'E_NO2', 'E_IOLE', 'E_OLE', 'E_PHEN', 
                       'E_PROD2', 'E_ALDX', 'E_SO2', 'E_PSULF', 'E_TERP', 'E_PM25I', 'E_PM25J', 'E_ECI', 
                       'E_ECJ', 'E_ORGI', 'E_ORGJ', 'E_SO4I', 'E_SO4J', 'E_NO3I', 'E_NO3J', 'E_SO4C', 
                       'E_NO3C', 'E_ORGC', 'E_ECC', 'E_PM10']
        out_species_aer = ['E_PM25I', 'E_PM25J', 'E_ECI', 'E_ECJ', 'E_ORGI', 'E_ORGJ', 'E_SO4I', 'E_SO4J', 
                           'E_NO3I', 'E_NO3J', 'E_SO4C', 'E_NO3C', 'E_ORGC', 'E_ECC', 'E_PM10']
    
    elif mechanism_name == 'radm2':
        ##########################################
        #------RADM2, emiss_opt=3, (42, 19)------#
        ##########################################
        out_species = ['E_ISO', 'E_SO2', 'E_NO', 'E_NO2', 'E_CO', 'E_CH4', 'E_ETH', 'E_HC3', 
                       'E_HC5', 'E_HC8', 'E_XYL', 'E_OL2', 'E_OLT', 'E_OLI', 'E_TOL', 'E_CSL', 
                       'E_HCHO', 'E_ALD', 'E_KET', 'E_ORA2', 'E_NH3', 'E_PM25I', 'E_PM25J', 'E_PM_10', 
                       'E_ECI', 'E_ECJ', 'E_ORGI', 'E_ORGJ', 'E_SO4I', 'E_SO4J', 'E_NO3I', 'E_NO3J', 
                       'E_NAAJ', 'E_NAAI', 'E_ORGI_A', 'E_ORGJ_A', 'E_ORGI_BB', 'E_ORGJ_BB', 'E_HCL', 'E_CLI', 
                       'E_CLJ', 'E_CH3CL']
        out_species_aer = ['E_PM25I', 'E_PM25J', 'E_PM_10', 'E_ECI', 'E_ECJ', 'E_ORGI', 'E_ORGJ', 'E_SO4I', 
                           'E_SO4J', 'E_NO3I', 'E_NO3J', 'E_NAAJ', 'E_NAAI', 'E_ORGI_A', 'E_ORGJ_A', 'E_ORGI_BB', 
                           'E_ORGJ_BB', 'E_CLI', 'E_CLJ']
    elif mechanism_name == 'saprc99':
        ###########################################
        #-----SAPRC99, emiss_opt=13, (55, 15)-----#
        ###########################################
        out_species = ['E_SO2', 'E_C2H6', 'E_C3H8', 'E_C2H2', 'E_ALK3', 'E_ALK4', 'E_ALK5', 'E_ETHENE', 
                       'E_C3H6', 'E_OLE1', 'E_OLE2', 'E_ARO1', 'E_ARO2', 'E_HCHO', 'E_CCHO', 'E_RCHO', 
                       'E_ACET', 'E_MEK', 'E_ISOPRENE', 'E_TERP', 'E_SESQ', 'E_CO', 'E_NO', 'E_NO2', 
                       'E_PHEN', 'E_CRES', 'E_MEOH', 'E_GLY', 'E_MGLY', 'E_BACL', 'E_ISOPROD', 'E_METHACRO', 
                       'E_MVK', 'E_PROD2', 'E_CH4', 'E_BALD', 'E_HCOOH', 'E_CCO_OH', 'E_RCO_OH', 'E_NH3', 
                       'E_PM25I', 'E_PM25J', 'E_ECI', 'E_ECJ', 'E_ORGI', 'E_ORGJ', 'E_SO4I', 'E_SO4J', 
                       'E_NO3I', 'E_NO3J', 'E_ORGI_A', 'E_ORGJ_A', 'E_ORGI_BB', 'E_ORGJ_BB', 'E_PM10']
        out_species_aer = ['E_PM25I', 'E_PM25J', 'E_ECI', 'E_ECJ', 'E_ORGI', 'E_ORGJ', 'E_SO4I', 'E_SO4J', 
                           'E_NO3I', 'E_NO3J', 'E_ORGI_A', 'E_ORGJ_A', 'E_ORGI_BB', 'E_ORGJ_BB', 'E_PM10']
                           
    elif mechanism_name == 'mozart':
        ##########################################
        #-----MOZART, emiss_opt=10, (53, 23)-----#
        ##########################################
        out_species = ['E_CO', 'E_NO', 'E_NO2', 'E_BIGALK', 'E_BIGENE', 'E_C2H4', 'E_C2H5OH', 'E_C2H6', 
                       'E_C3H6', 'E_C3H8', 'E_CH2O', 'E_CH3CHO', 'E_CH3COCH3', 'E_CH3OH', 'E_MEK', 'E_SO2', 
                       'E_TOLUENE', 'E_BENZENE', 'E_XYLENE', 'E_NH3', 'E_ISOP', 'E_APIN', 'E_PM25I', 'E_PM25J', 
                       'E_ECI', 'E_ECJ', 'E_ORGI', 'E_ORGJ', 'E_SO4I', 'E_SO4J', 'E_NO3I', 'E_NO3J', 
                       'E_NH4I', 'E_NH4J', 'E_NAI', 'E_NAJ', 'E_CLI', 'E_CLJ', 'E_CO_A', 'E_ORGI_A', 
                       'E_ORGJ_A', 'E_CO_BB', 'E_ORGI_BB', 'E_ORGJ_BB', 'E_PM_10', 'E_C2H2', 'E_GLY', 'E_SULF', 
                       'E_MACR', 'E_MGLY', 'E_MVK', 'E_HCOOH', 'E_HONO']
        out_species_aer = ['E_PM25I', 'E_PM25J', 'E_ECI', 'E_ECJ', 'E_ORGI', 'E_ORGJ', 'E_SO4I', 'E_SO4J', 
                            'E_NO3I', 'E_NO3J', 'E_NH4I', 'E_NH4J', 'E_NAI', 'E_NAJ', 'E_CLI', 'E_CLJ', 
                            'E_CO_A', 'E_ORGI_A', 'E_ORGJ_A', 'E_CO_BB', 'E_ORGI_BB', 'E_ORGJ_BB', 'E_PM_10']

    return out_species, out_species_aer
    