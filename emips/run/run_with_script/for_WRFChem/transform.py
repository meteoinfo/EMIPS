from emips.spatial_alloc import GridDesc
from collections import OrderedDict
from mipylib import dataset
import mipylib.numeric as np

def run(year, month, dir_inter, model_grid, out_species, out_species_aer, z):
    """
    Distribution of particulate matter and change unit.

    :param year: (*int*) Year.
    :param month: (*int*) Month.
    :param dir_inter: (*string*) The directory where data is stored.
    :param model_grid: (*GridDesc*) Model data grid describe.
    :param out_species: (*list*) The name of the output species(gases and aerosol).
    :param out_species_aer: (*list*) The name of the output species(aerosol).
    :param z: (*int*) The zdim of the output data.
    """
    print('Add input file...')
    fn_in = dir_inter + '\emis_{}_{}_hour.nc'.format(year, month)
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
