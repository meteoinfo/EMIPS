# coding=utf-8

import os

import java.awt as awt
import javax.swing as swing
from com.formdev.flatlaf.extras import FlatSVGIcon
from java.io import File
from java.util.concurrent import ExecutionException

from emips.run import run_pollutant, run_sector, run_total, for_CUACE, for_WRFChem


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

        # Whether run vertical
        self.checkbox_run_vertical = swing.JCheckBox("Run vertical")
        self.checkbox_run_vertical.actionPerformed = self.click_is_run_vertical

        # Single pollutant run
        label_pre_process = swing.JLabel("Preprocess:")
        button_run_pollutant = swing.JButton("Run (single pollutant)")
        button_run_pollutant.actionPerformed = self.click_run_pollutant

        # Single sector run
        button_run_sector = swing.JButton("Run (single sector)")
        button_run_sector.actionPerformed = self.click_run_sector

        # Total run
        button_run_total = swing.JButton("Run (total)")
        button_run_total.actionPerformed = self.click_run_total

        # Post process
        label_post_process = swing.JLabel("Post process:")
        '''
        self.text_post_process = swing.JTextField("")
        icon = FlatSVGIcon(File(os.path.join(self.frm_main.current_path, 'image', 'file-open.svg')))
        button_post = swing.JButton("", icon)
        button_post.actionPerformed = self.click_post_process
        button_run_post = swing.JButton("Run post process")
        button_run_post.actionPerformed = self.click_run_post
        '''
        button_run_for_cuace = swing.JButton("For CUACE")
        button_run_for_cuace.actionPerformed = self.click_run_for_cuace
        button_run_for_wrfchem = swing.JButton("For WRF-Chem")
        button_run_for_wrfchem.actionPerformed = self.click_run_for_wrfchem

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
                .addComponent(self.checkbox_run_vertical)
                .addGap(15)
                .addComponent(label_pre_process)
                .addGroup(swing.GroupLayout.Alignment.CENTER, layout.createSequentialGroup()
                          .addComponent(button_run_pollutant)
                          .addComponent(button_run_sector)
                          .addComponent(button_run_total))
                .addGap(15)
                # .addGroup(layout.createSequentialGroup()
                #           .addComponent(label_post_process)
                #           .addComponent(self.text_post_process)
                #           .addComponent(button_post))
                # .addGap(15)
                # .addComponent(button_run_post, swing.GroupLayout.Alignment.CENTER)
                .addComponent(label_post_process)
                .addGroup(swing.GroupLayout.Alignment.CENTER, layout.createSequentialGroup()
                          .addComponent(button_run_for_cuace)
                          .addComponent(button_run_for_wrfchem))
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
                .addComponent(self.checkbox_run_vertical)
                .addGap(15)
                .addComponent(label_pre_process)
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(button_run_pollutant)
                    .addComponent(button_run_sector)
                    .addComponent(button_run_total))
                .addGap(15)
                # .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                #           .addComponent(label_post_process)
                #           .addComponent(self.text_post_process)
                #           .addComponent(button_post))
                # .addGap(15)
                # .addComponent(button_run_post)
                .addComponent(label_post_process)
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                          .addComponent(button_run_for_cuace)
                          .addComponent(button_run_for_wrfchem))
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
        # self.text_post_process.setText(self.run_config.post_process_file)

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
        # choose_file.setFileSelectionMode(swing.JFileChooser.FILES_ONLY)
        choose_file.setFileSelectionMode(swing.JFileChooser.DIRECTORIES_ONLY)
        ret = choose_file.showOpenDialog(self)
        if ret == swing.JFileChooser.APPROVE_OPTION:
            ff = choose_file.getSelectedFile()
            self.text_output_dir.text = ff.getAbsolutePath()
            self.run_config.run_output_dir = ff.getAbsolutePath()

    def click_is_run_vertical(self, e):
        self.run_config.is_run_vertical = self.checkbox_run_vertical.isSelected()

    def click_run_pollutant(self, e):
        prun = RunPollutant(self)
        prun.execute()

    def click_run_sector(self, e):
        srun = RunSector(self)
        srun.execute()

    def click_run_total(self, e):
        trun = RunTotal(self)
        trun.execute()

    # def click_post_process(self, e):
    #     choose_file = swing.JFileChooser()
    #     ff = File(self.text_post_process.text)
    #     if ff.isFile():
    #         choose_file.setCurrentDirectory(ff.getParentFile())
    #     choose_file.setFileSelectionMode(swing.JFileChooser.FILES_ONLY)
    #     ret = choose_file.showOpenDialog(self)
    #     if ret == swing.JFileChooser.APPROVE_OPTION:
    #         ff = choose_file.getSelectedFile()
    #         self.text_post_process.text = ff.getAbsolutePath()
    #         self.run_config.post_process_file = ff.getAbsolutePath()
    #         self.run_config.load_post_process_module()

    # def click_run_post(self, e):
    #     self.run_config.post_process_module.run(self.run_config)

    def click_run_for_cuace(self, e):
        postrun = RunforCUACE(self)
        postrun.execute()

    def click_run_for_wrfchem(self, e):
        postrun = RunforWRFChem(self)
        postrun.execute()

class RunPollutant(swing.SwingWorker):

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

class RunSector(swing.SwingWorker):

    def __init__(self, panel):
        self.panel = panel
        swing.SwingWorker.__init__(self)

    def doInBackground(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.WAIT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(True)

        # Run
        sector = self.panel.combobox_sector.getSelectedItem()
        print("Sector: {}".format(sector))
        run_sector(sector, self.panel.run_config)


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
        run_total(self.panel.run_config)

    def done(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.DEFAULT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(False)

        try:
            self.get()  # raise exception if abnormal completion
        except ExecutionException, e:
            raise e.getCause()

class RunforCUACE(swing.SwingWorker):

    def __init__(self, panel):
        self.panel = panel
        swing.SwingWorker.__init__(self)

    def doInBackground(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.WAIT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(True)

        # Run
        for_CUACE(self.panel.run_config)

    def done(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.DEFAULT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(False)

        try:
            self.get()  # raise exception if abnormal completion
        except ExecutionException, e:
            raise e.getCause()

class RunforWRFChem(swing.SwingWorker):

    def __init__(self, panel):
        self.panel = panel
        swing.SwingWorker.__init__(self)

    def doInBackground(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.WAIT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(True)

        # Run
        for_WRFChem(self.panel.run_config)

    def done(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.DEFAULT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(False)

        try:
            self.get()  # raise exception if abnormal completion
        except ExecutionException, e:
            raise e.getCause()
