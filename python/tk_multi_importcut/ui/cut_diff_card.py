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
        CutDiffCard.resize(737, 82)
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
        self.shot_title_label = QtGui.QLabel(CutDiffCard)
        self.shot_title_label.setStyleSheet("")
        self.shot_title_label.setProperty("constant_title", True)
        self.shot_title_label.setObjectName("shot_title_label")
        self.gridLayout_2.addWidget(self.shot_title_label, 0, 0, 1, 1)
        self.version_title_label = QtGui.QLabel(CutDiffCard)
        self.version_title_label.setObjectName("version_title_label")
        self.gridLayout_2.addWidget(self.version_title_label, 1, 0, 1, 1)
        self.shot_name_label = QtGui.QLabel(CutDiffCard)
        self.shot_name_label.setObjectName("shot_name_label")
        self.gridLayout_2.addWidget(self.shot_name_label, 0, 1, 1, 1)
        self.status_label = QtGui.QLabel(CutDiffCard)
        self.status_label.setObjectName("status_label")
        self.gridLayout_2.addWidget(self.status_label, 2, 0, 1, 1)
        self.extra_label = QtGui.QLabel(CutDiffCard)
        self.extra_label.setText("")
        self.extra_label.setObjectName("extra_label")
        self.gridLayout_2.addWidget(self.extra_label, 2, 1, 1, 1)
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
        self.shot_head_in_label = QtGui.QLabel(CutDiffCard)
        self.shot_head_in_label.setStyleSheet("background-color : rgb(84, 84, 84);\n"
"border-top: 1px solid black;\n"
"border-left: 1px solid black;")
        self.shot_head_in_label.setAlignment(QtCore.Qt.AlignCenter)
        self.shot_head_in_label.setObjectName("shot_head_in_label")
        self.horizontalLayout_3.addWidget(self.shot_head_in_label)
        self.cut_in_label = QtGui.QLabel(CutDiffCard)
        self.cut_in_label.setStyleSheet("background-color : rgb(84, 84, 84);\n"
"border-top: 1px solid black;\n"
"")
        self.cut_in_label.setAlignment(QtCore.Qt.AlignCenter)
        self.cut_in_label.setObjectName("cut_in_label")
        self.horizontalLayout_3.addWidget(self.cut_in_label)
        self.label_5 = QtGui.QLabel(CutDiffCard)
        self.label_5.setStyleSheet("background-color : rgb(84, 84, 84);\n"
"border-top: 1px solid black;\n"
"")
        self.label_5.setLineWidth(0)
        self.label_5.setText("")
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setIndent(0)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_3.addWidget(self.label_5)
        self.cut_out_label = QtGui.QLabel(CutDiffCard)
        self.cut_out_label.setStyleSheet("background-color : rgb(84, 84, 84);\n"
"border-top: 1px solid black;\n"
"")
        self.cut_out_label.setAlignment(QtCore.Qt.AlignCenter)
        self.cut_out_label.setObjectName("cut_out_label")
        self.horizontalLayout_3.addWidget(self.cut_out_label)
        self.shot_tail_out_label = QtGui.QLabel(CutDiffCard)
        self.shot_tail_out_label.setStyleSheet("background-color : rgb(84, 84, 84);\n"
"border-top: 1px solid black;\n"
"border-right: 1px solid black;")
        self.shot_tail_out_label.setAlignment(QtCore.Qt.AlignCenter)
        self.shot_tail_out_label.setObjectName("shot_tail_out_label")
        self.horizontalLayout_3.addWidget(self.shot_tail_out_label)
        self.right_layout.addLayout(self.horizontalLayout_3)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.cut_title_label = QtGui.QLabel(CutDiffCard)
        self.cut_title_label.setStyleSheet("background-color : rgb(74, 74, 74);\n"
"border-top: 1px solid black;\n"
"border-left: 1px solid black;\n"
"")
        self.cut_title_label.setFrameShape(QtGui.QFrame.NoFrame)
        self.cut_title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.cut_title_label.setObjectName("cut_title_label")
        self.gridLayout.addWidget(self.cut_title_label, 0, 1, 1, 1)
        self.head_title_label = QtGui.QLabel(CutDiffCard)
        self.head_title_label.setStyleSheet("background-color : rgb(74, 74, 74);\n"
"border-top: 1px solid black;\n"
"border-left: 1px solid black;\n"
"")
        self.head_title_label.setFrameShape(QtGui.QFrame.NoFrame)
        self.head_title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.head_title_label.setMargin(1)
        self.head_title_label.setObjectName("head_title_label")
        self.gridLayout.addWidget(self.head_title_label, 0, 0, 1, 1)
        self.tail_title_label = QtGui.QLabel(CutDiffCard)
        self.tail_title_label.setStyleSheet("background-color : rgb(74, 74, 74);\n"
"border-top: 1px solid black;\n"
"border-left: 1px solid black;\n"
"border-right: 1px solid black;")
        self.tail_title_label.setFrameShape(QtGui.QFrame.NoFrame)
        self.tail_title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.tail_title_label.setObjectName("tail_title_label")
        self.gridLayout.addWidget(self.tail_title_label, 0, 2, 1, 1)
        self.head_duration_label = QtGui.QLabel(CutDiffCard)
        self.head_duration_label.setStyleSheet("background-color : rgb(84, 84, 84);\n"
"border-top: 1px solid black;\n"
"border-bottom: 1px solid black;\n"
"border-left: 1px solid black;\n"
"")
        self.head_duration_label.setFrameShape(QtGui.QFrame.NoFrame)
        self.head_duration_label.setAlignment(QtCore.Qt.AlignCenter)
        self.head_duration_label.setObjectName("head_duration_label")
        self.gridLayout.addWidget(self.head_duration_label, 1, 0, 1, 1)
        self.cut_duration_label = QtGui.QLabel(CutDiffCard)
        self.cut_duration_label.setStyleSheet("background-color : rgb(84, 84, 84);\n"
"border-top: 1px solid black;\n"
"border-bottom: 1px solid black;\n"
"border-left: 1px solid black;\n"
"")
        self.cut_duration_label.setFrameShape(QtGui.QFrame.NoFrame)
        self.cut_duration_label.setAlignment(QtCore.Qt.AlignCenter)
        self.cut_duration_label.setObjectName("cut_duration_label")
        self.gridLayout.addWidget(self.cut_duration_label, 1, 1, 1, 1)
        self.tail_duration_label = QtGui.QLabel(CutDiffCard)
        self.tail_duration_label.setStyleSheet("background-color : rgb(84, 84, 84);\n"
"border-top: 1px solid black;\n"
"border-left: 1px solid black;\n"
"border-right: 1px solid black;\n"
"border-bottom: 1px solid black;")
        self.tail_duration_label.setFrameShape(QtGui.QFrame.NoFrame)
        self.tail_duration_label.setAlignment(QtCore.Qt.AlignCenter)
        self.tail_duration_label.setObjectName("tail_duration_label")
        self.gridLayout.addWidget(self.tail_duration_label, 1, 2, 1, 1)
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
        self.shot_title_label.setText(QtGui.QApplication.translate("CutDiffCard", "SHOT", None, QtGui.QApplication.UnicodeUTF8))
        self.version_title_label.setText(QtGui.QApplication.translate("CutDiffCard", "VERSION", None, QtGui.QApplication.UnicodeUTF8))
        self.shot_name_label.setText(QtGui.QApplication.translate("CutDiffCard", "sh_001_001", None, QtGui.QApplication.UnicodeUTF8))
        self.status_label.setText(QtGui.QApplication.translate("CutDiffCard", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.shot_head_in_label.setText(QtGui.QApplication.translate("CutDiffCard", "1001", None, QtGui.QApplication.UnicodeUTF8))
        self.cut_in_label.setText(QtGui.QApplication.translate("CutDiffCard", "1009", None, QtGui.QApplication.UnicodeUTF8))
        self.cut_out_label.setText(QtGui.QApplication.translate("CutDiffCard", "1028", None, QtGui.QApplication.UnicodeUTF8))
        self.shot_tail_out_label.setText(QtGui.QApplication.translate("CutDiffCard", "1036", None, QtGui.QApplication.UnicodeUTF8))
        self.cut_title_label.setText(QtGui.QApplication.translate("CutDiffCard", "CUT", None, QtGui.QApplication.UnicodeUTF8))
        self.head_title_label.setText(QtGui.QApplication.translate("CutDiffCard", "HEAD", None, QtGui.QApplication.UnicodeUTF8))
        self.tail_title_label.setText(QtGui.QApplication.translate("CutDiffCard", "TAIL", None, QtGui.QApplication.UnicodeUTF8))
        self.head_duration_label.setText(QtGui.QApplication.translate("CutDiffCard", "8", None, QtGui.QApplication.UnicodeUTF8))
        self.cut_duration_label.setText(QtGui.QApplication.translate("CutDiffCard", "20", None, QtGui.QApplication.UnicodeUTF8))
        self.tail_duration_label.setText(QtGui.QApplication.translate("CutDiffCard", "8", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
