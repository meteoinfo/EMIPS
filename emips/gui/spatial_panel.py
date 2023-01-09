# coding=utf-8

import javax.swing as swing
import java.awt as awt

from mipylib import geolib
from mipylib import plotlib as plt
from mipylib import numeric as np
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
        proj_model = geolib.projinfo()
        label_proj = swing.JLabel("Projection:")
        self.text_proj = swing.JTextField(proj_model.toProj4String())
        # Grid
        label_xmin = swing.JLabel("X min:")
        self.text_xmin = swing.JTextField("")
        label_xnum = swing.JLabel("X number:")
        self.text_xnum = swing.JTextField("")
        label_xcell = swing.JLabel("X cell:")
        self.text_xcell = swing.JTextField("")
        label_ymin = swing.JLabel("Y min:")
        self.text_ymin = swing.JTextField("")
        label_ynum = swing.JLabel("Y number:")
        self.text_ynum = swing.JTextField("")
        label_ycell = swing.JLabel("Y cell:")
        self.text_ycell = swing.JTextField("")
        # Create grid button
        button_create_grid = swing.JButton("Create projected grid")
        # Read grid button
        button_read_grid = swing.JButton("Read grid from model file")
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
                .addGroup(swing.GroupLayout.Alignment.CENTER, layout.createSequentialGroup()
                    .addComponent(button_create_grid)
                    .addComponent(button_read_grid))
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
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(button_create_grid)
                    .addComponent(button_read_grid))
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
        )
        layout.setVerticalGroup(
            layout.createSequentialGroup()
                .addComponent(self.ta_emis_grid)
                .addComponent(panel_grid)
                .addGap(15)
                .addComponent(button_plot)
        )

    def update_run_configure(self, run_config):
        """
        Update run configure.

        :param run_config: (*RunConfigure*) Run configure object.
        """
        self.run_config = run_config
        
        self.emis_grid = self.run_config.emission_module.emis_grid
        self.ta_emis_grid.setText(self.emis_grid.__str__())
        
        self.model_grid = self.run_config.spatial_model_grid
        self.text_xmin.setText(str(self.model_grid.x_orig))
        self.text_xcell.setText(str(self.model_grid.x_cell))
        self.text_xnum.setText(str(self.model_grid.x_num))
        self.text_ymin.setText(str(self.model_grid.y_orig))
        self.text_ycell.setText(str(self.model_grid.y_cell))
        self.text_ynum.setText(str(self.model_grid.y_num))

    def click_plot(self, e):
        """
        Read script button click event.
        """
        proj_str = self.text_proj.getText()
        proj = geolib.projinfo(proj4string=proj_str)
        xmin = float(self.text_xmin.getText())
        xnum = int(self.text_xnum.getText())
        xcell = float(self.text_xcell.getText())
        ymin = float(self.text_ymin.getText())
        ynum = int(self.text_ynum.getText())
        ycell = float(self.text_ycell.getText())
        self.model_grid = GridDesc(proj=proj, x_orig=xmin, x_cell=xcell, x_num=xnum,
                                   y_orig=ymin, y_cell=ycell, y_num=ynum)

        # Plot
        plt.clf()
        plt.subplot(1, 2, 1, axestype='map', projection=self.emis_grid.proj)
        plt.geoshow('country')
        x = self.emis_grid.x_coord
        y = self.emis_grid.y_coord
        xx, yy = np.grid_edge(x, y)
        plt.plot(xx, yy, color='b', linewidth=2, proj=self.model_grid.proj)
        plt.title('Emission grid')
        plt.xlim(x[0] - (x[-1] - x[0]) * 0.1, x[-1] + (x[-1] - x[0]) * 0.1)
        plt.ylim(y[0] - (y[-1] - y[0]) * 0.1, y[-1] + (y[-1] - y[0]) * 0.1)

        plt.subplot(1, 2, 2, axestype='map', projection=self.model_grid.proj)
        plt.geoshow('country')
        x = self.model_grid.x_coord
        y = self.model_grid.y_coord
        xx, yy = np.grid_edge(x, y)
        plt.plot(xx, yy, color='r', linewidth=2, proj=self.model_grid.proj)
        plt.title('Model grid')
        plt.xlim(x[0] - (x[-1] - x[0]) * 0.1, x[-1] + (x[-1] - x[0]) * 0.1)
        plt.ylim(y[0] - (y[-1] - y[0]) * 0.1, y[-1] + (y[-1] - y[0]) * 0.1)
