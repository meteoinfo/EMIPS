"""
-----MEIC-----
"""
import mipylib.numeric as np
import os
from mipylib import dataset

import emips
from emips import ge_data_dir
from emips.chem_spec import PollutantEnum
from emips.spatial_alloc import GridDesc, transform
from emips.utils import Units, Weight, Area, Period, emis_util, \
    SectorEnum


def run(year, month, dir_inter, emission, model_grid):
    """
    Process VOC emission data by spatial allocation, temporal allocation
    and chemical speciation.

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

    # Set dimensions
    tdim = np.dimension(np.arange(24), 'hour')
    ydim = np.dimension(model_grid.y_coord, 'lat', 'Y')
    xdim = np.dimension(model_grid.x_coord, 'lon', 'X')
    dims = [tdim, ydim, xdim]

    # Set sectors and pollutants
    sectors = [SectorEnum.INDUSTRY, SectorEnum.AGRICULTURE, SectorEnum.ENERGY,
               SectorEnum.RESIDENTIAL, SectorEnum.TRANSPORT]
    fn_sectors = ['inc', 'agr', 'pow', 'res', 'tra']
    pollutant = PollutantEnum.NMVOC
    pollutant.units = Units(Weight.MG, Area.GRID, Period.MONTH)

    # Loop
    for sector, fn_sector in zip(sectors, fn_sectors):
        print('-----{}-----'.format(sector.name))

        # Get SCC
        scc = emis_util.get_scc(sector)

        print('Read emission data...')
        emis_data = emission.read_emis(sector, pollutant, year, month)

        #### Spatial allocation  
        print('Spatial allocation...')
        # print('Convert emission data untis from Mg/grid/month to g/m2/month...')
        emis_data = emis_data * 1e6 / emission.grid_areas

        # print('Spatial allocation of emission grid to model grid...')
        emis_data = transform(emis_data, emission.emis_grid, model_grid)

        #### Temporal allocation
        print('Temporal allocation...')
        #       month_profile, week_profile, diurnal_profile, diurnal_profile_we = \
        #           emips.temp_alloc.read_file(temp_ref_fn, temp_profile_fn, scc)
        month_profile, week_profile, diurnal_profile = \
            emips.temp_alloc.read_file_prof(temp_profile_fn, scc, ti=8)
        # print('To daily emission (g/m2/day)...')
        weekday_data, weekend_data = emips.temp_alloc.week_allocation(emis_data, week_profile, year, month)
        weekday_data = (weekday_data * 5 + weekend_data * 2) / 7
        # print('To hourly emission (g/m2/s)...')
        hour_data = emips.temp_alloc.diurnal_allocation(weekday_data, diurnal_profile) / 3600

        #### Chemical speciation
        print('Chemical speciation...')
        outfn = os.path.join(dir_inter,
                             '{}_emis_{}_{}_{}_hour.nc'.format(pollutant.value.name, sector.value.name, year, month))
        print('Output file: {}'.format(outfn))

        # print('Set grid speciation data...')
        fn = r'Z:\retro_nmvoc_ratio_{}_2000_0.1deg.nc'.format(fn_sector)
        print('Grid speciation file: {}'.format(fn))
        f = dataset.addfile(fn)

        # Create output netcdf file and define dimensions, global attributes and variables
        gattrs = dict(Conventions='CF-1.6', Tools='Created using MeteoInfo')
        dimvars = []
        for var in f.variables:
            if var.ndim == 2:
                dimvar = dataset.DimVariable()
                dimvar.name = var.name
                dimvar.dtype = np.dtype.float
                dimvar.dims = dims
                dimvar.addattr('units', 'g/m2/s')
                dimvars.append(dimvar)
        ncfile = dataset.addfile(outfn, 'c')
        ncfile.nc_define(dims, gattrs, dimvars)

        # Write variable values
        ratio_grid = GridDesc(x_orig=0.05, x_cell=0.1, x_num=3600,
                              y_orig=-89.95, y_cell=0.1, y_num=1800)
        for dimvar in dimvars:
            print(dimvar.name)
            rdata = f[dimvar.name][:]
            rdata = transform(rdata, ratio_grid, model_grid)
            spec_data = hour_data * rdata
            ncfile.write(dimvar.name, spec_data)

        # Close output netcdf file
        f.close()
        ncfile.close()
