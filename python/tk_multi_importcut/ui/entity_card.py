# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'entity_card.ui'
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


from ..dialog import ElidedLabel

from  . import resources_rc

class Ui_EntityCard(object):
    def setupUi(self, EntityCard):
        if not EntityCard.objectName():
            EntityCard.setObjectName(u"EntityCard")
        EntityCard.resize(358, 70)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(EntityCard.sizePolicy().hasHeightForWidth())
        EntityCard.setSizePolicy(sizePolicy)
        EntityCard.setMinimumSize(QSize(310, 70))
        EntityCard.setMaximumSize(QSize(470, 16777215))
        EntityCard.setBaseSize(QSize(358, 70))
        EntityCard.setFocusPolicy(Qt.StrongFocus)
        EntityCard.setStyleSheet(u"")
        EntityCard.setFrameShape(QFrame.Box)
        EntityCard.setFrameShadow(QFrame.Plain)
        EntityCard.setLineWidth(2)
        self.horizontalLayout = QHBoxLayout(EntityCard)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(4, 1, 0, 1)
        self.icon_label = QLabel(EntityCard)
        self.icon_label.setObjectName(u"icon_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.icon_label.sizePolicy().hasHeightForWidth())
        self.icon_label.setSizePolicy(sizePolicy1)
        self.icon_label.setMinimumSize(QSize(105, 59))
        self.icon_label.setMaximumSize(QSize(105, 59))
        self.icon_label.setBaseSize(QSize(105, 59))
        self.icon_label.setStyleSheet(u"background-color: black;")
        self.icon_label.setPixmap(QPixmap(u":/tk_multi_importcut/default_card_icon.png"))
        self.icon_label.setScaledContents(False)
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.icon_label)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(1)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, 4, -1, 4)
        self.title_label = QLabel(EntityCard)
        self.title_label.setObjectName(u"title_label")

        self.verticalLayout_2.addWidget(self.title_label)

        self.status_label = QLabel(EntityCard)
        self.status_label.setObjectName(u"status_label")

        self.verticalLayout_2.addWidget(self.status_label)

        self.details_label = ElidedLabel(EntityCard)
        self.details_label.setObjectName(u"details_label")

        self.verticalLayout_2.addWidget(self.details_label)

        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.select_button = QPushButton(EntityCard)
        self.select_button.setObjectName(u"select_button")
        sizePolicy2 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.select_button.sizePolicy().hasHeightForWidth())
        self.select_button.setSizePolicy(sizePolicy2)
        self.select_button.setMaximumSize(QSize(30, 30))
        icon = QIcon()
        icon.addFile(u":/tk_multi_importcut/right_arrow.png", QSize(), QIcon.Normal, QIcon.Off)
        self.select_button.setIcon(icon)
        self.select_button.setIconSize(QSize(30, 30))
        self.select_button.setCheckable(False)
        self.select_button.setFlat(True)

        self.horizontalLayout.addWidget(self.select_button)

        self.horizontalLayout.setStretch(1, 1)

        self.retranslateUi(EntityCard)

        QMetaObject.connectSlotsByName(EntityCard)
    # setupUi

    def retranslateUi(self, EntityCard):
        EntityCard.setWindowTitle(QCoreApplication.translate("EntityCard", u"Frame", None))
        self.icon_label.setText("")
        self.title_label.setText(QCoreApplication.translate("EntityCard", u"<big><b>Name</b></big>", None))
        self.status_label.setText(QCoreApplication.translate("EntityCard", u"Status", None))
        self.details_label.setText(QCoreApplication.translate("EntityCard", u"<small>details</small>", None))
#if QT_CONFIG(tooltip)
        self.select_button.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.select_button.setText("")
    # retranslateUi
