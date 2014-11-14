# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cut_diff_card.ui'
#
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_CutDiffCard(object):
    def setupUi(self, CutDiffCard):
        CutDiffCard.setObjectName("CutDiffCard")
        CutDiffCard.resize(708, 82)
        CutDiffCard.setFrameShape(QtGui.QFrame.StyledPanel)
        CutDiffCard.setFrameShadow(QtGui.QFrame.Raised)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(CutDiffCard)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.left_layout = QtGui.QHBoxLayout()
        self.left_layout.setObjectName("left_layout")
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.icon_label = QtGui.QLabel(CutDiffCard)
        self.icon_label.setText("")
        self.icon_label.setPixmap(QtGui.QPixmap(":/tk_multi_importcut/sg_logo.png"))
        self.icon_label.setObjectName("icon_label")
        self.horizontalLayout_4.addWidget(self.icon_label)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.version_name_label = QtGui.QLabel(CutDiffCard)
        self.version_name_label.setObjectName("version_name_label")
        self.gridLayout_2.addWidget(self.version_name_label, 1, 1, 1, 1)
        self.label_13 = QtGui.QLabel(CutDiffCard)
        self.label_13.setObjectName("label_13")
        self.gridLayout_2.addWidget(self.label_13, 0, 0, 1, 1)
        self.label_15 = QtGui.QLabel(CutDiffCard)
        self.label_15.setObjectName("label_15")
        self.gridLayout_2.addWidget(self.label_15, 1, 0, 1, 1)
        self.shot_name_label = QtGui.QLabel(CutDiffCard)
        self.shot_name_label.setObjectName("shot_name_label")
        self.gridLayout_2.addWidget(self.shot_name_label, 0, 1, 1, 1)
        self.status_label = QtGui.QLabel(CutDiffCard)
        self.status_label.setObjectName("status_label")
        self.gridLayout_2.addWidget(self.status_label, 2, 0, 1, 1)
        self.horizontalLayout_4.addLayout(self.gridLayout_2)
        self.horizontalLayout_4.setStretch(1, 1)
        self.left_layout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_2.addLayout(self.left_layout)
        self.right_layout = QtGui.QVBoxLayout()
        self.right_layout.setSpacing(0)
        self.right_layout.setContentsMargins(-1, -1, -1, 0)
        self.right_layout.setObjectName("right_layout")
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtGui.QLabel(CutDiffCard)
        self.label_2.setStyleSheet("background-color : rgb(126, 126, 126);\n"
"border-top: 1px solid black;\n"
"border-left: 1px solid black;")
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.label_4 = QtGui.QLabel(CutDiffCard)
        self.label_4.setStyleSheet("background-color : rgb(126, 126, 126);\n"
"border-top: 1px solid black;\n"
"")
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.label_5 = QtGui.QLabel(CutDiffCard)
        self.label_5.setStyleSheet("background-color : rgb(126, 126, 126);\n"
"border-top: 1px solid black;\n"
"")
        self.label_5.setLineWidth(0)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setIndent(0)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_3.addWidget(self.label_5)
        self.label_3 = QtGui.QLabel(CutDiffCard)
        self.label_3.setStyleSheet("background-color : rgb(126, 126, 126);\n"
"border-top: 1px solid black;\n"
"")
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.label = QtGui.QLabel(CutDiffCard)
        self.label.setStyleSheet("background-color : rgb(126, 126, 126);\n"
"border-top: 1px solid black;\n"
"border-right: 1px solid black;")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.right_layout.addLayout(self.horizontalLayout_3)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.cut_title_label = QtGui.QLabel(CutDiffCard)
        self.cut_title_label.setStyleSheet("background-color : rgb(126, 126, 126);\n"
"border-top: 1px solid black;\n"
"border-left: 1px solid black;\n"
"")
        self.cut_title_label.setFrameShape(QtGui.QFrame.NoFrame)
        self.cut_title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.cut_title_label.setObjectName("cut_title_label")
        self.gridLayout.addWidget(self.cut_title_label, 0, 1, 1, 1)
        self.head_title_label = QtGui.QLabel(CutDiffCard)
        self.head_title_label.setStyleSheet("background-color : rgb(126, 126, 126);\n"
"border-top: 1px solid black;\n"
"border-left: 1px solid black;\n"
"")
        self.head_title_label.setFrameShape(QtGui.QFrame.NoFrame)
        self.head_title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.head_title_label.setMargin(1)
        self.head_title_label.setObjectName("head_title_label")
        self.gridLayout.addWidget(self.head_title_label, 0, 0, 1, 1)
        self.tail_title_label = QtGui.QLabel(CutDiffCard)
        self.tail_title_label.setStyleSheet("background-color : rgb(126, 126, 126);\n"
"border-top: 1px solid black;\n"
"border-left: 1px solid black;\n"
"border-right: 1px solid black;")
        self.tail_title_label.setFrameShape(QtGui.QFrame.NoFrame)
        self.tail_title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.tail_title_label.setObjectName("tail_title_label")
        self.gridLayout.addWidget(self.tail_title_label, 0, 2, 1, 1)
        self.head_label = QtGui.QLabel(CutDiffCard)
        self.head_label.setStyleSheet("background-color : rgb(126, 126, 126);\n"
"border-top: 1px solid black;\n"
"border-bottom: 1px solid black;\n"
"border-left: 1px solid black;\n"
"")
        self.head_label.setFrameShape(QtGui.QFrame.NoFrame)
        self.head_label.setAlignment(QtCore.Qt.AlignCenter)
        self.head_label.setObjectName("head_label")
        self.gridLayout.addWidget(self.head_label, 1, 0, 1, 1)
        self.cut_label = QtGui.QLabel(CutDiffCard)
        self.cut_label.setStyleSheet("background-color : rgb(126, 126, 126);\n"
"border-top: 1px solid black;\n"
"border-bottom: 1px solid black;\n"
"border-left: 1px solid black;\n"
"")
        self.cut_label.setFrameShape(QtGui.QFrame.NoFrame)
        self.cut_label.setAlignment(QtCore.Qt.AlignCenter)
        self.cut_label.setObjectName("cut_label")
        self.gridLayout.addWidget(self.cut_label, 1, 1, 1, 1)
        self.tail_label = QtGui.QLabel(CutDiffCard)
        self.tail_label.setStyleSheet("background-color : rgb(126, 126, 126);\n"
"border-top: 1px solid black;\n"
"border-left: 1px solid black;\n"
"border-right: 1px solid black;\n"
"border-bottom: 1px solid black;")
        self.tail_label.setFrameShape(QtGui.QFrame.NoFrame)
        self.tail_label.setAlignment(QtCore.Qt.AlignCenter)
        self.tail_label.setObjectName("tail_label")
        self.gridLayout.addWidget(self.tail_label, 1, 2, 1, 1)
        self.right_layout.addLayout(self.gridLayout)
        self.right_layout.setStretch(0, 1)
        self.right_layout.setStretch(1, 2)
        self.horizontalLayout_2.addLayout(self.right_layout)
        self.horizontalLayout_2.setStretch(0, 9)
        self.horizontalLayout_2.setStretch(1, 10)

        self.retranslateUi(CutDiffCard)
        QtCore.QMetaObject.connectSlotsByName(CutDiffCard)

    def retranslateUi(self, CutDiffCard):
        CutDiffCard.setWindowTitle(QtGui.QApplication.translate("CutDiffCard", "Frame", None, QtGui.QApplication.UnicodeUTF8))
        self.version_name_label.setText(QtGui.QApplication.translate("CutDiffCard", "sh_001_001_fg_v001", None, QtGui.QApplication.UnicodeUTF8))
        self.label_13.setText(QtGui.QApplication.translate("CutDiffCard", "SHOT", None, QtGui.QApplication.UnicodeUTF8))
        self.label_15.setText(QtGui.QApplication.translate("CutDiffCard", "VERSION", None, QtGui.QApplication.UnicodeUTF8))
        self.shot_name_label.setText(QtGui.QApplication.translate("CutDiffCard", "sh_001_001", None, QtGui.QApplication.UnicodeUTF8))
        self.status_label.setText(QtGui.QApplication.translate("CutDiffCard", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("CutDiffCard", "1001", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("CutDiffCard", "1009", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("CutDiffCard", "125", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("CutDiffCard", "1028", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("CutDiffCard", "1036", None, QtGui.QApplication.UnicodeUTF8))
        self.cut_title_label.setText(QtGui.QApplication.translate("CutDiffCard", "CUT", None, QtGui.QApplication.UnicodeUTF8))
        self.head_title_label.setText(QtGui.QApplication.translate("CutDiffCard", "HEAD", None, QtGui.QApplication.UnicodeUTF8))
        self.tail_title_label.setText(QtGui.QApplication.translate("CutDiffCard", "TAIL", None, QtGui.QApplication.UnicodeUTF8))
        self.head_label.setText(QtGui.QApplication.translate("CutDiffCard", "8", None, QtGui.QApplication.UnicodeUTF8))
        self.cut_label.setText(QtGui.QApplication.translate("CutDiffCard", "20", None, QtGui.QApplication.UnicodeUTF8))
        self.tail_label.setText(QtGui.QApplication.translate("CutDiffCard", "8", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
