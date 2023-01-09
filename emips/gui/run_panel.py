# coding=utf-8

import javax.swing as swing
import java.awt as awt
from com.formdev.flatlaf.extras import FlatSVGIcon
from java.io import File

import os
from emips.utils import SectorEnum
from emips.chem_spec import PollutantEnum


class RunPanel(swing.JPanel):

    def __init__(self, frm_main):
        super(RunPanel, self).__init__()

        self.frm_main = frm_main
        self.run_config = frm_main.run_config
        self.init_gui()
        if self.run_config is not None:
            self.update_run_configure(self.run_config)

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
        for se in SectorEnum:
            self.combobox_sector.addItem(se)

        # Pollutant choose
        label_pollutant = swing.JLabel("Pollutant:")
        self.combobox_pollutant = swing.JComboBox()
        for poll in PollutantEnum:
            self.combobox_pollutant.addItem(poll)

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

        # Total run
        button_run_total = swing.JButton("Run (total)")

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
        

    def click_output_dir(self, e):
        pass

    def click_spatial(self, e):
        pass

    def click_temporal(self, e):
        pass

    def click_chemical(self, e):
        pass

    def click_vertical(self, e):
        pass
    