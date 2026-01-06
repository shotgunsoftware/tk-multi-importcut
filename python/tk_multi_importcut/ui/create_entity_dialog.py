# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'create_entity_dialog.ui'
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


class Ui_create_entity_dialog(object):
    def setupUi(self, create_entity_dialog):
        if not create_entity_dialog.objectName():
            create_entity_dialog.setObjectName(u"create_entity_dialog")
        create_entity_dialog.resize(501, 297)
        self.verticalLayout = QVBoxLayout(create_entity_dialog)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.create_new_entity_label = QLabel(create_entity_dialog)
        self.create_new_entity_label.setObjectName(u"create_new_entity_label")
        self.create_new_entity_label.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.create_new_entity_label.sizePolicy().hasHeightForWidth())
        self.create_new_entity_label.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamily(u"Helvetica Neue")
        font.setPointSize(24)
        font.setBold(False)
        font.setWeight(50)
        self.create_new_entity_label.setFont(font)
        self.create_new_entity_label.setMargin(12)
        self.create_new_entity_label.setIndent(3)

        self.verticalLayout.addWidget(self.create_new_entity_label)

        self.create_entity_line_1 = QFrame(create_entity_dialog)
        self.create_entity_line_1.setObjectName(u"create_entity_line_1")
        self.create_entity_line_1.setLineWidth(0)
        self.create_entity_line_1.setMidLineWidth(1)
        self.create_entity_line_1.setFrameShape(QFrame.HLine)
        self.create_entity_line_1.setFrameShadow(QFrame.Sunken)

        self.verticalLayout.addWidget(self.create_entity_line_1)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setHorizontalSpacing(10)
        self.formLayout.setVerticalSpacing(10)
        self.formLayout.setContentsMargins(22, 15, 12, -1)
        self.entity_name_label = QLabel(create_entity_dialog)
        self.entity_name_label.setObjectName(u"entity_name_label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.entity_name_label)

        self.entity_name_line_edit = QLineEdit(create_entity_dialog)
        self.entity_name_line_edit.setObjectName(u"entity_name_line_edit")
        self.entity_name_line_edit.setMinimumSize(QSize(320, 25))
        self.entity_name_line_edit.setFrame(True)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.entity_name_line_edit)

        self.description_label = QLabel(create_entity_dialog)
        self.description_label.setObjectName(u"description_label")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.description_label)

        self.description_line_edit = QLineEdit(create_entity_dialog)
        self.description_line_edit.setObjectName(u"description_line_edit")
        self.description_line_edit.setMinimumSize(QSize(320, 25))

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.description_line_edit)

        self.status_combo_box = QComboBox(create_entity_dialog)
        self.status_combo_box.setObjectName(u"status_combo_box")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.status_combo_box)

        self.status_label = QLabel(create_entity_dialog)
        self.status_label.setObjectName(u"status_label")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.status_label)

        self.project_label = QLabel(create_entity_dialog)
        self.project_label.setObjectName(u"project_label")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.project_label)

        self.project_name_label = QLabel(create_entity_dialog)
        self.project_name_label.setObjectName(u"project_name_label")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.project_name_label)

        self.verticalLayout.addLayout(self.formLayout)

        self.create_entity_line_2 = QFrame(create_entity_dialog)
        self.create_entity_line_2.setObjectName(u"create_entity_line_2")
        self.create_entity_line_2.setLineWidth(0)
        self.create_entity_line_2.setMidLineWidth(1)
        self.create_entity_line_2.setFrameShape(QFrame.HLine)
        self.create_entity_line_2.setFrameShadow(QFrame.Sunken)

        self.verticalLayout.addWidget(self.create_entity_line_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 9, 7, 8)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.cancel_button = QPushButton(create_entity_dialog)
        self.cancel_button.setObjectName(u"cancel_button")
        self.cancel_button.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.cancel_button)

        self.create_entity_button = QPushButton(create_entity_dialog)
        self.create_entity_button.setObjectName(u"create_entity_button")
        self.create_entity_button.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.create_entity_button)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(create_entity_dialog)

        QMetaObject.connectSlotsByName(create_entity_dialog)
    # setupUi

    def retranslateUi(self, create_entity_dialog):
        create_entity_dialog.setWindowTitle(QCoreApplication.translate("create_entity_dialog", u"Dialog", None))
        self.create_new_entity_label.setText(QCoreApplication.translate("create_entity_dialog", u"Create a new Entity", None))
        self.entity_name_label.setText(QCoreApplication.translate("create_entity_dialog", u"Sequence Name:", None))
        self.description_label.setText(QCoreApplication.translate("create_entity_dialog", u"Description:", None))
        self.status_label.setText(QCoreApplication.translate("create_entity_dialog", u"Status:", None))
        self.project_label.setText(QCoreApplication.translate("create_entity_dialog", u"Project:", None))
        self.project_name_label.setText(QCoreApplication.translate("create_entity_dialog", u"Some project", None))
        self.cancel_button.setText(QCoreApplication.translate("create_entity_dialog", u"Cancel", None))
        self.create_entity_button.setText(QCoreApplication.translate("create_entity_dialog", u"Create Entity", None))
    # retranslateUi
