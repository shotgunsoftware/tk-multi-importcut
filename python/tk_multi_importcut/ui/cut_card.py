# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cut_card.ui'
#
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_CutCard(object):
    def setupUi(self, CutCard):
        CutCard.setObjectName("CutCard")
        CutCard.resize(358, 70)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CutCard.sizePolicy().hasHeightForWidth())
        CutCard.setSizePolicy(sizePolicy)
        CutCard.setMinimumSize(QtCore.QSize(310, 70))
        CutCard.setFocusPolicy(QtCore.Qt.StrongFocus)
        CutCard.setStyleSheet("")
        CutCard.setFrameShape(QtGui.QFrame.Box)
        CutCard.setFrameShadow(QtGui.QFrame.Plain)
        CutCard.setLineWidth(2)
        self.horizontalLayout = QtGui.QHBoxLayout(CutCard)
        self.horizontalLayout.setContentsMargins(4, 1, 0, 1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.icon_label = QtGui.QLabel(CutCard)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.icon_label.sizePolicy().hasHeightForWidth())
        self.icon_label.setSizePolicy(sizePolicy)
        self.icon_label.setMinimumSize(QtCore.QSize(105, 59))
        self.icon_label.setMaximumSize(QtCore.QSize(105, 59))
        self.icon_label.setBaseSize(QtCore.QSize(105, 59))
        self.icon_label.setStyleSheet("background-color: black;")
        self.icon_label.setText("")
        self.icon_label.setPixmap(QtGui.QPixmap(":/tk_multi_importcut/sg_logo.png"))
        self.icon_label.setScaledContents(False)
        self.icon_label.setAlignment(QtCore.Qt.AlignCenter)
        self.icon_label.setObjectName("icon_label")
        self.horizontalLayout.addWidget(self.icon_label)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.title_label = QtGui.QLabel(CutCard)
        self.title_label.setObjectName("title_label")
        self.verticalLayout_2.addWidget(self.title_label)
        self.status_label = QtGui.QLabel(CutCard)
        self.status_label.setObjectName("status_label")
        self.verticalLayout_2.addWidget(self.status_label)
        self.details_label = QtGui.QLabel(CutCard)
        self.details_label.setObjectName("details_label")
        self.verticalLayout_2.addWidget(self.details_label)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.select_button = QtGui.QPushButton(CutCard)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.select_button.sizePolicy().hasHeightForWidth())
        self.select_button.setSizePolicy(sizePolicy)
        self.select_button.setMaximumSize(QtCore.QSize(30, 30))
        self.select_button.setToolTip("")
        self.select_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/tk_multi_importcut/right_arrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.select_button.setIcon(icon)
        self.select_button.setIconSize(QtCore.QSize(30, 30))
        self.select_button.setCheckable(False)
        self.select_button.setFlat(True)
        self.select_button.setObjectName("select_button")
        self.horizontalLayout.addWidget(self.select_button)
        self.horizontalLayout.setStretch(1, 1)

        self.retranslateUi(CutCard)
        QtCore.QMetaObject.connectSlotsByName(CutCard)

    def retranslateUi(self, CutCard):
        CutCard.setWindowTitle(QtGui.QApplication.translate("CutCard", "Frame", None, QtGui.QApplication.UnicodeUTF8))
        self.title_label.setText(QtGui.QApplication.translate("CutCard", "<big><b>Name</b></big>", None, QtGui.QApplication.UnicodeUTF8))
        self.status_label.setText(QtGui.QApplication.translate("CutCard", "Status", None, QtGui.QApplication.UnicodeUTF8))
        self.details_label.setText(QtGui.QApplication.translate("CutCard", "<small>details</small>", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc