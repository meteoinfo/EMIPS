"""
-----CAMS-----
"""
# Import
import os
import mipylib.numeric as np
from mipylib import dataset
from mipylib import geolib

import emips
from emips.utils import Sector, Units, Weight, Area, Period, \
    emis_util, SectorEnum
from emips.chem_spec import Pollutant, Species, PollutantProfile, \
    SpeciesProfile, PollutantEnum, SpeciesEnum
from emips.spatial_alloc import GridDesc, transform
from emips import ge_data_dir


def run(year, month, dir_inter, emission, model_grid):
    """
    Process emission data by spatial allocation, temporal allocation
    and chemical speciation except VOC pollution.

    :param year: (*int*) Year.
    :param month: (*int*) Month.
    :param dir_inter: (*string*) Data output path.
    :param emission: (*module*) Emission module.
    :param model_grid: (*GridDesc*) Model data grid describe.
    """
    # Set profile files
    #   temp_profile_fn = os.path.join(ge_data_dir, 'amptpro.m3.default.us+can.txt')
    #   temp_ref_fn = os.path.join(ge_data_dir, 'amptref.m3.us+can.cair.txt')
    temp_profile_fn = os.path.join(ge_data_dir, 'temporal.txt')

    spec_profile_fn = os.path.join(ge_data_dir, 'gspro.cmaq.radm2p25_rev.txt')
    spec_ref_fn = os.path.join(ge_data_dir, 'gsref.cmaq.radm2p25.txt')

    # Set data dimensions
    tdim = np.dimension(np.arange(24), 'hour')
    ydim = np.dimension(model_grid.y_coord, 'lat', 'Y')
    xdim = np.dimension(model_grid.x_coord, 'lon', 'X')
    dims = [tdim, ydim, xdim]

    # Set sectors and pollutants
    sectors = [SectorEnum.INDUSTRY, SectorEnum.AGRICULTURE, SectorEnum.ENERGY, \
               SectorEnum.RESIDENTIAL, SectorEnum.TRANSPORT, SectorEnum.SHIPS, \
               SectorEnum.AIR]

    pollutants = [PollutantEnum.BC, PollutantEnum.CH4, PollutantEnum.CO, \
                  PollutantEnum.NH3, PollutantEnum.NOx, PollutantEnum.OC, \
                  PollutantEnum.SO2]
    out_species = [SpeciesEnum.PEC, SpeciesEnum.CH4, SpeciesEnum.CO, SpeciesEnum.NH3, \
                   None, SpeciesEnum.POA, SpeciesEnum.SO2]

    # Loop
    for sector in sectors:
        print('------{}------'.format(sector.name))

        # Get SCC
        scc = emis_util.get_scc(sector)

        # Get pollutant profiles
        pollutant_profiles = emips.chem_spec.read_file(spec_ref_fn, spec_profile_fn, scc)
        for pollutant, out_spec in zip(pollutants, out_species):
            print(pollutant)

            print('Read emission data (kg/m2/s)...')
            emis_data = emission.read_emis(sector, pollutant, year, month)
            if emis_data is None:  # No emission of a pollutant for some sectors
                continue
            # Longitude pivot to global grid data from 0 longitude
            emis_data, emis_grid = emission.lonpivot(emis_data, 0, emission.get_emis_grid(sector))
            # Expand grid to aviod NaN interpolation values
            emis_data, emis_grid = emission.grid_expand(emis_data, emis_grid)
            if sector == SectorEnum.SHIPS:
                emis_data = emis_data[::-1, :]
            # Spatial allocation
            print('Spatial allocation of emission grid to model grid...')
            emis_data = transform(emis_data, emis_grid, model_grid)

            # Temporal allocation
            print('Temporal allocation...')
            #            month_profile, week_profile, diurnal_profile, diurnal_profile_we = \
            #                emips.temp_alloc.read_file(temp_ref_fn, temp_profile_fn, scc)
            month_profile, week_profile, diurnal_profile = \
                emips.temp_alloc.read_file_prof(temp_profile_fn, scc, ti=8)
            # print('To (kg/m2/month)')
            emis_data = emis_data * 3600 * 24 * emis_util.get_month_days(year, month)

            # print('To daily emission (kg/m2/day)...')
            weekday_data, weekend_data = emips.temp_alloc.week_allocation(emis_data, week_profile, year, month)
            weekday_data = (weekday_data * 5 + weekend_data * 2) / 7
            # print('To hourly emission (g/m2/s)...')
            hour_data = emips.temp_alloc.diurnal_allocation(weekday_data, diurnal_profile) / 3.6

            # Chemical speciation
            poll_prof = emips.chem_spec.get_pollutant_profile(pollutant_profiles, pollutant)
            if (pollutant == PollutantEnum.NOx) and (poll_prof is None):
                poll_prof = PollutantProfile(pollutant)
                poll_prof.append(SpeciesProfile(pollutant, Species('NO', molar_mass=30), 0.9, 46.0, 0.9))
                poll_prof.append(SpeciesProfile(pollutant, Species('NO2', molar_mass=46), 0.1, 46.0, 0.1))

            # Set output netcdf file path
            outfn = os.path.join(dir_inter, \
                                 '{}_emis_{}_{}_{}_hour.nc'.format(pollutant.name, sector.name, year, month))
            print('File_out:{}'.format(outfn))
            if poll_prof is None:
                # Save hourly emission data
                print('Save hourly emission data...')
                if out_spec.molar_mass is None:
                    attrs = dict(units='g/m2/s')
                else:
                    attrs = dict(units='mole/m2/s')
                    hour_data = hour_data / out_spec.molar_mass
                dataset.ncwrite(outfn, hour_data, out_spec.name, dims, attrs)
            else:
                print('Chemical speciation...')
                specs = poll_prof.get_species()
                gattrs = dict(Conventions='CF-1.6', Tools='Created using MeteoInfo')
                dimvars = []
                for spec in specs:
                    dimvar = dataset.DimVariable()
                    dimvar.name = spec.name
                    dimvar.dtype = np.dtype.float
                    dimvar.dims = dims
                    if spec.molar_mass is None:
                        dimvar.addattr('units', 'g/m2/s')
                    else:
                        dimvar.addattr('units', 'mole/m2/s')
                    dimvars.append(dimvar)
                ncfile = dataset.addfile(outfn, 'c')
                ncfile.nc_define(dims, gattrs, dimvars)
                for spec_prof, dimvar, spec in zip(poll_prof.species_profiles, dimvars, specs):
                    print(dimvar.name)
                    if spec.molar_mass is None:
                        spec_data = hour_data * spec_prof.mass_fraction
                    else:
                        spec_data = hour_data * spec_prof.mass_fraction / spec.molar_mass
                    ncfile.write(dimvar.name, spec_data)
                ncfile.close()
