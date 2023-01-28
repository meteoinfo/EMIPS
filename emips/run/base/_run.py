from emips.utils import Units, Weight, Area, Period
from emips.spatial_alloc import transform, GridDesc
from emips.chem_spec import PollutantEnum
from emips.utils import SectorEnum
from emips import ge_data_dir
from emips import temp_alloc
from emips import chem_spec
from emips import vertical_alloc
from emips.chem_spec import get_model_species_wrf

from mipylib import numeric as np
from mipylib import dataset
from mipylib import miutil
from mipylib import geolib

import datetime
import os
from collections import OrderedDict

__all__ = ["read_emission", "convert_units", "run_spatial", "run_temporal", "run_chemical",
           "run_chemical_grid_spec", "lump_VOC", "run_pollutant", "merge_sector",
           "run_vertical_sector", "run_sector", "run_total", "write_ctl", "convert_grads", "for_CUACE",
           "merge_wrf", "height_wrf", "transform_wrf", "proj_wrf", "for_WRFChem"]


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


def convert_grads(run_config):
    """
    Convert netcdf model-ready emission file to GrADS data
    format for CUACE model.

    :param year: (*int*) Year.
    :param months: (*list*) List of months.
    :param dir_in: (*string*) The directory where netcdf data is stored.
    :param dir_out: (*string*) The directory where GrADS data is writed.
    :param xn: (*int*) x-dimension of output files.
    :param yn: (*int*) y-dimension of output files.
    """
    year = run_config.emission_year
    months = [run_config.emission_month]
    dir_in = run_config.run_output_dir
    dir_out = run_config.run_output_dir
    model_grid = run_config.spatial_model_grid
    xn = model_grid.x_num
    yn = model_grid.y_num

    emis_cuace = {}
    emis_cuace['low'] = [SectorEnum.AGRICULTURE, SectorEnum.RESIDENTIAL,
                         SectorEnum.TRANSPORT, SectorEnum.SHIPS]
    emis_cuace['poi'] = [SectorEnum.INDUSTRY]
    emis_cuace['pow'] = [SectorEnum.ENERGY]
    emis_cuace['air'] = [SectorEnum.AIR]

    # Get emission species
    chem_mech = run_config.chemical_mechanism
    all_species = chem_mech.all_species()
    # Set time dimension of output file.
    tn = 25  # 0 - 24 hour

    for month in months:
        print('**************')
        print('Month: {}'.format(month))
        print('**************')

        # Set directory for input and output files
        # dir_in = os.path.join(dir_in, str(year), '{}{:>02d}'.format(year, month))
        dir_out = os.path.join(dir_out, str(year), '{}{:>02d}'.format(year, month))
        if not os.path.exists(dir_out):
            os.makedirs(dir_out)
        print('------------------Filepath------------------')
        print('dir_data: {}\ndir_out: {}'.format(dir_in, dir_out))
        # Loop
        for emis_type, sectors in emis_cuace.iteritems():
            print(emis_type, sectors)

            # set output binary dta file
            outfn = os.path.join(dir_out, 'emis_{}_{}_{}.grd'.format(year,
                                                                     month, emis_type))
            outer = dataset.bincreate(outfn)

            # Loop time number
            for t in range(tn):
                print('Time number: {}'.format(t))
                if t == tn - 1:
                    t = 0
                # Loop species
                for species in all_species:
                    data = None
                    # Loop sectors
                    for sector in sectors:
                        fn = os.path.join(dir_in, 'emis_{}_{}_{}_hour.nc'.format(sector.name, year, month))
                        if os.path.exists(fn):
                            f_in = dataset.addfile(fn)
                            if species.name in f_in.varnames:
                                dd = f_in[species.name][t]
                                if dd.sum() == 0:
                                    continue
                                if dd.contains_nan():
                                    dd[dd == np.nan] = 0
                                if data is None:
                                    data = dd
                                else:
                                    data = data + dd
                            f_in.close()
                        else:
                            print('Alarm! File not exists: {}'.format(fn))
                            continue
                    if data is None:
                        print('Is None: {}'.format(species))
                        data = np.zeros((yn, xn))
                    # Check the dimensions of the input and output files
                    if data.shape[0] != yn or data.shape[1] != xn:
                        print('The dimensions of input data and output data do not match!!!')
                        os.system("pause")

                    dataset.binwrite(outer, data.astype('float'), byteorder='little_endian', sequential=True)
            outer.close()
    print('Convert to grads completed!')
def write_ctl(run_config):
    """
    Write the description file of the output binary data files.

    :param year: (*int*) Year.
    :param months: (*list*) List of months.
    :param dir_out: (*string*) The directory where files is wrtied.
    :param xn: (*int*) x-dimension of output files.
    :param yn: (*int*) y-dimension of output files.
    :param xmin: (*float*) The initial longitude of output files.
    :param ymin: (*float*) The initial latitude of output files.
    :param xdelta: (*float*) The spacing of longitudes of output files.
    :param ydelta: (*float*) The spacing of latitudes of output files.
    """
    year = run_config.emission_year
    months = [run_config.emission_month]
    dir_out = run_config.run_output_dir
    model_grid = run_config.spatial_model_grid
    xn = model_grid.x_num
    yn = model_grid.y_num
    xmin = model_grid.x_orig
    ymin = model_grid.y_orig
    xdelta = model_grid.x_cell
    ydelta = model_grid.y_cell

    types = ['low','poi','pow','air']
    for month in months:
        dir_out = os.path.join(dir_out, str(year), '{}{:>02d}'.format(year, month))
        for tps in types:
            fn = os.path.join(dir_out, 'emis_{}_{}_{}.ctl'.format(year,month,tps))
            print(fn)
            f = open(fn, 'w')
            f.write('dset ^emis_{}_{}_{}.grd\n'.format(year,month, tps))
            f.write('title model output from grapes\n')
            f.write('options sequential\n')
            f.write('undef -9.99E+33\n')
            f.write('xdef  {} linear   {:.2f}00     {:.2f}00\n'.format(xn, xmin, xdelta))
            f.write('ydef  {} linear   {:.2f}00     {:.2f}00\n'.format(yn, ymin, ydelta))
            f.write('zdef   1  linear 1 1\n')
            month_abbr = miutil.dateformat(datetime.datetime(year, month, 1), 'MMM', 'eng')
            month_abbr = month_abbr.upper()
            f.write('tdef   25 linear 00z01{}{}   60mn\n'.format(month_abbr, year))
            f.write('vars     32\n')
            f.write('  CO 1 99 Emission_CO (moles/m2/s)\n')
            f.write('  NO 1 99 Emission_NO (moles/m2/s)\n')
            f.write('  NO2 1 99 Emission_NO2 (moles/m2/s)\n')
            f.write('  ALD 1 99 Emission_ALD (moles/m2/s)\n')
            f.write('  CH4 1 99 Emission_CH4 (moles/m2/s)\n')
            f.write('  CSL 1 99 Emission_CSL (moles/m2/s)\n')
            f.write('  ETH 1 99 Emission_ETH (moles/m2/s)\n')
            f.write('  HC3 1 99 Emission_HC3 (moles/m2/s)\n')
            f.write('  HC5 1 99 Emission_HC5 (moles/m2/s)\n')
            f.write('  HC8 1 99 Emission_HC8 (moles/m2/s)\n')
            f.write('  HCHO 1 99 Emission_HCHO (moles/m2/s)\n')
            f.write('  ISOP 1 99 Emission_ISOP (moles/m2/s)\n')
            f.write('  KET 1 99 Emission_KET (moles/m2/s)\n')
            f.write('  NR 1 99 Emission_NR (g/m2/s)\n')
            f.write('  OL2 1 99 Emission_OL2 (moles/m2/s)\n')
            f.write('  OLE 1 99 Emission_OLE (g/m2/s)\n')
            f.write('  OLI 1 99 Emission_OLI (moles/m2/s)\n')
            f.write('  OLT 1 99 Emission_OLT (moles/m2/s)\n')
            f.write('  ORA2 1 99 Emission_ORA2 (moles/m2/s)\n')
            f.write('  PAR 1 99 Emission_PAR (g/m2/s)\n')
            f.write('  TERP 1 99 Emission_TERP (moles/m2/s)\n')
            f.write('  TOL 1 99 Emission_TOL (moles/m2/s)\n')
            f.write('  XYL 1 99 Emission_XYL (moles/m2/s)\n')
            f.write('  NH3 1 99 Emission_NH3 (moles/m2/s)\n')
            f.write('  SO2 1 99 Emission_SO2 (moles/m2/s)\n')
            f.write('  SULF 1 99 Emission_SULF (g/m2/s)\n')
            f.write('  PEC 1 99 Emission_PEC (g/m2/s)\n')
            f.write('  PMFINE 1 99 Emission_PMFINE (g/m2/s)\n')
            f.write('  PNO3 1 99 Emission_PNO3 (g/m2/s)\n')
            f.write('  POA 1 99 Emission_POA (g/m2/s)\n')
            f.write('  PSO4 1 99 Emission_PSO4 (g/m2/s)\n')
            f.write('  PMC 1 99 Emission_PMC (g/m2/s)\n')
            f.write('endvars')
            f.close()
    print('Write .ctl file completed!')
def for_CUACE(run_config):
    """
    Total emission processing to all sectors.

    :param run_config: (*RunConfigure*) The run configure.
    """
    print('Convert to grads...')
    convert_grads(run_config)

    print('Write .ctl files...')
    write_ctl(run_config)

    print("Done total!")

def height_wrf(run_config):
    """
    Allocate data to different heights.

    :param year: (*int*) Year.
    :param month: (*int*) Month.
    :param dir_in: (*string*) The directory where data is stored.
    :param model_grid: (*GridDesc*) Model data grid describe.
    :param sectors: (*GridDesc*) The sectors need to be processed.
    :param vertical_pro: Vertical profile.
    :param z: (*int*) The zdim of the output data.
    """
    year = run_config.emission_year
    month = run_config.emission_month
    dir_in = run_config.run_output_dir
    model_grid = run_config.spatial_model_grid
    sectors = run_config.emission_sectors
    z = 7

    out_species_unit = ['PEC', 'POA', 'PMFINE', 'PNO3', 'PSO4', 'PMC']
    print('Define dimension and global attributes...')
    tdim = np.dimension(np.arange(24), 'hour')
    ydim = np.dimension(model_grid.y_coord, 'lat', 'Y')
    xdim = np.dimension(model_grid.x_coord, 'lon', 'X')
    zdim = np.dimension(np.arange(z), 'emissions_zdim')
    dims = [tdim, zdim, ydim, xdim]

    gattrs = OrderedDict()
    gattrs['Conventions'] = 'CF-1.6'
    gattrs['Tools'] = 'Created using MeteoInfo'

    for sector in sectors:
        fn = dir_in + '\emis_{}_{}_{}_hour.nc'.format(sector.name, year, month)
        print('File input: {}'.format(fn))
        vertical_pro = vertical_alloc.read_file(run_config.vertical_prof_file, sector.scc)
        dimvars = []
        if os.path.exists(fn):
            f = dataset.addfile(fn)
            for var in f.varnames:
                if var == 'lat' or var == 'lon':
                    continue
                else:
                    dimvar = dataset.DimVariable()
                    dimvar.name = var
                    dimvar.dtype = np.dtype.float
                    dimvar.dims = dims
                    dimvar.addattr('description', "EMISSION_{}".format(var))
                    if var in out_species_unit:
                        dimvar.addattr('units', 'g/m2/s')
                    else:
                        dimvar.addattr('units', 'mole/m2/s')
                    dimvars.append(dimvar)

            out_fn = dir_inter + '\emis_{}_{}_{}_hour_height.nc'.format(sector.name, year, month)
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
            continue
    print('Allocate of height finished!')


def merge_wrf(run_config):
    """
    Combine all sectors into one file

    :param year: (*int*) Year.
    :param month: (*int*) Month.
    :param dir_inter: (*string*) The directory where data is stored.
    :param model_grid: (*GridDesc*) Model data grid describe.
    :param sectors: (*list*) Sectors that needs to be merged.
    :param z: (*int*) The zdim of the output data.
    """
    year = run_config.emission_year
    month = run_config.emission_month
    dir_in = run_config.run_output_dir
    model_grid = run_config.spatial_model_grid
    sectors = run_config.emission_sectors
    z = 7

    out_species_aer = ['PEC', 'POA', 'PMFINE', 'PNO3', 'PSO4', 'PMC']
    print('Define dimension and global attributes...')
    tdim = np.dimension(np.arange(24), 'hour')
    zdim = np.dimension(np.arange(z), 'emissions_zdim')
    ydim = np.dimension(model_grid.y_coord, 'lat', 'Y')
    xdim = np.dimension(model_grid.x_coord, 'lon', 'X')
    dims = [tdim, zdim, ydim, xdim]
    #Set the definition of the output variable
    print('Define variables...')
    dimvars = []
    count = []
    dict_spec = {}
    print('Add files...')
    for sector in sectors:
        fn = dir_in + '\emis_{}_{}_{}_hour_height.nc'.format(sector.name, year, month)
        vertical_pro = vertical_alloc.read_file(run_config.vertical_prof_file, sector.scc)
        if os.path.exists(fn):
            print(fn)
            f = dataset.addfile(fn)
            for var in f.variables:
                if var.ndim == 4:
                    if dict_spec.has_key(var.name):
                        dict_spec[var.name].append(fn)
                    else:
                        dict_spec[var.name] = [fn]
            for var in f.varnames:
                if var == 'lat' or var == 'lon':
                    continue
                if var in count:
                    continue
                else:
                    dimvar = dataset.DimVariable()
                    dimvar.name = var
                    dimvar.dtype = np.dtype.float
                    dimvar.dims = dims
                    dimvar.addattr('description', "EMISSION_{}".format(var))
                    if var in out_species_aer:
                        dimvar.addattr('units', 'g/m2/s')
                    else:
                        dimvar.addattr('units', 'mole/m2/s')
                count.append(var)
                dimvars.append(dimvar)
            f.close()
        else:
            print('File not exist: {}'.format(fn))
            continue

    #Set dimension and define ncfile
    out_fn = dir_inter + '\emis_{}_{}_hour.nc'.format(year, month)
    gattrs = OrderedDict()
    gattrs['Conventions'] = 'CF-1.6'
    gattrs['Tools'] = 'Created using MeteoInfo'
    print('Create output data file:{}'.format(out_fn))
    ncfile = dataset.addfile(out_fn, 'c', largefile=True)
    ncfile.nc_define(dims, gattrs, dimvars)
    #read, merge and output
    print('Write variables data...')
    for sname, fns in dict_spec.iteritems():
        print(sname)
        spec_data = np.zeros((tdim.length, z, ydim.length, xdim.length))
        dd = np.zeros((tdim.length, z, ydim.length, xdim.length))
        for fn in fns:
            f = dataset.addfile(fn)
            dd = f[sname][:]
            #turn nan to zero
            dd[dd==np.nan] = 0.0
            if spec_data.sum() == 0.0:
                spec_data = dd
            else:
                spec_data = spec_data + dd
            f.close()
        ncfile.write(sname, spec_data)
    ncfile.close()
    print('Merge data finished!')

def transform_wrf(run_config):
    """
    Distribution of particulate matter and change unit.

    :param year: (*int*) Year.
    :param month: (*int*) Month.
    :param dir_in: (*string*) The directory where data is stored.
    :param model_grid: (*GridDesc*) Model data grid describe.
    :param out_species: (*list*) The name of the output species(gases and aerosol).
    :param out_species_aer: (*list*) The name of the output species(aerosol).
    :param z: (*int*) The zdim of the output data.
    """
    year = run_config.emission_year
    month = run_config.emission_month
    dir_in = run_config.run_output_dir
    model_grid = run_config.spatial_model_grid
    out_species, out_species_aer = get_model_species_wrf(run_config.chemical_mechanism.name)
    z = 7

    print('Add input file...')
    fn_in = dir_in + '\emis_{}_{}_hour.nc'.format(year, month)
    f_in = dataset.addfile(fn_in)

    #Set dimension
    print('Define dimensions and global attributes...')
    tdim = np.dimension(np.arange(24), 'Time')
    zdim = np.dimension(np.arange(z), 'emissions_zdim')
    ydim = np.dimension(model_grid.y_coord, 'south_north', 'Y')
    xdim = np.dimension(model_grid.x_coord, 'west_east', 'X')
    dims = [tdim, zdim, ydim, xdim]
    gattrs = OrderedDict()
    gattrs['Conventions'] = 'CF-1.6'
    gattrs['Tools'] = 'Created using MeteoInfo'

    #Set the definition of the output variable and ncfile
    fn_out = dir_inter + '\emis_{}_{}_hour_transform.nc'.format(year, month)
    print('Define variables and output file...')
    dimvars = []
    for out_specie in out_species:
        dimvar = dataset.DimVariable()
        dimvar.name = out_specie
        dimvar.dtype = np.dtype.float
        dimvar.dims = dims
        dimvar.addattr('FieldType', '104')
        dimvar.addattr('MemoryOrder', "XYZ")
        dimvar.addattr('description', "EMISSION_{}".format(out_specie[2:]))
        if out_specie in out_species_aer:
            #g/m2/s to ug/m^3 m/s
            dimvar.addattr('units', 'ug/m3 m/s')
        else:
            #mole/m2/s to mol/km^2/hr
            dimvar.addattr('units', 'mol km^-2 hr^-1')
        dimvar.addattr('stagger', "")
        dimvar.addattr('coordinates', "XLONG XLAT XTIME")
        #dimvar.addattr('_ChunkSizes', '1U, 3U, 137U, 167U')
        dimvars.append(dimvar)
    print('Create output data file:{}'.format(fn_out))
    ncfile = dataset.addfile(fn_out, 'c', largefile=True)
    ncfile.nc_define(dims, gattrs, dimvars)

    #add data to ncfile
    print('Process data and write to file...')
    for name in out_species:
        data = np.zeros((tdim.length, z, ydim.length, xdim.length))
        sname = name[2:]
        print(sname)
        if sname in f_in.varnames:
            data = f_in[sname][:, :, :]
            data = data * 3600 * 1e6
            ncfile.write(name, data)
        elif sname == 'PM25I':
            data = f_in['PMFINE'][:, :, :]
            data = data * 1e6
            ncfile.write(name, data*0.2)
        elif sname == 'PM25J':
            data = f_in['PMFINE'][:, :, :]
            data = data * 1e6
            ncfile.write(name, data*0.8)
        ##radm2, mozart
        elif sname == 'PM_10' :
            data = f_in['PMC'][:, :, :]
            data = data * 1e6
            ncfile.write(name, data)
            #saprc99, cb05
        elif sname == 'PM10' :
            data = f_in['PMC'][:, :, :]
            data = data * 1e6
            ncfile.write(name, data)
        elif sname == 'ECI':
            data = f_in['PEC'][:, :, :]
            data = data * 1e6
            ncfile.write(name, data*0.2)
        elif sname == 'ECJ':
            data = f_in['PEC'][:, :, :]
            data = data * 1e6
            ncfile.write(name, data*0.8)
        elif sname == 'ORGI':
            data = f_in['POA'][:, :, :]
            data = data * 1e6
            ncfile.write(name, data*0.2)
        elif sname == 'ORGJ':
            data = f_in['POA'][:, :, :]
            data = data * 1e6
            ncfile.write(name, data*0.8)
        elif sname == 'SO4I':
            data = f_in['PSO4'][:, :, :]
            data = data * 1e6
            ncfile.write(name, data*0.2)
        elif sname == 'SO4J':
            data = f_in['PSO4'][:, :, :]
            data = data * 1e6
            ncfile.write(name, data*0.8)
        elif sname == 'NO3I':
            data = f_in['PNO3'][:, :, :]
            data = data * 1e6
            ncfile.write(name, data*0.2)
        elif sname == 'NO3J':
            data = f_in['PNO3'][:, :, :]
            data = data * 1e6
            ncfile.write(name, data*0.8)
        else:
            ncfile.write(name, data)
    f_in.close()
    ncfile.close()
    print('Distribution of particulate matter and change unit finised!')

def proj_wrf(run_config):
    """
    Write Times variable, add global attributes, convert data's projection.
	io_style_emissions = 1

    :param year: (*int*) Year.
    :param month: (*int*) Month.
    :param dir_in: (*string*) The directory where data is stored.
    :param model_grid: (*GridDesc*) Model data grid describe.
    :param target_grid: (*GridDesc*) Target data grid describe.
    :param out_species: (*list*) The name of the output species(gases and aerosol).
    :param out_species_aer: (*list*) The name of the output species(aerosol).
    :param global_attributes: (*OrderedDict*) The global attributes of the output file.
    :param mechanism_name: (*string*) The name of the chemical mechanism.
    :param z: (*int*) The zdim of the output data.
    """
    #set global attributes
    gattrs = OrderedDict()
    #gattrs['Conventions'] = 'CF-1.6'
    gattrs['TITLE'] = 'Created using MeteoInfo, mechanism: {}'.format(mechanism_name.upper())
    gattrs['START_DATE'] = "{}-{:0>2d}-01_00:00:00".format(year, month)
    gattrs['WEST-EAST_GRID_DIMENSION'] = 335
    gattrs['SOUTH-NORTH_GRID_DIMENSION'] = 275
    gattrs['BOTTOM-TOP_GRID_DIMENSION'] = 8
    gattrs['DX'] = 15000.0
    gattrs['DY'] = 15000.0
    gattrs['WEST-EAST_PATCH_START_UNSTAG '] = 1
    gattrs['WEST-EAST_PATCH_END_UNSTAG'] = 334
    gattrs['WEST-EAST_PATCH_START_STAG'] = 1
    gattrs['WEST-EAST_PATCH_END_STAG'] = 335
    gattrs['SOUTH-NORTH_PATCH_START_UNSTAG'] = 1
    gattrs['SOUTH-NORTH_PATCH_END_UNSTAG'] = 274
    gattrs['SOUTH-NORTH_PATCH_START_STAG'] = 1
    gattrs['SOUTH-NORTH_PATCH_END_STAG'] = 275
    gattrs['BOTTOM-TOP_PATCH_START_UNSTAG'] = 1
    gattrs['BOTTOM-TOP_PATCH_END_UNSTAG'] = 7
    gattrs['BOTTOM-TOP_PATCH_START_STAG'] = 1
    gattrs['BOTTOM-TOP_PATCH_END_STAG'] = 8
    gattrs['CEN_LAT'] = 36.500008
    gattrs['CEN_LON'] = 103.5
    gattrs['TRUELAT1'] = 30.0
    gattrs['TRUELAT2'] = 60.0
    gattrs['MOAD_CEN_LAT'] = 36.500008
    gattrs['STAND_LON'] = 103.5
    gattrs['POLE_LAT'] = 90.0
    gattrs['POLE_LON'] = 0.0
    gattrs['GMT'] = 0.0
    gattrs['MAP_PROJ'] = 1
    gattrs['MAP_PROJ_CHAR'] = 'Lambert Conformal'
    gattrs['MMINLU'] = 'MODIFIED_IGBP_MODIS_NOAH'
    gattrs['NUM_LAND_CAT'] = 21
    gattrs['ISWATER'] = 17
    gattrs['ISLAKE'] = 21
    gattrs['ISICE'] = 15
    gattrs['ISURBAN'] = 13
    gattrs['ISOILWATER'] = 14

    year = run_config.emission_year
    month = run_config.emission_month
    dir_in = run_config.run_output_dir
    model_grid = run_config.spatial_model_grid
    target_proj = geolib.projinfo(proj='lcc', lon_0=103.5, lat_0=36.500008, lat_1=30.0, lat_2=60.0, a=6370000, b=6370000)
    target_grid = GridDesc(target_proj, x_orig=-2497499.597352108, x_cell=15000.0, x_num=334,
                       y_orig=-2047499.8096037393, y_cell=15000.0, y_num=274)
    mechanism_name = run_config.chemical_mechanism.name
    out_species, out_species_aer = get_model_species_wrf(mechanism_name)
    global_attributes = gattrs
    z = 7

    print('Add input file...')
    fn_in = dir_in + '\emis_{}_{}_hour_transform.nc'.format(year, month)
    print(fn_in)
    f_in = dataset.addfile(fn_in)
    #set dimension
    tdim = np.dimension(np.arange(12), 'Time')
    ydim = np.dimension(target_grid.y_coord, 'south_north', 'Y')
    xdim = np.dimension(target_grid.x_coord, 'west_east', 'X')
    zdim = np.dimension(np.arange(z), 'emissions_zdim')
    sdim = np.dimension(np.arange(19), 'DateStrLen')
    dims = [tdim, zdim, ydim, xdim]
    all_dims = [tdim, sdim, xdim, ydim, zdim]

    #set variables
    dimvars = []

    dimvar = dataset.DimVariable()
    dimvar.name = 'Times'
    dimvar.dtype = np.dtype.char
    dimvar.dims = [tdim, sdim]
    #dimvar.addattr('_ChunkSizes', [1, 19])
    dimvars.append(dimvar)

    for out_specie in out_species:
        dimvar = dataset.DimVariable()
        dimvar.name = out_specie
        dimvar.dtype = np.dtype.float
        dimvar.dims = dims
        dimvar.addattr('FieldType', 104)
        dimvar.addattr('MemoryOrder', "XYZ")
        dimvar.addattr('description', "EMISSION_{}".format(out_specie[2:]))
        if out_specie in out_species_aer:
            #g/m2/s to ug/m^3 m/s
            dimvar.addattr('units', 'ug/m3 m/s')
        else:
            #mole/m2/s to mol/km^2/hr
            dimvar.addattr('units', 'mol km^-2 hr^-1')
        dimvar.addattr('stagger', "")
        dimvar.addattr('coordinates', "XLONG XLAT XTIME")
        #dimvar.addattr('_ChunkSizes', [1, 3, 137, 167])
        dimvars.append(dimvar)
    for num in [0, 12]:
        fn_out = dir_inter + '\wrfchemi_{:0>2d}z_d01_{}'.format(num, mechanism_name)

        print('Create output data file...')
        print(fn_out)
        ncfile = dataset.addfile(fn_out, 'c', largefile=True)
        print('Define dimensions, global attributes and variables...')
        ncfile.nc_define(all_dims, global_attributes, dimvars, write_dimvars=False)

        #Times
        print('Write Times variable...')
        s_out = []
        for i in range(num, num+12):
            s = '{}-{:0>2d}-01_{:0>2d}:00:00'.format(year, month, i)
            s_out.append(s)
        s_out = np.array(s_out, dtype=np.dtype.char)
        ncfile.write('Times', s_out)

        print('Write variable data except times...')
        for out_specie in out_species:
            data = np.zeros((tdim.length, zdim.length, ydim.length, xdim.length))
            if out_specie in f_in.varnames:
                print(out_specie)
                dd = f_in[out_specie][num:num+12]
                #Conversion
                dd = transform(dd, model_grid, target_grid)
                #Set the fourth dimension
                #dd = dd.reshape(12, 1, ydim.length, xdim.length)
                #Set default values
                dd[dd==np.nan] = 0
            else:
                print('{} no data!'.format(out_specie))
                '''
                dd = f_in['E_ISO'][num:num+12]
                dd[:, :, :, :] = 0
                dd = transform(dd, model_grid, target_grid)
                #Set the fourth dimension 
                #dd = dd.reshape(12, 1, ydim.length, xdim.length)
                #Set default values
                dd[dd==np.nan] = 0
                '''
            data[:, :, :, :] = dd
            ncfile.write(out_specie, data)
        ncfile.close()
    f_in.close()
    print('Convert projection finished and split into two files finished!')

def for_WRFChem(run_config):
    """
    Total emission processing to all sectors.

    :param run_config: (*RunConfigure*) The run configure.
    """
    print('Allocate according to height...')
    height_wrf(run_config)
    print('Merge data from different sectors...')
    merge_wrf(run_config)
    print('Distribution of particulate matter and change unit...')
    transform_wrf(run_config)
    print('Conversion projection...')
    proj_wrf(yrun_config)

    print("Done total!")