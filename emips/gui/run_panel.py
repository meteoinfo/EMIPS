# coding=utf-8

import javax.swing as swing
import java.awt as awt
from com.formdev.flatlaf.extras import FlatSVGIcon
from java.io import File
from java.util.concurrent import ExecutionException
from mipylib import plotlib as plt
from mipylib import numeric as np

import os
from emips.utils import Units, Weight, Area, Period
from emips import ge_data_dir
from emips.spatial_alloc import transform
from emips import temp_alloc
from emips.run import run_pollutant


class RunPanel(swing.JPanel):

    def __init__(self, frm_main):
        super(RunPanel, self).__init__()

        self.frm_main = frm_main
        self.run_config = frm_main.run_config
        self.init_gui()
        if self.run_config is not None:
            self.update_run_configure(self.run_config)

        self.temp_data = None

    def init_gui(self):
        # Output directory
        label_output_dir = swing.JLabel("Output directory:")
        self.text_output_dir = swing.JTextField("")        
        icon = FlatSVGIcon(File(os.path.join(self.frm_main.current_path, 'image', 'file-open.svg')))
        button_output_dir = swing.JButton("", icon)
        button_output_dir.actionPerformed = self.click_output_dir
    
        # Sector choose
        label_sector = swing.JLabel("Sector:")
        self.combobox_sector = swing.JComboBox()

        # Pollutant choose
        label_pollutant = swing.JLabel("Pollutant:")
        self.combobox_pollutant = swing.JComboBox()

        # Test step by step
        panel_test = swing.JPanel()
        border = swing.BorderFactory.createTitledBorder("Test step by step")
        panel_test.setBorder(border)
        # Spatial
        button_spatial = swing.JButton("Spatial")
        button_spatial.actionPerformed = self.click_spatial
        # Temporal
        button_temporal = swing.JButton("Temporal")
        button_temporal.actionPerformed = self.click_temporal
        # Chemical
        button_chemical = swing.JButton("Chemical")
        button_chemical.actionPerformed = self.click_chemical
        # Vertical
        button_vertical = swing.JButton("Vertical")
        button_vertical.actionPerformed = self.click_vertical
        # Test layout
        layout = swing.GroupLayout(panel_test)
        panel_test.setLayout(layout)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)
        layout.setHorizontalGroup(
            layout.createParallelGroup()
                .addGroup(layout.createSequentialGroup()
                    .addComponent(button_spatial)
                    .addComponent(button_temporal)
                    .addComponent(button_chemical)
                    .addComponent(button_vertical))
        )
        layout.setVerticalGroup(
            layout.createSequentialGroup()
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(button_spatial)
                    .addComponent(button_temporal)
                    .addComponent(button_chemical)
                    .addComponent(button_vertical))
        )

        # Single pollutant run
        button_run_single = swing.JButton("Run (single pollutant)")
        button_run_single.actionPerformed = self.click_run_single

        # Total run
        button_run_total = swing.JButton("Run (total)")
        button_run_total.actionPerformed = self.click_run_total

        # Layout
        layout = swing.GroupLayout(self)
        self.setLayout(layout)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)
        layout.setHorizontalGroup(
            layout.createParallelGroup()
                .addGroup(layout.createSequentialGroup()
                    .addComponent(label_output_dir)
                    .addComponent(self.text_output_dir)
                    .addComponent(button_output_dir))
                .addGap(15)
                .addGroup(layout.createSequentialGroup()
                    .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
                        .addComponent(label_sector)
                        .addComponent(label_pollutant))
                    .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
                        .addComponent(self.combobox_sector)
                        .addComponent(self.combobox_pollutant)))
                .addGap(15)
                .addComponent(panel_test)
                .addGap(15)
                .addGroup(swing.GroupLayout.Alignment.CENTER, layout.createSequentialGroup()
                    .addComponent(button_run_single)
                    .addComponent(button_run_total))
        )
        layout.setVerticalGroup(
            layout.createSequentialGroup()
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_output_dir)
                    .addComponent(self.text_output_dir)
                    .addComponent(button_output_dir))
                .addGap(15)
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_sector)
                    .addComponent(self.combobox_sector))
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_pollutant)
                    .addComponent(self.combobox_pollutant))
                .addGap(15)
                .addComponent(panel_test)
                .addGap(15)
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(button_run_single)
                    .addComponent(button_run_total))
        )

    def update_run_configure(self, run_config):
        """
        Update run configure.

        :param run_config: (*RunConfigure*) Run configure object.
        """
        self.run_config = run_config
        self.text_output_dir.setText(self.run_config.run_output_dir)
        self.update_sectors()
        self.update_pollutants()

    def update_sectors(self):
        self.combobox_sector.removeAllItems()
        for sector in self.run_config.emission_sectors:
            self.combobox_sector.addItem(sector)

    def update_pollutants(self):
        self.combobox_pollutant.removeAllItems()
        for pollutant in self.run_config.emission_pollutants:
            self.combobox_pollutant.addItem(pollutant)

    def click_output_dir(self, e):
        choose_file = swing.JFileChooser()
        ff = File(self.text_output_dir.text)
        if ff.isFile():
            choose_file.setCurrentDirectory(ff.getParentFile())
        choose_file.setFileSelectionMode(swing.JFileChooser.FILES_ONLY)
        ret = choose_file.showOpenDialog(self)
        if ret == swing.JFileChooser.APPROVE_OPTION:
            ff = choose_file.getSelectedFile()
            self.text_output_dir.text = ff.getAbsolutePath()
            self.run_config.run_output_dir = ff.getAbsolutePath()

    def click_spatial(self, e):
        run_spatial = RunSpatial(self)
        run_spatial.execute()

    def click_temporal(self, e):
        run_temporal = RunTemporal(self)
        run_temporal.execute()

    def click_chemical(self, e):
        pass

    def click_vertical(self, e):
        pass

    def click_run_single(self, e):
        run_single = RunSingle(self)
        run_single.execute()

    def click_run_total(self, e):
        pass


class RunSpatial(swing.SwingWorker):

    def __init__(self, panel):
        self.panel = panel
        swing.SwingWorker.__init__(self)

    def doInBackground(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.WAIT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(True)

        # Read data
        print("Read emission data...")
        sector = self.panel.combobox_sector.getSelectedItem()
        pollutant = self.panel.combobox_pollutant.getSelectedItem()
        year = self.panel.run_config.emission_year
        month = self.panel.run_config.emission_month
        emission = self.panel.run_config.emission_module
        data = emission.read_emis(sector, pollutant, year, month)
        emis_grid = emission.get_emis_grid()

        # Emission units conversion
        print("Units conversion...")
        units = Units(Weight.G, Area.M2, Period.MONTH)
        if pollutant.units.area == Area.GRID:
            convert_ratio = pollutant.units.convert_ratio(units, ignore_area=True)
            print(convert_ratio)
            data = data * convert_ratio / emis_grid.grid_areas()
        else:
            convert_ratio = pollutant.units.convert_ratio(units)
            data = data * convert_ratio

        # Spatial transform
        print("Spatial allocation...")
        model_grid = self.panel.run_config.spatial_model_grid
        self.panel.temp_data = transform(data, emis_grid, model_grid)

        # Plot
        print("Plot...")
        plt.clf()
        plt.axesm(projection=model_grid.proj)
        plt.geoshow('country', edgecolor='k')
        levs = np.logspace(-12, 1, num=14)
        layer = plt.imshow(model_grid.x_coord, model_grid.y_coord, self.panel.temp_data, levs, proj=model_grid.proj)
        plt.colorbar(layer, shrink=0.8, label=str(units))
        plt.title('Emission - {} - {} - ({}-{})'.format(sector.name, pollutant.name, year, month))

    def done(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.DEFAULT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(False)

        try:
            self.get()  # raise exception if abnormal completion
        except ExecutionException, e:
            raise e.getCause()


class RunTemporal(swing.SwingWorker):

    def __init__(self, panel):
        self.panel = panel
        swing.SwingWorker.__init__(self)

    def doInBackground(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.WAIT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(True)

        sector = self.panel.combobox_sector.getSelectedItem()
        pollutant = self.panel.combobox_pollutant.getSelectedItem()
        year = self.panel.run_config.emission_year
        month = self.panel.run_config.emission_month
        model_grid = self.panel.run_config.spatial_model_grid

        # Temporal allocation
        print('Temporal allocation...')
        units = Units(Weight.G, Area.M2, Period.SECOND)
        temp_ref_fn = os.path.join(ge_data_dir, self.panel.run_config.temporal_ref_file)
        temp_profile_fn = os.path.join(ge_data_dir, self.panel.run_config.temporal_prof_file)
        month_profile, week_profile, diurnal_profile, diurnal_profile_we = \
            temp_alloc.read_file(temp_ref_fn, temp_profile_fn, sector.scc)

        print('To daily emission (g/m2/day)...')
        weekday_data, weekend_data = temp_alloc.week_allocation(self.panel.temp_data, week_profile, year, month)
        weekday_data = (weekday_data * 5 + weekend_data * 2) / 7
        print('To hourly emission (g/m2/s)...')
        hour_data = temp_alloc.diurnal_allocation(weekday_data, diurnal_profile) / 3600
        self.panel.temp_data = hour_data[0]

        # Plot
        print("Plot...")
        plt.clf()
        plt.axesm(projection=model_grid.proj)
        plt.geoshow('country', edgecolor='k')
        levs = np.logspace(-18, -5, num=14)
        layer = plt.imshow(model_grid.x_coord, model_grid.y_coord, self.panel.temp_data, levs, proj=model_grid.proj)
        plt.colorbar(layer, shrink=0.8, label=str(units))
        plt.title('Emission - {} - {} - ({}-{})'.format(sector.name, pollutant.name, year, month))

    def done(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.DEFAULT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(False)

        try:
            self.get()  # raise exception if abnormal completion
        except ExecutionException, e:
            raise e.getCause()


class RunSingle(swing.SwingWorker):

    def __init__(self, panel):
        self.panel = panel
        swing.SwingWorker.__init__(self)

    def doInBackground(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.WAIT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(True)

        # Run
        sector = self.panel.combobox_sector.getSelectedItem()
        pollutant = self.panel.combobox_pollutant.getSelectedItem()
        run_pollutant(self.panel.run_config, sector, pollutant)

    def done(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.DEFAULT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(False)

        try:
            self.get()  # raise exception if abnormal completion
        except ExecutionException, e:
            raise e.getCause()
