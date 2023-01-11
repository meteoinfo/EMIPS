import importlib
import sys

gui_path = 'D:/MyProgram/java/MeteoInfoDev/toolbox/EMIPS/emips/gui'
if gui_path not in sys.path:
    sys.path.append(gui_path)
#emips.gui.run_panel = importlib.import_module('run_panel')

reload(emips.gui.form.frm_about)
reload(emips.gui.form)
reload(emips.gui.emission_panel)
reload(emips.gui.temporal_panel)
reload(emips.gui.spatial_panel)
reload(emips.gui.chemical_panel)
reload(emips.gui.vertical_panel)
reload(emips.gui.run_panel)
reload(emips.gui.main_gui)
reload(emips.gui.configure)
reload(emips.gui)
reload(emips)