# coding=utf-8

import os

import javax.swing as swing
from mipylib import plotlib as plt

from emips import ge_data_dir, temp_alloc
from emips.utils import SectorEnum


class TemporalPanel(swing.JPanel):

    def __init__(self, frm_main):
        super(TemporalPanel, self).__init__()

        self.frm_main = frm_main
        self.run_config = frm_main.run_config
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

        # Sector choose
        label_sector = swing.JLabel("Sector:")
        self.combobox_sector = swing.JComboBox()
        for se in SectorEnum:
            self.combobox_sector.addItem(se.value)

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
                        .addComponent(label_sector))
                    .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
                        .addComponent(self.combobox_tpro)
                        .addComponent(self.combobox_tref)
                        .addComponent(self.combobox_sector)))
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

    def click_plot(self, e):
        tpro_file = os.path.join(ge_data_dir, self.combobox_tpro.getSelectedItem())
        tref_file = os.path.join(ge_data_dir, self.combobox_tref.getSelectedItem())
        sector = self.combobox_sector.getSelectedItem()
        scc = sector.scc

        month_profile, week_profile, diurnal_profile, diurnal_profile_we = \
            temp_alloc.read_file(tref_file, tpro_file, scc)

        print("profile: {}".format(tpro_file))
        print("reference: {}".format(tref_file))
        print(month_profile)

        # Plot
        plt.clf()
        plt.subplot(2,2,1)
        plt.plot(month_profile.weights, '-*b')
        plt.title('Month profile')
        plt.subplot(2,2,2)
        plt.plot(week_profile.weights, '-*b')
        plt.title('Week profile')
        plt.subplot(2,2,3)
        plt.plot(diurnal_profile.weights, '-*b')
        plt.title('Diurnal profile')
        plt.subplot(2,2,4)
        plt.plot(diurnal_profile_we.weights, '-*b')
        plt.title('Diurnal profile (Weekend)')
