# coding=utf-8

from javax import swing
from java import awt
from java.awt.event import MouseEvent
from javax.swing.table import AbstractTableModel
from emips.chem_spec import PollutantEnum


class FrmPollutants(swing.JDialog):

    def __init__(self, frm_main, model):
        super(FrmPollutants, self).__init__(frm_main, model)

        self.frm_main = frm_main
        self.run_config = frm_main.run_config
        self.title = "Edit pollutants"
        self.ok = False
        self.init_gui()

    def init_gui(self):
        # Pollutant table
        self.pollutants = self.run_config.emission_pollutants
        col_names = ["Pollutant", "Units"]
        self.data_model = PollutantTableModel(self.pollutants, col_names)
        self.table = swing.JTable(self.data_model)
        self.table.mouseClicked = self.click_table

        scrollPane = swing.JScrollPane()
        scrollPane.setPreferredSize(awt.Dimension(300, 200))
        scrollPane.getViewport().setView(self.table)

        # Add pollutant
        self.combobox_pollutants = swing.JComboBox()
        self.update_combobox_pollutants()
        button_add = swing.JButton("Add a pollutant")
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
                      .addComponent(self.combobox_pollutants)
                      .addComponent(button_add))
            .addGap(15)
            .addComponent(button_ok, swing.GroupLayout.Alignment.CENTER)
            .addGap(15)
        )
        layout.setVerticalGroup(
            layout.createSequentialGroup()
            .addComponent(scrollPane)
            .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
                      .addComponent(self.combobox_pollutants)
                      .addComponent(button_add))
            .addGap(15)
            .addComponent(button_ok)
            .addGap(15)
        )

        self.pack()

    def update_combobox_pollutants(self):
        self.combobox_pollutants.removeAllItems()
        for pollutant in PollutantEnum:
            if pollutant not in self.pollutants:
                self.combobox_pollutants.addItem(pollutant)

    def click_table(self, e):
        if e.getButton() == MouseEvent.BUTTON3:
            menu = swing.JPopupMenu()
            menu_remove = swing.JMenuItem("Remove pollutant")
            menu_remove.actionPerformed = self.click_menu_remove
            menu.add(menu_remove)
            menu.show(e.getComponent(), e.getX(), e.getY())

    def click_menu_remove(self, e):
        row = self.table.getSelectedRow()
        if row >= 0:
            self.data_model.removeRow(row)
            self.update_combobox_pollutants()

    def click_add(self, e):
        pollutant = self.combobox_pollutants.getSelectedItem()
        self.data_model.addRow(pollutant)
        self.update_combobox_pollutants()

    def click_ok(self, e):
        self.ok = True
        self.dispose()


class PollutantTableModel(AbstractTableModel):

    def __init__(self, pollutants, col_names):
        self.pollutants = pollutants
        self.col_names = col_names

    def isCellEditable(self, row, column):
        if column == 1:
            return True
        else:
            return False

    def getRowCount(self):
        return len(self.pollutants)

    def getColumnCount(self):
        return len(self.col_names)

    def getValueAt(self, row, column):
        if column == 0:
            return self.pollutants[row].name
        else:
            return self.pollutants[row].units

    def addRow(self, pollutant):
        self.pollutants.append(pollutant)
        self.fireTableDataChanged()

    def removeRow(self, row):
        self.pollutants.remove(self.pollutants[row])
        self.fireTableDataChanged()
