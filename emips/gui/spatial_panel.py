# coding=utf-8
import os.path

import javax.swing as swing
import java.awt as awt
from java.util.concurrent import ExecutionException

from mipylib import geolib
from mipylib import plotlib as plt
from mipylib import numeric as np
from mipylib import dataset
from emips.spatial_alloc import GridDesc


class SpatialPanel(swing.JPanel):

    def __init__(self, frm_main):
        super(SpatialPanel, self).__init__()

        self.frm_main = frm_main
        self.run_config = frm_main.run_config
        self.init_gui()
        if self.run_config is not None:
            self.update_run_configure(self.run_config)

    def init_gui(self):
        # Emission grid setting
        self.ta_emis_grid = swing.JTextArea()
        self.ta_emis_grid.setLineWrap(True)
        self.ta_emis_grid.setEditable(False)        
        border = swing.BorderFactory.createTitledBorder("Emission grid")
        self.ta_emis_grid.setBorder(border)

        # Model grid setting
        self.model_grid = self.run_config.spatial_model_grid
        panel_grid = swing.JPanel()
        border = swing.BorderFactory.createTitledBorder("Model grid")
        panel_grid.setBorder(border)
        # Projection
        label_proj = swing.JLabel("Projection:")
        self.text_proj = swing.JTextField("")
        # Grid
        label_xmin = swing.JLabel("X origin:")
        self.text_xmin = swing.JTextField("")
        label_xnum = swing.JLabel("X number:")
        self.text_xnum = swing.JTextField("")
        label_xcell = swing.JLabel("X cell:")
        self.text_xcell = swing.JTextField("")
        label_ymin = swing.JLabel("Y origin:")
        self.text_ymin = swing.JTextField("")
        label_ynum = swing.JLabel("Y number:")
        self.text_ynum = swing.JTextField("")
        label_ycell = swing.JLabel("Y cell:")
        self.text_ycell = swing.JTextField("")
        # Update button
        button_update = swing.JButton("Update configure")
        button_update.actionPerformed = self.click_update
        # Model grid layout
        layout = swing.GroupLayout(panel_grid)
        panel_grid.setLayout(layout)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)
        layout.setHorizontalGroup(
            layout.createParallelGroup()
                .addGroup(layout.createSequentialGroup()
                      .addComponent(label_proj)
                      .addComponent(self.text_proj))
                .addGroup(layout.createSequentialGroup()
                      .addComponent(label_xmin)
                      .addComponent(self.text_xmin)
                      .addComponent(label_xnum)
                      .addComponent(self.text_xnum)
                      .addComponent(label_xcell)
                      .addComponent(self.text_xcell))
                .addGroup(layout.createSequentialGroup()
                      .addComponent(label_ymin)
                      .addComponent(self.text_ymin)
                      .addComponent(label_ynum)
                      .addComponent(self.text_ynum)
                      .addComponent(label_ycell)
                      .addComponent(self.text_ycell))
                .addGap(15)
                .addComponent(button_update, swing.GroupLayout.Alignment.CENTER)
        )
        layout.setVerticalGroup(
            layout.createSequentialGroup()
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                      .addComponent(label_proj)
                      .addComponent(self.text_proj))
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                      .addComponent(label_xmin)
                      .addComponent(self.text_xmin)
                      .addComponent(label_xnum)
                      .addComponent(self.text_xnum)
                      .addComponent(label_xcell)
                      .addComponent(self.text_xcell))
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                      .addComponent(label_ymin)
                      .addComponent(self.text_ymin)
                      .addComponent(label_ynum)
                      .addComponent(self.text_ynum)
                      .addComponent(label_ycell)
                      .addComponent(self.text_ycell))
                .addGap(15)
                .addComponent(button_update)
        )

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
                .addComponent(self.ta_emis_grid)
                .addComponent(panel_grid, swing.GroupLayout.Alignment.CENTER)
                .addGap(15)
                .addComponent(button_plot, swing.GroupLayout.Alignment.CENTER)
                .addGap(15)
        )
        layout.setVerticalGroup(
            layout.createSequentialGroup()
                .addComponent(self.ta_emis_grid)
                .addComponent(panel_grid)
                .addGap(15)
                .addComponent(button_plot)
                .addGap(15)
        )

    def update_run_configure(self, run_config):
        """
        Update run configure.

        :param run_config: (*RunConfigure*) Run configure object.
        """
        self.run_config = run_config
        sector = self.frm_main.panel_emission.combobox_sector.getSelectedItem()
        if self.run_config.emission_module is not None:
            self.emis_grid = self.run_config.emission_module.get_emis_grid(sector)
            self.ta_emis_grid.setText(self.emis_grid.__str__())
            
        self.model_grid = self.run_config.spatial_model_grid
        self.text_proj.setText(self.model_grid.proj.toProj4String())
        self.text_xmin.setText(str(self.model_grid.x_orig))
        self.text_xcell.setText(str(self.model_grid.x_cell))
        self.text_xnum.setText(str(self.model_grid.x_num))
        self.text_ymin.setText(str(self.model_grid.y_orig))
        self.text_ycell.setText(str(self.model_grid.y_cell))
        self.text_ynum.setText(str(self.model_grid.y_num))

    def update_emission_module(self):
        """
        Update emission module.
        """
        sector = self.frm_main.panel_emission.combobox_sector.getSelectedItem()
        if self.run_config.emission_module is not None:
            self.emis_grid = self.run_config.emission_module.get_emis_grid(sector)
            self.ta_emis_grid.setText(self.emis_grid.__str__())

    def click_update(self, e):
        """
        Model grid changed event.
        :param e: Document event.
        """
        proj = geolib.projinfo(self.text_proj.getText())
        x_origin = float(self.text_xmin.getText())
        x_cell = float(self.text_xcell.getText())
        x_num = int(self.text_xnum.getText())
        y_origin = float(self.text_ymin.getText())
        y_cell = float(self.text_ycell.getText())
        y_num = int(self.text_ynum.getText())
        self.run_config.spatial_model_grid = GridDesc(proj=proj, x_orig=x_origin, x_cell=x_cell, x_num=x_num,
                                   y_orig=y_origin, y_cell=y_cell, y_num=y_num)
        self.model_grid = self.run_config.spatial_model_grid
        print("Model grid updated!\n{}".format(self.model_grid))

    def click_plot(self, e):
        """
        Read script button click event.
        """
        plot_spatial = PlotSpatial(self)
        plot_spatial.execute()


class PlotSpatial(swing.SwingWorker):

    def __init__(self, panel):
        self.panel = panel
        swing.SwingWorker.__init__(self)

    def doInBackground(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.WAIT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(True)

        # Plot
        plt.clf()
        plt.subplot(1, 2, 1, axestype='map', projection=self.panel.emis_grid.proj)
        plt.geoshow('country')
        ex = self.panel.emis_grid.x_coord
        ey = self.panel.emis_grid.y_coord
        exx, eyy = np.grid_edge(ex, ey)
        plt.plot(exx, eyy, color='b', linewidth=2, proj=self.panel.emis_grid.proj)
        plt.title('Emission grid')
        plt.xlim(ex[0] - (ex[-1] - ex[0]) * 0.1, ex[-1] + (ex[-1] - ex[0]) * 0.1)
        plt.ylim(ey[0] - (ey[-1] - ey[0]) * 0.1, ey[-1] + (ey[-1] - ey[0]) * 0.1)

        plt.subplot(1, 2, 2, axestype='map', projection=self.panel.model_grid.proj)
        plt.geoshow('country')
        x = self.panel.model_grid.x_coord
        y = self.panel.model_grid.y_coord
        xx, yy = np.grid_edge(x, y)
        plt.plot(xx, yy, color='r', linewidth=2, proj=self.panel.model_grid.proj)
        plt.title('Model grid')
        plt.xlim(x[0] - (x[-1] - x[0]) * 0.1, x[-1] + (x[-1] - x[0]) * 0.1)
        plt.ylim(y[0] - (y[-1] - y[0]) * 0.1, y[-1] + (y[-1] - y[0]) * 0.1)

    def done(self):
        # Set cursor and progress bar
        self.panel.setCursor(awt.Cursor(awt.Cursor.DEFAULT_CURSOR))
        self.panel.frm_main.milab_app.getProgressBar().setVisible(False)

        try:
            self.get()  # raise exception if abnormal completion
        except ExecutionException, e:
            raise e.getCause()
