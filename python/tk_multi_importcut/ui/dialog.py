# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog.ui'
#
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(844, 478)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.sg_icon_labe = QtGui.QLabel(Dialog)
        self.sg_icon_labe.setText("")
        self.sg_icon_labe.setPixmap(QtGui.QPixmap(":/tk_multi_importcut/sg_logo.png"))
        self.sg_icon_labe.setObjectName("sg_icon_labe")
        self.horizontalLayout.addWidget(self.sg_icon_labe)
        self.title_label = QtGui.QLabel(Dialog)
        self.title_label.setObjectName("title_label")
        self.horizontalLayout.addWidget(self.title_label)
        self.secondary_title_label = QtGui.QLabel(Dialog)
        self.secondary_title_label.setText("")
        self.secondary_title_label.setObjectName("secondary_title_label")
        self.horizontalLayout.addWidget(self.secondary_title_label)
        self.horizontalLayout.setStretch(2, 1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.stackedWidget = QtGui.QStackedWidget(Dialog)
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtGui.QWidget()
        self.page.setObjectName("page")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.page)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtGui.QLabel(self.page)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtGui.QWidget()
        self.page_2.setObjectName("page_2")
        self.stackedWidget.addWidget(self.page_2)
        self.verticalLayout.addWidget(self.stackedWidget)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.title_label.setText(QtGui.QApplication.translate("Dialog", "Cut Summary", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "DRAG & DROP\n"
"EDL", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
