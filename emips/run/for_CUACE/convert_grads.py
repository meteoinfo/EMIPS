import os

from mipylib import dataset
from mipylib import numeric

from emips.chem_spec import RADM2
from emips.utils import SectorEnum

# Set emission low, poi, pow
emis_cuace = {}
emis_cuace['low'] = [SectorEnum.AGRICULTURE, SectorEnum.RESIDENTIAL,
                     SectorEnum.TRANSPORT, SectorEnum.SHIPS]
emis_cuace['poi'] = [SectorEnum.INDUSTRY]
emis_cuace['pow'] = [SectorEnum.ENERGY]
emis_cuace['air'] = [SectorEnum.AIR]

# Get RADM2 emission species
all_species = [RADM2.CO, RADM2.NO, RADM2.NO2, RADM2.ALD, RADM2.CH4,
               RADM2.CSL, RADM2.ETH, RADM2.HC3, RADM2.HC5, RADM2.HC8, RADM2.HCHO,
               RADM2.ISOP, RADM2.KET, RADM2.NR, RADM2.OL2, RADM2.OLE, RADM2.OLI,
               RADM2.OLT, RADM2.ORA2, RADM2.PAR, RADM2.TERP, RADM2.TOL, RADM2.XYL,
               RADM2.NH3, RADM2.SO2, RADM2.SULF, RADM2.PEC, RADM2.PMFINE,
               RADM2.PNO3, RADM2.POA, RADM2.PSO4, RADM2.PMC]

# Set time dimension of output file.
tn = 25  # 0 - 24 hour


def run(year, months, dir_in, dir_out, xn, yn):
    """
    Convert netcdf model-ready emission file to GrADS data 
    format for CUACE model.
    
    :param year: (*int*) Year.
    :param months: (*list*) List of months.
    :param dir_data: (*string*) The directory where netcdf data is stored.
    :param dir_out: (*string*) The directory where GrADS data is writed.
    :param xn: (*int*) x-dimension of output files.
    :param yn: (*int*) y-dimension of output files.
    """
    for month in months:
        print('**************')
        print('Month: {}'.format(month))
        print('**************')

        # Set directory for input and output files
        dir_in = os.path.join(dir_in, str(year), '{}{:>02d}'.format(year, month))
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
                        f_in = dataset.addfile(fn)
                        if species.name in f_in.varnames:
                            dd = f_in[species.name][t]
                            if dd.sum() == 0:
                                continue
                            if dd.contains_nan():
                                dd[dd == numeric.nan] = 0
                            if data is None:
                                data = dd
                            else:
                                data = data + dd
                        f_in.close()
                    if data is None:
                        print('Is None: {}'.format(species))
                        data = numeric.zeros((yn, xn))
                    # Check the dimensions of the input and output files
                    if data.shape[0] != yn or data.shape[1] != xn:
                        print('The dimensions of input data and output data do not match!!!')
                        os.system("pause")

                    dataset.binwrite(outer, data.astype('float'), byteorder='little_endian', sequential=True)
            outer.close()
    print('#########################')
    print('Data convert completed!!!')
    print('#########################')


if __name__ == '__main__':
    import time

    time_start = time.time()

    # Settings
    year = 2017
    months = [1]
    dir_in = r'G:\test'
    dir_out = r'G:\test'
    xn = 751
    yn = 501
    run(year, months, dir_in, dir_out, xn, yn)

    time_end = time.time()
    time = (time_end - time_start) / 60
    print('Time: {:.2f}min'.format(time))
