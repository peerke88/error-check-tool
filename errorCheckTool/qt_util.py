# -*- coding: utf-8 -*-
QT_VERSION = "none"
ERROR_LIST = {}

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide.QtSvg import *
    from PySide import QtGui
    from PySide.QtUiTools import *
    import sip

    QString = None
    QT_VERSION = "pyside"
except Exception as e:
    ERROR_LIST["Pyside import"] = e
    try:
        from PySide2.QtGui import *
        from PySide2.QtCore import *
        from PySide2.QtWidgets import *
        from PySide2.QtSvg import *
        from PySide2 import QtGui
        from PySide2.QtUiTools import *
        import shiboken2 as shiboken

        QString = None
        QT_VERSION = "pyside2"
    except Exception as e:
        ERROR_LIST["Pyside2 import"] = e
        try:
            from PyQt4.QtCore import *
            from PyQt4.QtGui import *
            from PyQt4.QtSvg import *
            from PyQt4 import QtGui
            from PyQt4.QtUiTools import *
            import shiboken

            QT_VERSION = "pyqt4"
        except Exception as e:
            ERROR_LIST["PyQt4 import"] = e

if QT_VERSION == "none":
    for version in ERROR_LIST.keys():
        print(version, ERROR_LIST[version])


nameRegExp = QRegExp('\\w+')
from maya.api import OpenMaya


def wrapinstance(ptr, base=None):
    '''workaround to be able to wrap objects with both PySide and PyQt4'''
    # http://nathanhorne.com/?p=485'''
    if ptr is None:
        return None
    ptr = int(ptr)
    if 'shiboken' in globals().keys():
        if base is None:
            qObj = shiboken.wrapInstance(int(ptr), QObject)
            metaObj = qObj.metaObject()
            cls = metaObj.className()
            superCls = metaObj.superClass().className()
            if hasattr(QtGui, cls):
                base = getattr(QtGui, cls)
            elif hasattr(QtGui, superCls):
                base = getattr(QtGui, superCls)
            else:
                base = QWidget
        return shiboken.wrapInstance(int(ptr), base)
    elif "sip" in globals().keys():
        base = QObject
        return sip.wrapinstance(int(ptr), base)
    else:
        return None


def nullVBoxLayout(parent=None, size=0):
    """ convenience function for the QVBoxLayout

    :param parent: the possible parent for the layout
    :type parent: QWidget
    :param size: the size of the margins
    :type size: int
    :return: the layout
    :rtype: QVBoxLayout
    """
    v = QVBoxLayout()
    v.setContentsMargins(size, size, size, size)
    return v


def nullHBoxLayout(parent=None, size=0):
    """ convenience function for the QHBoxLayout

    :param parent: the possible parent for the layout
    :type parent: QWidget
    :param size: the size of the margins
    :type size: int
    :return: the layout
    :rtype: QHBoxLayout
    """
    h = QHBoxLayout()
    h.setContentsMargins(size, size, size, size)
    return h


def nullGridLayout(parent=None, size=0):
    """ convenience function for the QGridLayout

    :param parent: the possible parent for the layout
    :type parent: QWidget
    :param size: the size of the margins
    :type size: int
    :return: the layout
    :rtype: QGridLayout
    """
    h = QGridLayout()
    h.setContentsMargins(size, size, size, size)
    return h


def toolButton(pixmap='', orientation=0, size=None):
    """ toolbutton function with image

    :param pixmap: location of the image
    :type pixmap: string
    :param orientation: rotation in degrees clockwise
    :type orientation: int
    :param size: height and width of image in pixels
    :type size: int
    :return: the button  
    :rtype: QToolButton
    """
    btn = QToolButton()
    if isinstance(pixmap, str):
        pixmap = QPixmap(pixmap)
    if orientation != 0 and not _isSVG:
        transform = QTransform().rotate(orientation, Qt.ZAxis)
        pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
    btn.setIcon(QIcon(pixmap))
    btn.setFocusPolicy(Qt.NoFocus)
    btn.setStyleSheet('border: 0px;')
    if size is not None:
        if type(size) == int:
            btn.setFixedSize(QSize(size, size))
            btn.setIconSize(QSize(size, size))
        else:
            btn.setFixedSize(size)
            btn.setIconSize(size)
    return btn


def FalseFolderCharacters(inString):
    """ checking a string for characters that are not allowed in folder structures

    :param inString: the string to check
    :type inString: string
    :return: if the string has bad characters
    :rtype: bool
    """
    return re.search(r'[\\/:\[\]<>"!@#$%^&-.]', inString) or re.search(r'[*?|]', inString) or re.match(r'[0-9]', inString) or re.search(u'[\u4E00-\u9FFF]+', inString, re.U) or re.search(u'[\u3040-\u309Fー]+', inString, re.U) or re.search(u'[\u30A0-\u30FF]+', inString, re.U)


def FalseFolderCharactersJapanese(self, inString):
    """ checking a string for characters that are not allowed in folder structures

    :param inString: the string to check
    :type inString: string
    :return: if the string has bad characters
    :rtype: bool
    """
    return re.search(r'[\\/:\[\]<>"!@#$%^&-]', inString) or re.search(r'[*?|]', inString) or "." in inString or (len(inString) > 0 and inString[0].isdigit()) or re.search(u'[\u4E00-\u9FFF]+', inString, re.U) or re.search(u'[\u3040-\u309Fー]+', inString, re.U) or re.search(u'[\u30A0-\u30FF]+', inString, re.U)


def checkStringForBadChars(self, inText, button, option=1, *args):
    """ checking a string for characters that are not allowed in folder structures

    :param inText: the text to check
    :type inText: string
    :param option: the type of structure to check for
    :type option: int

    :return: if the string has bad characters
    :rtype: bool
    """
    if (option == 1 and not FalseFolderCharacters(inText) in [None, True]) or (option == 2 and not FalseFolderCharactersJapanese(inText) in [None, False]):
        return False
    if inText == "":
        return False
    return True


def textProgressBar(progress, message=''):
    """ set the current progress of a function using test only

    :param progress: percentage of progress 
    :type progress: float
    :param message: the message to be displayed
    :type message: string
    """
    barLength = 10
    if progress <= 0:
        progress = 0
    progress = progress / 100.0
    if progress >= 1:
        progress = 1
    block = int(round(barLength * progress))
    text = "[%s] %.1f%%, %s" % ("#" * block + "-" * (barLength - block), progress * 100, message)
    OpenMaya.MGlobal.displayInfo(text)


def setProgress(inValue, progressBar=None, inText=''):
    """ convenience function to set the progress bar value even when a qProgressbar does not exist

    :param inValue: the current percentage of the progressbar
    :type inValue: int
    :param progressbar: the progressbar to update
    :type progressbar: QProgressBar
    :param inText: additional text to show with the progressbar
    :type inText: string
    """
    if progressBar is False:
        return
    if progressBar is None:
        textProgressBar(inValue, inText)
        return
    progressBar.message = inText
    progressBar.setValue(inValue)
    QApplication.processEvents()
