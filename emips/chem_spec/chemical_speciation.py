from .species_reference import SpeciesReferenceItem, SpeciesReference
from .pollutant_profile import PollutantProfileItem, PollutantProfile
from .pollutant import Pollutant
import mipylib.numeric as np

__all__ = ['get_pollutant_profile', 'read_file', 'speciation']

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
        if profile.pollutant == pollutant:
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
            ppi = PollutantProfileItem.read_string(line)
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