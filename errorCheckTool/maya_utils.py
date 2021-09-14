from maya import cmds
from qt_util import *


def history_objects(uniqueGeometryList, allShapes, progressBar=None):
    # find all history information
    historyList = []
    shadingGroupList = []

    totalObjects = len(uniqueGeometryList)
    percentage = 99.0 / totalObjects
    for index, geo in enumerate(uniqueGeometryList):
        history = cmds.listHistory(geo)
        shapeNode = cmds.listRelatives(geo, ad=True, s=True)
        for shape in shapeNode:
            if not cmds.objExists(shape + '.instObjGroups[0]'):
                continue
            shadingGroup = cmds.listConnections(shape + '.instObjGroups[0]')
            if not shadingGroup is None:
                shadingGroupList.append(shadingGroup[0])
            objGroup = cmds.listConnections(shape + '.instObjGroups[0]')
            if not objGroup == None:
                shadingGroupList.append(objGroup[0])
        for j in history:
            if not j in allShapes and not j in shadingGroupList:
                if not 'groupId' in j and not 'lambert2SG' in j:
                    if not 'initialShadingGroup' in j and not 'doneUV' in j:
                        historyList.append(geo)
        setProgress(percentage * index, progressBar)

    newhistoryList = list(set(historyList))
    return {'history': newhistoryList}


def xforms(uniqueGeometryList, progressBar=None):
     # search for xforms
    totalObjects = len(uniqueGeometryList)
    percentage = 99.0 / totalObjects
    # self.currentWorkingItem.setText('Xforms')
    xformsList = []
    for index, geo in enumerate(uniqueGeometryList):
        xforms = cmds.xform(geo, q=True, t=True)
        if not xforms == [0.0, 0.0, 0.0]:
            xformsList.append(geo)
        xforms = cmds.xform(geo, q=True, ro=True)
        if not xforms == [0.0, 0.0, 0.0]:
            xformsList.append(geo)
        xforms = cmds.xform(geo, q=True, r=True, s=True)
        if not xforms == [1.0, 1.0, 1.0]:
            xformsList.append(geo)
        setProgress(percentage * index, progressBar)

    return {'Xforms': xformsList}


def layers(progressBar=None):
    # layers
    allLayers = cmds.ls(type="displayLayer")
    lockedlayers = []
    totalObjects = len(allLayers)
    percentage = 99.0 / totalObjects
    # self.currentWorkingItem.setText('Layers')
    for index, layer in enumerate(allLayers):
        try:
            layerQuerystate = cmds.layerButton(i, q=True, ls=True)
            layerQueryvis = cmds.layerButton(i, q=True, lv=True)
            if not layerQuerystate == "normal" or not layerQueryvis == True:
                lockedlayers.append(i)
        except:
            pass
        setProgress(percentage * index, progressBar)

    return {'Locked Layers': lockedlayers}


def hidden_objects(uniqueGeometryList, progressBar=None):
    # amount of hidden objects
    invisibleList = []
    totalObjects = len(uniqueGeometryList)
    percentage = 99.0 / totalObjects
    # self.currentWorkingItem.setText('Hidden Objects')
    for index, geo in enumerate(uniqueGeometryList):
        if cmds.getAttr(str(geo) + '.v') == 0:
            invisibleList.append(geo)
        setProgress(percentage * index, progressBar)

    return {'Hidden objects': invisibleList}


def default_and_pasted_objects(uniqueGeometryList, progressBar=None):
    namedList = []
    totalObjects = len(uniqueGeometryList)
    percentage = 99.0 / totalObjects
    # self.currentWorkingItem.setText('Default and Pasted')
    for index, geo in enumerate(uniqueGeometryList):
        geo = geo.split('|')[-1]
        if any(x in geo for x in ['pCube', 'polySurface', 'pCylinder',
                                  'pSphere', 'pCone', 'pPlane', 'pTorus',
                                  'pPyramid', 'pPipe', '__Pasted']):
            namedList.append(geo)
        setProgress(percentage * index, progressBar)

    return {'Default and Pasted': namedList}


def uniqueNames(progressBar=None):
    # unique naming
    similarNames = cmds.ls(type="transform")
    nonUnique = []
    totalObjects = len(similarNames)
    percentage = 99.0 / totalObjects

    # self.currentWorkingItem.setText('Unique Names')
    for index, object in enumerate(similarNames):
        longname = object.split("|")
        if len(longname) > 1:
            nonUnique.append(object)
        setProgress(percentage * index, progressBar)

    return {'Unique Names': nonUnique}


def default_shader(uniqueGeometryList, progressBar=None):
    defaultLambertGrp = []
    totalObjects = len(uniqueGeometryList)
    percentage = 99.0 / totalObjects
    # self.currentWorkingItem.setText('Default Shaders')
    for index, geo in enumerate(uniqueGeometryList):
        shaders = cmds.listConnections(cmds.listHistory(i, f=1), type='lambert')

        if not shaders == None:
            for j in shaders:
                if j == 'lambert1':
                    defaultLambertGrp.append(i)
        setProgress(percentage * index, progressBar)
    return {'Default Shader': defaultLambertGrp}


def all_shaders(allCommonShaders, progressBar=None):
    # search shaders
    pastedShaders = []
    totalObjects = len(allCommonShaders)
    percentage = 99.0 / totalObjects
    # self.currentWorkingItem.setText('Pasted Shaders')
    for index, shader in enumerate(allCommonShaders):
        if 'pasted__' in shader:
            pastedShaders.append(shader)
        setProgress(percentage * index, progressBar)

    return {"Pasted Shaders": pastedShaders}


def holes(progressBar=None):
    # find holes
    setProgress(0, progressBar)
    # self.currentWorkingItem.setText('Holes')
    FacesWithHoles = mel.eval('polyCleanupArgList 3 { "1","2","0","0","0","0","1","0","0","1e-005","0","1e-005","0","1e-005","0","-1","0" };')

    setProgress(100, progressBar)
    return {'Holes': FacesWithHoles}


def locked_normals(uniqueGeometryList, progressBar=None):
    # check for locked normals
    lockedNormals = []
    totalObjects = len(uniqueGeometryList)
    percentage = 99.0 / totalObjects
    # self.currentWorkingItem.setText('Locked Normals')
    for index, geo in enumerate(uniqueGeometryList):
        try:
            vertices = cmds.filterExpand(cmds.polyListComponentConversion(geo, tv=True), sm=31)
            for vert in vertices:
                locked = cmds.polyNormalPerVertex(vert, q=True, al=True)[0]
                if locked:
                    lockedNormals.append(geo)
        except:
            pass

        setProgress(percentage * index, progressBar)

    uniqueLockedList = set(lockedNormals)

    return {'Locked Normals': list(uniqueLockedList)}


def ngons(uniqueGeometryList, progressBar):
    # faces vs triangle ratio + n-gons
    faces = 0
    triangles = 0
    quads = 0
    ngons = 0
    ngonObj = []
    totalObjects = len(uniqueGeometryList)
    percentage = 99.0 / totalObjects

    # self.currentWorkingItem.setText('N-Gons')
    for imdex, geo in enumerate(uniqueGeometryList):
        shapeNode = cmds.listRelatives(geo, ad=True, s=True)
        try:
            if cmds.objectType(shapeNode[0], isType="mesh"):
                numberFaces = cmds.polyEvaluate(geo, f=True)
                if not type(numberFaces) == type(int(1)):
                    continue
                faces += int(numberFaces)
                allFaces = cmds.filterExpand(cmds.polyListComponentConversion(geo, tf=True), sm=34)
                for face in allFaces:
                    allvertices = cmds.filterExpand(cmds.polyListComponentConversion(face, tv=True), sm=31)
                    if len(allvertices) == 3:
                        triangles += 1
                    if len(allvertices) == 4:
                        quads += 1
                    if len(allvertices) >= 5:
                        ngons += 1
                        ngonObj.append(j)
        except:
            pass
        setProgress(percentage * index, progressBar)

    return {'N-Gons': ngonObj}


def legal_uvs(uniqueGeometryList, progressBar=None):
    # search for uv's outside legal space
    UVList = []
    NoUvList = []
    totalObjects = len(uniqueGeometryList)
    percentage = 99.0 / totalObjects

    # self.currentWorkingItem.setText("Legal uv's")
    for index, geo in enumerate(uniqueGeometryList):
        try:
            objectUVs = cmds.filterExpand(cmds.polyListComponentConversion(geo, tuv=True), sm=35)
            for uv in objectUVs:
                uvPos = cmds.polyEditUV(uv, q=True, v=True, u=True)
                for pos in uvPos:
                    if float(pos) < 0.0 or float(pos) > 1.0:
                        UVList.append(uv)
        except:
            NoUvList.append(i)
        setProgress(percentage * index, progressBar)

    return {"Legal uv's": UVList, "No uv's": NoUvList}


def lamina_faces(uniqueGeometryList, progressBar=None):
    # check for lamina faces
    laminaFacesList = []
    totalObjects = len(uniqueGeometryList)
    percentage = 99.0 / totalObjects
    # self.currentWorkingItem.setText('Lamina Faces')
    for index, geo in enumerate(uniqueGeometryList):
        laminaFaces = cmds.polyInfo(geo, laminaFaces=True)
        if not laminaFaces == None:
            laminaFacesList += laminaFaces
        setProgress(percentage * index, progressBar)

    return {"Lamina Faces": laminaFacesList}


def zero_edge_length(progressBar=None):
    # zero edge lenght

    setProgress(0, progressBar)
    # self.currentWorkingItem.setText('Zero Edge Length')
    zeroEdgeLenght = mel.eval('polyCleanupArgList 3 { "1","2","0","0","0","0","0","0","0","1e-005","1","1e-005","0","1e-005","0","-1","0" };')

    setProgress(100, progressBar)
    return {'Zero Edge Length': zeroEdgeLenght}


def zero_geometry_area(progressBar=None):
    # zero geometry area
    setProgress(0, progressBar)
    # self.currentWorkingItem.setText('Zero Face Length')
    zerofaceLenght = mel.eval('polyCleanupArgList 3 { "1","2","0","0","0","0","0","0","1","1e-005","0","1e-005","0","1e-005","0","-1","0" };')

    setProgress(100, progressBar)
    return {'Zero Face Length': zerofaceLenght}


def unmapped_faces(progressBar=None):
    # unmapped faces
    setProgress(0, progressBar)
    # self.currentWorkingItem.setText('Zero Map Area')
    zeromaparea = mel.eval('polyCleanupArgList 3 { "1","2","0","0","0","0","0","0","0","1e-005","0","1e-005","0","1e-005","0","-1","0" };')

    setProgress(100, progressBar)
    return {'Zero Map Area': zeromaparea}


def concave_faces(progressBar=None):
    # concave faces
    concave = mel.eval('polyCleanupArgList 3 { "1","2","0","0","0","1","0","0","0","1e-005","0","1e-005","0","1e-005","0","-1","0" };')
    ngons = mel.eval('polyCleanupArgList 3 { "1","2","0","0","1","0","0","0","0","1e-005","0","1e-005","0","1e-005","0","-1","0" };')
    concaveNotNgon = []
    totalObjects = len(concave)
    percentage = 99.0 / totalObjects

    # self.currentWorkingItem.setText('Concave Faces')
    for index, geo in enumerate(concave):
        if not i in ngons:
            concaveNotNgon.append(i)
        setProgress(percentage * index, progressBar)

    return {'Concave Faces': concaveNotNgon}


def keyed_objects(uniqueGeometryList, progressBar=None):
    # keyed objects
    objectWithKeys = []
    totalObjects = len(uniqueGeometryList)
    percentage = 99.0 / totalObjects

    # self.currentWorkingItem.setText('Keyed Objects')
    for index, geo in enumerate(uniqueGeometryList):
        translatekey = cmds.keyframe(geo, query=True, at='translate', timeChange=True)
        rotatekey = cmds.keyframe(geo, query=True, at='rotate', timeChange=True)
        scalekey = cmds.keyframe(geo, query=True, at='scale', timeChange=True)
        if not translatekey == None:
            objectWithKeys.append(geo)
        elif not rotatekey == None:
            objectWithKeys.append(geo)
        elif not scalekey == None:
            objectWithKeys.append(geo)
        setProgress(percentage * index, progressBar)

    return {'Keyed Objects': objectWithKeys}


def constraints(progressBar=None):
    # constraints
    setProgress(0, progressBar)
    # self.currentWorkingItem.setText('Constraints')
    constraints = cmds.ls(type="constraint")

    setProgress(100, progressBar)
    return {'Constraints': constraints}


def expressions(progressBar=None):
     # expressions
    setProgress(0, progressBar)
    # self.currentWorkingItem.setText('Expressions')
    expressions = cmds.ls(type="expression")

    setProgress(100, progressBar)
    return {'Expressions': expressions}


def triangulation_percentage(uniqueGeometryList, progressBar=None):
    # faces vs triangle ratio + n-gons
    faces = 0
    triangles = 0
    quads = 0
    ngons = 0
    ngonObj = []
    totalObjects = len(uniqueGeometryList)
    percentage = 99.0 / totalObjects

    # self.currentWorkingItem.setText('Triangulation')
    for index, geo in enumerate(uniqueGeometryList):
        shapeNode = cmds.listRelatives(geo, ad=True, s=True)
        try:
            if cmds.objectType(shapeNode[0], isType="mesh"):
                numberFaces = cmds.polyEvaluate(geo, f=True)
                if not type(numberFaces) == type(int(1)):
                    continue
                faces += int(numberFaces)
                allFaces = cmds.filterExpand(cmds.polyListComponentConversion(geo, tf=True), sm=34)
                for face in allFaces:
                    allvertices = cmds.filterExpand(cmds.polyListComponentConversion(face, tv=True), sm=31)
                    if len(allvertices) == 3:
                        triangles += 1
                    if len(allvertices) == 4:
                        quads += 1
                    if len(allvertices) >= 5:
                        ngons += 1
                        ngonObj.append(i)
        except:
            pass
        setProgress(percentage * index, progressBar)

    return '%.2f' % ((float(triangles) / float(faces)) * 100) + ' %'


def scene_size_position(uniqueGeometryList, boundingbox=False, averagePos=False, progressBar=None):
    # total boundingbox size
    w1 = 0
    w2 = 0
    h1 = 0
    h2 = 0
    d1 = 0
    d2 = 0
    totalObjects = len(uniqueGeometryList)
    percentage = 99.0 / totalObjects
    _retInfo = {}
    # self.currentWorkingItem.setText('BBOX and Pos')
    for index, geo in enumerate(uniqueGeometryList):
        bbox = cmds.exactWorldBoundingBox(geo)
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
        setProgress(percentage * index, progressBar)

    if boundingbox == True:
        _retInfo["bbox"] = ['%.2f' % (abs(w1) + abs(w2)), '%.2f' % (abs(h1) + abs(h2)), '%.2f' % (abs(d1) + abs(d2))]

    if averagePos == True:
        centerPosx = (w1 + w2) / 2
        centerPosz = (d1 + d2) / 2

        _retInfo["avg"] = ['%.2f' % (centerPosx), '%.2f' % (centerPosz)]
    return _retInfo


def resolution_gate(progressBar=None):
    # render resolution
    setProgress(0, progressBar)
    # self.currentWorkingItem.setText('Resolution')
    wdth = cmds.getAttr("defaultResolution.width")
    hght = cmds.getAttr("defaultResolution.height")

    return {"res", [wdth, hght]}
    setProgress(100, progressBar)
