# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cut_diff_card.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from tank.platform.qt import QtCore
for name, cls in QtCore.__dict__.items():
    if isinstance(cls, type): globals()[name] = cls

from tank.platform.qt import QtGui
for name, cls in QtGui.__dict__.items():
    if isinstance(cls, type): globals()[name] = cls


from ..dialog import EntityLineWidget
from ..dialog import ExtendedThumbnail

from  . import resources_rc

class Ui_CutDiffCard(object):
    def setupUi(self, CutDiffCard):
        if not CutDiffCard.objectName():
            CutDiffCard.setObjectName(u"CutDiffCard")
        CutDiffCard.resize(876, 94)
        CutDiffCard.setFrameShape(QFrame.StyledPanel)
        CutDiffCard.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(CutDiffCard)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.left_layout = QHBoxLayout()
        self.left_layout.setSpacing(5)
        self.left_layout.setObjectName(u"left_layout")
        self.left_layout.setContentsMargins(4, 4, 0, 4)
        self.icon_label = ExtendedThumbnail(CutDiffCard)
        self.icon_label.setObjectName(u"icon_label")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.icon_label.sizePolicy().hasHeightForWidth())
        self.icon_label.setSizePolicy(sizePolicy)
        self.icon_label.setMinimumSize(QSize(142, 80))
        self.icon_label.setMaximumSize(QSize(142, 80))
        self.icon_label.setBaseSize(QSize(142, 80))
        self.icon_label.setStyleSheet(u"background-color: black;")
        self.icon_label.setPixmap(QPixmap(u":/tk_multi_importcut/sg_logo.png"))
        self.icon_label.setScaledContents(False)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setMargin(0)
        self.icon_label.setIndent(0)

        self.left_layout.addWidget(self.icon_label)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(-1)
        self.gridLayout_2.setVerticalSpacing(2)
        self.version_name_label = QLabel(CutDiffCard)
        self.version_name_label.setObjectName(u"version_name_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.version_name_label.sizePolicy().hasHeightForWidth())
        self.version_name_label.setSizePolicy(sizePolicy1)

        self.gridLayout_2.addWidget(self.version_name_label, 1, 1, 1, 1)

        self.version_title_label = QLabel(CutDiffCard)
        self.version_title_label.setObjectName(u"version_title_label")

        self.gridLayout_2.addWidget(self.version_title_label, 1, 0, 1, 1)

        self.shot_title_label = QLabel(CutDiffCard)
        self.shot_title_label.setObjectName(u"shot_title_label")
        self.shot_title_label.setStyleSheet(u"")
        self.shot_title_label.setProperty("constant_title", True)

        self.gridLayout_2.addWidget(self.shot_title_label, 0, 0, 1, 1)

        self.shot_name_line = EntityLineWidget(CutDiffCard)
        self.shot_name_line.setObjectName(u"shot_name_line")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.shot_name_line.sizePolicy().hasHeightForWidth())
        self.shot_name_line.setSizePolicy(sizePolicy2)

        self.gridLayout_2.addWidget(self.shot_name_line, 0, 1, 1, 1)

        self.status_label = QLabel(CutDiffCard)
        self.status_label.setObjectName(u"status_label")
        self.status_label.setWordWrap(True)

        self.gridLayout_2.addWidget(self.status_label, 2, 0, 1, 2)

        self.gridLayout_2.setRowStretch(0, 1)
        self.gridLayout_2.setRowStretch(1, 1)
        self.gridLayout_2.setRowStretch(2, 1)
        self.gridLayout_2.setColumnStretch(0, 1)
        self.gridLayout_2.setColumnStretch(1, 4)

        self.left_layout.addLayout(self.gridLayout_2)

        self.left_layout.setStretch(1, 1)

        self.horizontalLayout_2.addLayout(self.left_layout)

        self.right_layout = QVBoxLayout()
        self.right_layout.setSpacing(0)
        self.right_layout.setObjectName(u"right_layout")
        self.right_layout.setContentsMargins(0, -1, 0, 0)
        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tail_title_label = QLabel(CutDiffCard)
        self.tail_title_label.setObjectName(u"tail_title_label")
        self.tail_title_label.setFrameShape(QFrame.NoFrame)
        self.tail_title_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.tail_title_label, 1, 5, 1, 2)

        self.head_title_label = QLabel(CutDiffCard)
        self.head_title_label.setObjectName(u"head_title_label")
        self.head_title_label.setFrameShape(QFrame.NoFrame)
        self.head_title_label.setAlignment(Qt.AlignCenter)
        self.head_title_label.setMargin(1)

        self.gridLayout.addWidget(self.head_title_label, 1, 0, 1, 2)

        self.separator_label = QLabel(CutDiffCard)
        self.separator_label.setObjectName(u"separator_label")

        self.gridLayout.addWidget(self.separator_label, 0, 3, 1, 1)

        self.cut_out_label = QLabel(CutDiffCard)
        self.cut_out_label.setObjectName(u"cut_out_label")
        self.cut_out_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.cut_out_label, 0, 4, 1, 2)

        self.cut_title_label = QLabel(CutDiffCard)
        self.cut_title_label.setObjectName(u"cut_title_label")
        self.cut_title_label.setFrameShape(QFrame.NoFrame)
        self.cut_title_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.cut_title_label, 1, 2, 1, 3)

        self.cut_in_label = QLabel(CutDiffCard)
        self.cut_in_label.setObjectName(u"cut_in_label")
        self.cut_in_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.cut_in_label, 0, 1, 1, 2)

        self.shot_head_in_label = QLabel(CutDiffCard)
        self.shot_head_in_label.setObjectName(u"shot_head_in_label")
        self.shot_head_in_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.shot_head_in_label.setMargin(4)
        self.shot_head_in_label.setIndent(-1)

        self.gridLayout.addWidget(self.shot_head_in_label, 0, 0, 1, 1)

        self.shot_tail_out_label = QLabel(CutDiffCard)
        self.shot_tail_out_label.setObjectName(u"shot_tail_out_label")
        self.shot_tail_out_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.shot_tail_out_label.setMargin(4)
        self.shot_tail_out_label.setIndent(-1)

        self.gridLayout.addWidget(self.shot_tail_out_label, 0, 6, 1, 1)

        self.head_duration_label = QLabel(CutDiffCard)
        self.head_duration_label.setObjectName(u"head_duration_label")
        self.head_duration_label.setFrameShape(QFrame.NoFrame)
        self.head_duration_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.head_duration_label, 2, 0, 1, 2)

        self.cut_duration_label = QLabel(CutDiffCard)
        self.cut_duration_label.setObjectName(u"cut_duration_label")
        self.cut_duration_label.setFrameShape(QFrame.NoFrame)
        self.cut_duration_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.cut_duration_label, 2, 2, 1, 3)

        self.tail_duration_label = QLabel(CutDiffCard)
        self.tail_duration_label.setObjectName(u"tail_duration_label")
        self.tail_duration_label.setFrameShape(QFrame.NoFrame)
        self.tail_duration_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.tail_duration_label, 2, 5, 1, 2)

        self.gridLayout.setRowStretch(0, 3)
        self.gridLayout.setRowStretch(1, 2)
        self.gridLayout.setRowStretch(2, 3)

        self.right_layout.addLayout(self.gridLayout)

        self.right_layout.setStretch(0, 2)

        self.horizontalLayout_2.addLayout(self.right_layout)

        self.horizontalLayout_2.setStretch(0, 2)
        self.horizontalLayout_2.setStretch(1, 2)

        self.retranslateUi(CutDiffCard)

        QMetaObject.connectSlotsByName(CutDiffCard)
    # setupUi

    def retranslateUi(self, CutDiffCard):
        CutDiffCard.setWindowTitle(QCoreApplication.translate("CutDiffCard", u"Frame", None))
        self.icon_label.setText("")
        self.version_name_label.setText("")
        self.version_title_label.setText(QCoreApplication.translate("CutDiffCard", u"Version", None))
        self.shot_title_label.setText(QCoreApplication.translate("CutDiffCard", u"Shot", None))
        self.shot_name_line.setText("")
        self.status_label.setText(QCoreApplication.translate("CutDiffCard", u"New", None))
        self.tail_title_label.setText(QCoreApplication.translate("CutDiffCard", u"<b>TAIL</b>", None))
        self.head_title_label.setText(QCoreApplication.translate("CutDiffCard", u"<b>HEAD</b>", None))
        self.separator_label.setText("")
        self.cut_out_label.setText(QCoreApplication.translate("CutDiffCard", u"1028", None))
        self.cut_title_label.setText(QCoreApplication.translate("CutDiffCard", u"<b>CUT</b>", None))
        self.cut_in_label.setText(QCoreApplication.translate("CutDiffCard", u"1009", None))
        self.shot_head_in_label.setText(QCoreApplication.translate("CutDiffCard", u"1001", None))
        self.shot_tail_out_label.setText(QCoreApplication.translate("CutDiffCard", u"1036", None))
        self.head_duration_label.setText(QCoreApplication.translate("CutDiffCard", u"8", None))
        self.cut_duration_label.setText(QCoreApplication.translate("CutDiffCard", u"20", None))
        self.tail_duration_label.setText(QCoreApplication.translate("CutDiffCard", u"8", None))
    # retranslateUi
