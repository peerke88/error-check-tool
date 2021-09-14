from errorCheckTool.py23 import *
from errorCheckTool.qt_util import *

import os, re, stat, shutil, platform, logging, tempfile, glob, warnings, webbrowser
from functools import partial
from maya import cmds

from errorCheckTool import mayaWidget
from errorCheckTool.maya_utils import *

__VERSION__ = "2.0.20210914"
_DIR = os.path.dirname(__file__)


class ErrorCheckUI(mayaWidget.DockWidget):

    toolName = 'Check Tool: %s' % __VERSION__

    def __init__(self, newPlacement=False, parent=None):
        super(ErrorCheckUI, self).__init__(parent)

        self.setWindowIcon(QIcon(":/commandButton.png"))
        self.setWindowTitle(self.__class__.toolName)

        mainLayout = nullVBoxLayout()
        self.setLayout(mainLayout)

        self.__defaults()
        self.__uiElements()
        self.addSearchFunctions()

        if not newPlacement:
            self.loadUIState()

    def __defaults(self):
        _ini = os.path.join(_DIR, 'settings.ini')
        self.settings = QSettings(_ini, QSettings.IniFormat)
        self.buildInfo = {}
        self.uniqueGeometryList = []
        self.allShapes = []
        self.allCommonShaders = []
        self.searchFunctions = OrderedDict()
        self.searchFunctions["Basic"] = ["History", "xForms"]
        self.searchFunctions["Layout"] = ["layers", "Hidden Objects"]
        self.searchFunctions["Naming"] = ["Default and pasted Objects", "Unigue names"]
        self.searchFunctions["Shaders"] = ["Default and pasted Objects", "Pasted shaders"]
        self.searchFunctions["Modelling"] = ["Holes", "Locked normals", "N-gons", "Legal UV's", "Lamina faces", "Zero edge lenght",
                                             "Zero geometry data", "Unmapped faces", "Concave faces"]
        self.searchFunctions["Channels"] = ["Keyed objects", "constraints", "Expressions"]
        self.searchFunctions["Extra"] = ["Triangulation percentage", "Resolution gate", "Bounding box", "Average position"]
        self.checkConnections = OrderedDict()

    def __uiElements(self):
        # --- top
        topLayout = nullHBoxLayout()
        topLayout.addItem(QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Minimum))
        _toolIcon = toolButton(os.path.join(_DIR, "perryToolLogo.png"), size=40)
        topLayout.addWidget(_toolIcon)
        topLayout.addItem(QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.layout().addLayout(topLayout)
        # --- search + errorList
        vLayout = QHBoxLayout()
        self.layout().addLayout(vLayout)

        self._splitter = QSplitter()
        vLayout.addWidget(self._splitter)

        self.searchGroup = QGroupBox("search for:")
        self.errorList = QGroupBox("Errors:")

        for w in [self.searchGroup, self.errorList]:
            w.setLayout(nullVBoxLayout(size=3))
            self._splitter.addWidget(w)

        # --- progress and execute
        exLayout = nullHBoxLayout()
        self.exButton = QPushButton("Check current scene")
        self._progressBar = QProgressBar()
        for w in [self.exButton, self._progressBar]:
            exLayout.addWidget(w)
        self.layout().addLayout(exLayout)

    def addSearchFunctions(self):
        for topic, info in self.searchFunctions.items():

            topicGrp = QGroupBox(topic.upper())
            topicGrp.setStyleSheet("QGroupBox { border: 2px solid gray; border-radius: 10px; } ")
            topicGrp.setCheckable(True)
            topicGrp.setLayout(nullVBoxLayout(size=5))
            topicGrp.layout().addWidget(QLabel())
            topicGrp.toggled.connect(self.onToggled)

            self.checkConnections[topic] = []
            for check in info:
                _check = QCheckBox(check)
                _check.setChecked(True)
                topicGrp.layout().addWidget(_check)
                self.checkConnections[check] = True
                _check.toggled.connect(partial(self.toggleConn, check))

            self.searchGroup.layout().addWidget(topicGrp)
        self.searchGroup.layout().addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def toggleConn(self, check, *args):
        self.checkConnections[check] = self.sender().isChecked()

    def onToggled(self, on):
        # hacky override to make sure everything in the groupbox is not disabled on click
        for box in self.sender().findChildren(QCheckBox):
            box.setChecked(on)
            box.setEnabled(True)

    def saveUIState(self):
        """ save the current state of the ui in a seperate ini file, this should also hold information later from a seperate settings window

        :todo: instead of only geometry also store torn of tabs for each posssible object
        :todo: save the geometries of torn of tabs as well
        """
        self.settings.setValue("geometry", self.saveGeometry())

    def loadUIState(self):
        """ load the previous set information from the ini file where possible, if the ini file is not there it will start with default settings
        """
        getGeo = self.settings.value("geometry", None)
        if not getGeo in [None, "None"]:
            self.restoreGeometry(getGeo)

    def hideEvent(self, event):
        """ the hide event is something that is triggered at the same time as close,
        sometimes the close event is not handled correctly by maya so we add the save state in here to make sure its always triggered
        :note: its only storing info so it doesnt break anything
        """
        self.saveUIState()

        if not event is None:
            super(ErrorCheckUI, self).hideEvent(event)

    def closeEvent(self, event):
        """ the close event,
        we save the state of the ui but we also force delete a lot of the skinningtool elements,
        normally python would do garbage collection for you, but to be sure that nothing is stored in memory that does not get deleted we
        force the deletion here as well. somehow this avoids crashes in maya!
        """
        self.saveUIState()
        self.deleteLater()
        return True


def showUI(newPlacement=False):
    """ convenience function to show the current user interface in maya,

    :param newPlacement: if `True` will force the tool to not read the ini file, if `False` will open the tool as intended
    :type newPlacement: bool
    """
    dock = ErrorCheckUI(newPlacement, parent=None)
    dock.run()
    return dock


'''
import sys

sys.path.insert(0,r"\error-check-tool")

toRem = []
for key in list(sys.modules.keys()):
    if key.startswith('error'):
        del sys.modules[key]

from errorCheckTool import checkTool
_bla = checkTool.showUI()
'''

# self.searchFunctions = {
#             "Basic": {"History": partial(history_objects, self.uniqueGeometryList, self.allShapes, self._progressBar),
#                       "xForms": partial(xforms, self.uniqueGeometryList, self._progressBar)},
#             "Layout": {"layers": partial(layers, self._progressBar),
#                        "Hidden Objects": partial(hidden_objects, self.uniqueGeometryList, self._progressBar)},
#             "Naming": {"Default and pasted Objects": partial(default_and_pasted_objects, self.uniqueGeometryList, self._progressBar),
#                        "Unigue names": partial(uniqueNames, self._progressBar)},
#             "Shaders": {"Default and pasted Objects": partial(default_shader, self.uniqueGeometryList, self._progressBar),
#                         "Pasted shaders": partial(all_shaders, self.allCommonShaders, self._progressBar)},
#             "Modelling": {"Holes": partial(holes, self._progressBar),
#                           "Locked normals": partial(locked_normals, self.uniqueGeometryList, self._progressBar),
#                           "N-gons": partial(ngons, self.uniqueGeometryList, self._progressBar),
#                           "Legal UV's": partial(legal_uvs, self.uniqueGeometryList, self._progressBar),
#                           "Lamina faces": partial(lamina_faces, self.uniqueGeometryList, self._progressBar),
#                           "Zero edge lenght": partial(zero_edge_length, self._progressBar),
#                           "Zero geometry data": partial(zero_geometry_area, self._progressBar),
#                           "Unmapped faces": partial(unmapped_faces, self._progressBar),
#                           "Concave faces": partial(concave_faces, self._progressBar)},
#             "Channels": {"Keyed objects": partial(keyed_objects, self.uniqueGeometryList, self._progressBar),
#                          "constraints": partial(constraints, self._progressBar),
#                          "Expressions": partial(expressions, self._progressBar)},
#             "Extra": {"Triangulation percentage": partial(triangulation_percentage, self.uniqueGeometryList, self._progressBar),
#                       "Resolution gate": partial(resolution_gate, self._progressBar),
#                       "Bounding box": partial(scene_size_position, self.uniqueGeometryList, True, False, self._progressBar),
#                       "Average position": partial(scene_size_position, self.uniqueGeometryList, False, True, self._progressBar)},

#         }
