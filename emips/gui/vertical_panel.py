# coding=utf-8

from java import awt
from javax import swing
from java.util.concurrent import ExecutionException
import os
from emips import ge_data_dir, vertical_alloc
from mipylib import plotlib as plt


class VerticalPanel(swing.JPanel):

    def __init__(self, frm_main):
        super(VerticalPanel, self).__init__()

        self.frm_main = frm_main
        self.run_config = frm_main.run_config
        self.vertical_profile = None
        
        self.init_gui()
        if self.run_config is not None:
            self.update_run_configure(self.run_config)

    def init_gui(self):
        # Vertical profile file
        label_vpro = swing.JLabel("Profile file:")
        self.combobox_vpro = swing.JComboBox()
        ge_files = os.listdir(ge_data_dir)
        for fn in ge_files:
            if fn.startswith("vpro"):
                self.combobox_vpro.addItem(fn)

        # Vertical profile data
        label_vpro_data = swing.JLabel("Vertical profile:")
        self.text_vpro = swing.JTextField("")

        # Sector choose
        label_sector = swing.JLabel("Sector:")
        self.combobox_sector = swing.JComboBox()
        self.combobox_sector.itemListener = self.click_sector

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
                        .addComponent(label_vpro)
                        .addComponent(label_sector)
                        .addGap(15)
                        .addComponent(label_vpro_data))
                    .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
                        .addComponent(self.combobox_vpro)
                        .addComponent(self.combobox_sector)
                        .addGap(15)
                        .addComponent(self.text_vpro)))
                .addGap(15)
                .addComponent(button_plot, swing.GroupLayout.Alignment.CENTER)
        )
        layout.setVerticalGroup(
            layout.createSequentialGroup()
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_vpro)
                    .addComponent(self.combobox_vpro))
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_sector)
                    .addComponent(self.combobox_sector))
                .addGap(15)
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_vpro_data)
                    .addComponent(self.text_vpro))
                .addGap(15)
                .addComponent(button_plot)
        )

    def update_run_configure(self, run_config):
        """
        Update run configure.

        :param run_config: (*RunConfigure*) Run configure object.
        """
        self.run_config = run_config
        self.combobox_vpro.setSelectedItem(os.path.basename(self.run_config.vertical_prof_file))
        self.combobox_sector.removeAllItems()
        for sector in self.run_config.emission_sectors:
            self.combobox_sector.addItem(sector)

    def read_vertical_profile(self, scc):
        vpro_file = os.path.join(ge_data_dir, self.combobox_vpro.getSelectedItem())
        self.vertical_profile = vertical_alloc.read_file(vpro_file, scc)

    def click_sector(self, e):        
        cb = e.getSource()
        if e.getStateChange() == awt.event.ItemEvent.SELECTED:
            sector = cb.getSelectedItem()
            scc = sector.scc
            self.read_vertical_profile(scc)
            if self.vertical_profile is not None:
                self.text_vpro.setText(str(self.vertical_profile.weights)[7:-2])

    def click_plot(self, e):        
        plot_vertical = PlotVertical(self)
        plot_vertical.execute()


class PlotVertical(swing.SwingWorker):

    def __init__(self, panel):
        self.panel = panel
        swing.SwingWorker.__init__(self)

    def doInBackground(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.WAIT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(True)

        # Plot
        plt.clf()
        plt.plot(self.panel.vertical_profile.weights, '-*b')
        plt.title('Vertical profile')

    def done(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.DEFAULT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(False)

        try:
            self.get()  # raise exception if abnormal completion
        except ExecutionException, e:
            raise e.getCause()
