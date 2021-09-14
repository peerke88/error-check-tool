from errorCheckTool.py23 import *
from errorCheckTool.qt_util import *

import os, re, stat, shutil, platform, logging, tempfile, glob, warnings, webbrowser
from functools import partial
from maya import cmds

from errorCheckTool import mayaWidget
from errorCheckTool.maya_utils import *
from messageProgressBar import MessageProgressBar
__VERSION__ = "3.0.20210914"
_DIR = os.path.dirname(__file__)


class ErrorCheckUI(mayaWidget.DockWidget):

    toolName = 'Error Check Tool: %s' % __VERSION__

    def __init__(self, newPlacement=False, parent=None):
        super(ErrorCheckUI, self).__init__(parent)

        self.setWindowIcon(QIcon(os.path.join(_DIR, "icons", "perryToolLogo.png")))
        self.setWindowTitle(self.__class__.toolName)

        mainLayout = nullVBoxLayout()
        self.setLayout(mainLayout)

        self.__defaults()
        self.__uiElements()
        self.addSearchFunctions()
        self.addErrorFunctions()

        if not newPlacement:
            self.loadUIState()

    def __defaults(self):
        _ini = os.path.join(_DIR, 'settings.ini')
        self.settings = QSettings(_ini, QSettings.IniFormat)

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
        _toolIcon = toolButton(os.path.join(_DIR, "icons", "perryToolLogo.png"), size=40)
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
        self.exButton.clicked.connect(self.checkScene)
        self._detailProgressBar = MessageProgressBar()
        self._globalProgressBar = MessageProgressBar()
        for w in [self.exButton, self._detailProgressBar, self._globalProgressBar]:
            exLayout.addWidget(w)
        self.layout().addLayout(exLayout)

    def addErrorFunctions(self):
        selectLayout = nullHBoxLayout()
        rb1 = QRadioButton("single", self)
        rb2 = QRadioButton("multi", self)

        self.errorTree = QTreeWidget()
        self.errorTree.setHeaderHidden(True)
        self.errorTree.itemSelectionChanged.connect(self.handleChanged)

        for rb in [rb1, rb2]:
            rb.toggled.connect(self.setSelectionMode)
            selectLayout.addWidget(rb)

        self.errorList.layout().addLayout(selectLayout)
        self.errorList.layout().addWidget(self.errorTree)

        self._extraGrpBox = QGroupBox()
        self.errorList.layout().addWidget(self._extraGrpBox)
        rb2.setChecked(True)

    def setSelectionMode(self, *args):
        if self.sender().text().lower() == "multi":
            self.errorTree.setSelectionMode(QAbstractItemView.ExtendedSelection)
            return
        self.errorTree.setSelectionMode(QAbstractItemView.SingleSelection)

    def handleChanged(self, *args):
        items = []
        allSelected = self.errorTree.selectedItems()
        if allSelected != []:
            for item in allSelected:
                if str(item.toolTip(0)) != 'emptyData':
                    items.append(str(item.toolTip(0)))
            if len(items) == 0:
                cmds.select(cl=True)
            else:
                cmds.select(items)

    def addSearchFunctions(self):
        for topic, info in self.searchFunctions.items():

            topicGrp = QGroupBox(topic.upper())
            topicGrp.setStyleSheet("QGroupBox { border: 2px solid gray; border-radius: 10px; } ")
            topicGrp.setCheckable(True)
            topicGrp.setLayout(nullVBoxLayout(size=5))
            topicGrp.layout().addWidget(QLabel())
            topicGrp.toggled.connect(self.onToggled)

            # self.checkConnections[topic] = []
            for check in info:
                _check = QCheckBox(check)
                _check.setChecked(True)
                topicGrp.layout().addWidget(_check)
                self.checkConnections[check] = True
                _check.toggled.connect(partial(self.toggleConn, _check, check))

            self.searchGroup.layout().addWidget(topicGrp)
        self.searchGroup.layout().addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def toggleConn(self, sender, check, *args):
        if self.sender() is not None:
            sender = self.sender()
        self.checkConnections[check] = sender.isChecked()

    def onToggled(self, on):
        # hacky override to make sure everything in the groupbox is not disabled on click
        for box in self.sender().findChildren(QCheckBox):
            box.setChecked(on)
            box.setEnabled(True)

    def checkScene(self):
        self.errorTree.clear()
        self.allObjects = cmds.ls(o=True, g=True, l=True)
        if len(self.allObjects) == 0:
            cmds.error('no objects in scene!')
            return

        self.allShapes = cmds.ls(o=True, g=True)
        self.allCommonShaders = cmds.ls(type=["lambert", "phong", "blinn", "anisotropic", "phongE"])
        self.allobjectsparents = cmds.listRelatives(self.allObjects, p=True, f=True)
        self.uniqueGeometryList = set(self.allobjectsparents)

        _functions = {
            "History": partial(history_objects, self.uniqueGeometryList, self.allShapes, self._detailProgressBar),
            "xForms": partial(xforms, self.uniqueGeometryList, self._detailProgressBar),
            "layers": partial(layers, self._detailProgressBar),
            "Hidden Objects": partial(hidden_objects, self.uniqueGeometryList, self._detailProgressBar),
            "Default and pasted Objects": partial(default_and_pasted_objects, self.uniqueGeometryList, self._detailProgressBar),
            "Unigue names": partial(uniqueNames, self._detailProgressBar),
            "Default and pasted Objects": partial(default_shader, self.uniqueGeometryList, self._detailProgressBar),
            "Pasted shaders": partial(all_shaders, self.allCommonShaders, self._detailProgressBar),
            "Holes": partial(holes, self._detailProgressBar),
            "Locked normals": partial(locked_normals, self.uniqueGeometryList, self._detailProgressBar),
            "N-gons": partial(ngons, self.uniqueGeometryList, self._detailProgressBar),
            "Legal UV's": partial(legal_uvs, self.uniqueGeometryList, self._detailProgressBar),
            "Lamina faces": partial(lamina_faces, self.uniqueGeometryList, self._detailProgressBar),
            "Zero edge lenght": partial(zero_edge_length, self._detailProgressBar),
            "Zero geometry data": partial(zero_geometry_area, self._detailProgressBar),
            "Unmapped faces": partial(unmapped_faces, self._detailProgressBar),
            "Concave faces": partial(concave_faces, self._detailProgressBar),
            "Keyed objects": partial(keyed_objects, self.uniqueGeometryList, self._detailProgressBar),
            "constraints": partial(constraints, self._detailProgressBar),
            "Expressions": partial(expressions, self._detailProgressBar),
            "Triangulation percentage": partial(triangulation_percentage, self.uniqueGeometryList, self._detailProgressBar),
            "Resolution gate": partial(resolution_gate, self._detailProgressBar),
            "Bounding box": partial(scene_size_position, self.uniqueGeometryList, True, False, self._detailProgressBar),
            "Average position": partial(scene_size_position, self.uniqueGeometryList, False, True, self._detailProgressBar)
        }

        amount = sum(self.checkConnections.values())
        percentage = 99.0 / amount

        for index, (name, toUse) in enumerate(self.checkConnections.items()):
            if not toUse:
                continue
            _dict = _functions[name]()
            for key, value in _dict.items():
                if key in ["res", "avg", "bbox", "tri"]:
                    continue
                self.createListWidget(value, key)
            setProgress(index * percentage, self._globalProgressBar, "Processing %s" % name)

        setProgress(100, self._globalProgressBar, "Finished")

    def addParent(self, parent, column, title, data):
        item = QTreeWidgetItem(parent, [title])
        item.setData(column, Qt.UserRole, data)
        item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
        item.setExpanded(False)
        item.setToolTip(column, data)
        return item

    def addChild(self, parent, column, title, data):
        item = QTreeWidgetItem(parent, [title])
        item.setData(column, Qt.UserRole, data)
        item.setToolTip(column, data)
        return item

    def createListWidget(self, inPutList, title):
        self.CurrentItem = self.addParent(self.errorTree.invisibleRootItem(), 0, title, 'emptyData')

        if inPutList == []:
            self.addChild(self.CurrentItem, 0, "'empty'", "emptyData")
            self.CurrentItem.setForeground(0, QBrush(QColor("green")))
        else:
            self.CurrentItem.setForeground(0, QBrush(QColor("red")))
            for object in inPutList:
                self.addChild(self.CurrentItem, 0, object.split('|')[-1], object)

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
