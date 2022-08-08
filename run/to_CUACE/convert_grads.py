#Import from emips package
import emips
from emips.utils import Sector, SectorEnum
from emips.spatial_alloc import GridDesc
from emips.chem_spec import RADM2
from mipylib import dataset

#Set emission low, poi, pow
emis_cuace = {}
emis_cuace['low'] = [SectorEnum.AGRICULTURE, SectorEnum.RESIDENTIAL, \
    SectorEnum.TRANSPORT, SectorEnum.SHIPS]
emis_cuace['poi'] = [SectorEnum.INDUSTRY]
emis_cuace['pow'] = [SectorEnum.ENERGY]
emis_cuace['air'] = [SectorEnum.AIR]

#Get RADM2 emission species
all_species = [RADM2.CO, RADM2.NO, RADM2.NO2, RADM2.ALD, RADM2.CH4, \
    RADM2.CSL, RADM2.ETH, RADM2.HC3, RADM2.HC5, RADM2.HC8, RADM2.HCHO, \
    RADM2.ISOP, RADM2.KET, RADM2.NR, RADM2.OL2, RADM2.OLE, RADM2.OLI, \
    RADM2.OLT, RADM2.ORA2, RADM2.PAR, RADM2.TERP, RADM2.TOL, RADM2.XYL, \
    RADM2.NH3, RADM2.SO2, RADM2.SULF, RADM2.PEC, RADM2.PMFINE, \
    RADM2.PNO3, RADM2.POA, RADM2.PSO4, RADM2.PMC]

#Set time dimension of output file.
tn = 25    # 0 - 24 hour
def run(year, months, dir_data, dir_out, xn, yn):
    """
    Convert netcdf model-ready emission file to GrADS data 
    format for CUACE model.
    
    :param year: (*int*) Year.
    :param months: (*list*) List of months.
    :param dir_data: (*string*) The directory where netcdf data is stored.
    :param dir_out: (*string*) The directory where GrADS data is writed.
    :param xn: (*int*) x-Dimension of output files.
    :param yn: (*int*) y-Dimension of output files.
    """
    for month in months:
        print('**************')
        print('Month: {}'.format(month))
        print('**************')
    
        #Set directory for input and output files
        dir_data = r'E:\test'
        dir_data = os.path.join(dir_data, str(year), '{}{:>02d}'.format(year, month))
        dir_out = r'E:\test'
        dir_out = os.path.join(dir_out, str(year), '{}{:>02d}'.format(year, month))
        if not os.path.exists(dir_out):
            os.makedirs(dir_out)
        print('------------------Filepath------------------')
        print('dir_data: {}\ndir_out: {}'.format(dir_data, dir_out))
        #Loop
        for emis_type, sectors in emis_cuace.iteritems():
            print(emis_type, sectors)
            
            #set output binary dta file
            outfn = os.path.join(dir_out, 'emis_{}_{}_{}.grd'.format(year, \
                month, emis_type))
            outer = dataset.bincreate(outfn)
        
            #Loop time number
            for t in range(tn):
                print('Time number: {}'.format(t))
                if t == tn - 1:
                    t = 0
                #Loop species
                for species in all_species:
                    data = None
                    #Loop sectors
                    for sector in sectors:
                        fn = os.path.join(dir_data, 'emis_{}_{}_{}_hour.nc'.format(sector.name, year, month))
                        f_in = addfile(fn)
                        if species.name in f_in.varnames():
                            dd = f_in[species.name][t]
                            if dd.sum() == 0:
                                continue
                            if dd.contains_nan():
                                dd[dd==nan] = 0
                            if data is None:
                                data = dd
                            else:
    							data = data + dd
    					f_in.close()
                    if data is None:
                        print('Is None: {}'.format(species))
                        data = zeros((yn, xn))
                    dataset.binwrite(outer, data.astype('float'), byteorder='little_endian', sequential=True)
            outer.close()      
print('#########################')
print('Data convert completed!!!')
print('#########################')