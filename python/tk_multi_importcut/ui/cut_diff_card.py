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
        CutDiffCard.resize(764, 101)
        CutDiffCard.setFrameShape(QtGui.QFrame.StyledPanel)
        CutDiffCard.setFrameShadow(QtGui.QFrame.Raised)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(CutDiffCard)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.left_layout = QtGui.QHBoxLayout()
        self.left_layout.setSpacing(5)
        self.left_layout.setContentsMargins(0, -1, 10, -1)
        self.left_layout.setObjectName("left_layout")
        self.cut_order_label = QtGui.QLabel(CutDiffCard)
        self.cut_order_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.cut_order_label.setMargin(0)
        self.cut_order_label.setIndent(0)
        self.cut_order_label.setObjectName("cut_order_label")
        self.left_layout.addWidget(self.cut_order_label)
        self.icon_label = QtGui.QLabel(CutDiffCard)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.icon_label.sizePolicy().hasHeightForWidth())
        self.icon_label.setSizePolicy(sizePolicy)
        self.icon_label.setMinimumSize(QtCore.QSize(160, 90))
        self.icon_label.setMaximumSize(QtCore.QSize(160, 90))
        self.icon_label.setBaseSize(QtCore.QSize(160, 90))
        self.icon_label.setStyleSheet("background-color: black;")
        self.icon_label.setText("")
        self.icon_label.setPixmap(QtGui.QPixmap(":/tk_multi_importcut/sg_logo.png"))
        self.icon_label.setAlignment(QtCore.Qt.AlignCenter)
        self.icon_label.setMargin(0)
        self.icon_label.setIndent(0)
        self.icon_label.setObjectName("icon_label")
        self.left_layout.addWidget(self.icon_label)
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
        self.status_label.setWordWrap(True)
        self.status_label.setObjectName("status_label")
        self.gridLayout_2.addWidget(self.status_label, 2, 0, 1, 2)
        self.gridLayout_2.setColumnStretch(1, 1)
        self.left_layout.addLayout(self.gridLayout_2)
        self.left_layout.setStretch(2, 1)
        self.horizontalLayout_2.addLayout(self.left_layout)
        self.right_layout = QtGui.QVBoxLayout()
        self.right_layout.setSpacing(0)
        self.right_layout.setContentsMargins(-1, -1, -1, 0)
        self.right_layout.setObjectName("right_layout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.tail_title_label = QtGui.QLabel(CutDiffCard)
        self.tail_title_label.setStyleSheet("background-color : rgb(74, 74, 74);\n"
"border-top: 1px solid black;\n"
"border-left: 1px solid black;\n"
"border-right: 1px solid black;")
        self.tail_title_label.setFrameShape(QtGui.QFrame.NoFrame)
        self.tail_title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.tail_title_label.setObjectName("tail_title_label")
        self.gridLayout.addWidget(self.tail_title_label, 1, 5, 1, 2)
        self.head_title_label = QtGui.QLabel(CutDiffCard)
        self.head_title_label.setStyleSheet("background-color : rgb(74, 74, 74);\n"
"border-top: 1px solid black;\n"
"border-left: 1px solid black;\n"
"")
        self.head_title_label.setFrameShape(QtGui.QFrame.NoFrame)
        self.head_title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.head_title_label.setMargin(1)
        self.head_title_label.setObjectName("head_title_label")
        self.gridLayout.addWidget(self.head_title_label, 1, 0, 1, 2)
        self.label_4 = QtGui.QLabel(CutDiffCard)
        self.label_4.setStyleSheet("background-color : rgb(84, 84, 84);\n"
"border-top: 1px solid black;\n"
"")
        self.label_4.setText("")
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 3, 1, 1)
        self.cut_out_label = QtGui.QLabel(CutDiffCard)
        self.cut_out_label.setStyleSheet("background-color : rgb(84, 84, 84);\n"
"border-top: 1px solid black;\n"
"")
        self.cut_out_label.setAlignment(QtCore.Qt.AlignCenter)
        self.cut_out_label.setObjectName("cut_out_label")
        self.gridLayout.addWidget(self.cut_out_label, 0, 4, 1, 2)
        self.cut_title_label = QtGui.QLabel(CutDiffCard)
        self.cut_title_label.setStyleSheet("background-color : rgb(74, 74, 74);\n"
"border-top: 1px solid black;\n"
"border-left: 1px solid black;\n"
"")
        self.cut_title_label.setFrameShape(QtGui.QFrame.NoFrame)
        self.cut_title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.cut_title_label.setObjectName("cut_title_label")
        self.gridLayout.addWidget(self.cut_title_label, 1, 2, 1, 3)
        self.cut_in_label = QtGui.QLabel(CutDiffCard)
        self.cut_in_label.setStyleSheet("background-color : rgb(84, 84, 84);\n"
"border-top: 1px solid black;\n"
"")
        self.cut_in_label.setAlignment(QtCore.Qt.AlignCenter)
        self.cut_in_label.setObjectName("cut_in_label")
        self.gridLayout.addWidget(self.cut_in_label, 0, 1, 1, 2)
        self.shot_head_in_label = QtGui.QLabel(CutDiffCard)
        self.shot_head_in_label.setStyleSheet("background-color : rgb(84, 84, 84);\n"
"border-top: 1px solid black;\n"
"border-left: 1px solid black;")
        self.shot_head_in_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.shot_head_in_label.setObjectName("shot_head_in_label")
        self.gridLayout.addWidget(self.shot_head_in_label, 0, 0, 1, 1)
        self.shot_tail_out_label = QtGui.QLabel(CutDiffCard)
        self.shot_tail_out_label.setStyleSheet("background-color : rgb(84, 84, 84);\n"
"border-top: 1px solid black;\n"
"border-right: 1px solid black;")
        self.shot_tail_out_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.shot_tail_out_label.setObjectName("shot_tail_out_label")
        self.gridLayout.addWidget(self.shot_tail_out_label, 0, 6, 1, 1)
        self.head_duration_label = QtGui.QLabel(CutDiffCard)
        self.head_duration_label.setStyleSheet("background-color : rgb(84, 84, 84);\n"
"border-top: 1px solid black;\n"
"border-bottom: 1px solid black;\n"
"border-left: 1px solid black;\n"
"")
        self.head_duration_label.setFrameShape(QtGui.QFrame.NoFrame)
        self.head_duration_label.setAlignment(QtCore.Qt.AlignCenter)
        self.head_duration_label.setObjectName("head_duration_label")
        self.gridLayout.addWidget(self.head_duration_label, 2, 0, 1, 2)
        self.cut_duration_label = QtGui.QLabel(CutDiffCard)
        self.cut_duration_label.setStyleSheet("background-color : rgb(84, 84, 84);\n"
"border-top: 1px solid black;\n"
"border-bottom: 1px solid black;\n"
"border-left: 1px solid black;\n"
"")
        self.cut_duration_label.setFrameShape(QtGui.QFrame.NoFrame)
        self.cut_duration_label.setAlignment(QtCore.Qt.AlignCenter)
        self.cut_duration_label.setObjectName("cut_duration_label")
        self.gridLayout.addWidget(self.cut_duration_label, 2, 2, 1, 3)
        self.tail_duration_label = QtGui.QLabel(CutDiffCard)
        self.tail_duration_label.setStyleSheet("background-color : rgb(84, 84, 84);\n"
"border-top: 1px solid black;\n"
"border-left: 1px solid black;\n"
"border-right: 1px solid black;\n"
"border-bottom: 1px solid black;")
        self.tail_duration_label.setFrameShape(QtGui.QFrame.NoFrame)
        self.tail_duration_label.setAlignment(QtCore.Qt.AlignCenter)
        self.tail_duration_label.setObjectName("tail_duration_label")
        self.gridLayout.addWidget(self.tail_duration_label, 2, 5, 1, 2)
        self.gridLayout.setRowStretch(0, 3)
        self.gridLayout.setRowStretch(1, 2)
        self.gridLayout.setRowStretch(2, 3)
        self.right_layout.addLayout(self.gridLayout)
        self.right_layout.setStretch(0, 2)
        self.horizontalLayout_2.addLayout(self.right_layout)
        self.horizontalLayout_2.setStretch(0, 3)
        self.horizontalLayout_2.setStretch(1, 2)

        self.retranslateUi(CutDiffCard)
        QtCore.QMetaObject.connectSlotsByName(CutDiffCard)

    def retranslateUi(self, CutDiffCard):
        CutDiffCard.setWindowTitle(QtGui.QApplication.translate("CutDiffCard", "Frame", None, QtGui.QApplication.UnicodeUTF8))
        self.cut_order_label.setText(QtGui.QApplication.translate("CutDiffCard", "001", None, QtGui.QApplication.UnicodeUTF8))
        self.version_name_label.setText(QtGui.QApplication.translate("CutDiffCard", "sh_001_001_fg_v001", None, QtGui.QApplication.UnicodeUTF8))
        self.shot_title_label.setText(QtGui.QApplication.translate("CutDiffCard", "SHOT", None, QtGui.QApplication.UnicodeUTF8))
        self.version_title_label.setText(QtGui.QApplication.translate("CutDiffCard", "VERSION", None, QtGui.QApplication.UnicodeUTF8))
        self.shot_name_label.setText(QtGui.QApplication.translate("CutDiffCard", "sh_001_001", None, QtGui.QApplication.UnicodeUTF8))
        self.status_label.setText(QtGui.QApplication.translate("CutDiffCard", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.tail_title_label.setText(QtGui.QApplication.translate("CutDiffCard", "<b>TAIL</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.head_title_label.setText(QtGui.QApplication.translate("CutDiffCard", "<b>HEAD</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.cut_out_label.setText(QtGui.QApplication.translate("CutDiffCard", "1028", None, QtGui.QApplication.UnicodeUTF8))
        self.cut_title_label.setText(QtGui.QApplication.translate("CutDiffCard", "<b>CUT</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.cut_in_label.setText(QtGui.QApplication.translate("CutDiffCard", "1009", None, QtGui.QApplication.UnicodeUTF8))
        self.shot_head_in_label.setText(QtGui.QApplication.translate("CutDiffCard", "1001", None, QtGui.QApplication.UnicodeUTF8))
        self.shot_tail_out_label.setText(QtGui.QApplication.translate("CutDiffCard", "1036", None, QtGui.QApplication.UnicodeUTF8))
        self.head_duration_label.setText(QtGui.QApplication.translate("CutDiffCard", "8", None, QtGui.QApplication.UnicodeUTF8))
        self.cut_duration_label.setText(QtGui.QApplication.translate("CutDiffCard", "20", None, QtGui.QApplication.UnicodeUTF8))
        self.tail_duration_label.setText(QtGui.QApplication.translate("CutDiffCard", "8", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc