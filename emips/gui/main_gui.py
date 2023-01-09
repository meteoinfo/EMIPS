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
from emips.gui.vertical_panel import VerticalPanel
from emips.gui.run_panel import RunPanel


class MainGUI(swing.JFrame):

    def __init__(self, app):
        super(MainGUI, self).__init__()
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
            self.config.run_config_path = os.path.join(self.current_path, "run_config.xml")
            self.run_config = RunConfigure(self.config.run_config_path)

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
        open_button.setToolTipText("Open configure file")
        toolbar.add(open_button)
        toolbar.addSeparator()
        # Add save file button
        icon = FlatSVGIcon(File(os.path.join(self.current_path, 'image', 'file-save.svg')))
        save_button = swing.JButton(icon, actionPerformed=self.click_savefile)
        save_button.setToolTipText("Save configure file")
        toolbar.add(save_button)
        # Add save as file button
        icon = FlatSVGIcon(File(os.path.join(self.current_path, 'image', 'file-save-as.svg')))
        save_as_button = swing.JButton(icon, actionPerformed=self.click_saveasfile)
        save_as_button.setToolTipText("Save as configure file")
        toolbar.add(save_as_button)
        toolbar.addSeparator()
        # Add about button
        icon = FlatSVGIcon(File(os.path.join(self.current_path, 'image', 'information.svg')))
        about_button = swing.JButton(icon, actionPerformed=self.click_about)
        about_button.setToolTipText("About EMIPS")
        toolbar.add(about_button)

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
        # Add vertical panel
        self.panel_vertical = VerticalPanel(self)
        tabbed_pane.addTab('Vertical', self.panel_vertical)
        # Add run panel
        self.panel_run = RunPanel(self)
        tabbed_pane.addTab("Run", self.panel_run)

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
        self.label_run_config_file.setText(' {}'.format(self.run_config.filename))
        self.panel_emission.update_run_configure(self.run_config)
        self.panel_spatial.update_run_configure(self.run_config)

    def update_emission_module(self):
        """
        Update emission module.
        """
        self.panel_spatial.update_emission_module()

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

    def click_savefile(self, e):
        """
        Save run configure file.
        """
        self.config.save_configure()
        self.run_config.save_configure()

    def click_saveasfile(self, e):
        """
        Save as run configure file
        """
        print("Save as run configure file")
        fc = swing.JFileChooser()
        fc.setSelectedFile(File(self.run_config.filename))
        r = fc.showSaveDialog(self)
        if r == swing.JFileChooser.APPROVE_OPTION:
            f = fc.getSelectedFile()
            self.run_config.save_configure(f.path)
            self.run_config.filename = f.path
            self.config.run_config_path = f.path
            self.label_run_config_file.setText(' {}'.format(self.run_config.filename))

    def click_about(self, e):
        pass

    def form_closing(self, e):
        self.config.save_configure()
        self.dispose()

    def click_exit(self, e):
        self.dispose()


if __name__ == '__main__':
    frm = MainGUI(milapp)
    frm.pack()
    frm.locationRelativeTo = None
    frm.visible = True
