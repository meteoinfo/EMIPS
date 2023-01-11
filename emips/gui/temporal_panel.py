# coding=utf-8

import os

from java.awt.event import ItemEvent
from java import awt
from javax import swing
from java.util.concurrent import ExecutionException
from mipylib import plotlib as plt

from emips import ge_data_dir, temp_alloc
from emips.utils import SectorEnum


class TemporalPanel(swing.JPanel):

    def __init__(self, frm_main):
        super(TemporalPanel, self).__init__()

        self.frm_main = frm_main
        self.run_config = frm_main.run_config
        self.month_profile = None
        self.week_profile = None
        self.diurnal_profile = None
        self.diurnal_profile_we = None
        
        self.init_gui()
        if self.run_config is not None:
            self.update_run_configure(self.run_config)

    def init_gui(self):
        # Temporal profile file
        label_tpro = swing.JLabel("Profile file:")
        self.combobox_tpro = swing.JComboBox()
        ge_files = os.listdir(ge_data_dir)
        for fn in ge_files:
            if fn.startswith("amptpro"):
                self.combobox_tpro.addItem(fn)

        # Temporal reference file
        label_tref = swing.JLabel("Reference file:")
        self.combobox_tref = swing.JComboBox()
        for fn in ge_files:
            if fn.startswith("amptref"):
                self.combobox_tref.addItem(fn)

        # Temporal profile data
        label_month_pro = swing.JLabel("Month profile:")
        self.text_month_pro = swing.JTextField("")
        label_week_pro = swing.JLabel("Week profile:")
        self.text_week_pro = swing.JTextField("")
        label_diurnal_pro = swing.JLabel("Diurnal profile:")
        self.text_diurnal_pro = swing.JTextArea("")
        self.text_diurnal_pro.setLineWrap(True)        
        self.text_diurnal_pro.setWrapStyleWord(True)
        label_diurnal_pro_we = swing.JLabel("Diurnal (Weekend):")
        self.text_diurnal_pro_we = swing.JTextArea("")
        self.text_diurnal_pro_we.setLineWrap(True)        
        self.text_diurnal_pro_we.setWrapStyleWord(True)

        # Sector choose
        label_sector = swing.JLabel("Sector:")
        self.combobox_sector = swing.JComboBox()
        self.combobox_sector.itemListener = self.click_sector
        for se in SectorEnum:
            self.combobox_sector.addItem(se)       

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
                    .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
                        .addComponent(label_tpro)
                        .addComponent(label_tref)
                        .addComponent(label_sector)
                        .addGap(15)
                        .addComponent(label_month_pro)
                        .addComponent(label_week_pro)
                        .addComponent(label_diurnal_pro)
                        .addComponent(label_diurnal_pro_we))
                    .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
                        .addComponent(self.combobox_tpro)
                        .addComponent(self.combobox_tref)
                        .addComponent(self.combobox_sector)
                        .addGap(15)
                        .addComponent(self.text_month_pro)
                        .addComponent(self.text_week_pro)
                        .addComponent(self.text_diurnal_pro)
                        .addComponent(self.text_diurnal_pro_we)))
                .addGap(15)
                .addComponent(button_plot, swing.GroupLayout.Alignment.CENTER)
        )
        layout.setVerticalGroup(
            layout.createSequentialGroup()
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_tpro)
                    .addComponent(self.combobox_tpro))
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_tref)
                    .addComponent(self.combobox_tref))
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_sector)
                    .addComponent(self.combobox_sector))
                .addGap(15)
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_month_pro)
                    .addComponent(self.text_month_pro))
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_week_pro)
                    .addComponent(self.text_week_pro))
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_diurnal_pro)
                    .addComponent(self.text_diurnal_pro))
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_diurnal_pro_we)
                    .addComponent(self.text_diurnal_pro_we))
                .addGap(15)
                .addComponent(button_plot)
        )

    def update_run_configure(self, run_config):
        """
        Update run configure.

        :param run_config: (*RunConfigure*) Run configure object.
        """
        self.run_config = run_config
        self.combobox_tpro.setSelectedItem(os.path.basename(self.run_config.temporal_prof_file))
        self.combobox_tref.setSelectedItem(os.path.basename(self.run_config.temporal_ref_file))

    def read_temporal_profiles(self, scc):
        tpro_file = os.path.join(ge_data_dir, self.combobox_tpro.getSelectedItem())
        tref_file = os.path.join(ge_data_dir, self.combobox_tref.getSelectedItem())
        if os.path.isfile(tpro_file) and os.path.isfile(tref_file):
            self.month_profile, self.week_profile, self.diurnal_profile, self.diurnal_profile_we = \
                temp_alloc.read_file(tref_file, tpro_file, scc)

    def click_sector(self, e):        
        cb = e.getSource()
        if e.getStateChange() == ItemEvent.SELECTED:
            sector = cb.getSelectedItem()
            scc = sector.scc
            self.read_temporal_profiles(scc)
            if self.month_profile is not None:
                self.text_month_pro.setText(str(self.month_profile.weights)[7:-2])
            if self.week_profile is not None:
                self.text_week_pro.setText(str(self.week_profile.weights)[7:-2])
            if self.diurnal_profile is not None:
                self.text_diurnal_pro.setText(str(self.diurnal_profile.weights)[7:-2])
            if self.diurnal_profile_we is not None:
                self.text_diurnal_pro_we.setText(str(self.diurnal_profile_we.weights)[7:-2])

    def click_plot(self, e):
        plot_temporal = PlotTemporal(self)
        plot_temporal.execute()


class PlotTemporal(swing.SwingWorker):

    def __init__(self, panel):
        self.panel = panel
        swing.SwingWorker.__init__(self)

    def doInBackground(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.WAIT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(True)

        # Plot
        plt.clf()
        plt.subplot(2,2,1)
        plt.plot(self.panel.month_profile.weights, '-*b')
        plt.title('Month profile')
        plt.subplot(2,2,2)
        plt.plot(self.panel.week_profile.weights, '-*b')
        plt.title('Week profile')
        plt.subplot(2,2,3)
        plt.plot(self.panel.diurnal_profile.weights, '-*b')
        plt.title('Diurnal profile')
        plt.subplot(2,2,4)
        plt.plot(self.panel.diurnal_profile_we.weights, '-*b')
        plt.title('Diurnal profile (Weekend)')

    def done(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.DEFAULT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(False)

        try:
            self.get()  # raise exception if abnormal completion
        except ExecutionException, e:
            raise e.getCause()
