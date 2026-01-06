# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'submit_dialog.ui'
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


class Ui_submit_dialog(object):
    def setupUi(self, submit_dialog):
        if not submit_dialog.objectName():
            submit_dialog.setObjectName(u"submit_dialog")
        submit_dialog.resize(382, 526)
        submit_dialog.setModal(True)
        self.gridLayout_2 = QGridLayout(submit_dialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(0)
        self.gridLayout_2.setVerticalSpacing(12)
        self.gridLayout_2.setContentsMargins(-1, -1, 12, 12)
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setContentsMargins(0, -1, 0, -1)
        self.label = QLabel(submit_dialog)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.title_text = QLineEdit(submit_dialog)
        self.title_text.setObjectName(u"title_text")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.title_text)

        self.label_2 = QLabel(submit_dialog)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.from_label = QLabel(submit_dialog)
        self.from_label.setObjectName(u"from_label")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.from_label)

        self.label_4 = QLabel(submit_dialog)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_4)

        self.to_text = QLineEdit(submit_dialog)
        self.to_text.setObjectName(u"to_text")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.to_text)

        self.label_5 = QLabel(submit_dialog)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_5)

        self.description_text = QTextEdit(submit_dialog)
        self.description_text.setObjectName(u"description_text")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.description_text)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setVerticalSpacing(-1)
        self.gridLayout.setContentsMargins(1, 0, 1, 0)
        self.line_3 = QFrame(submit_dialog)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShadow(QFrame.Plain)
        self.line_3.setFrameShape(QFrame.HLine)

        self.gridLayout.addWidget(self.line_3, 7, 0, 1, 4)

        self.label_9 = QLabel(submit_dialog)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setStyleSheet(u"")
        self.label_9.setMargin(0)

        self.gridLayout.addWidget(self.label_9, 6, 0, 1, 1)

        self.label_3 = QLabel(submit_dialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setStyleSheet(u"")
        self.label_3.setMargin(0)

        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 1)

        self.label_7 = QLabel(submit_dialog)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setStyleSheet(u"")
        self.label_7.setFrameShape(QFrame.NoFrame)
        self.label_7.setMargin(0)

        self.gridLayout.addWidget(self.label_7, 2, 0, 1, 1)

        self.label_8 = QLabel(submit_dialog)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setStyleSheet(u"")

        self.gridLayout.addWidget(self.label_8, 4, 2, 1, 1)

        self.label_6 = QLabel(submit_dialog)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setFrameShape(QFrame.NoFrame)
        self.label_6.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_6.setMargin(0)

        self.gridLayout.addWidget(self.label_6, 0, 0, 1, 4)

        self.rescans_label = QLabel(submit_dialog)
        self.rescans_label.setObjectName(u"rescans_label")
        self.rescans_label.setStyleSheet(u"")
        self.rescans_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.rescans_label, 4, 3, 1, 1)

        self.label_11 = QLabel(submit_dialog)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setStyleSheet(u"")
        self.label_11.setMargin(0)

        self.gridLayout.addWidget(self.label_11, 8, 0, 1, 1)

        self.repeated_label = QLabel(submit_dialog)
        self.repeated_label.setObjectName(u"repeated_label")
        self.repeated_label.setStyleSheet(u"")
        self.repeated_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.repeated_label, 6, 3, 1, 1)

        self.cut_changes_label = QLabel(submit_dialog)
        self.cut_changes_label.setObjectName(u"cut_changes_label")
        self.cut_changes_label.setStyleSheet(u"")
        self.cut_changes_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.cut_changes_label, 2, 3, 1, 1)

        self.total_shots_label = QLabel(submit_dialog)
        self.total_shots_label.setObjectName(u"total_shots_label")
        self.total_shots_label.setStyleSheet(u"")
        self.total_shots_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.total_shots_label, 2, 1, 1, 1)

        self.label_12 = QLabel(submit_dialog)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setStyleSheet(u"")

        self.gridLayout.addWidget(self.label_12, 2, 2, 1, 1)

        self.new_shots_label = QLabel(submit_dialog)
        self.new_shots_label.setObjectName(u"new_shots_label")
        self.new_shots_label.setStyleSheet(u"")
        self.new_shots_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.new_shots_label, 4, 1, 1, 1)

        self.line_2 = QFrame(submit_dialog)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShadow(QFrame.Plain)
        self.line_2.setFrameShape(QFrame.HLine)

        self.gridLayout.addWidget(self.line_2, 5, 0, 1, 4)

        self.no_link_label = QLabel(submit_dialog)
        self.no_link_label.setObjectName(u"no_link_label")
        self.no_link_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.no_link_label, 8, 3, 1, 1)

        self.reinstated_label = QLabel(submit_dialog)
        self.reinstated_label.setObjectName(u"reinstated_label")
        self.reinstated_label.setStyleSheet(u"")
        self.reinstated_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.reinstated_label, 8, 1, 1, 1)

        self.omitted_label = QLabel(submit_dialog)
        self.omitted_label.setObjectName(u"omitted_label")
        self.omitted_label.setStyleSheet(u"")
        self.omitted_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.omitted_label, 6, 1, 1, 1)

        self.no_link_title_label = QLabel(submit_dialog)
        self.no_link_title_label.setObjectName(u"no_link_title_label")
        self.no_link_title_label.setEnabled(True)

        self.gridLayout.addWidget(self.no_link_title_label, 8, 2, 1, 1)

        self.label_10 = QLabel(submit_dialog)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setStyleSheet(u"")

        self.gridLayout.addWidget(self.label_10, 6, 2, 1, 1)

        self.line_4 = QFrame(submit_dialog)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShadow(QFrame.Plain)
        self.line_4.setFrameShape(QFrame.HLine)

        self.gridLayout.addWidget(self.line_4, 3, 0, 1, 4)

        self.line_1 = QFrame(submit_dialog)
        self.line_1.setObjectName(u"line_1")
        self.line_1.setFrameShadow(QFrame.Plain)
        self.line_1.setFrameShape(QFrame.HLine)

        self.gridLayout.addWidget(self.line_1, 1, 0, 1, 4)

        self.update_shot_fields_checkbox = QCheckBox(submit_dialog)
        self.update_shot_fields_checkbox.setObjectName(u"update_shot_fields_checkbox")

        self.gridLayout.addWidget(self.update_shot_fields_checkbox, 10, 0, 1, 4)

        self.line_5 = QFrame(submit_dialog)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShadow(QFrame.Plain)
        self.line_5.setFrameShape(QFrame.HLine)

        self.gridLayout.addWidget(self.line_5, 9, 0, 1, 4)

        self.formLayout.setLayout(4, QFormLayout.FieldRole, self.gridLayout)

        self.gridLayout_2.addLayout(self.formLayout, 0, 1, 1, 1)

        self.line = QFrame(submit_dialog)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout_2.addWidget(self.line, 2, 0, 1, 3)

        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer, 0, 2, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 34, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer, 1, 1, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)

        self.cancel_button = QPushButton(submit_dialog)
        self.cancel_button.setObjectName(u"cancel_button")

        self.horizontalLayout.addWidget(self.cancel_button)

        self.horizontalSpacer_4 = QSpacerItem(10, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_4)

        self.import_cut_button = QPushButton(submit_dialog)
        self.import_cut_button.setObjectName(u"import_cut_button")

        self.horizontalLayout.addWidget(self.import_cut_button)

        self.gridLayout_2.addLayout(self.horizontalLayout, 4, 0, 1, 3)

        self.gridLayout_2.setRowStretch(0, 1)
        self.gridLayout_2.setColumnStretch(0, 1)
        self.gridLayout_2.setColumnStretch(2, 1)

        self.retranslateUi(submit_dialog)

        QMetaObject.connectSlotsByName(submit_dialog)
    # setupUi

    def retranslateUi(self, submit_dialog):
        submit_dialog.setWindowTitle(QCoreApplication.translate("submit_dialog", u"Import Cut", None))
        self.label.setText(QCoreApplication.translate("submit_dialog", u"Title", None))
        self.label_2.setText(QCoreApplication.translate("submit_dialog", u"From", None))
        self.from_label.setText(QCoreApplication.translate("submit_dialog", u"me", None))
        self.label_4.setText(QCoreApplication.translate("submit_dialog", u"To", None))
        self.label_5.setText(QCoreApplication.translate("submit_dialog", u"Description", None))
        self.label_9.setText(QCoreApplication.translate("submit_dialog", u"Omitted", None))
        self.label_3.setText(QCoreApplication.translate("submit_dialog", u"New", None))
        self.label_7.setText(QCoreApplication.translate("submit_dialog", u"Total Shots", None))
        self.label_8.setText(QCoreApplication.translate("submit_dialog", u"Rescan Needed", None))
        self.label_6.setText(QCoreApplication.translate("submit_dialog", u"Summary", None))
        self.rescans_label.setText("")
        self.label_11.setText(QCoreApplication.translate("submit_dialog", u"Reinstated", None))
        self.repeated_label.setText("")
        self.cut_changes_label.setText("")
        self.total_shots_label.setText("")
        self.label_12.setText(QCoreApplication.translate("submit_dialog", u"Cut Changes", None))
        self.new_shots_label.setText("")
        self.no_link_label.setText("")
        self.reinstated_label.setText("")
        self.omitted_label.setText("")
        self.no_link_title_label.setText(QCoreApplication.translate("submit_dialog", u"No Link", None))
        self.label_10.setText(QCoreApplication.translate("submit_dialog", u"Repeated", None))
#if QT_CONFIG(tooltip)
        self.update_shot_fields_checkbox.setToolTip(QCoreApplication.translate("submit_dialog", u"If off, Shot fields will not be updated, but, if needed, new Shots will be created", None))
#endif // QT_CONFIG(tooltip)
        self.update_shot_fields_checkbox.setText(QCoreApplication.translate("submit_dialog", u"Update Cut Fields on Shots", None))
        self.cancel_button.setText(QCoreApplication.translate("submit_dialog", u"Cancel", None))
#if QT_CONFIG(shortcut)
        self.cancel_button.setShortcut(QCoreApplication.translate("submit_dialog", u"Esc", None))
#endif // QT_CONFIG(shortcut)
        self.import_cut_button.setText(QCoreApplication.translate("submit_dialog", u"Import Cut", None))
#if QT_CONFIG(shortcut)
        self.import_cut_button.setShortcut(QCoreApplication.translate("submit_dialog", u"Return", None))
#endif // QT_CONFIG(shortcut)
    # retranslateUi
