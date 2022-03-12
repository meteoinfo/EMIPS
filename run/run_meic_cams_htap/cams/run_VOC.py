#Import
import os
import mipylib.numeric as np
from mipylib import dataset
from mipylib import geolib

import emips
from emips.utils import Sector, Units, Weight, Area, Period, emis_util, \
    SectorEnum
from emips.chem_spec import Pollutant, Species, PollutantEnum, SpeciesEnum
from emips.spatial_alloc import GridDesc, transform
from emips import ge_data_dir

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
    #Set profile files
    temp_profile_fn = os.path.join(ge_data_dir, 'amptpro.m3.default.us+can.txt')
    temp_ref_fn = os.path.join(ge_data_dir, 'amptref.m3.us+can.cair.txt')
    
    #Set data dimensions   
    tdim = np.dimension(np.arange(24), 'hour')
    ydim = np.dimension(model_grid.y_coord, 'lat', 'Y')
    xdim = np.dimension(model_grid.x_coord, 'lon', 'X')
    dims = [tdim, ydim, xdim]
    
    #Set sectors and pollutants
    sectors = [SectorEnum.INDUSTRY, SectorEnum.AGRICULTURE, SectorEnum.ENERGY, \
        SectorEnum.RESIDENTIAL, SectorEnum.TRANSPORT, SectorEnum.AIR, SectorEnum.SHIPS]
    fn_sectors = ['inc', 'agr','pow','res','tra','tra','tra']
    pollutant = PollutantEnum.NMVOC
    pollutant.units = Units(Weight.KG, Area.M2, Period.SECOND)
    
    #Loop
    for sector,fn_sector in zip(sectors,fn_sectors):
        print('####################################')
        print(sector)
        print('####################################')
    
        #Get SCC
        scc = emis_util.get_scc(sector)
    
        print('Read emission data...')
        emis_data = emission.read_emis(sector, pollutant, year, month)    
        if emis_data is None:    #No emission of NMVOC for some sectors
            continue
        #Longitude pivot to global grid data from 0 longitude
        emis_data, emis_grid = emission.lonpivot(emis_data, 0, emission.get_emis_grid(sector))
        #Expand grid to aviod NaN interpolation values
        emis_data, emis_grid = emission.grid_expand(emis_data, emis_grid)
        if sector == SectorEnum.SHIPS:
                emis_data = emis_data[::-1, :]
        #### Spatial allocation        
        print('Spatial allocation of emission grid to model grid...')
        emis_data = transform(emis_data, emis_grid, model_grid)
        
        #### Temporal allocation
        print('Temporal allocation...')
        month_profile, week_profile, diurnal_profile, diurnal_profile_we = \
            emips.temp_alloc.read_file(temp_ref_fn, temp_profile_fn, scc)
        print('To (kg/m2/month)')
        emis_data = emis_data * 3600 * 24 * emis_util.get_month_days(year, month)
        print('To daily emission (kg/m2/day)...')
        weekday_data, weekend_data = emips.temp_alloc.week_allocation(emis_data, week_profile, year, month)
        print('To hourly emission (g/m2/s)...')
        hour_data = emips.temp_alloc.diurnal_allocation(weekday_data, diurnal_profile) / 3.6
    
        #### Chemical speciation
        print('Chemical speciation...')
        #### Set output netcdf file path
        outfn = os.path.join(dir_inter, \
            '{}_emis_{}_{}_{}_hour.nc'.format(pollutant.name, sector.name, year, month))
        print('Output file: {}'.format(outfn))
    
        print('Set grid speciation data...')
        fn = r'Z:\chen\MEIC_data\Grid_speciation_data(VOC)\retro_nmvoc_ratio_{}_2000_0.1deg.nc'.format(fn_sector)
        print('Grid speciation file: {}'.format(fn))
        f = dataset.addfile(fn)
    
        #Create output netcdf file and define dimensions, global attributes and variables
        gattrs = dict(Conventions='CF-1.6', Tools='Created using MeteoInfo')
        dimvars = []
        for var in f.variables():
            if var.ndim == 2:
                dimvar = dataset.DimVariable()
                dimvar.name = var.name
                dimvar.dtype = np.dtype.float
                dimvar.dims = dims
                dimvar.addattr('units', 'g/m2/s')
                dimvars.append(dimvar)
        ncfile = dataset.addfile(outfn, 'c')
        ncfile.nc_define(dims, gattrs, dimvars)     
    
        #Write variable values
        proj = geolib.projinfo()
        ratio_grid = GridDesc(proj, x_orig=0.05, x_cell=0.1, x_num=3600,
            y_orig=-89.95, y_cell=0.1, y_num=1800)
        for dimvar in dimvars:
            print(dimvar.name)
            rdata = f[dimvar.name][:]
            rdata, rgrid = emission.grid_expand(rdata, ratio_grid)
            rdata = transform(rdata, rgrid, model_grid)
            spec_data = hour_data * rdata
            ncfile.write(dimvar.name, spec_data)
            
        #Close output netcdf file
        ncfile.close()
    
if __name__ == '__main__':
    #Set current working directory
    from inspect import getsourcefile
    dir_run = os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))
    if not dir_run in sys.path:
        sys.path.append(dir_run)  
    import emission_cams_year as emission

    #Set year, month and output data path
    year = 2017
    month = 1
    dir_inter = r'F:\emips_data\CAMS\2017\{}{:>02d}'.format(year, month)
    if not os.path.exists(dir_inter):
        os.mkdir(dir_inter)

    #Set model grids
    proj = geolib.projinfo()
    model_grid = GridDesc(proj, x_orig=0., x_cell=0.25, x_num=1440,
        y_orig=-89.875, y_cell=0.25, y_num=720)
        
    #Run
    run(year, month, dir_inter, emission, model_grid)