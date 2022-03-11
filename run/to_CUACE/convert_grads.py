"""
Convert netcdf model-ready emission file to GrADS data format for
GRAPES/CUACE model
"""

#Import from emips package
import emips
from emips.utils import Sector, SectorEnum
from emips.spatial_alloc import GridDesc
from emips.chem_spec import RADM2

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

#Set dimension length
xn = 1440
yn = 720
tn = 25    # 0 - 24 hour

#Set year month
year = 2016
for month in [6, 7, 8, 9, 10, 11, 12]:
    print('**************')
    print('Month: {}'.format(month))
    print('**************')

    #Set directory
    dir_data = r'E:\emips_data\merge\global_0.25'
    dir_data = os.path.join(dir_data, str(year), '{}{:>02d}'.format(year, month))
    dir_out = r'N:\Emis_model\GRAPES_CUACE\global_0.25'
    dir_out = os.path.join(dir_out, str(year), '{}{:>02d}'.format(year, month))
    if not os.path.exists(dir_out):
        os.makedirs(dir_out)
    print('------------------Filepath------------------')
    print('dir_data: {}\ndir_out: {}'.format(dir_data, dir_out))
    #Loop
    for emis_type, sectors in emis_cuace.iteritems():
        print(emis_type)
        
        #set output binary dta file
        outfn = os.path.join(dir_out, 'emis_{}_{}_{}.grd'.format(year, \
            month, emis_type))
        outer = bincreate(outfn)
    
        #Loop time number
        for t in range(tn):
            print('Time number: {}'.format(t))
            if t == tn - 1:
                t = 0
            #Loop species
            for species in all_species:
                #print(species)
                data = None
                #Loop sectors
                for sector in sectors:
                    fn = os.path.join(dir_data, 'emis_{}_{}_{}_hour.nc'.format(sector.name, year, month))
                    #print('\t{}'.format(fn))
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
                binwrite(outer, data.astype('float'), byteorder='little_endian', sequential=True)
        outer.close()

print('Data convert completed!!!')