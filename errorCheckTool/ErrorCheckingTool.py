#              only for maya 2011+
#
#
#             ErrorCheckingTool.py 
#             version 1.1, last modified 19-08-2015
#             Copyright (C) 2014 Perry Leijten
#             Email: perryleijten@gmail.com
#             Website: www.perryleijten.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# See http://www.gnu.org/licenses/gpl.html for a copy of the GNU General 
# Public License.
#--------------------------------------------------------------------------------#
#                    I N S T A L L A T I O N:
#
# Copy the "ErrorCheckingTool.py" together with "ErrorCheckingTool.ui" and the Icon folder to your Maya scriptsdirectory:
#     windows:
#      MyDocuments\Maya\scripts\
#   mac osx:
#      /Library/Preferences/Autodesk/maya/scripts/
#         use this text as a python script within Maya:
'''
import ErrorCheckingTool
ErrorCheckingTool.StartUI()
'''
# this text can be entered from the script editor and can be made into a button
#
# note: pyside(standard with maya 2014) libraries are necessary to run this file!!!
import os, sys, re, stat, functools,shutil, platform, logging
from maya import mel, cmds, OpenMayaUI

default = "none"
try:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
    from PyQt4 import uic, QtGui
    import sip
    logging.Logger.manager.loggerDict["PyQt4.uic.uiparser"].setLevel(logging.CRITICAL)
    logging.Logger.manager.loggerDict["PyQt4.uic.properties"].setLevel(logging.CRITICAL)
    default = "pyqt4"
except:
    try:
        import xml.etree.ElementTree as xml
        from cStringIO import StringIO
        from PySide.QtGui import *
        from PySide.QtCore import *
        from PySide import QtGui
        import pysideuic, shiboken
        logging.Logger.manager.loggerDict["pysideuic.uiparser"].setLevel(logging.CRITICAL)
        logging.Logger.manager.loggerDict["pysideuic.properties"].setLevel(logging.CRITICAL)
        default = "pyside"
    except:
        try:
            import xml.etree.ElementTree as xml
            from cStringIO import StringIO
            from PySide2.QtGui import *
            from PySide2.QtCore import *
            from PySide2.QtWidgets import *
            from PySide2 import QtGui
            import pyside2uic as pysideuic
            import shiboken2 as shiboken
            logging.Logger.manager.loggerDict["pyside2uic.uiparser"].setLevel(logging.CRITICAL)
            logging.Logger.manager.loggerDict["pyside2uic.properties"].setLevel(logging.CRITICAL)
            default = "pyside2"
        except:
            print "Pyqt or pyside(2) not found please install one of these libraries"



def loadUiType( uiFile ):
    '''workaround to be able to load QT designer uis with both PySide and PyQt4'''
    # http://nathanhorne.com/?p=451
    if default ==  "pyqt4":
        form_class, base_class =  uic.loadUiType( uiFile )
    else:
        parsed = xml.parse( uiFile )
        widget_class = parsed.find( 'widget' ).get( 'class' )
        form_class = parsed.find( 'class' ).text

        with open( uiFile, 'r' ) as f:
            o = StringIO()
            frame = {}

            pysideuic.compileUi( f, o, indent=0 )
            pyc = compile( o.getvalue(), '<string>', 'exec' )
            exec pyc in frame

            form_class = frame[ 'Ui_%s'%form_class ]
            base_class = eval( '%s'%widget_class )
    return form_class, base_class

def wrapinstance( ptr, base=None ):
    '''workaround to be able to wrap objects with both PySide and PyQt4'''
    # http://nathanhorne.com/?p=485'''
    if ptr is None:
        return None
    ptr = long( ptr ) 
    if globals().has_key( 'shiboken' ):
        if base is None:
            qObj = shiboken.wrapInstance( long( ptr ), QObject )
            metaObj = qObj.metaObject()
            cls = metaObj.className()
            superCls = metaObj.superClass().className()
            if hasattr( QtGui, cls ):
                base = getattr( QtGui, cls )
            elif hasattr( QtGui, superCls ):
                base = getattr( QtGui, superCls ) 
            else:
                base = QWidget
        return shiboken.wrapInstance( long( ptr ), base )
    elif globals().has_key( 'sip' ):
        base = QObject
        return sip.wrapinstance( long( ptr ), base )
    else:
        return None

Ui_MainWindow, Ui_BaseClass = loadUiType( '%s/ErrorCheckingTool.ui'%os.path.dirname(__file__) )

class ErrorCheckingTool(Ui_MainWindow, Ui_BaseClass):
    def __init__(self, parent=None):
            # Parent UI to Dock
        super(ErrorCheckingTool, self).__init__(parent)
        self.setupUi( self )
        self.HistoryscrollArea = ''
        self.ExecuteButton.clicked.connect(self.__base_getAllObjects)

        Icon = QIcon("%s/%s.png"%(os.path.dirname(__file__), "perryToolLogo"))
        self.logoLabel.setIcon(Icon)

        self.BasicCheckButton.clicked.connect(self.basic_check)
        self.LayoutCheckButton.clicked.connect(self.layout_check)
        self.NamingCheckButton.clicked.connect(self.naming_check)
        self.ShadersCheckButton.clicked.connect(self.shaders_check)
        self.ModdelingCheckButton.clicked.connect(self.modeling_check)
        self.ChannelsCheckButton.clicked.connect(self.channels_check)
        self.InfoCheckButton.clicked.connect(self.info_check)
        
        self.singleRadial.clicked.connect(self.__selectionSwitch)
        self.multiRadial.clicked.connect(self.__selectionSwitch)
        self.splitter.setSizes([215, 250])
        self.__BuildWidget()

    def __BuildWidget(self):
        self.HistoryscrollArea = QTreeWidget()
        self.HistoryscrollArea.setHeaderHidden(True)
        
        layout = self.verticalLayoutHSA
        layout.addWidget(self.HistoryscrollArea)
        self.HistoryscrollArea.itemSelectionChanged.connect(self.handleChanged)
    
    def __selectionSwitch(self, *args):
        if self.HistoryscrollArea != '':
            if self.singleRadial.isChecked():
                self.HistoryscrollArea.setSelectionMode(QAbstractItemView.SingleSelection)
            else:
                self.HistoryscrollArea.setSelectionMode(QAbstractItemView.ExtendedSelection)
        

    def basic_check(self,*args):
        if str(self.BasicCheckButton.text()) == "uncheck all":
            self.BasicCheckButton.setText("check all")
            self.HistoryCheckBox.setChecked(False)
            self.xformsCheckBox.setChecked(False)
        else:
            self.BasicCheckButton.setText("uncheck all")
            self.HistoryCheckBox.setChecked(True)
            self.xformsCheckBox.setChecked(True)
    
    def layout_check(self,*args):
        if str(self.LayoutCheckButton.text()) == "uncheck all":
            self.LayoutCheckButton.setText("check all")
            self.LayersCheckBox.setChecked(False)
            self.hiddenCheckBox.setChecked(False)
        else:
            self.LayoutCheckButton.setText("uncheck all")
            self.LayersCheckBox.setChecked(True)
            self.hiddenCheckBox.setChecked(True)
    
    def naming_check(self,*args):
        if str(self.NamingCheckButton.text()) == "uncheck all":
            self.NamingCheckButton.setText("check all")
            self.defaultCheckBox.setChecked(False)
            self.uniqueCheckBox.setChecked(False)
        else:
            self.NamingCheckButton.setText("uncheck all")
            self.defaultCheckBox.setChecked(True)
            self.uniqueCheckBox.setChecked(True)
    
    def shaders_check(self,*args):
        if str(self.ShadersCheckButton.text()) == "uncheck all":
            self.ShadersCheckButton.setText("check all")
            self.dshaderCheckBox.setChecked(False)
            self.AllShadersCheckBox.setChecked(False)
        else:
            self.ShadersCheckButton.setText("uncheck all")
            self.dshaderCheckBox.setChecked(True)
            self.AllShadersCheckBox.setChecked(True)

    def modeling_check(self,*args):
        if str(self.ModdelingCheckButton.text()) == "uncheck all":
            self.ModdelingCheckButton.setText("check all")
            self.holeCheckBox.setChecked(False)
            self.lockedCheckBox.setChecked(False)
            self.ngonsCheckBox.setChecked(False)
            self.legalCheckBox.setChecked(False)
            self.laminaCheckBox.setChecked(False)
            self.zeroedgeCheckBox.setChecked(False)
            self.zerogeoCheckBox.setChecked(False)
            self.unmappedCheckBox.setChecked(False)
            self.concaveCheckBox.setChecked(False)
        else:
            self.ModdelingCheckButton.setText("uncheck all")
            self.holeCheckBox.setChecked(True)
            self.lockedCheckBox.setChecked(True)
            self.ngonsCheckBox.setChecked(True)
            self.legalCheckBox.setChecked(True)
            self.laminaCheckBox.setChecked(True)
            self.zeroedgeCheckBox.setChecked(True)
            self.zerogeoCheckBox.setChecked(True)
            self.unmappedCheckBox.setChecked(True)
            self.concaveCheckBox.setChecked(True)

    def channels_check(self,*args):
        if str(self.ChannelsCheckButton.text()) == "uncheck all":
            self.ChannelsCheckButton.setText("check all")
            self.keyedCheckBox.setChecked(False)
            self.constraintsCheckBox.setChecked(False)
            self.exprCheckBox.setChecked(False)
        else:
            self.ChannelsCheckButton.setText("uncheck all")
            self.keyedCheckBox.setChecked(True)
            self.constraintsCheckBox.setChecked(True)    
            self.exprCheckBox.setChecked(True)    
    
    def info_check(self,*args):
        if str(self.InfoCheckButton.text()) == "uncheck all":
            self.InfoCheckButton.setText("check all")
            self.triPercheckBox.setChecked(False)
            self.resolutionCheckBox.setChecked(False)
            self.boundingCheckBox.setChecked(False)
            self.averageCheckBox.setChecked(False)
        else:
            self.InfoCheckButton.setText("uncheck all")
            self.triPercheckBox.setChecked(True)
            self.resolutionCheckBox.setChecked(True)    
            self.boundingCheckBox.setChecked(True)    
            self.averageCheckBox.setChecked(True)    

    def __base_getAllObjects(self,*args):
        
        self.verticalLayoutHSA.removeWidget(self.HistoryscrollArea)
        self.__BuildWidget()
        self.allObjects=cmds.ls(o=True,g=True, l=True)
        if len(self.allObjects) == 0:
            cmds.error('no objects in scene!')
            return

        self.allShapes=cmds.ls(o=True,g=True)
        self.allCommonShaders = cmds.ls(type=["lambert","phong","blinn","anisotropic","phongE"])
        self.allobjectsparents = cmds.listRelatives(self.allObjects, p=True, f=True)
        self.uniqueGeometryList = set(self.allobjectsparents)
        
        if self.HistoryCheckBox.isChecked():
            self.history_objects()
        if self.xformsCheckBox.isChecked():
            self.xforms()
        if self.LayersCheckBox.isChecked():
            self.layers()
        if self.hiddenCheckBox.isChecked():
            self.hidden_objects()
        if self.defaultCheckBox.isChecked():
            self.default_and_pasted_objects()
        if self.uniqueCheckBox.isChecked():
            self.uniqueNames()
        if self.dshaderCheckBox.isChecked():
            self.default_shader()
        if self.AllShadersCheckBox.isChecked():
            self.all_shaders()
        if self.holeCheckBox.isChecked():
            self.holes()
        if self.lockedCheckBox.isChecked():
            self.locked_normals()
        if self.ngonsCheckBox.isChecked():
            self.ngons()    
        if self.legalCheckBox.isChecked():
            self.legal_uvs()    
        if self.laminaCheckBox.isChecked():
            self.lamina_faces()    
        if self.zeroedgeCheckBox.isChecked():
            self.zero_edge_length()    
        if self.zerogeoCheckBox.isChecked():
            self.zero_geometry_area()
        if self.unmappedCheckBox.isChecked():
            self.unmapped_faces()
        if self.concaveCheckBox.isChecked():
            self.concave_faces()
        if self.keyedCheckBox.isChecked():
            self.keyed_objects()
        if self.constraintsCheckBox.isChecked():
            self.constraints()
        if self.exprCheckBox.isChecked():
            self.expressions()
        
        if self.triPercheckBox.isChecked():
            self.triangulation_percentage()
        if self.resolutionCheckBox.isChecked():
            self.resolution_gate()
        if self.boundingCheckBox.isChecked():
            self.scene_size_position(boundingbox=True)
        if self.averageCheckBox.isChecked():
            self.scene_size_position(averagePos=True)
        cmds.select(cl=True)
        self.currentWorkingItem.setText('Finished!')
    
    '''
    for new error checks:
    - add a new checkbox in the qt ui
    - add the checkbox also in the def above
    and create a new defenition like this:

    def xforms(self,*args):
        emptyList = []
        for object in self.uniqueGeometryList:
            error = checkfor error
            emptyList.append(error)
        self.createListWidget( emptyList, 'nameOfList')
            
    '''

    def __lineEdit_Color(self, inLineEdit, inColor):                                                                        
        PalleteColor = QPalette(inLineEdit.palette())
        PalleteColor.setColor(QPalette.Base,QColor(inColor))
        inLineEdit.setPalette(PalleteColor)
    
    def addParent(self, parent, column, title, data):
        item = QTreeWidgetItem(parent, [title])
        item.setData(column, Qt.UserRole, data)
        item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
        item.setExpanded (False)
        item.setToolTip(column, data)
        return item

    def addChild(self, parent, column, title, data):
        item = QTreeWidgetItem(parent, [title])
        item.setData(column, Qt.UserRole, data)
        item.setToolTip(column, data)
        return item
    
    def createListWidget(self, inPutList,  title):
        self.CurrentItem = self.addParent(self.HistoryscrollArea.invisibleRootItem(), 0, title, 'emptyData')
        
        if inPutList == []:
            self.addChild(self.CurrentItem, 0, "'empty'", "emptyData")
            self.CurrentItem.setForeground(0, QBrush(QColor("green")))
        else:
            self.CurrentItem.setForeground(0, QBrush(QColor("red")))
            for object in inPutList:
                self.addChild(self.CurrentItem, 0, object.split('|')[-1], object)

    def history_objects(self,*args):
        ## find all history information
        historyList=[]
        shadingGroupList=[]
        
        totalObjects        = len(self.uniqueGeometryList)
        percentage             = 100.0/totalObjects
        iteration=1;
        self.currentWorkingItem.setText('History')
        for i in self.uniqueGeometryList:
            history = cmds.listHistory(i)
            shapeNode = cmds.listRelatives(i,ad=True, s=True)
            for shape in shapeNode:
                if not cmds.objExists(shape + '.instObjGroups[0]'):
                    continue
                shadingGroup = cmds.listConnections(shape + '.instObjGroups[0]')
                if not shadingGroup == None:
                    shadingGroupList.append(shadingGroup[0])
                objGroup = cmds.listConnections(shape + '.instObjGroups[0]')
                if not objGroup == None:
                    shadingGroupList.append(objGroup[0])
            for j in history:
                if not j in self.allShapes and not j in shadingGroupList:
                    if not 'groupId' in j and not 'lambert2SG' in j:
                        if not 'initialShadingGroup' in j and not 'doneUV' in j:
                            historyList.append(i)
            self.CurrentTool_progressBar.setValue(percentage*iteration)
            qApp.processEvents()
            iteration+=1;

        newhistoryList = list(set(historyList))
        self.createListWidget( newhistoryList, 'history')

    def xforms(self,*args):
         ## search for xforms 
        totalObjects        = len(self.uniqueGeometryList)
        percentage             = 100.0/totalObjects
        iteration=1;
        self.currentWorkingItem.setText('Xforms')
        xformsList=[]
        for i in self.uniqueGeometryList:
            xforms = cmds.xform(i, q=True, t=True)
            if not xforms == [0.0,0.0,0.0]:
                xformsList.append(i)
            xforms = cmds.xform(i, q=True, ro=True)
            if not xforms == [0.0,0.0,0.0]:
                xformsList.append(i)
            xforms = cmds.xform(i, q=True,r=True, s=True)
            if not xforms == [1.0,1.0,1.0]:
                xformsList.append(i)
            self.CurrentTool_progressBar.setValue(percentage*iteration)
            qApp.processEvents()
            iteration+=1;

        self.createListWidget( xformsList, 'Xforms')
            
    def layers(self,*args):
        # layers
        allLayers = cmds.ls(type="displayLayer")
        lockedlayers = []
        totalObjects        = len(self.uniqueGeometryList)
        percentage             = 100.0/totalObjects
        iteration=1;
        self.currentWorkingItem.setText('Layers')
        for i in allLayers:
            try:
                layerQuerystate = cmds.layerButton(i, q=True, ls=True)
                layerQueryvis = cmds.layerButton(i, q=True, lv=True)
                if not layerQuerystate == "normal" or not layerQueryvis == True:
                    lockedlayers.append(i)
            except:
                pass
            self.CurrentTool_progressBar.setValue(percentage*iteration)
            qApp.processEvents()
            iteration+=1;
        self.createListWidget( lockedlayers, 'Locked Layers')
        
    def hidden_objects(self,*args):
        ## amount of hidden objects
        invisibleList =[]
        totalObjects        = len(self.uniqueGeometryList)
        percentage             = 100.0/totalObjects
        iteration=1;
        self.currentWorkingItem.setText('Hidden Objects')
        for i in self.uniqueGeometryList:
            if cmds.getAttr(str(i)+'.v') == 0:
                invisibleList.append(i)
            self.CurrentTool_progressBar.setValue(percentage*iteration)
            qApp.processEvents()
            iteration+=1;

        self.createListWidget( invisibleList, 'Hidden objects')


    def default_and_pasted_objects(self,*args):
        namedList = []
        totalObjects        = len(self.uniqueGeometryList)
        percentage             = 100.0/totalObjects
        iteration=1;
        self.currentWorkingItem.setText('Default and Pasted')
        for i in self.uniqueGeometryList:
            i=i.split('|')[-1]
            if any(x in i for x in ['pCube', 'polySurface', 'pCylinder', 'pSphere',
                                    'pCone', 'pPlane','pTorus', 'pPyramid', 'pPipe', '__Pasted'])
                namedList.append(i)
            self.CurrentTool_progressBar.setValue(percentage*iteration)
            qApp.processEvents()
            iteration+=1;
        self.createListWidget( namedList, 'Default and Pasted')
        
    def uniqueNames(self,*args):
        #unique naming
        similarNames = cmds.ls(type="transform")
        nonUnique=[]
        totalObjects        = len(self.uniqueGeometryList)
        percentage             = 100.0/totalObjects
        iteration=1;
        self.currentWorkingItem.setText('Unique Names')
        for object in similarNames:
            longname = object.split("|")
            if len(longname) > 1:
                nonUnique.append(object)
            self.CurrentTool_progressBar.setValue(percentage*iteration)
            qApp.processEvents()
            
            iteration+=1;

        self.createListWidget( nonUnique, 'Unique Names')

    def default_shader(self,*args):
        defaultLambertGrp = []
        totalObjects        = len(self.uniqueGeometryList)
        percentage             = 100.0/totalObjects
        iteration=1;
        self.currentWorkingItem.setText('Default Shaders')
        for i in self.uniqueGeometryList:
            shaders = cmds.listConnections(cmds.listHistory(i,f=1),type='lambert')
            print shaders
            if not shaders == None:
                for j in shaders:
                    if j == 'lambert1':
                        defaultLambertGrp.append(i)
            self.CurrentTool_progressBar.setValue(percentage*iteration)
            qApp.processEvents()
            
            iteration+=1;
        self.createListWidget( defaultLambertGrp, 'Default Shader')
        
    def all_shaders(self,*args):
        ## search shaders
        pastedShaders = []
        totalObjects        = len(self.uniqueGeometryList)
        percentage             = 100.0/totalObjects
        iteration=1;
        self.currentWorkingItem.setText('Pasted Shaders')
        for i in self.allCommonShaders:
            if 'pasted__' in i:
                pastedShaders.append(i)
            self.CurrentTool_progressBar.setValue(percentage*iteration)
            qApp.processEvents()
            
            iteration+=1;
        
        self.createListWidget( pastedShaders, 'Pasted Shaders')

    def holes(self,*args):
        # find holes
        self.CurrentTool_progressBar.setValue(0)
        self.currentWorkingItem.setText('Holes')
        FacesWithHoles = mel.eval('polyCleanupArgList 3 { "1","2","0","0","0","0","1","0","0","1e-005","0","1e-005","0","1e-005","0","-1","0" };')
        
        self.createListWidget( FacesWithHoles, 'Holes')
        self.CurrentTool_progressBar.setValue(99)

    def locked_normals(self, *args):
        # check for locked normals
        lockedNormals=[]
        totalObjects        = len(self.uniqueGeometryList)
        percentage             = 100.0/totalObjects
        iteration=1;
        self.currentWorkingItem.setText('Locked Normals')
        for object  in self.uniqueGeometryList:
            try:
                vertices =  cmds.filterExpand(cmds.polyListComponentConversion(object,tv=True),sm=31)
                for j in vertices:
                    vertex = j
                    locked = cmds.polyNormalPerVertex(j, q=True, al=True)[0]
                    if locked :
                        lockedNormals.append(object)
            except:
                pass
            self.CurrentTool_progressBar.setValue(percentage*iteration)
            qApp.processEvents()
            
            iteration+=1;
        uniqueLockedList = set(lockedNormals)
        
        self.createListWidget( list(uniqueLockedList), 'Locked Normals')

    def ngons(self,*args):
        ## faces vs triangle ratio + n-gons
        faces = 0
        triangles = 0
        quads = 0
        ngons = 0
        ngonObj = []
        totalObjects        = len(self.uniqueGeometryList)
        percentage             = 100.0/totalObjects
        iteration=1;
        self.currentWorkingItem.setText('N-Gons')
        for i in self.uniqueGeometryList:
            shapeNode = cmds.listRelatives(i,ad=True, s=True)
            try:
                if cmds.objectType(shapeNode[0], isType="mesh"): 
                    numberFaces = cmds.polyEvaluate(i, f=True )
                    if not type(numberFaces) == type(int(1)):
                        continue
                    faces += int(numberFaces)
                    allFaces= cmds.filterExpand(cmds.polyListComponentConversion(i, tf=True), sm=34)
                    for j in allFaces:
                        allvertices= cmds.filterExpand(cmds.polyListComponentConversion(j, tv=True), sm=31)
                        if len(allvertices)==3:
                            triangles+=1
                        if len(allvertices)==4:
                            quads+=1
                        if len(allvertices)>=5:
                            ngons+=1
                            ngonObj.append(j)
            except:
                pass
            self.CurrentTool_progressBar.setValue(percentage*iteration)
            qApp.processEvents()
            iteration+=1;
        
        self.createListWidget( ngonObj, 'N-Gons')

    def legal_uvs(self,*args):
        ## search for uv's outside legal space
        UVList = []
        NoUvList = []
        totalObjects        = len(self.uniqueGeometryList)
        percentage             = 100.0/totalObjects
        iteration=1;
        self.currentWorkingItem.setText("Legal uv's")
        for i in self.uniqueGeometryList:
            try:
                objectUVs = cmds.filterExpand(cmds.polyListComponentConversion(i, tuv=True), sm=35)
                for j in objectUVs:
                    uvPos = cmds.polyEditUV(j, q=True, v=True, u=True)
                    for k in uvPos:
                        if float(k) < 0.0 or float(k) > 1.0:
                            UVList.append(j)
            except:
                NoUvList.append(i)
            self.CurrentTool_progressBar.setValue(percentage*iteration)
            qApp.processEvents()
            
            iteration+=1;
        
        
        self.createListWidget( UVList, "Legal uv's")
        self.createListWidget( NoUvList, "No uv's")

        
    def lamina_faces(self,*args):
        # check for lamina faces
        laminaFacesList = []
        totalObjects        = len(self.uniqueGeometryList)
        percentage             = 100.0/totalObjects
        iteration=1;
        self.currentWorkingItem.setText('Lamina Faces')
        for object  in self.uniqueGeometryList:
            laminaFaces = cmds.polyInfo(object,laminaFaces=True)
            if not laminaFaces == None:
                laminaFacesList += laminaFaces
            self.CurrentTool_progressBar.setValue(percentage*iteration)
            qApp.processEvents()
            
            iteration+=1;
    

        self.createListWidget( laminaFacesList, "Lamina Faces")
        
    def zero_edge_length(self,*args):
        # zero edge lenght
        
        self.CurrentTool_progressBar.setValue(0)
        self.currentWorkingItem.setText('Zero Edge Length')
        zeroEdgeLenght = mel.eval('polyCleanupArgList 3 { "1","2","0","0","0","0","0","0","0","1e-005","1","1e-005","0","1e-005","0","-1","0" };')
        
        self.createListWidget( zeroEdgeLenght, 'Zero Edge Length')
        self.CurrentTool_progressBar.setValue(99)

    def zero_geometry_area(self,*args):
        # zero geometry area
        self.CurrentTool_progressBar.setValue(0)
        self.currentWorkingItem.setText('Zero Face Length')
        zerofaceLenght = mel.eval('polyCleanupArgList 3 { "1","2","0","0","0","0","0","0","1","1e-005","0","1e-005","0","1e-005","0","-1","0" };')
        
        self.createListWidget( zerofaceLenght, 'Zero Face Length')
        self.CurrentTool_progressBar.setValue(99)

    def unmapped_faces(self,*args):
        # unmapped faces
        self.CurrentTool_progressBar.setValue(0)
        self.currentWorkingItem.setText('Zero Map Area')
        zeromaparea = mel.eval('polyCleanupArgList 3 { "1","2","0","0","0","0","0","0","0","1e-005","0","1e-005","0","1e-005","0","-1","0" };')
        
        self.createListWidget( zeromaparea, 'Zero Map Area')
        self.CurrentTool_progressBar.setValue(99)

    def concave_faces(self,*args):
        #concave faces
        concave = mel.eval('polyCleanupArgList 3 { "1","2","0","0","0","1","0","0","0","1e-005","0","1e-005","0","1e-005","0","-1","0" };')
        ngons = mel.eval('polyCleanupArgList 3 { "1","2","0","0","1","0","0","0","0","1e-005","0","1e-005","0","1e-005","0","-1","0" };')
        concaveNotNgon = []
        totalObjects        = len(self.uniqueGeometryList)
        percentage             = 100.0/totalObjects
        iteration=1;
        self.currentWorkingItem.setText('Concave Faces')
        for i in concave:
            if not i in ngons:
                concaveNotNgon.append(i)
            self.CurrentTool_progressBar.setValue(percentage*iteration)
            qApp.processEvents()
            
            iteration+=1;
        
        self.createListWidget( concaveNotNgon, 'Concave Faces')
    
    def keyed_objects(self,*args):
        #keyed objects
        objectWithKeys = []
        totalObjects        = len(self.uniqueGeometryList)
        percentage             = 100.0/totalObjects
        iteration=1;
        self.currentWorkingItem.setText('Keyed Objects')
        for object  in self.uniqueGeometryList:
            translatekey = cmds.keyframe(object, query=True, at='translate',timeChange=True )
            rotatekey = cmds.keyframe(object, query=True, at='rotate',timeChange=True )
            scalekey = cmds.keyframe(object, query=True, at='scale',timeChange=True )
            if not translatekey == None:
                objectWithKeys.append(object)
            elif not rotatekey == None:
                objectWithKeys.append(object)
            elif not scalekey == None:  
                objectWithKeys.append(object) 
            self.CurrentTool_progressBar.setValue(percentage*iteration)
            qApp.processEvents()
            
            iteration+=1;
        
        self.createListWidget( objectWithKeys, 'Keyed Objects')
    
    def constraints(self,*args):
        #constraints
        self.CurrentTool_progressBar.setValue(0)
        self.currentWorkingItem.setText('Constraints')
        constraints = cmds.ls(type="constraint")
        
        self.createListWidget( constraints, 'Constraints')
        self.CurrentTool_progressBar.setValue(99)

    def expressions(self,*args):
         # expressions
        self.CurrentTool_progressBar.setValue(0)
        self.currentWorkingItem.setText('Expressions')
        expressions = cmds.ls(type="expression")
        
        self.createListWidget( expressions, 'Expressions')
        self.CurrentTool_progressBar.setValue(99)
    
    def triangulation_percentage(self,*args):
        ## faces vs triangle ratio + n-gons
        faces = 0
        triangles = 0
        quads = 0
        ngons = 0
        ngonObj = []
        totalObjects        = len(self.uniqueGeometryList)
        percentage             = 100.0/totalObjects
        iteration=1;
        self.currentWorkingItem.setText('Triangulation')
        for i in self.uniqueGeometryList:
            shapeNode = cmds.listRelatives(i,ad=True, s=True)
            try:
                if cmds.objectType(shapeNode[0], isType="mesh"): 
                    numberFaces = cmds.polyEvaluate(i, f=True )
                    if not type(numberFaces) == type(int(1)):
                        continue
                    faces += int(numberFaces)
                    allFaces= cmds.filterExpand(cmds.polyListComponentConversion(i, tf=True), sm=34)
                    for j in allFaces:
                        allvertices= cmds.filterExpand(cmds.polyListComponentConversion(j, tv=True), sm=31)
                        if len(allvertices)==3:
                            triangles+=1
                        if len(allvertices)==4:
                            quads+=1
                        if len(allvertices)>=5:
                            ngons+=1
                            ngonObj.append(i)
            except:
                pass
            self.CurrentTool_progressBar.setValue(percentage*iteration)
            qApp.processEvents()
            
            iteration+=1;
        
        self.triangulation_lineEdit.setText('%.2f'%((float(triangles)/float(faces))*100) + ' %')
    
    def scene_size_position(self,boundingbox=False,averagePos=False):
        #total boundingbox size
        w1=0
        w2=0
        h1=0
        h2=0
        d1=0
        d2=0
        totalObjects        = len(self.uniqueGeometryList)
        percentage             = 100.0/totalObjects
        iteration=1;
        self.currentWorkingItem.setText('BBOX and Pos')
        for object  in self.uniqueGeometryList:
            bbox = cmds.exactWorldBoundingBox(object)
            if bbox[0] < w1:
                w1 = bbox[0]
            if bbox[1] < h1:
                h1 = bbox[1]
            if bbox[2] < d1:
                d1 = bbox[2]
            if bbox[3] > w2:
                w2 = bbox[3]
            if bbox[4] > h2:
                h2 = bbox[4]
            if bbox[5] > d2:
                d2 = bbox[5]
            self.CurrentTool_progressBar.setValue(percentage*iteration)
            qApp.processEvents()
            
            iteration+=1;
        if boundingbox == True:
            self.bbx.setText('%.2f'%(abs(w1)+ abs(w2)))
            self.bby.setText('%.2f'%(abs(h1)+ abs(h2)))
            self.bbz.setText('%.2f'%(abs(d1)+ abs(d2)))
        
        if averagePos == True:
            centerPosx= (w1+w2)/2
            centerPosz= (d1+d2)/2
            
            self.ax.setText('%.2f'%(centerPosx))
            self.az.setText('%.2f'%(centerPosz))

    def resolution_gate(self,*args):
        ## render resolution    
        self.CurrentTool_progressBar.setValue(0)
        self.currentWorkingItem.setText('Resolution')
        wdth = cmds.getAttr("defaultResolution.width")
        hght = cmds.getAttr("defaultResolution.height")
        
        self.resGateWidth.setText(str(wdth))
        self.resGateHeight.setText(str(hght)    )
        self.CurrentTool_progressBar.setValue(100)
    
    def handleChanged(self,*args):
        items = []
        allSelected =  self.HistoryscrollArea.selectedItems()
        if allSelected != []:
            for item in allSelected:
                if str(item.toolTip(0)) != 'emptyData':
                    items.append(str(item.toolTip(0)))
            if len(items) == 0:
                cmds.select(cl=True)
            else:
                cmds.select(items)

    def __dockWindow_Delete(self, *args):                                                                                    
        window_name     = 'ErrorCheck'
        dock_control     = 'ErrorCheck_Dock'
        
            # Remove window
        if cmds.window( window_name, exists=True ):
            cmds.deleteUI( window_name )
        
            # Remove dock
        if (cmds.dockControl(dock_control, q=True, ex=True)):
            cmds.deleteUI(dock_control)    

'''!to do!'''
# channel connection direct connection
# size of uvs
# check for unclosed geometry
# render flags(double sided, reflections refractions etc)
# namespaces ->  cmds.namespaceInfo(lon=True)
# incorrect shape names
# too close vertices and not merged
            
def StartUI():    
    '''starts UI and makes it dockable within Maya'''
    MayaWindowPtr     = wrapinstance(long(OpenMayaUI.MQtUtil.mainWindow()))
    
    window_name     = 'ErrorCheck'
    dock_control     = 'ErrorCheck_Dock'
    
    if cmds.window( window_name, exists=True ):
        cmds.deleteUI( window_name )
    if cmds.window( dock_control, exists=True ):
        cmds.deleteUI( dock_control )
        
    window = ErrorCheckingTool(MayaWindowPtr)
    window.setObjectName(window_name)

    main = QDockWidget(MayaWindowPtr)
    main.setObjectName(dock_control)
    main.setWidget(window)
    main.setFloating(True)
    main.show()
