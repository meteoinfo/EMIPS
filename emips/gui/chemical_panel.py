# coding=utf-8

import java.awt as awt
from java.awt.event import ItemEvent
import javax.swing as swing
from com.formdev.flatlaf.extras import FlatSVGIcon
from java.io import File
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
        self.combobox_spro.itemListener = self.click_spro
        # Species reference file
        label_sref = swing.JLabel("Reference file:")
        self.combobox_sref = swing.JComboBox()
        for fn in ge_files:
            if fn.startswith("gsref"):
                self.combobox_sref.addItem(fn)
        self.combobox_sref.itemListener = self.click_sref
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

        # Grid speciation file
        self.checkbox_gsf = swing.JCheckBox("Using voc grid speciation files")
        self.checkbox_gsf.actionPerformed = self.click_enable_grid_spec

        # Grid speciation panel
        self.panel_grid_spec = swing.JPanel()
        border = swing.BorderFactory.createTitledBorder("VOC grid speciation")
        self.panel_grid_spec.setBorder(border)
        # Grid speciation read module
        label_read = swing.JLabel("Read module:")
        self.text_read = swing.JTextField("")
        icon = FlatSVGIcon(File(os.path.join(self.frm_main.current_path, 'image', 'file-open.svg')))
        button_read = swing.JButton("", icon)
        button_read.actionPerformed = self.click_read_script
        # Chemical mechanism
        self.ta_mech = swing.JTextArea()
        self.ta_mech.setLineWrap(True)        
        self.ta_mech.setWrapStyleWord(True)
        self.ta_mech.setEditable(False)                
        border = swing.BorderFactory.createTitledBorder("All species")
        self.ta_mech.setBorder(border)
        label_mech = swing.JLabel("Chemical mechanism:")
        self.combobox_mech = swing.JComboBox()
        for cm in ChemMechEnum:
            self.combobox_mech.addItem(cm)
        self.combobox_mech.itemListener = self.click_chem_mech
        # Layout of grid speciation panel
        layout = swing.GroupLayout(self.panel_grid_spec)
        self.panel_grid_spec.setLayout(layout)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)
        layout.setHorizontalGroup(
            layout.createParallelGroup()
            .addGroup(layout.createSequentialGroup()
                      .addComponent(label_read)
                      .addComponent(self.text_read)
                      .addComponent(button_read))
            .addGroup(layout.createSequentialGroup()
                      .addComponent(label_mech)
                      .addComponent(self.combobox_mech))
            .addComponent(self.ta_mech)
        )
        layout.setVerticalGroup(
            layout.createSequentialGroup()
            .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                      .addComponent(label_read)
                      .addComponent(self.text_read)
                      .addComponent(button_read))
            .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                      .addComponent(label_mech)
                      .addComponent(self.combobox_mech))
            .addComponent(self.ta_mech)
        )

        # Layout
        layout = swing.GroupLayout(self)
        self.setLayout(layout)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)
        layout.setHorizontalGroup(
            layout.createParallelGroup()
                .addComponent(panel_profile)
                .addGap(15)
                .addComponent(self.checkbox_gsf)
                .addComponent(self.panel_grid_spec)
        )
        layout.setVerticalGroup(
            layout.createSequentialGroup()
                .addComponent(panel_profile)
                .addGap(15)
                .addComponent(self.checkbox_gsf)
                .addComponent(self.panel_grid_spec)
        )

    def update_run_configure(self, run_config):
        """
        Update run configure.

        :param run_config: (*RunConfigure*) Run configure object.
        """
        self.run_config = run_config
        self.combobox_spro.setSelectedItem(os.path.basename(self.run_config.chemical_prof_file))
        self.combobox_sref.setSelectedItem(os.path.basename(self.run_config.chemical_ref_file))
        self.checkbox_gsf.setSelected(self.run_config.voc_use_grid_spec)
        self.text_read.setText(self.run_config.grid_spec_read_file)
        self.combobox_mech.setSelectedItem(self.run_config.chemical_mechanism)

    def click_spro(self, e):
        cb = e.getSource()
        if e.getStateChange() == ItemEvent.SELECTED:
            spro_file = cb.getSelectedItem()
            self.run_config.chemical_prof_file = os.path.join(ge_data_dir, spro_file)

    def click_sref(self, e):
        cb = e.getSource()
        if e.getStateChange() == ItemEvent.SELECTED:
            sref_file = cb.getSelectedItem()
            self.run_config.chemical_ref_file = os.path.join(ge_data_dir, sref_file)

    def click_chem_mech(self, e):
        cb = e.getSource()
        if e.getStateChange() == awt.event.ItemEvent.SELECTED:
            self.run_config.chemical_mechanism = cb.getSelectedItem()
            sp_str = ""
            for sp in self.run_config.chemical_mechanism.all_species():
                sp_str += sp.name + "; "
            self.ta_mech.setText(sp_str)

    def click_enable_grid_spec(self, e):
        self.run_config.voc_use_grid_spec = self.checkbox_gsf.isSelected()
        self.panel_grid_spec.setVisible(self.checkbox_gsf.isSelected())

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
            self.run_config.grid_spec_read_file = ff.getAbsolutePath()
            self.run_config.load_grid_spec_module()
        