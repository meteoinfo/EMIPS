import xml.dom.minidom as minidom
from emips.spatial_alloc import GridDesc
from emips.utils import SectorEnum, Units, Weight, Area, Period
from emips.chem_spec import PollutantEnum, ChemMechEnum
from mipylib import geolib
import os
import sys
import importlib
from inspect import getsourcefile

dir_configure = os.path.dirname(os.path.abspath(getsourcefile(lambda: 0)))


class Configure(object):

    def __init__(self, filename):
        self.filename = filename
        self.run_config_path = None

        self.load_configure(filename)

    def load_configure(self, filename):
        dom = minidom.parse(filename)
        root = dom.documentElement

        # Load path
        run_configure = root.getElementsByTagName('RunConfigure')[0]
        rel_path = run_configure.getAttribute('FilePath')
        self.run_config_path = os.path.abspath(os.path.join(dir_configure, rel_path))

    def save_configure(self):
        doc = minidom.Document()

        # generate the setting
        root = doc.createElement('EMIPS')
        doc.appendChild(root)

        # The directories
        run_configure = doc.createElement('RunConfigure')
        rel_path = os.path.relpath(self.run_config_path, dir_configure)
        run_configure.setAttribute('FilePath', rel_path)
        root.appendChild(run_configure)

        # Write config file
        with open(self.filename, 'w') as f:
            f.write(doc.toprettyxml(indent='\t', encoding='utf-8'))


class RunConfigure(object):

    def __init__(self, filename):
        self.filename = filename

        self.emission_read_file = None
        self.emission_sectors = []
        self.emission_pollutants = []
        self.emission_year = None
        self.emission_month = None

        self.spatial_model_grid = None

        self.temporal_prof_file = None
        self.temporal_ref_file = None

        self.chemical_prof_file = None
        self.chemical_ref_file = None
        self.voc_use_grid_spec = None
        self.grid_spec_read_file = None
        self.chemical_mechanism = None

        self.vertical_prof_file = None

        self.run_output_dir = None
        self.is_run_vertical = None
        self.post_process_file = None

        self.emission_module = None
        self.grid_spec_module = None
        self.post_process_module = None

        self.load_configure(filename)
        self.load_emission_module()
        self.load_grid_spec_module()
        self.load_post_process_module()

    def load_configure(self, filename):
        dom = minidom.parse(filename)
        root = dom.documentElement

        # Emission
        emission = root.getElementsByTagName('Emission')[0]
        emission_read = emission.getElementsByTagName('Read')[0]
        self.emission_read_file = os.path.abspath(os.path.join(dir_configure, emission_read.getAttribute('ScriptFile')))
        emission_sectors = emission.getElementsByTagName("Sectors")[0]
        sector_list = emission_sectors.getElementsByTagName("Sector")
        for sector in sector_list:
            name = sector.getAttribute("Name")
            scc = sector.getAttribute("SCC")
            self.emission_sectors.append(SectorEnum.of(name, scc))
        emission_pollutants = emission.getElementsByTagName("Pollutants")[0]
        elem_pollutants = emission_pollutants.getElementsByTagName("Pollutant")
        for elem_pollutant in elem_pollutants:
            name = elem_pollutant.getAttribute("Name")
            elem_units = elem_pollutant.getElementsByTagName("Units")[0]
            weight = elem_units.getAttribute("Weight")
            area = elem_units.getAttribute("Area")
            period = elem_units.getAttribute("Period")
            units = Units(Weight[weight], Area[area], Period[period])
            self.emission_pollutants.append(PollutantEnum.of(name, units))
        emission_time = emission.getElementsByTagName("Time")[0]
        self.emission_year = emission_time.getAttribute("Year")
        self.emission_month = emission_time.getAttribute("Month")

        # Spatial
        spatial = root.getElementsByTagName('Spatial')[0]
        model_grid = spatial.getElementsByTagName('ModelGrid')[0]
        proj_str = model_grid.getAttribute('Projection')
        proj = geolib.projinfo(proj_str)
        x_origin = float(model_grid.getAttribute('XOrigin'))
        x_cell = float(model_grid.getAttribute('XCell'))
        x_num = int(model_grid.getAttribute('XNumber'))
        y_origin = float(model_grid.getAttribute('YOrigin'))
        y_cell = float(model_grid.getAttribute('YCell'))
        y_num = int(model_grid.getAttribute('YNumber'))
        self.spatial_model_grid = GridDesc(proj=proj, x_orig=x_origin, x_cell=x_cell, x_num=x_num,
                                           y_orig=y_origin, y_cell=y_cell, y_num=y_num)

        # Temporal
        temporal = root.getElementsByTagName('Temporal')[0]
        file_name = temporal.getElementsByTagName('FileName')[0]
        self.temporal_prof_file = file_name.getAttribute('Profile')
        self.temporal_ref_file = file_name.getAttribute('Reference')

        # Chemical
        chemical = root.getElementsByTagName("Chemical")[0]
        cfiles = chemical.getElementsByTagName("FileName")[0]
        self.chemical_prof_file = cfiles.getAttribute("Profile")
        self.chemical_ref_file = cfiles.getAttribute("Reference")
        grid_spec = chemical.getElementsByTagName("GridSpeciation")[0]
        use_gsf = grid_spec.getAttribute("Enable")
        self.voc_use_grid_spec = True if use_gsf == "True" else False
        grid_spec_read = grid_spec.getElementsByTagName("Read")[0]
        self.grid_spec_read_file = os.path.abspath(os.path.join(dir_configure,grid_spec_read.getAttribute("ScriptFile")))
        grid_spec_mech = grid_spec.getElementsByTagName("ChemMech")[0]
        self.chemical_mechanism = ChemMechEnum[grid_spec_mech.getAttribute("name")]

        # Vertical
        vertical = root.getElementsByTagName('Vertical')[0]
        vfile_name = vertical.getElementsByTagName('FileName')[0]
        self.vertical_prof_file = vfile_name.getAttribute('Profile')

        # Run
        run = root.getElementsByTagName("Run")[0]
        output = run.getElementsByTagName("Output")[0]
        self.run_output_dir = output.getAttribute("Directory")
        steps = run.getElementsByTagName("Steps")[0]
        self.is_run_vertical = True if steps.getAttribute("RunVertical") == "True" else False
        post_process = run.getElementsByTagName("PostProcess")[0]
        self.post_process_file = os.path.abspath(os.path.join(dir_configure, post_process.getAttribute("ScriptFile")))

    def load_emission_module(self):
        emission_read_file = os.path.abspath(os.path.join(dir_configure, os.pardir, self.emission_read_file))
        if os.path.isfile(emission_read_file):
            run_path = os.path.dirname(emission_read_file)
            if run_path not in sys.path:
                sys.path.append(run_path)
            run_module = os.path.basename(emission_read_file)
            run_module = os.path.splitext(run_module)[0]
            self.emission_module = importlib.import_module(run_module)
        else:
            print('Read emission script file not exist!\n {}'.format(emission_read_file))

    def load_grid_spec_module(self):
        grid_spec_read_file = os.path.abspath(os.path.join(dir_configure, os.pardir, self.grid_spec_read_file))
        if os.path.isfile(grid_spec_read_file):
            run_path = os.path.dirname(grid_spec_read_file)
            if run_path not in sys.path:
                sys.path.append(run_path)
            run_module = os.path.basename(grid_spec_read_file)
            run_module = os.path.splitext(run_module)[0]
            self.grid_spec_module = importlib.import_module(run_module)
        else:
            print('Read grid speciation script file not exist!\n {}'.format(grid_spec_read_file))

    def load_post_process_module(self):
        if os.path.isfile(self.post_process_file):
            run_path = os.path.dirname(self.post_process_file)
            if run_path not in sys.path:
                sys.path.append(run_path)
            run_module = os.path.basename(self.post_process_file)
            run_module = os.path.splitext(run_module)[0]
            self.post_process_module = importlib.import_module(run_module)
        else:
            print('Post process script file not exist!\n {}'.format(self.post_process_file))

    def save_configure(self, filename=None):
        doc = minidom.Document()

        # generate the setting
        root = doc.createElement('EMIPS_Run')
        doc.appendChild(root)

        # Emission
        emission = doc.createElement('Emission')
        emission_read = doc.createElement('Read')
        emission_read.setAttribute('ScriptFile', os.path.relpath(self.emission_read_file, dir_configure))
        emission.appendChild(emission_read)

        elem_sectors = doc.createElement("Sectors")
        for sector in self.emission_sectors:
            elem_sector = doc.createElement("Sector")
            elem_sector.setAttribute("Name", sector.name)
            elem_sector.setAttribute("SCC", sector.scc)
            elem_sectors.appendChild(elem_sector)
        emission.appendChild(elem_sectors)

        elem_pollutants = doc.createElement("Pollutants")
        for pollutant in self.emission_pollutants:
            elem_pollutant = doc.createElement("Pollutant")
            elem_pollutant.setAttribute("Name", pollutant.name)
            elem_units = doc.createElement("Units")
            elem_units.setAttribute("Weight", pollutant.units.weight.name)
            elem_units.setAttribute("Area", pollutant.units.area.name)
            elem_units.setAttribute("Period", pollutant.units.period.name)
            elem_pollutant.appendChild(elem_units)
            elem_pollutants.appendChild(elem_pollutant)
        emission.appendChild(elem_pollutants)

        elem_time = doc.createElement("Time")
        elem_time.setAttribute("Year", str(self.emission_year))
        elem_time.setAttribute("Month", str(self.emission_month))
        emission.appendChild(elem_time)
        root.appendChild(emission)

        # Spatial
        spatial = doc.createElement('Spatial')
        model_grid = doc.createElement('ModelGrid')
        model_grid.setAttribute('Projection', self.spatial_model_grid.proj.toProj4String())
        model_grid.setAttribute('XOrigin', str(self.spatial_model_grid.x_orig))
        model_grid.setAttribute('XCell', str(self.spatial_model_grid.x_cell))
        model_grid.setAttribute('XNumber', str(self.spatial_model_grid.x_num))
        model_grid.setAttribute('YOrigin', str(self.spatial_model_grid.y_orig))
        model_grid.setAttribute('YCell', str(self.spatial_model_grid.y_cell))
        model_grid.setAttribute('YNumber', str(self.spatial_model_grid.y_num))
        spatial.appendChild(model_grid)
        root.appendChild(spatial)

        # Temporal
        temporal = doc.createElement('Temporal')
        file_name = doc.createElement('FileName')
        file_name.setAttribute('Profile', os.path.basename(self.temporal_prof_file))
        file_name.setAttribute('Reference', os.path.basename(self.temporal_ref_file))
        temporal.appendChild(file_name)
        root.appendChild(temporal)

        # Chemical
        chemical = doc.createElement("Chemical")
        cfiles = doc.createElement("FileName")
        cfiles.setAttribute("Profile", os.path.basename(self.chemical_prof_file))
        cfiles.setAttribute("Reference", os.path.basename(self.chemical_ref_file))
        chemical.appendChild(cfiles)
        grid_spec = doc.createElement("GridSpeciation")
        grid_spec.setAttribute("Enable", "True" if self.voc_use_grid_spec else "False")
        grid_spec_read = doc.createElement("Read")
        grid_spec_read.setAttribute("ScriptFile", os.path.relpath(self.grid_spec_read_file, dir_configure))
        grid_spec.appendChild(grid_spec_read)
        grid_spec_mech = doc.createElement("ChemMech")
        grid_spec_mech.setAttribute("name", self.chemical_mechanism.name)
        grid_spec.appendChild(grid_spec_mech)
        chemical.appendChild(grid_spec)
        root.appendChild(chemical)

        # Vertical
        vertical = doc.createElement('Vertical')
        vfile_name = doc.createElement('FileName')
        vfile_name.setAttribute('Profile', self.vertical_prof_file)
        vertical.appendChild(vfile_name)
        root.appendChild(vertical)

        # Run
        run = doc.createElement("Run")
        output = doc.createElement("Output")
        output.setAttribute("Directory", self.run_output_dir)
        run.appendChild(output)
        steps = doc.createElement("Steps")
        steps.setAttribute("RunVertical", "True" if self.is_run_vertical else "False")
        run.appendChild(steps)
        post_process = doc.createElement("PostProcess")
        post_process.setAttribute("ScriptFile", os.path.relpath(self.post_process_file, dir_configure))
        run.appendChild(post_process)
        root.appendChild(run)

        # Write config file
        if filename is None:
            filename = self.filename
            
        with open(filename, 'w') as f:
            f.write(doc.toprettyxml(indent='\t', encoding='utf-8'))


if __name__ == '__main__':
    fn = r'D:\MyProgram\java\MeteoInfoDev\toolbox\EMIPS\emips\gui\config.xml'
    config = Configure(fn)
    run_fn = config.run_config_path
    run_config = RunConfigure(run_fn)
    ofn = 'D:/Temp/test/test_run_config.xml'
    run_config.save_configure(ofn)
