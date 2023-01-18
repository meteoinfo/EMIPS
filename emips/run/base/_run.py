from emips.utils import Units, Weight, Area, Period
from emips.spatial_alloc import transform
from emips.chem_spec import PollutantEnum
from emips import ge_data_dir
from emips import temp_alloc
from emips import chem_spec
from emips import vertical_alloc

from mipylib import numeric as np
from mipylib import dataset

import os
from collections import OrderedDict

__all__ = ["read_emission", "convert_units", "run_spatial", "run_temporal", "run_chemical",
           "run_chemical_grid_spec", "lump_VOC", "run_pollutant", "merge_sector",
           "run_vertical_sector", "run_sector", "run_total"]


def read_emission(run_config, sector, pollutant):
    """
    Read emission data.

    :param run_config: (*RunConfigure*) The run configure.
    :param sector: (*Sector*) The sector.
    :param pollutant: (*Pollutant*) The pollutant.

    :return: Emission data array and emission grid description.
    """
    # Read emission data
    print("Read emission data...")
    year = run_config.emission_year
    month = run_config.emission_month
    emission = run_config.emission_module
    emis_data = emission.read_emis(sector, pollutant, year, month)
    emis_grid = emission.get_emis_grid()
    return emis_data, emis_grid


def convert_units(data, pollutant, emis_grid):
    """
    Convert emission data units to g/m2/s.

    :param data: (*array*) Input emission data.
    :param pollutant: (*Pollutant*) The pollutant.
    :param emis_grid: (*GridDesc*) The emission grid description.

    :return: Converted emission data array
    """
    # Emission units conversion
    print("Units conversion...")
    units = Units(Weight.G, Area.M2, Period.MONTH)
    if pollutant.units.area == Area.GRID:
        convert_ratio = pollutant.units.convert_ratio(units, ignore_area=True)
        print(convert_ratio)
        data = data * convert_ratio / emis_grid.grid_areas()
    else:
        convert_ratio = pollutant.units.convert_ratio(units)
        data = data * convert_ratio

    return data


def run_spatial(data, run_config, emis_grid):
    """
    Spatial transform.

    :param data: (*array*) Input emission data array.
    :param run_config: (*RunConfigure*) The run configure.
    :param emis_grid: (*GridDesc*) The emission grid description.

    :return: Spatial transformed emission data array.
    """
    # Spatial transform
    print("Spatial allocation...")
    model_grid = run_config.spatial_model_grid
    data = transform(data, emis_grid, model_grid)
    return data


def run_temporal(data, run_config, sector):
    """
    Temporal allocation.

    :param data: (*array*) Input emission data array.
    :param run_config: (*RunConfigure*) The run configure.
    :param sector: (*Sector*) The sector.

    :return: Temporal allocated data array.
    """
    year = run_config.emission_year
    month = run_config.emission_month

    # Temporal allocation
    print('Temporal allocation...')
    units = Units(Weight.G, Area.M2, Period.SECOND)
    temp_ref_fn = os.path.join(ge_data_dir, run_config.temporal_ref_file)
    temp_profile_fn = os.path.join(ge_data_dir, run_config.temporal_prof_file)
    month_profile, week_profile, diurnal_profile, diurnal_profile_we = \
        temp_alloc.read_file(temp_ref_fn, temp_profile_fn, sector.scc)

    print('To daily emission (g/m2/day)...')
    weekday_data, weekend_data = temp_alloc.week_allocation(data, week_profile, year, month)
    weekday_data = (weekday_data * 5 + weekend_data * 2) / 7
    print('To hourly emission (g/m2/s)...')
    hour_data = temp_alloc.diurnal_allocation(weekday_data, diurnal_profile) / 3600
    return hour_data


def run_chemical(hour_data, run_config, sector, pollutant):
    """
    Chemical speciation and write output NC file.

    :param hour_data: (*array*) Hourly emission data array.
    :param run_config: (*RunConfigure*) The run configure.
    :param sector: (*Sector*) The sector.
    :param pollutant: (*Pollutant*) The pollutant.
    """
    year = run_config.emission_year
    month = run_config.emission_month
    model_grid = run_config.spatial_model_grid

    # Chemical speciation
    print("Chemical speciation...")
    spec_ref_fn = os.path.join(ge_data_dir, run_config.chemical_ref_file)
    spec_profile_fn = os.path.join(ge_data_dir, run_config.chemical_prof_file)
    pollutant_profiles = chem_spec.read_file(spec_ref_fn, spec_profile_fn, sector.scc)
    poll_prof = chem_spec.get_pollutant_profile(pollutant_profiles, pollutant)

    # Write to NC file
    print("Write to NC file...")
    # Set dimensions
    tdim = np.dimension(np.arange(24), 'hour')
    ydim = np.dimension(model_grid.y_coord, 'lat', 'Y')
    xdim = np.dimension(model_grid.x_coord, 'lon', 'X')
    dims = [tdim, ydim, xdim]
    outfn = os.path.join(run_config.run_output_dir,
                         '{}_emis_{}_{}_{}_hour.nc'.format(pollutant.name, sector.name, year, month))
    print('Output file: {}'.format(outfn))
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
        spec_data = hour_data * spec_prof.mass_fraction
        if spec.molar_mass is not None:
            print('To (mole/m2/s)')
            spec_data = spec_data / spec.molar_mass
        ncfile.write(dimvar.name, spec_data)
    ncfile.close()


def run_chemical_grid_spec(hour_data, run_config, sector, pollutant):
    """
    Chemical speciation using grid speciation files and write output NC file.

    :param hour_data: (*array*) Hourly emission data array.
    :param run_config: (*RunConfigure*) The run configure.
    :param sector: (*Sector*) The sector.
    :param pollutant: (*Pollutant*) The pollutant.
    """
    year = run_config.emission_year
    month = run_config.emission_month
    model_grid = run_config.spatial_model_grid

    # Chemical speciation
    print('Chemical speciation...')
    # Set dimensions
    tdim = np.dimension(np.arange(24), 'hour')
    ydim = np.dimension(model_grid.y_coord, 'lat', 'Y')
    xdim = np.dimension(model_grid.x_coord, 'lon', 'X')
    dims = [tdim, ydim, xdim]
    outfn = os.path.join(run_config.run_output_dir,
                         '{}_emis_{}_{}_{}_hour.nc'.format(pollutant.name, sector.name, year, month))
    print('Output file: {}'.format(outfn))

    print('Grid speciation...')

    # Create output netcdf file and define dimensions, global attributes and variables
    gattrs = dict(Conventions='CF-1.6', Tools='Created using MeteoInfo')
    dimvars = run_config.grid_spec_module.get_spec_vars(sector, dims)
    ncfile = dataset.addfile(outfn, 'c')
    ncfile.nc_define(dims, gattrs, dimvars)

    # Write variable values
    ratio_grid = run_config.grid_spec_module.get_spec_grid()
    for dimvar in dimvars:
        print(dimvar.name)
        rdata = run_config.grid_spec_module.read_spec(sector, dimvar)
        rdata = transform(rdata, ratio_grid, model_grid)
        spec_data = hour_data * rdata
        ncfile.write(dimvar.name, spec_data)

    # Close output netcdf file
    ncfile.close()


def lump_VOC(run_config, sector, pollutant):
    """
    Lump VOC species according chemical mechanism.

    :param run_config: (*RunConfigure*) The run configure.
    :param sector: (*Sector*) The sector.
    :param pollutant: (*Pollutant*) The pollutant.
    """
    year = run_config.emission_year
    month = run_config.emission_month
    model_grid = run_config.spatial_model_grid
    chem_mech = run_config.chemical_mechanism

    # Set input file
    infn = os.path.join(run_config.run_output_dir,
                        '{}_emis_{}_{}_{}_hour.nc'.format(pollutant.name, sector.name, year, month))
    print('Input file: {}'.format(infn))
    # Open input file
    inf = dataset.addfile(infn)
    # Read a reference data
    vname = inf.varnames[4]
    rdata = inf[vname][:]
    rdata[rdata!=np.nan] = 0.

    #Set dimensions
    tdim = np.dimension(np.arange(24), 'hour')
    ydim = np.dimension(model_grid.y_coord, 'lat', 'Y')
    xdim = np.dimension(model_grid.x_coord, 'lon', 'X')
    dims = [tdim, ydim, xdim]

    # Set output file
    outfn = os.path.join(run_config.run_output_dir,
                         '{}_emis_lump_{}_{}_{}_hour.nc'.format(pollutant.name, sector.name, year, month))
    print('Output file: {}'.format(outfn))
    # Create output netcdf file
    ncfile = dataset.addfile(outfn, 'c')
    # Set global attribute
    gattrs = dict(Conventions='CF-1.6', Tools='Created using MeteoInfo')
    # Set variables
    dimvars = []
    for spec in chem_mech.nmvoc_species():
        dimvar = dataset.DimVariable()
        dimvar.name = spec.name
        dimvar.dtype = np.dtype.float
        dimvar.dims = dims
        dimvar.addattr('units', 'mol/m2/s')
        dimvars.append(dimvar)
    # Define dimensions, global attributes and variables
    ncfile.nc_define(dims, gattrs, dimvars)

    # Write variable values
    for spec, dimvar in zip(chem_mech.nmvoc_species(), dimvars):
        print('{} species: {}'.format(chem_mech.name, spec))
        rspecs = chem_mech.lump_RETRO(spec)
        print('RETRO species: {}'.format(rspecs))
        data = None
        for rspec, ratio in rspecs.iteritems():
            if rspec.name in inf.varnames:
                if data is None:
                    data = inf[rspec.name][:] * ratio
                else:
                    data = data + inf[rspec.name][:] * ratio
        if data is None:
            print('No RETRO species!')
            ncfile.write(dimvar.name, rdata)
        else:
            print('Convert (g/m2/s) to (mole/m2/s)')
            data = data / spec.molar_mass
            ncfile.write(dimvar.name, data)

    # Close output netcdf file
    ncfile.close()


def run_pollutant(run_config, sector, pollutant):
    """
    Run emission processing for a pollutant.

    :param run_config: (*RunConfigure*) The run configure.
    :param sector: (*Sector*) The sector.
    :param pollutant: (*Pollutant*) The pollutant.
    """
    # Read emission data
    data, emis_grid = read_emission(run_config, sector, pollutant)

    # Emission units conversion
    data = convert_units(data, pollutant, emis_grid)

    # Spatial transform
    data = run_spatial(data, run_config, emis_grid)

    # Temporal allocation
    hour_data = run_temporal(data, run_config, sector)

    # Chemical speciation
    if pollutant.is_VOC and run_config.voc_use_grid_spec:
        run_chemical_grid_spec(hour_data, run_config, sector, pollutant)
        lump_VOC(run_config, sector, pollutant)
    else:
        run_chemical(hour_data, run_config, sector, pollutant)
    print("Done: {}_{}".format(sector.name, pollutant.name))


def merge_sector(sector, run_config):
    """
    Merge all pollutant emission files in one file for each sector.

    :param sector: (*Sector*) The sector.
    :param run_config: (*RunConfigure*) The run configure.
    """
    year = run_config.emission_year
    month = run_config.emission_month
    model_grid = run_config.spatial_model_grid

    # Set dimensions
    tdim = np.dimension(np.arange(24), 'hour')
    ydim = np.dimension(model_grid.y_coord, 'lat', 'Y')
    xdim = np.dimension(model_grid.x_coord, 'lon', 'X')
    dims = [tdim, ydim, xdim]

    print('-----{}-----'.format(sector.name))

    # Set output sector emission file name
    outfn = os.path.join(run_config.run_output_dir,
                         'emis_{}_{}_{}_hour.nc'.format(sector.name, year, month))
    print('File_out: {}'.format(outfn))

    # Pollutant loop
    dimvars = []
    dict_spec = {}
    for pollutant in run_config.emission_pollutants:
        # Read data in pollutant file
        if pollutant.is_VOC and run_config.voc_use_grid_spec:
            fn = os.path.join(run_config.run_output_dir,
                              '{}_emis_lump_{}_{}_{}_hour.nc'.format(pollutant.name,
                                                                     sector.name, year, month))
        else:
            fn = os.path.join(run_config.run_output_dir,
                              '{}_emis_{}_{}_{}_hour.nc'.format(pollutant.name,
                                                                sector.name, year, month))
        print('File_in: {}'.format(fn))
        f = dataset.addfile(fn)

        for var in f.variables:
            if var.ndim == 3:
                if dict_spec.has_key(var.name):
                    dict_spec[var.name].append(fn)
                else:
                    dimvars.append(var)
                    dict_spec[var.name] = [fn]

    # Create output merged netcdf data file
    gattrs = dict(Conventions='CF-1.6', Tools='Created using MeteoInfo')
    ncfile = dataset.addfile(outfn, 'c', largefile=True)
    ncfile.nc_define(dims, gattrs, dimvars)
    for sname, fns in dict_spec.iteritems():
        spec_data = None
        for fn in fns:
            f = dataset.addfile(fn)
            if spec_data is None:
                spec_data = f[sname][:]
            else:
                spec_data = spec_data + f[sname][:]
        ncfile.write(sname, spec_data)
    f.close()
    ncfile.close()


def run_vertical_sector(sector, run_config):
    """
    Vertical allocation to a sector.

    :param sector: (*Sector*) The sector.
    :param run_config: (*RunConfigure*) The run configure.
    """
    year = run_config.emission_year
    month = run_config.emission_month
    model_grid = run_config.spatial_model_grid

    # get vertical profiles
    vertical_pro = vertical_alloc.read_file(run_config.vertical_prof_file, sector.scc)
    z = len(vertical_pro.weights)

    print('Define dimension and global attributes...')
    tdim = np.dimension(np.arange(24), 'hour')
    ydim = np.dimension(model_grid.y_coord, 'lat', 'Y')
    xdim = np.dimension(model_grid.x_coord, 'lon', 'X')
    zdim = np.dimension(np.arange(z), 'emissions_zdim')
    dims = [tdim, zdim, ydim, xdim]

    gattrs = OrderedDict()
    gattrs['Conventions'] = 'CF-1.6'
    gattrs['Tools'] = 'Created using MeteoInfo'

    fn = os.path.join(run_config.run_output_dir,
                      'emis_{}_{}_{}_hour.nc'.format(sector.name, year, month))
    print('File input: {}'.format(fn))
    dimvars = []
    if os.path.exists(fn):
        f = dataset.addfile(fn)
        for var in f.variables:
            if var.ndim == 3:
                dimvar = dataset.DimVariable()
                dimvar.name = var.name
                dimvar.dtype = np.dtype.float
                dimvar.dims = dims
                dimvar.addattr('description', "EMISSION_{}".format(var.name))
                dimvar.addattr('units', var.attrvalue('units')[0])
                dimvars.append(dimvar)

        out_fn = os.path.join(run_config.run_output_dir,
                              'emis_{}_{}_{}_hour_height.nc'.format(sector.name, year, month))
        print('Create output data file:{}'.format(out_fn))
        ncfile = dataset.addfile(out_fn, 'c', largefile=True)
        ncfile.nc_define(dims, gattrs, dimvars)

        data = np.zeros((tdim.length, z, ydim.length, xdim.length))
        dd = np.zeros((tdim.length, z, ydim.length, xdim.length))

        # read, merge and output
        if round(vertical_pro.get_ratios()[0], 2) != 1.0:
            print('Allocating: {}'.format(sector.name))
        else:
            print('Do not need to be allocated: {}'.format(sector.name))
        print('Write data to file...')
        for var in f.varnames:
            if var == 'lat' or var == 'lon':
                continue
            else:
                print(var)
                dd[:, 0, :, :] = f[var][:]
                if round(vertical_pro.get_ratios()[0], 2) == 1.0:
                    data[:, 0, :, :] = dd[:, 0, :, :]
                else:
                    for lay in np.arange(len(vertical_pro.get_ratios())):
                        data[:, lay, :, :] = dd[:, 0, :, :] * vertical_pro.get_ratios()[lay]
                # Turn nan to zero
                data[data == np.nan] = 0
            ncfile.write(var, data)
        ncfile.close()
        f.close()
    else:
        print('File not exist: {}'.format(fn))


def run_sector(sector, run_config):
    """
    Total emission processing to a sector.

    :param sector: (*Sector*) The sector.
    :param run_config: (*RunConfigure*) The run configure.
    """
    for pollutant in run_config.emission_pollutants:
        print("-------------------------------")
        print("Pollutant: {}".format(pollutant))
        print("-------------------------------")
        run_pollutant(run_config, sector, pollutant)

    merge_sector(sector, run_config)

    if run_config.is_run_vertical:
        run_vertical_sector(sector, run_config)

    print("Done: {}".format(sector.name))


def run_total(run_config):
    """
    Total emission processing to all sectors.

    :param run_config: (*RunConfigure*) The run configure.
    """
    for sector in run_config.emission_sectors:
        print("############################")
        print("Sector: {}".format(sector))
        print("############################")
        run_sector(sector, run_config)

    print("Done total!")
