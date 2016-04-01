# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'entity_type_card.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_entity_type_frame(object):
    def setupUi(self, entity_type_frame):
        entity_type_frame.setObjectName("entity_type_frame")
        entity_type_frame.resize(179, 157)
        entity_type_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        entity_type_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.verticalLayout = QtGui.QVBoxLayout(entity_type_frame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.icon_label = QtGui.QLabel(entity_type_frame)
        self.icon_label.setText("")
        self.icon_label.setScaledContents(True)
        self.icon_label.setAlignment(QtCore.Qt.AlignCenter)
        self.icon_label.setObjectName("icon_label")
        self.verticalLayout.addWidget(self.icon_label)
        self.title_label = QtGui.QLabel(entity_type_frame)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setObjectName("title_label")
        self.verticalLayout.addWidget(self.title_label)
        self.verticalLayout.setStretch(0, 2)
        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(entity_type_frame)
        QtCore.QMetaObject.connectSlotsByName(entity_type_frame)

    def retranslateUi(self, entity_type_frame):
        entity_type_frame.setWindowTitle(QtGui.QApplication.translate("entity_type_frame", "Frame", None, QtGui.QApplication.UnicodeUTF8))
        self.title_label.setText(QtGui.QApplication.translate("entity_type_frame", "Project", None, QtGui.QApplication.UnicodeUTF8))

