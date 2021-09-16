# -*- coding: utf-8 -*-
"""
this file will handle everything to make sure that we have a correct package installed
these functions should only be called from the MEL file
and its only created because MEL is extremely limited
"""
import os, shutil, datetime, tempfile, zipfile, warnings

CURRENTFOLDER = os.path.dirname(__file__)

from errorCheckTool.qt_util import *
from maya import cmds

__VERSION__ = "3.0.20210916"


class InstallWindow(QDialog):
    def __init__(self, scriptDir, parent=None):
        super(InstallWindow, self).__init__(parent)

        self.setWindowTitle("install errorCheckTool tools %s" % __VERSION__)

        self.__scriptDir = scriptDir
        self.__errCheckFile = os.path.normpath(os.path.join(self.__scriptDir, "errorCheckTool"))
        self.__exists = os.path.exists(self.__errCheckFile)
        self.__oldSettings = os.path.normpath(os.path.join(self.__errCheckFile, "settings.ini"))

        # ---- simple banner
        self.setLayout(nullLayout(QVBoxLayout, size=1))

        lbl = toolButton(os.path.join(CURRENTFOLDER, "curveCreator", "icons", "TextCurve.png"))
        self.layout().addWidget(lbl)

        # ---- install location
        h = nullLayout(QHBoxLayout)
        self.layout().addLayout(h)
        self._installLine = QLineEdit(self.__scriptDir)
        self._installLine.setEnabled(False)
        folderBtn = toolButton(":/SP_DirOpenIcon.png")
        folderBtn.clicked.connect(self._searchInstallLocation)

        for w in [QLabel("install location:"), self._installLine, folderBtn]:
            h.addWidget(w)

        # ---- bbasic functions when curve creator already exist
        self.cbx = QComboBox()
        for item in ["backup", "replace"]:
            self.cbx.addItem(item)
        self.layout().addWidget(self.cbx)
        self.cbx.hide()

        self.oldSettings = QCheckBox("keep old settings?")
        if os.path.exists(self.__oldSettings):
            self.oldSettings.setChecked(True)
        self.layout().addWidget(self.oldSettings)
        self.oldSettings.hide()

        if self.__exists:
            self.cbx.show()
            self.oldSettings.show()

        # ---- the installButtons

        self.layout().addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))
        installBtn = pushButton("install error check tool")
        self.layout().addWidget(installBtn)
        self.progress = QProgressBar()
        self.layout().addWidget(self.progress)

        self.layout().addWidget(QLabel("use the following python code to start the tool"))
        self.layout().addWidget(QLabel("(note: maya needs to be restarted for it to work!)"))
        infoEdit = QPlainTextEdit()
        infoString = "from errorCheckTool import checkTool\nerTool = checkTool.showUI()"
        infoEdit.setPlainText(infoString)
        infoEdit.setReadOnly(True)
        self.layout().addWidget(infoEdit)

        installBtn.clicked.connect(self.install)

    def _searchInstallLocation(self, *args):
        fd = QFileDialog.getExistingDirectory(self, "choose install location", self.__scriptDir)
        if fd is None or fd in ['', []]:
            return
        self.__scriptDir = fd
        self._installLine.setText(fd)

        self.__errCheckFile = os.path.normpath(os.path.join(self.__scriptDir, "errorCheckTool"))
        self.__exists = os.path.exists(self.__errCheckFile)
        if self.__exists:
            self.cbx.show()
            self.oldSettings.show()
        else:
            self.cbx.hide()
            self.oldSettings.hide()
        self.__oldSettings = os.path.normpath(os.path.join(self.__errCheckFile, "settings.ini"))

    def install(self):
        setProgress(0, self.progress, "start installing the error check tool")
        if self.__exists:
            # ---- copy old settings file
            if os.path.exists(self.__oldSettings) and self.oldSettings.isChecked():
                newIni = os.path.normpath(os.path.join(CURRENTFOLDER, "errorCheckTool/settings.ini"))
                with open(newIni, "w") as fh:
                    pass
                shutil.copy2(self.__oldSettings, newIni)
                setProgress(10, self.progress, "copied old settings")

            # ---- check what to do with previous version
            if self.cbx.currentIndex() == 1:
                shutil.rmtree(self.__errCheckFile)
                setProgress(30, self.progress, "removed original folder")
            else:
                now = datetime.datetime.now()
                versionDate = "%s%02d%02d" % (now.year, now.month, now.day)
                backup = os.path.normpath(os.path.join(self.__scriptDir, "Backup_%s" % versionDate))
                if os.path.exists(backup):
                    print("backup already created: %s" % backup)
                else:
                    shutil.move(self.__errCheckFile, backup)
                    setProgress(30, self.progress, "backed up folder as: Backup_%s" % versionDate)

        setProgress(50, self.progress, "move error check tool")
        shutil.move(os.path.normpath(os.path.join(CURRENTFOLDER, "errorCheckTool")), os.path.normpath(os.path.join(self.__scriptDir)))
        if not os.path.exists(os.path.normpath(os.path.join(self.__scriptDir, "__init__.py"))):
            shutil.move(os.path.normpath(os.path.join(CURRENTFOLDER, "__init__.py")), os.path.normpath(os.path.join(self.__scriptDir, "__init__.py")))
        setProgress(100, self.progress, "error check tool installed")

        self.close()


def doFunction(useLocalMayaFolder=True):
    """use this function to gather all the data necessary that is to be moved"""
    currentMaya = cmds.about(v=1)
    if useLocalMayaFolder:
        scriptDir = cmds.internalVar(userScriptDir=1)  # < move to a local path in maya for testing purposes
    else:
        scriptDir = cmds.internalVar(userScriptDir=1).replace("%s/" % currentMaya, "")

    myWindow = InstallWindow(scriptDir, parent=get_maya_window())
    myWindow.exec_()
