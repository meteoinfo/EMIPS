# coding=utf-8

import java.awt as awt
import javax.swing as swing
import os
from emips.chem_spec import ChemMechEnum
from emips import ge_data_dir


class ChemicalPanel(swing.JPanel):

    def __init__(self, frm_main):
        super(ChemicalPanel, self).__init__()

        self.frm_main = frm_main
        self.run_config = frm_main.run_config
        self.init_gui()
        if self.run_config is not None:
            self.update_run_configure(self.run_config)

    def init_gui(self):
        # Profile panel
        panel_profile = swing.JPanel()        
        # Species profile file
        label_spro = swing.JLabel("Profile file:")
        self.combobox_spro = swing.JComboBox()
        ge_files = os.listdir(ge_data_dir)
        for fn in ge_files:
            if fn.startswith("gspro"):
                self.combobox_spro.addItem(fn)
        # Species reference file
        label_sref = swing.JLabel("Reference file:")
        self.combobox_sref = swing.JComboBox()
        for fn in ge_files:
            if fn.startswith("gsref"):
                self.combobox_sref.addItem(fn)
        # Layout of profile panel
        layout = swing.GroupLayout(panel_profile)
        panel_profile.setLayout(layout)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)
        layout.setHorizontalGroup(
            layout.createParallelGroup()
                .addGroup(layout.createSequentialGroup()
                    .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
                        .addComponent(label_spro)
                        .addComponent(label_sref))
                    .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
                        .addComponent(self.combobox_spro)
                        .addComponent(self.combobox_sref)))
        )
        layout.setVerticalGroup(
            layout.createSequentialGroup()
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_spro)
                    .addComponent(self.combobox_spro))
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_sref)
                    .addComponent(self.combobox_sref))
        )
    
        # Chemical mechanism
        self.ta_mech = swing.JTextArea()
        self.ta_mech.setLineWrap(True)        
        self.ta_mech.setWrapStyleWord(True)
        self.ta_mech.setEditable(False)                
        border = swing.BorderFactory.createTitledBorder("All species")
        self.ta_mech.setBorder(border)
        label_mech = swing.JLabel("Chemical mechanism:")
        combobox_mech = swing.JComboBox()
        combobox_mech.itemListener = self.click_chem_mech
        for cm in ChemMechEnum:
            combobox_mech.addItem(cm.value)               

        # Layout
        layout = swing.GroupLayout(self)
        self.setLayout(layout)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)
        layout.setHorizontalGroup(
            layout.createParallelGroup()
                .addComponent(panel_profile)
                .addGap(15)
                .addGroup(layout.createSequentialGroup()
                    .addComponent(label_mech)
                    .addComponent(combobox_mech))
                .addComponent(self.ta_mech)
        )
        layout.setVerticalGroup(
            layout.createSequentialGroup()
                .addComponent(panel_profile)
                .addGap(15)
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_mech)
                    .addComponent(combobox_mech))
                .addComponent(self.ta_mech)
        )

    def update_run_configure(self, run_config):
        """
        Update run configure.

        :param run_config: (*RunConfigure*) Run configure object.
        """
        self.run_config = run_config

    def click_chem_mech(self, e):
        cb = e.getSource()
        if e.getStateChange() == awt.event.ItemEvent.SELECTED:
            self.chem_mech = cb.getSelectedItem()
            sp_str = ""
            for sp in self.chem_mech.all_species():
                sp_str += sp.name + "; "
            self.ta_mech.setText(sp_str)
        