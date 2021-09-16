# -*- coding: utf-8 -*-
QT_VERSION = "none"
ERROR_LIST = {}

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide.QtSvg import *
    from PySide import QtGui
    from PySide.QtCore import Signal as pyqtSignal
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
        from PySide2.QtCore import Signal as pyqtSignal
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


def nullLayout(inType, parent=None, size=0):
    v = inType(parent)
    v.setContentsMargins(size, size, size, size)
    return v


def nullVBoxLayout(parent=None, size=0):
    """ convenience function for the QVBoxLayout

    :param parent: the possible parent for the layout
    :type parent: QWidget
    :param size: the size of the margins
    :type size: int
    :return: the layout
    :rtype: QVBoxLayout
    """
    return nullLayout(QVBoxLayout, parent, size)


def nullHBoxLayout(parent=None, size=0):
    """ convenience function for the QHBoxLayout

    :param parent: the possible parent for the layout
    :type parent: QWidget
    :param size: the size of the margins
    :type size: int
    :return: the layout
    :rtype: QHBoxLayout
    """
    return nullLayout(QHBoxLayout, parent, size)


def nullGridLayout(parent=None, size=0):
    """ convenience function for the QGridLayout

    :param parent: the possible parent for the layout
    :type parent: QWidget
    :param size: the size of the margins
    :type size: int
    :return: the layout
    :rtype: QGridLayout
    """
    return QGridLayout(QHBoxLayout, parent, size)


def get_maya_window():
    for widget in QApplication.allWidgets():
        try:
            if widget.objectName() == "MayaWindow":
                return widget
        except:
            pass
    return None


def QuickDialog(title):
    """ convenience Quick dialog for simple accept and reject functions

    :param title: title for the dialog
    :type title: string
    :return: the window to be created
    :rtype: QDialog
    """
    myWindow = QDialog()
    myWindow.setWindowTitle(title)
    myWindow.setLayout(nullVBoxLayout())
    h = nullHBoxLayout()
    myWindow.layout().addLayout(h)
    btn = pushButton("Accept")
    btn.clicked.connect(myWindow.accept)
    h.addWidget(btn)
    btn = pushButton("Reject")
    btn.clicked.connect(myWindow.reject)
    h.addWidget(btn)
    return myWindow


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


def pushButton(text=''):
    """ simple button command with correct stylesheet

    :param text: text to add to the button
    :type text: string
    :return: the button  
    :rtype: QPushButton
    """
    btn = QPushButton(text)
    btn.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #595959, stop:1 #444444);")
    return btn


def buttonsToAttach(name, command, *_):
    """ convenience function to attach signal command to qpushbutton on creation

    :param name: text to add to the button
    :type name: string
    :param command: python command to attach to the current button on clicked signal
    :type command: <function>
    :return: the button  
    :rtype: QPushButton
    """
    button = pushButton()

    button.setText(name)
    button.setObjectName(name)

    button.clicked.connect(command)
    button.setMinimumHeight(23)
    return button


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


class LineEdit(QLineEdit):
    """override the focus steal on the lineedit"""
    allowText = pyqtSignal(bool)

    def __init__(self, folderSpecific=True, *args):
        super(LineEdit, self).__init__(*args)
        self.__qt_normal_color = QPalette(self.palette()).color(QPalette.Base)

        if folderSpecific:
            self.textChanged[unicode].connect(self._checkString)

    def __lineEdit_Color(self, inColor):
        PalleteColor = QPalette(self.palette())
        PalleteColor.setColor(QPalette.Base, QColor(inColor))
        self.setPalette(PalleteColor)

    def _checkString(self):
        _curText = self.displayText()
        if FalseFolderCharacters(_curText) != None:
            self.__lineEdit_Color('red')
            self.allowText.emit(False)
        else:
            self.__lineEdit_Color(self.__qt_normal_color)
            self.allowText.emit(True)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Control or key == Qt.Key.Key_Shift:
            return
        else:
            super(self.__class__, self).keyPressEvent(event)
