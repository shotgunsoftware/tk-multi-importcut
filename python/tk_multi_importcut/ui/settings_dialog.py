# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_dialog.ui'
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


from  . import resources_rc

class Ui_settings_dialog(object):
    def setupUi(self, settings_dialog):
        if not settings_dialog.objectName():
            settings_dialog.setObjectName(u"settings_dialog")
        settings_dialog.resize(530, 426)
        self.verticalLayout_2 = QVBoxLayout(settings_dialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(14, 12, -1, 4)
        self.settings_label = QLabel(settings_dialog)
        self.settings_label.setObjectName(u"settings_label")
        self.settings_label.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.settings_label.sizePolicy().hasHeightForWidth())
        self.settings_label.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamily(u"Helvetica Neue")
        font.setPointSize(24)
        font.setBold(False)
        font.setWeight(50)
        self.settings_label.setFont(font)

        self.verticalLayout_7.addWidget(self.settings_label)

        self.verticalLayout_2.addLayout(self.verticalLayout_7)

        self.general_timecode_frames_tab = QTabWidget(settings_dialog)
        self.general_timecode_frames_tab.setObjectName(u"general_timecode_frames_tab")
        self.general_timecode_frames_tab.setContextMenuPolicy(Qt.PreventContextMenu)
        self.general_timecode_frames_tab.setLayoutDirection(Qt.LeftToRight)
        self.general_timecode_frames_tab.setTabPosition(QTabWidget.North)
        self.general_timecode_frames_tab.setTabShape(QTabWidget.Rounded)
        self.general_timecode_frames_tab.setElideMode(Qt.ElideRight)
        self.general_timecode_frames_tab.setUsesScrollButtons(False)
        self.general_timecode_frames_tab.setTabsClosable(False)
        self.general_tab = QWidget()
        self.general_tab.setObjectName(u"general_tab")
        self.general_tab.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout = QVBoxLayout(self.general_tab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(12, -1, 12, 0)
        self.note_addressing_label = QLabel(self.general_tab)
        self.note_addressing_label.setObjectName(u"note_addressing_label")
        font1 = QFont()
        font1.setBold(False)
        font1.setWeight(50)
        self.note_addressing_label.setFont(font1)

        self.verticalLayout.addWidget(self.note_addressing_label)

        self.cut_summary_layout = QHBoxLayout()
        self.cut_summary_layout.setSpacing(6)
        self.cut_summary_layout.setObjectName(u"cut_summary_layout")
        self.cut_summary_layout.setContentsMargins(-1, 0, -1, 0)
        self.send_cut_summary_note_to_label = QLabel(self.general_tab)
        self.send_cut_summary_note_to_label.setObjectName(u"send_cut_summary_note_to_label")
        self.send_cut_summary_note_to_label.setFrameShape(QFrame.NoFrame)
        self.send_cut_summary_note_to_label.setScaledContents(False)
        self.send_cut_summary_note_to_label.setMargin(0)
        self.send_cut_summary_note_to_label.setIndent(14)

        self.cut_summary_layout.addWidget(self.send_cut_summary_note_to_label)

        self.email_groups_line_edit = QLineEdit(self.general_tab)
        self.email_groups_line_edit.setObjectName(u"email_groups_line_edit")

        self.cut_summary_layout.addWidget(self.email_groups_line_edit)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.cut_summary_layout.addItem(self.horizontalSpacer)

        self.verticalLayout.addLayout(self.cut_summary_layout)

        self.statuses_label = QLabel(self.general_tab)
        self.statuses_label.setObjectName(u"statuses_label")
        self.statuses_label.setFont(font1)

        self.verticalLayout.addWidget(self.statuses_label)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(-1, 2, -1, 5)
        self.description_1_label = QLabel(self.general_tab)
        self.description_1_label.setObjectName(u"description_1_label")
        self.description_1_label.setWordWrap(True)
        self.description_1_label.setIndent(14)

        self.verticalLayout_3.addWidget(self.description_1_label)

        self.verticalLayout.addLayout(self.verticalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        self.formLayout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        self.formLayout.setLabelAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.formLayout.setFormAlignment(Qt.AlignBottom|Qt.AlignHCenter)
        self.formLayout.setContentsMargins(14, -1, -1, -1)
        self.omit_status_label = QLabel(self.general_tab)
        self.omit_status_label.setObjectName(u"omit_status_label")
        self.omit_status_label.setEnabled(True)
        self.omit_status_label.setFrameShadow(QFrame.Plain)
        self.omit_status_label.setMargin(0)

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.omit_status_label)

        self.omit_status_combo_box = QComboBox(self.general_tab)
        self.omit_status_combo_box.setObjectName(u"omit_status_combo_box")
        sizePolicy1 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.omit_status_combo_box.sizePolicy().hasHeightForWidth())
        self.omit_status_combo_box.setSizePolicy(sizePolicy1)
        self.omit_status_combo_box.setLayoutDirection(Qt.LeftToRight)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.omit_status_combo_box)

        self.reinstate_shot_if_status_is_label = QLabel(self.general_tab)
        self.reinstate_shot_if_status_is_label.setObjectName(u"reinstate_shot_if_status_is_label")
        self.reinstate_shot_if_status_is_label.setEnabled(True)
        self.reinstate_shot_if_status_is_label.setMargin(0)
        self.reinstate_shot_if_status_is_label.setIndent(0)

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.reinstate_shot_if_status_is_label)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setSpacing(10)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.reinstate_shot_if_status_is_line_edit = QLineEdit(self.general_tab)
        self.reinstate_shot_if_status_is_line_edit.setObjectName(u"reinstate_shot_if_status_is_line_edit")

        self.horizontalLayout_4.addWidget(self.reinstate_shot_if_status_is_line_edit)

        self.reinstate_status_label = QLabel(self.general_tab)
        self.reinstate_status_label.setObjectName(u"reinstate_status_label")
        self.reinstate_status_label.setEnabled(True)

        self.horizontalLayout_4.addWidget(self.reinstate_status_label)

        self.reinstate_status_combo_box = QComboBox(self.general_tab)
        self.reinstate_status_combo_box.setObjectName(u"reinstate_status_combo_box")
        sizePolicy.setHeightForWidth(self.reinstate_status_combo_box.sizePolicy().hasHeightForWidth())
        self.reinstate_status_combo_box.setSizePolicy(sizePolicy)
        self.reinstate_status_combo_box.setMinimumSize(QSize(115, 0))
        self.reinstate_status_combo_box.setLayoutDirection(Qt.LeftToRight)

        self.horizontalLayout_4.addWidget(self.reinstate_status_combo_box)

        self.formLayout.setLayout(3, QFormLayout.FieldRole, self.horizontalLayout_4)

        self.update_shot_statuses_checkbox = QCheckBox(self.general_tab)
        self.update_shot_statuses_checkbox.setObjectName(u"update_shot_statuses_checkbox")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.update_shot_statuses_checkbox.sizePolicy().hasHeightForWidth())
        self.update_shot_statuses_checkbox.setSizePolicy(sizePolicy2)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.update_shot_statuses_checkbox)

        self.update_shot_statuses_label = QLabel(self.general_tab)
        self.update_shot_statuses_label.setObjectName(u"update_shot_statuses_label")
        self.update_shot_statuses_label.setMargin(0)
        self.update_shot_statuses_label.setIndent(0)

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.update_shot_statuses_label)

        self.horizontalLayout_2.addLayout(self.formLayout)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.cut_fields_on_shot_label = QLabel(self.general_tab)
        self.cut_fields_on_shot_label.setObjectName(u"cut_fields_on_shot_label")

        self.verticalLayout.addWidget(self.cut_fields_on_shot_label)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(-1, 2, -1, -1)
        self.use_smart_fields_label = QLabel(self.general_tab)
        self.use_smart_fields_label.setObjectName(u"use_smart_fields_label")
        self.use_smart_fields_label.setIndent(14)

        self.horizontalLayout_5.addWidget(self.use_smart_fields_label)

        self.use_smart_fields_checkbox = QCheckBox(self.general_tab)
        self.use_smart_fields_checkbox.setObjectName(u"use_smart_fields_checkbox")
        self.use_smart_fields_checkbox.setLayoutDirection(Qt.LeftToRight)

        self.horizontalLayout_5.addWidget(self.use_smart_fields_checkbox)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_2)

        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.general_timecode_frames_tab.addTab(self.general_tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_4 = QVBoxLayout(self.tab_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(12, -1, 12, 0)
        self.timecode_label = QLabel(self.tab_2)
        self.timecode_label.setObjectName(u"timecode_label")

        self.verticalLayout_4.addWidget(self.timecode_label)

        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setLabelAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.default_frame_rate_label = QLabel(self.tab_2)
        self.default_frame_rate_label.setObjectName(u"default_frame_rate_label")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.default_frame_rate_label)

        self.default_frame_rate_line_edit = QLineEdit(self.tab_2)
        self.default_frame_rate_line_edit.setObjectName(u"default_frame_rate_line_edit")
        sizePolicy1.setHeightForWidth(self.default_frame_rate_line_edit.sizePolicy().hasHeightForWidth())
        self.default_frame_rate_line_edit.setSizePolicy(sizePolicy1)
        self.default_frame_rate_line_edit.setMaximumSize(QSize(50, 16777215))

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.default_frame_rate_line_edit)

        self.timecode_to_frame_mapping_label = QLabel(self.tab_2)
        self.timecode_to_frame_mapping_label.setObjectName(u"timecode_to_frame_mapping_label")
        self.timecode_to_frame_mapping_label.setIndent(20)

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.timecode_to_frame_mapping_label)

        self.timecode_to_frame_mapping_combo_box = QComboBox(self.tab_2)
        self.timecode_to_frame_mapping_combo_box.setObjectName(u"timecode_to_frame_mapping_combo_box")

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.timecode_to_frame_mapping_combo_box)

        self.verticalLayout_4.addLayout(self.formLayout_2)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(-1, 1, -1, 0)
        self.timecode_to_frame_mapping_instructions_label = QLabel(self.tab_2)
        self.timecode_to_frame_mapping_instructions_label.setObjectName(u"timecode_to_frame_mapping_instructions_label")
        self.timecode_to_frame_mapping_instructions_label.setWordWrap(True)
        self.timecode_to_frame_mapping_instructions_label.setIndent(14)

        self.verticalLayout_5.addWidget(self.timecode_to_frame_mapping_instructions_label)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setSpacing(5)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(-1, 5, -1, -1)
        self.timecode_mapping_label = QLabel(self.tab_2)
        self.timecode_mapping_label.setObjectName(u"timecode_mapping_label")
        self.timecode_mapping_label.setMargin(0)
        self.timecode_mapping_label.setIndent(20)

        self.horizontalLayout_8.addWidget(self.timecode_mapping_label)

        self.timecode_mapping_line_edit = QLineEdit(self.tab_2)
        self.timecode_mapping_line_edit.setObjectName(u"timecode_mapping_line_edit")
        sizePolicy1.setHeightForWidth(self.timecode_mapping_line_edit.sizePolicy().hasHeightForWidth())
        self.timecode_mapping_line_edit.setSizePolicy(sizePolicy1)
        self.timecode_mapping_line_edit.setMaximumSize(QSize(80, 16777215))

        self.horizontalLayout_8.addWidget(self.timecode_mapping_line_edit)

        self.frame_mapping_label = QLabel(self.tab_2)
        self.frame_mapping_label.setObjectName(u"frame_mapping_label")
        self.frame_mapping_label.setIndent(3)

        self.horizontalLayout_8.addWidget(self.frame_mapping_label)

        self.frame_mapping_line_edit = QLineEdit(self.tab_2)
        self.frame_mapping_line_edit.setObjectName(u"frame_mapping_line_edit")
        sizePolicy1.setHeightForWidth(self.frame_mapping_line_edit.sizePolicy().hasHeightForWidth())
        self.frame_mapping_line_edit.setSizePolicy(sizePolicy1)
        self.frame_mapping_line_edit.setMaximumSize(QSize(80, 16777215))

        self.horizontalLayout_8.addWidget(self.frame_mapping_line_edit)

        self.mapping_spacer = QSpacerItem(40, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_8.addItem(self.mapping_spacer)

        self.verticalLayout_5.addLayout(self.horizontalLayout_8)

        self.verticalLayout_4.addLayout(self.verticalLayout_5)

        self.verticalLayout_10 = QVBoxLayout()
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(-1, 2, -1, -1)
        self.new_shots_label = QLabel(self.tab_2)
        self.new_shots_label.setObjectName(u"new_shots_label")

        self.verticalLayout_10.addWidget(self.new_shots_label)

        self.verticalLayout_4.addLayout(self.verticalLayout_10)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(-1, 2, -1, 2)
        self.description_2_label = QLabel(self.tab_2)
        self.description_2_label.setObjectName(u"description_2_label")
        self.description_2_label.setWordWrap(True)
        self.description_2_label.setIndent(14)

        self.verticalLayout_6.addWidget(self.description_2_label)

        self.verticalLayout_4.addLayout(self.verticalLayout_6)

        self.formLayout_3 = QFormLayout()
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.formLayout_3.setLabelAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.default_head_in_label = QLabel(self.tab_2)
        self.default_head_in_label.setObjectName(u"default_head_in_label")

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.default_head_in_label)

        self.default_head_in_line_edit = QLineEdit(self.tab_2)
        self.default_head_in_line_edit.setObjectName(u"default_head_in_line_edit")
        sizePolicy1.setHeightForWidth(self.default_head_in_line_edit.sizePolicy().hasHeightForWidth())
        self.default_head_in_line_edit.setSizePolicy(sizePolicy1)
        self.default_head_in_line_edit.setMaximumSize(QSize(50, 16777215))

        self.formLayout_3.setWidget(0, QFormLayout.FieldRole, self.default_head_in_line_edit)

        self.default_head_duration_label = QLabel(self.tab_2)
        self.default_head_duration_label.setObjectName(u"default_head_duration_label")
        self.default_head_duration_label.setIndent(20)

        self.formLayout_3.setWidget(1, QFormLayout.LabelRole, self.default_head_duration_label)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.default_head_duration_line_edit = QLineEdit(self.tab_2)
        self.default_head_duration_line_edit.setObjectName(u"default_head_duration_line_edit")
        self.default_head_duration_line_edit.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout_6.addWidget(self.default_head_duration_line_edit)

        self.default_tail_duration_label = QLabel(self.tab_2)
        self.default_tail_duration_label.setObjectName(u"default_tail_duration_label")

        self.horizontalLayout_6.addWidget(self.default_tail_duration_label)

        self.default_tail_duration_line_edit = QLineEdit(self.tab_2)
        self.default_tail_duration_line_edit.setObjectName(u"default_tail_duration_line_edit")
        self.default_tail_duration_line_edit.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout_6.addWidget(self.default_tail_duration_line_edit)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_3)

        self.formLayout_3.setLayout(1, QFormLayout.FieldRole, self.horizontalLayout_6)

        self.verticalLayout_4.addLayout(self.formLayout_3)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_2)

        self.general_timecode_frames_tab.addTab(self.tab_2, "")

        self.verticalLayout_2.addWidget(self.general_timecode_frames_tab)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setSpacing(15)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_4)

        self.cancel_button = QPushButton(settings_dialog)
        self.cancel_button.setObjectName(u"cancel_button")

        self.horizontalLayout_9.addWidget(self.cancel_button)

        self.apply_button = QPushButton(settings_dialog)
        self.apply_button.setObjectName(u"apply_button")

        self.horizontalLayout_9.addWidget(self.apply_button)

        self.verticalLayout_2.addLayout(self.horizontalLayout_9)

        self.retranslateUi(settings_dialog)

        self.general_timecode_frames_tab.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(settings_dialog)
    # setupUi

    def retranslateUi(self, settings_dialog):
        settings_dialog.setWindowTitle(QCoreApplication.translate("settings_dialog", u"Dialog", None))
        self.settings_label.setText(QCoreApplication.translate("settings_dialog", u"Settings", None))
        self.note_addressing_label.setText(QCoreApplication.translate("settings_dialog", u"Note Addressing", None))
        self.send_cut_summary_note_to_label.setText(QCoreApplication.translate("settings_dialog", u"Send Cut Summary Note To:", None))
        self.email_groups_line_edit.setPlaceholderText(QCoreApplication.translate("settings_dialog", u"Group", None))
        self.statuses_label.setText(QCoreApplication.translate("settings_dialog", u"Statuses", None))
        self.description_1_label.setText(QCoreApplication.translate("settings_dialog", u"When a new Cut omits a Shot or reinstates a previously-omitted Shot, the app can automatically update the status in Flow Production Tracking.", None))
        self.omit_status_label.setText(QCoreApplication.translate("settings_dialog", u"Omit Status:", None))
#if QT_CONFIG(whatsthis)
        self.omit_status_combo_box.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
#if QT_CONFIG(accessibility)
        self.omit_status_combo_box.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.reinstate_shot_if_status_is_label.setText(QCoreApplication.translate("settings_dialog", u"Reinstate Shot if Status is:", None))
        self.reinstate_status_label.setText(QCoreApplication.translate("settings_dialog", u"Reinstate Status:", None))
#if QT_CONFIG(whatsthis)
        self.reinstate_status_combo_box.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
#if QT_CONFIG(accessibility)
        self.reinstate_status_combo_box.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.update_shot_statuses_label.setText(QCoreApplication.translate("settings_dialog", u"Update Shot Statuses", None))
        self.cut_fields_on_shot_label.setText(QCoreApplication.translate("settings_dialog", u"Cut Fields on Shot", None))
        self.use_smart_fields_label.setText(QCoreApplication.translate("settings_dialog", u"Use \"Smart\" Fields", None))
        self.use_smart_fields_checkbox.setText("")
        self.general_timecode_frames_tab.setTabText(self.general_timecode_frames_tab.indexOf(self.general_tab), QCoreApplication.translate("settings_dialog", u"       General", None))
        self.timecode_label.setText(QCoreApplication.translate("settings_dialog", u"Timecode", None))
        self.default_frame_rate_label.setText(QCoreApplication.translate("settings_dialog", u"Default Frame Rate", None))
        self.timecode_to_frame_mapping_label.setText(QCoreApplication.translate("settings_dialog", u"Timecode to Frame Mapping", None))
        self.timecode_to_frame_mapping_instructions_label.setText("")
        self.timecode_mapping_label.setText(QCoreApplication.translate("settings_dialog", u"Timecode Mapping:", None))
        self.timecode_mapping_line_edit.setText("")
        self.timecode_mapping_line_edit.setPlaceholderText(QCoreApplication.translate("settings_dialog", u"##:##:##:##", None))
        self.frame_mapping_label.setText(QCoreApplication.translate("settings_dialog", u"Frame Mapping:", None))
        self.new_shots_label.setText(QCoreApplication.translate("settings_dialog", u"New Shots", None))
        self.description_2_label.setText(QCoreApplication.translate("settings_dialog", u"When creating new Shots in Flow Production Tracking, the app will use the following numbers for start frame and handles.", None))
        self.default_head_in_label.setText(QCoreApplication.translate("settings_dialog", u"Default Head In:", None))
        self.default_head_duration_label.setText(QCoreApplication.translate("settings_dialog", u"Default Head Duration:", None))
        self.default_tail_duration_label.setText(QCoreApplication.translate("settings_dialog", u"Default Tail Duration:", None))
        self.general_timecode_frames_tab.setTabText(self.general_timecode_frames_tab.indexOf(self.tab_2), QCoreApplication.translate("settings_dialog", u"Timecode/Frames", None))
        self.cancel_button.setText(QCoreApplication.translate("settings_dialog", u"Cancel", None))
#if QT_CONFIG(shortcut)
        self.cancel_button.setShortcut(QCoreApplication.translate("settings_dialog", u"Esc", None))
#endif // QT_CONFIG(shortcut)
        self.apply_button.setText(QCoreApplication.translate("settings_dialog", u"Apply", None))
#if QT_CONFIG(shortcut)
        self.apply_button.setShortcut(QCoreApplication.translate("settings_dialog", u"Return", None))
#endif // QT_CONFIG(shortcut)
    # retranslateUi
