# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'project_card.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui


class Ui_ProjectCard(object):
    def setupUi(self, ProjectCard):
        ProjectCard.setObjectName("ProjectCard")
        ProjectCard.resize(358, 70)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.MinimumExpanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ProjectCard.sizePolicy().hasHeightForWidth())
        ProjectCard.setSizePolicy(sizePolicy)
        ProjectCard.setMinimumSize(QtCore.QSize(310, 70))
        ProjectCard.setMaximumSize(QtCore.QSize(470, 16777215))
        ProjectCard.setBaseSize(QtCore.QSize(358, 70))
        ProjectCard.setFocusPolicy(QtCore.Qt.StrongFocus)
        ProjectCard.setStyleSheet("")
        ProjectCard.setFrameShape(QtGui.QFrame.Box)
        ProjectCard.setFrameShadow(QtGui.QFrame.Plain)
        ProjectCard.setLineWidth(2)
        self.horizontalLayout = QtGui.QHBoxLayout(ProjectCard)
        self.horizontalLayout.setContentsMargins(4, 1, 0, 1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.icon_label = QtGui.QLabel(ProjectCard)
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
        self.icon_label.setPixmap(
            QtGui.QPixmap(":/tk_multi_importcut/default_card_icon.png")
        )
        self.icon_label.setScaledContents(False)
        self.icon_label.setAlignment(QtCore.Qt.AlignCenter)
        self.icon_label.setObjectName("icon_label")
        self.horizontalLayout.addWidget(self.icon_label)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setSpacing(1)
        self.verticalLayout_2.setContentsMargins(-1, 4, -1, 4)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.title_label = QtGui.QLabel(ProjectCard)
        self.title_label.setObjectName("title_label")
        self.verticalLayout_2.addWidget(self.title_label)
        self.status_label = QtGui.QLabel(ProjectCard)
        self.status_label.setObjectName("status_label")
        self.verticalLayout_2.addWidget(self.status_label)
        self.details_label = ElidedLabel(ProjectCard)
        self.details_label.setObjectName("details_label")
        self.verticalLayout_2.addWidget(self.details_label)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.select_button = QtGui.QPushButton(ProjectCard)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.select_button.sizePolicy().hasHeightForWidth()
        )
        self.select_button.setSizePolicy(sizePolicy)
        self.select_button.setMaximumSize(QtCore.QSize(30, 30))
        self.select_button.setToolTip("")
        self.select_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/tk_multi_importcut/right_arrow.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.select_button.setIcon(icon)
        self.select_button.setIconSize(QtCore.QSize(30, 30))
        self.select_button.setCheckable(False)
        self.select_button.setFlat(True)
        self.select_button.setObjectName("select_button")
        self.horizontalLayout.addWidget(self.select_button)
        self.horizontalLayout.setStretch(1, 1)

        self.retranslateUi(ProjectCard)
        QtCore.QMetaObject.connectSlotsByName(ProjectCard)

    def retranslateUi(self, ProjectCard):
        ProjectCard.setWindowTitle(
            QtGui.QApplication.translate(
                "ProjectCard", "Frame", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.title_label.setText(
            QtGui.QApplication.translate(
                "ProjectCard",
                "<big><b>Name</b></big>",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.status_label.setText(
            QtGui.QApplication.translate(
                "ProjectCard", "Status", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.details_label.setText(
            QtGui.QApplication.translate(
                "ProjectCard",
                "<small>details</small>",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )


from ..dialog import ElidedLabel
from . import resources_rc
