import inspect
import os
from javax.swing import JMenuItem
from org.meteoinfo.ui.plugin import PluginBase

from .gui.main_gui import MainGUI


class LoadApp(PluginBase):

    def __init__(self):
        self.setName("EMIPS")
        self.setAuthor("Yaqiang Wang & Wenchong Chen")
        self.setVersion("1.0")
        self.setDescription("EMission Inventory Processing System")
        self.app_menu_item = None
        self.milab_app = None

        this_file = inspect.getfile(inspect.currentframe())
        self.path = os.path.abspath(os.path.dirname(this_file))
        # print(self.path)

    def load(self):
        if self.app_menu_item is None:
            self.app_menu_item = JMenuItem('EMIPS', None, actionPerformed=self.click_app_menu_item)
        self.milab_app = self.getApplication()
        app_menu_bar = self.milab_app.getMainMenuBar()
        app_menu = self.milab_app.getPluginMenu()
        app_menu.add(self.app_menu_item)
        app_menu_bar.validate()

    def unload(self):
        if not self.app_menu_item is None:
            self.getApplication().getPluginMenu().remove(self.app_menu_item)
            self.getApplication().getMainMenuBar().repaint()

    def click_app_menu_item(self, e):
        frm_main = MainGUI(self.milab_app)
        #frm_main.size = (1000, 650)
        frm_main.locationRelativeTo = None
        frm_main.visible = True


if __name__ == '__main__':
    app = LoadApp()
    app.click_app_menu_item(None)
