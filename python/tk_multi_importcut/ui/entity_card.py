# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'entity_card.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_EntityCard(object):
    def setupUi(self, EntityCard):
        EntityCard.setObjectName("EntityCard")
        EntityCard.resize(358, 70)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(EntityCard.sizePolicy().hasHeightForWidth())
        EntityCard.setSizePolicy(sizePolicy)
        EntityCard.setMinimumSize(QtCore.QSize(310, 70))
        EntityCard.setMaximumSize(QtCore.QSize(470, 16777215))
        EntityCard.setBaseSize(QtCore.QSize(358, 70))
        EntityCard.setFocusPolicy(QtCore.Qt.StrongFocus)
        EntityCard.setStyleSheet("")
        EntityCard.setFrameShape(QtGui.QFrame.Box)
        EntityCard.setFrameShadow(QtGui.QFrame.Plain)
        EntityCard.setLineWidth(2)
        self.horizontalLayout = QtGui.QHBoxLayout(EntityCard)
        self.horizontalLayout.setContentsMargins(4, 1, 0, 1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.icon_label = QtGui.QLabel(EntityCard)
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
        self.icon_label.setPixmap(QtGui.QPixmap(":/tk_multi_importcut/default_card_icon.png"))
        self.icon_label.setScaledContents(False)
        self.icon_label.setAlignment(QtCore.Qt.AlignCenter)
        self.icon_label.setObjectName("icon_label")
        self.horizontalLayout.addWidget(self.icon_label)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setSpacing(1)
        self.verticalLayout_2.setContentsMargins(-1, 4, -1, 4)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.title_label = QtGui.QLabel(EntityCard)
        self.title_label.setObjectName("title_label")
        self.verticalLayout_2.addWidget(self.title_label)
        self.status_label = QtGui.QLabel(EntityCard)
        self.status_label.setObjectName("status_label")
        self.verticalLayout_2.addWidget(self.status_label)
        self.details_label = ElidedLabel(EntityCard)
        self.details_label.setObjectName("details_label")
        self.verticalLayout_2.addWidget(self.details_label)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.select_button = QtGui.QPushButton(EntityCard)
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

        self.retranslateUi(EntityCard)
        QtCore.QMetaObject.connectSlotsByName(EntityCard)

    def retranslateUi(self, EntityCard):
        EntityCard.setWindowTitle(QtGui.QApplication.translate("EntityCard", "Frame", None, QtGui.QApplication.UnicodeUTF8))
        self.title_label.setText(QtGui.QApplication.translate("EntityCard", "<big><b>Name</b></big>", None, QtGui.QApplication.UnicodeUTF8))
        self.status_label.setText(QtGui.QApplication.translate("EntityCard", "Status", None, QtGui.QApplication.UnicodeUTF8))
        self.details_label.setText(QtGui.QApplication.translate("EntityCard", "<small>details</small>", None, QtGui.QApplication.UnicodeUTF8))

from ..dialog import ElidedLabel
from . import resources_rc
