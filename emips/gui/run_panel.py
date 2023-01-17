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
                .addComponent(button_run_single, swing.GroupLayout.Alignment.CENTER)
                .addGap(30)
                .addComponent(button_run_total, swing.GroupLayout.Alignment.CENTER)
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
                .addComponent(button_run_single)
                .addGap(30)
                .addComponent(button_run_total)
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

    def click_run_single(self, e):
        run_single = RunSingle(self)
        run_single.execute()

    def click_run_total(self, e):
        run_total = RunTotal(self)
        run_total.execute()


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


class RunTotal(swing.SwingWorker):

    def __init__(self, panel):
        self.panel = panel
        swing.SwingWorker.__init__(self)

    def doInBackground(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.WAIT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(True)

        # Run
        for sector in self.panel.run_config.emission_sectors:
            print("Sector: {}".format(sector))
            for pollutant in self.panel.run_config.emission_pollutants:
                print("Pollutant: {}".format(pollutant))
                run_pollutant(self.panel.run_config, sector, pollutant)

    def done(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.DEFAULT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(False)

        try:
            self.get()  # raise exception if abnormal completion
        except ExecutionException, e:
            raise e.getCause()
