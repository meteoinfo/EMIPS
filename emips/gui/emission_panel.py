# coding=utf-8

import os

import java.awt as awt
from java.awt.event import ItemEvent
import javax.swing as swing
from javax.swing.event import DocumentListener
from com.formdev.flatlaf.extras import FlatSVGIcon
from java.io import File
from java.util.concurrent import ExecutionException
from mipylib import plotlib as plt
from mipylib import numeric as np
from .form import FrmSectors, FrmPollutants


class EmissionPanel(swing.JPanel):

    def __init__(self, frm_main):
        super(EmissionPanel, self).__init__()

        self.frm_main = frm_main
        self.run_config = frm_main.run_config
        self.init_gui()
        if self.run_config is not None:
            self.update_run_configure(self.run_config)

    def init_gui(self):
        # Read emission script file
        label_read = swing.JLabel("Read module:")
        self.text_read = swing.JTextField("")        
        icon = FlatSVGIcon(File(os.path.join(self.frm_main.current_path, 'image', 'file-open.svg')))
        button_read = swing.JButton("", icon)
        button_read.actionPerformed = self.click_read_script

        # Sector choose
        label_sector = swing.JLabel("Sector:")
        self.combobox_sector = swing.JComboBox()
        button_edit_sectors = swing.JButton("Edit sectors")
        button_edit_sectors.actionPerformed = self.click_edit_sectors

        # Pollutant choose
        label_pollutant = swing.JLabel("Pollutant:")
        self.combobox_pollutant = swing.JComboBox()
        button_edit_pollutants = swing.JButton("Edit pollutants")
        button_edit_pollutants.actionPerformed = self.click_edit_pollutants

        # Year and Month
        label_year = swing.JLabel("Year:")
        self.text_year = swing.JTextField("")
        self.text_year.getDocument().addDocumentListener(YearDocumentListener(self))
        label_month = swing.JLabel("Month:")
        self.combobox_month = swing.JComboBox()
        self.combobox_month.itemListener = self.click_month
        for m in range(1, 13):
            self.combobox_month.addItem(m)

        # Plot button
        button_plot = swing.JButton("Plot")
        button_plot.actionPerformed = self.click_plot

        # Layout
        layout = swing.GroupLayout(self)
        self.setLayout(layout)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)
        layout.setHorizontalGroup(
            layout.createParallelGroup()
                .addGroup(layout.createSequentialGroup()
                    .addComponent(label_read)
                    .addComponent(self.text_read)
                    .addComponent(button_read))
                .addGap(15)
                .addGroup(layout.createSequentialGroup()
                    .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
                        .addComponent(label_sector)
                        .addComponent(label_pollutant)
                        .addComponent(label_year)
                        .addComponent(label_month))
                    .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
                        .addGroup(layout.createSequentialGroup()
                            .addComponent(self.combobox_sector)
                            .addComponent(button_edit_sectors))
                        .addGroup(layout.createSequentialGroup()
                            .addComponent(self.combobox_pollutant)
                            .addComponent(button_edit_pollutants))
                        .addComponent(self.text_year)
                        .addComponent(self.combobox_month)))
                .addGap(15)
                .addComponent(button_plot, swing.GroupLayout.Alignment.CENTER)
        )
        layout.setVerticalGroup(
            layout.createSequentialGroup()
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_read)
                    .addComponent(self.text_read)
                    .addComponent(button_read))
                .addGap(15)
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_sector)
                    .addComponent(self.combobox_sector)
                    .addComponent(button_edit_sectors))
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_pollutant)
                    .addComponent(self.combobox_pollutant)
                    .addComponent(button_edit_pollutants))
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_year)
                    .addComponent(self.text_year))
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_month)
                    .addComponent(self.combobox_month))
                .addGap(15)
                .addComponent(button_plot)
        )

    def update_run_configure(self, run_config):
        """
        Update run configure.

        :param run_config: (*RunConfigure*) Run configure object.
        """
        self.run_config = run_config
        self.text_read.setText(self.run_config.emission_read_file)
        self.update_sectors()
        self.update_pollutants()
        self.text_year.setText(self.run_config.emission_year)
        self.combobox_month.setSelectedItem(self.run_config.emission_month)

    def update_sectors(self):
        self.combobox_sector.removeAllItems()
        for sector in self.run_config.emission_sectors:
            self.combobox_sector.addItem(sector)

    def update_pollutants(self):
        self.combobox_pollutant.removeAllItems()
        for pollutant in self.run_config.emission_pollutants:
            self.combobox_pollutant.addItem(pollutant)

    def click_read_script(self, e):
        """
        Read script button click event.
        """
        choose_file = swing.JFileChooser()
        ff = File(self.text_read.text)
        if ff.isFile():
            choose_file.setCurrentDirectory(ff.getParentFile())
        choose_file.setFileSelectionMode(swing.JFileChooser.FILES_ONLY)
        ret = choose_file.showOpenDialog(self)
        if ret == swing.JFileChooser.APPROVE_OPTION:
            ff = choose_file.getSelectedFile()
            self.text_read.text = ff.getAbsolutePath()
            self.run_config.emission_read_file = ff.getAbsolutePath()
            self.run_config.load_emission_module()
            self.frm_main.update_emission_module()

    def click_edit_sectors(self, e):
        frm_sectors = FrmSectors(self.frm_main, True)
        frm_sectors.setLocationRelativeTo(self.frm_main)
        frm_sectors.setVisible(True)

        if frm_sectors.ok:
            self.update_sectors()

    def click_edit_pollutants(self, e):
        frm_pollutants = FrmPollutants(self.frm_main, True)
        frm_pollutants.setLocationRelativeTo(self.frm_main)
        frm_pollutants.setVisible(True)

        if frm_pollutants.ok:
            self.update_pollutants()

    def click_month(self, e):
        cb = e.getSource()
        if e.getStateChange() == ItemEvent.SELECTED:
            self.run_config.emission_month = cb.getSelectedItem()

    def click_plot(self, e):
        """
        Plot button click event.
        """
        if self.run_config is None:
            return

        plot_emission = PlotEmission(self)
        plot_emission.execute()


class YearDocumentListener(DocumentListener):

    def __init__(self, panel):
        self.panel = panel
        DocumentListener.__init__(self)

    def insertUpdate(self, e):
        self.changedUpdate(e)

    def removeUpdate(self, e):
        self.changedUpdate(e)

    def changedUpdate(self, e):
        year_str = self.panel.text_year.text
        if year_str.isdigit():
            self.panel.run_config.emission_year = int(year_str)


class PlotEmission(swing.SwingWorker):

    def __init__(self, panel):
        self.panel = panel
        swing.SwingWorker.__init__(self)

    def doInBackground(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.WAIT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(True)

        # Read data
        sector = self.panel.combobox_sector.getSelectedItem()
        pollutant = self.panel.combobox_pollutant.getSelectedItem()
        year = self.panel.run_config.emission_year
        month = self.panel.run_config.emission_month
        emission = self.panel.run_config.emission_module
        data = emission.read_emis(sector, pollutant, year, month)
        print(data)
        emis_grid = emission.get_emis_grid()
        lon = emis_grid.x_coord
        lat = emis_grid.y_coord

        # Plot
        plt.clf()
        plt.axesm()
        plt.geoshow('country', edgecolor='k')
        levs = np.logspace(-10, 2, num=13)
        layer = plt.imshow(lon, lat, data, levs)
        plt.colorbar(layer, shrink=0.8)
        plt.title('Emission - {} - {} - ({}-{})'.format(sector.name, pollutant.name, year, month))

    def done(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.DEFAULT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(False)

        try:
            self.get()  # raise exception if abnormal completion
        except ExecutionException, e:
            raise e.getCause()
