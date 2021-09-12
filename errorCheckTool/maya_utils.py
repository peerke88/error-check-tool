from maya import cmds


def history_objects():
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