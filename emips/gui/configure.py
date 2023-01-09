import xml.dom.minidom as minidom
from emips.spatial_alloc import GridDesc
from mipylib import geolib
import os
import sys
import importlib


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
        self.run_config_path = run_configure.getAttribute('FilePath')

    def save_configure(self):
        doc = minidom.Document()

        # generate the setting
        root = doc.createElement('EMIPS')
        doc.appendChild(root)

        # The directories
        run_configure = doc.createElement('RunConfigure')
        run_configure.setAttribute('FilePath', self.run_config_path)
        root.appendChild(run_configure)

        # Write config file
        with open(self.filename, 'w') as f:
            f.write(doc.toprettyxml(indent='\t', encoding='utf-8'))


class RunConfigure(object):

    def __init__(self, filename):
        self.filename = filename

        self.emission_read_file = None
        self.spatial_model_grid = None
        self.temporal_prof_file = None
        self.temporal_ref_file = None
        self.chemical_prof_file = None
        self.chemical_ref_file = None
        self.use_grid_spec_file = None
        self.run_output_dir = None
        self.vertical_prof_file = None

        self.emission_module = None

        self.load_configure(filename)
        self.load_emission_module()

    def load_configure(self, filename):
        dom = minidom.parse(filename)
        root = dom.documentElement

        # Emission
        emission = root.getElementsByTagName('Emission')[0]
        emission_read = emission.getElementsByTagName('Read')[0]
        self.emission_read_file = emission_read.getAttribute('ScriptFile')

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
        self.use_grid_spec_file = True if use_gsf == "True" else False

        # Vertical
        vertical = root.getElementsByTagName('Vertical')[0]
        vfile_name = vertical.getElementsByTagName('FileName')[0]
        self.vertical_prof_file = vfile_name.getAttribute('Profile')

        # Run
        run = root.getElementsByTagName("Run")[0]
        output = run.getElementsByTagName("Output")[0]
        self.run_output_dir = output.getAttribute("Directory")

    def load_emission_module(self):
        if os.path.isfile(self.emission_read_file):
            run_path = os.path.dirname(self.emission_read_file)
            if run_path not in sys.path:
                sys.path.append(run_path)
            run_module = os.path.basename(self.emission_read_file)
            run_module = os.path.splitext(run_module)[0]
            self.emission_module = importlib.import_module(run_module)
        else:
            print('Read emission script file not exist! {}'.format(self.emission_read_file))

    def save_configure(self, filename=None):
        doc = minidom.Document()

        # generate the setting
        root = doc.createElement('EMIPS_Run')
        doc.appendChild(root)

        # Emission
        emission = doc.createElement('Emission')
        emission_read = doc.createElement('Read')
        emission_read.setAttribute('ScriptFile', self.emission_read_file)
        emission.appendChild(emission_read)
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
        file_name.setAttribute('Profile', self.temporal_prof_file)
        file_name.setAttribute('Reference', self.temporal_ref_file)
        temporal.appendChild(file_name)
        root.appendChild(temporal)

        # Chemical
        chemical = doc.createElement("Chemical")
        cfiles = doc.createElement("FileName")
        cfiles.setAttribute("Profile", self.chemical_prof_file)
        cfiles.setAttribute("Reference", self.chemical_ref_file)
        chemical.appendChild(cfiles)
        grid_spec = doc.createElement("GridSpeciation")
        grid_spec.setAttribute("Enable", "True" if self.use_grid_spec_file else "False")
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