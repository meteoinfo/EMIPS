# coding=utf-8

from javax import swing
from java import awt
from java.awt.event import MouseEvent
from javax.swing.table import AbstractTableModel
from emips.utils import SectorEnum


class FrmSectors(swing.JDialog):

    def __init__(self, frm_main, model):
        super(FrmSectors, self).__init__(frm_main, model)

        self.frm_main = frm_main
        self.run_config = frm_main.run_config
        self.title = "Edit sectors"
        self.ok = False
        self.init_gui()

    def init_gui(self):
        # Sector table
        self.sectors = self.run_config.emission_sectors
        col_names = ["Sector", "SCC"]
        self.data_model = SectorTableModel(self.sectors, col_names)
        self.table = swing.JTable(self.data_model)
        self.table.mouseClicked = self.click_table

        scrollPane = swing.JScrollPane()
        scrollPane.setPreferredSize(awt.Dimension(300, 200))
        scrollPane.getViewport().setView(self.table)

        # Add sector
        self.combobox_sectors = swing.JComboBox()
        self.update_combobox_sectors()
        button_add = swing.JButton("Add a sector")
        button_add.actionPerformed = self.click_add

        # OK button
        button_ok = swing.JButton("OK")
        button_ok.actionPerformed = self.click_ok

        # Layout
        layout = swing.GroupLayout(self.contentPane)
        self.contentPane.setLayout(layout)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)
        layout.setHorizontalGroup(
            layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
            .addComponent(scrollPane)
            .addGroup(swing.GroupLayout.Alignment.CENTER, layout.createSequentialGroup()
                      .addComponent(self.combobox_sectors)
                      .addComponent(button_add))
            .addGap(15)
            .addComponent(button_ok, swing.GroupLayout.Alignment.CENTER)
            .addGap(15)
        )
        layout.setVerticalGroup(
            layout.createSequentialGroup()
            .addComponent(scrollPane)
            .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
                      .addComponent(self.combobox_sectors)
                      .addComponent(button_add))
            .addGap(15)
            .addComponent(button_ok)
            .addGap(15)
        )

        self.pack()

    def update_combobox_sectors(self):
        self.combobox_sectors.removeAllItems()
        for sector in SectorEnum:
            if sector not in self.sectors:
                self.combobox_sectors.addItem(sector)

    def click_table(self, e):
        if e.getButton() == MouseEvent.BUTTON3:
            menu = swing.JPopupMenu()
            menu_remove = swing.JMenuItem("Remove sector")
            menu_remove.actionPerformed = self.click_menu_remove
            menu.add(menu_remove)
            menu.show(e.getComponent(), e.getX(), e.getY())

    def click_menu_remove(self, e):
        row = self.table.getSelectedRow()
        if row >= 0:
            self.data_model.removeRow(row)
            self.update_combobox_sectors()

    def click_add(self, e):
        sector = self.combobox_sectors.getSelectedItem()
        self.data_model.addRow(sector)
        self.update_combobox_sectors()

    def click_ok(self, e):
        self.ok = True
        self.dispose()


class SectorTableModel(AbstractTableModel):

    def __init__(self, sectors, col_names):
        self.sectors = sectors
        self.col_names = col_names

    def isCellEditable(self, row, column):
        if column == 1:
            return True
        else:
            return False

    def getRowCount(self):
        return len(self.sectors)

    def getColumnCount(self):
        return len(self.col_names)

    def getValueAt(self, row, column):
        if column == 0:
            return self.sectors[row].name
        else:
            return self.sectors[row].scc

    def addRow(self, sector):
        self.sectors.append(sector)
        self.fireTableDataChanged()

    def removeRow(self, row):
        self.sectors.remove(self.sectors[row])
        self.fireTableDataChanged()
