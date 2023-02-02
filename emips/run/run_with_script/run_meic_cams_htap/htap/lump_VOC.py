"""
-----HTAP-----
"""
import os
import mipylib.numeric as np
from mipylib import dataset
from mipylib import geolib

import emips
from emips.utils import Sector, SectorEnum
from emips.chem_spec import Pollutant, PollutantEnum
from emips.spatial_alloc import GridDesc

def run(year, month, dir_inter, chem_mech, model_grid):
    """
    Lump VOC species according chemical mechanism.

    :param year: (*int*) Year.
    :param month: (*int*) Month.
    :param dir_inter: (*string*) Data input and output path.
    :param chem_mech: (*ChemicalMechanism*) Chemical mechanism.
    """
    #Set sectors and pollutants
    sectors = [SectorEnum.INDUSTRY, SectorEnum.AGRICULTURE, SectorEnum.ENERGY, \
        SectorEnum.RESIDENTIAL, SectorEnum.TRANSPORT, SectorEnum.SHIPS, \
        SectorEnum.AIR]
    pollutant = PollutantEnum.NMVOC

    #Set dimensions
    tdim = np.dimension(np.arange(24), 'hour')
    ydim = np.dimension(model_grid.y_coord, 'lat', 'Y')
    xdim = np.dimension(model_grid.x_coord, 'lon', 'X')
    dims = [tdim, ydim, xdim]
    
    #Sector loop
    for sector in sectors:
        print(sector.name)
        
        #Set input file
        infn = os.path.join(dir_inter, \
            '{}_emis_{}_{}_{}_hour.nc'.format(pollutant.name, sector.name, year, month))
        if not os.path.exists(infn):
            print('Alarm! File not exists: {}'.format(infn))
            continue
            
        print('Input file: {}'.format(infn))
        #Open input file
        inf = dataset.addfile(infn)
        #Read a reference data
        vname = inf.varnames[4]
        rdata = inf[vname][:]
        rdata[rdata!=np.nan] = 0.
    
        #Set output file
        outfn = os.path.join(dir_inter, \
            '{}_emis_lump_{}_{}_{}_hour.nc'.format(pollutant.name, sector.name, year, month))
        print('Output file: {}'.format(outfn))
        #Create output netcdf file
        ncfile = dataset.addfile(outfn, 'c')
        #Set global attribute
        gattrs = dict(Conventions='CF-1.6', Tools='Created using MeteoInfo')
        #Set variables
        dimvars = []
        for spec in chem_mech.nmvoc_species():
            dimvar = dataset.DimVariable()
            dimvar.name = spec.name
            dimvar.dtype = np.dtype.float
            dimvar.dims = dims
            dimvar.addattr('units', 'mol/m2/s')
            dimvars.append(dimvar)
        #Define dimensions, global attributes and variables
        ncfile.nc_define(dims, gattrs, dimvars)
    
        #Write variable values
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
                print('No RETRO species: {}'.format(dimvar.name))
                ncfile.write(dimvar.name, rdata)
            else:
                print('Convert (g/m2/s) to (mole/m2/s)')
                data = data / spec.molar_mass
                ncfile.write(dimvar.name, data)
    
        #Close output netcdf file
        ncfile.close()
