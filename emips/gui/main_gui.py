# coding=utf-8

import inspect
import os

import java.awt as awt
import javax.swing as swing
import mipylib.dataset as dataset
from com.formdev.flatlaf.extras import FlatSVGIcon
from java.io import File
from javax.imageio import ImageIO

from emips.gui.chemical_panel import ChemicalPanel
from emips.gui.configure import Configure, RunConfigure
from emips.gui.emission_panel import EmissionPanel
from emips.gui.spatial_panel import SpatialPanel
from emips.gui.temporal_panel import TemporalPanel


class MainGUI(swing.JFrame):

    def __init__(self, app):
        super(MainGUI, self).__init__(app)
        self.milab_app = app

        this_file = inspect.getfile(inspect.currentframe())
        self.current_path = os.path.abspath(os.path.dirname(this_file))
        print(self.current_path)

        # Load config file
        fn = os.path.join(self.current_path, 'config.xml')
        self.config = Configure(fn)
        if os.path.isfile(self.config.run_config_path):
            self.run_config = RunConfigure(self.config.run_config_path)
        else:
            self.run_config = None

        self.datafile = None
        self.init_gui()

    def init_gui(self):
        # Add toolbar
        toolbar = swing.JToolBar()
        toolbar.setPreferredSize(awt.Dimension(300, 25))
        self.add(toolbar, awt.BorderLayout.NORTH)
        # Add open file button
        icon = FlatSVGIcon(File(os.path.join(self.current_path, 'image', 'file-open.svg')))
        open_button = swing.JButton(icon, actionPerformed=self.click_openfile)
        toolbar.add(open_button)
        toolbar.addSeparator()

        # Add main panel
        tabbed_pane = swing.JTabbedPane()
        tabbed_pane.setBorder(swing.BorderFactory.createEtchedBorder())
        # Add emission panel        
        self.panel_emission = EmissionPanel(self)
        tabbed_pane.addTab('Emission', self.panel_emission)
        # Add spatial panel
        self.panel_spatial = SpatialPanel(self)
        tabbed_pane.addTab('Spatial', self.panel_spatial)
        # Add temporal panel
        self.panel_temporal = TemporalPanel(self)
        tabbed_pane.addTab('Temporal', self.panel_temporal)
        # Add chemical panel
        self.panel_chemical = ChemicalPanel(self)
        tabbed_pane.addTab('Chemical', self.panel_chemical)

        self.add(tabbed_pane, awt.BorderLayout.CENTER)

        # Add status panel
        panel_status = swing.JPanel()
        panel_status.setLayout(awt.BorderLayout())
        #panel_status.setBorder(swing.BorderFactory.createLoweredBevelBorder())
        # Run configure file
        self.label_run_config_file = swing.JLabel(' ...')
        if self.run_config is not None:
            self.label_run_config_file.setText(' {}'.format(self.run_config.filename))
            
        panel_status.add(self.label_run_config_file, awt.BorderLayout.WEST)

        self.add(panel_status, awt.BorderLayout.SOUTH)

        self.pack()

        # Set main form
        icon = ImageIO.read(File(os.path.join(self.current_path, 'image', 'factory_24.png')))
        self.title = 'EMIPS'
        self.setIconImage(icon)
        self.defaultCloseOperation = swing.JFrame.DISPOSE_ON_CLOSE
        self.windowClosing = self.form_closing

    def upate_run_configure(self):
        """
        Update run configure file.
        """
        self.emission_module = self.run_config.load_emission_module()
        self.label_run_config_file.setText(' {}'.format(self.run_config.filename))
        self.panel_emission.update_run_configure(self.run_config)
        self.panel_spatial.update_run_configure(self.run_config)

    def click_openfile(self, e):
        """
        Open run configure file.
        """
        if self.run_config is None:
            fc = swing.JFileChooser()
        else:
            fc = swing.JFileChooser(self.run_config.filename)
        r = fc.showOpenDialog(self)
        if r == swing.JFileChooser.APPROVE_OPTION:
            f = fc.getSelectedFile()
            print(f)
            self.config.run_config_path = f.path
            self.run_config = RunConfigure(f.path)
            self.update_run_configure()

    def form_closing(self, e):
        self.config.save_configure()
        self.dispose()

    def click_exit(self, e):
        self.dispose()


if __name__ == '__main__':
    frm = MainGUI(None)
    frm.pack()
    frm.locationRelativeTo = None
    frm.visible = True
