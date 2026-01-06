# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog.ui'
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


from ..dialog import AnimatedStackedWidget
from ..dialog import SearchWidget
from ..dialog import DropAreaFrame
from ..dialog import SelectorButton

from  . import resources_rc

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(990, 598)
        self.main_layout = QVBoxLayout(Dialog)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setObjectName(u"main_layout")
        self.stackedWidget = AnimatedStackedWidget(Dialog)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.drop_page = QWidget()
        self.drop_page.setObjectName(u"drop_page")
        self.verticalLayout_2 = QVBoxLayout(self.drop_page)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(12, 12, 12, 0)
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalSpacer_9 = QSpacerItem(100, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_9)

        self.horizontalSpacer_18 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_18)

        self.help_button = QPushButton(self.drop_page)
        self.help_button.setObjectName(u"help_button")
        self.help_button.setMaximumSize(QSize(22, 22))
        self.help_button.setLayoutDirection(Qt.RightToLeft)
        icon = QIcon()
        icon.addFile(u":/tk_multi_importcut/Help.png", QSize(), QIcon.Normal, QIcon.Off)
        self.help_button.setIcon(icon)
        self.help_button.setIconSize(QSize(22, 22))
        self.help_button.setFlat(True)

        self.horizontalLayout_9.addWidget(self.help_button)

        self.drop_page_settings_button = QPushButton(self.drop_page)
        self.drop_page_settings_button.setObjectName(u"drop_page_settings_button")
        self.drop_page_settings_button.setMaximumSize(QSize(22, 22))
        icon1 = QIcon()
        icon1.addFile(u":/tk_multi_importcut/settings_dialog_gear_icon.png", QSize(), QIcon.Normal, QIcon.Off)
        self.drop_page_settings_button.setIcon(icon1)
        self.drop_page_settings_button.setIconSize(QSize(22, 22))
        self.drop_page_settings_button.setFlat(True)

        self.horizontalLayout_9.addWidget(self.drop_page_settings_button)

        self.verticalLayout_2.addLayout(self.horizontalLayout_9)

        self.drop_area_frame = DropAreaFrame(self.drop_page)
        self.drop_area_frame.setObjectName(u"drop_area_frame")
        self.drop_area_frame.setFrameShape(QFrame.StyledPanel)
        self.drop_area_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_12 = QVBoxLayout(self.drop_area_frame)
        self.verticalLayout_12.setSpacing(0)
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setSpacing(0)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(27, 30, -1, -1)
        self.edl_added_icon = QLabel(self.drop_area_frame)
        self.edl_added_icon.setObjectName(u"edl_added_icon")
        self.edl_added_icon.setEnabled(False)
        self.edl_added_icon.setMinimumSize(QSize(0, 30))
        self.edl_added_icon.setMaximumSize(QSize(30, 30))
        self.edl_added_icon.setPixmap(QPixmap(u":/tk_multi_importcut/edl_added_icon_30px.png"))
        self.edl_added_icon.setScaledContents(True)

        self.horizontalLayout_12.addWidget(self.edl_added_icon)

        self.mov_added_icon = QLabel(self.drop_area_frame)
        self.mov_added_icon.setObjectName(u"mov_added_icon")
        self.mov_added_icon.setEnabled(False)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mov_added_icon.sizePolicy().hasHeightForWidth())
        self.mov_added_icon.setSizePolicy(sizePolicy)
        self.mov_added_icon.setMinimumSize(QSize(0, 30))
        self.mov_added_icon.setMaximumSize(QSize(30, 30))
        self.mov_added_icon.setPixmap(QPixmap(u":/tk_multi_importcut/mov_added_icon_30px.png"))
        self.mov_added_icon.setScaledContents(True)

        self.horizontalLayout_12.addWidget(self.mov_added_icon)

        self.file_added_label = QLabel(self.drop_area_frame)
        self.file_added_label.setObjectName(u"file_added_label")
        self.file_added_label.setMinimumSize(QSize(0, 30))
        self.file_added_label.setIndent(10)

        self.horizontalLayout_12.addWidget(self.file_added_label)

        self.verticalLayout_12.addLayout(self.horizontalLayout_12)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(-1, 40, -1, -1)
        self.drop_area_icon_label = QLabel(self.drop_area_frame)
        self.drop_area_icon_label.setObjectName(u"drop_area_icon_label")
        sizePolicy.setHeightForWidth(self.drop_area_icon_label.sizePolicy().hasHeightForWidth())
        self.drop_area_icon_label.setSizePolicy(sizePolicy)
        self.drop_area_icon_label.setMaximumSize(QSize(184, 80))
        self.drop_area_icon_label.setPixmap(QPixmap(u":/tk_multi_importcut/edl_mov_icon.png"))
        self.drop_area_icon_label.setScaledContents(True)
        self.drop_area_icon_label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_13.addWidget(self.drop_area_icon_label)

        self.verticalLayout_12.addLayout(self.horizontalLayout_13)

        self.verticalSpacer_7 = QSpacerItem(20, 25, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout_12.addItem(self.verticalSpacer_7)

        self.verticalLayout_11 = QVBoxLayout()
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.drop_area_label = QLabel(self.drop_area_frame)
        self.drop_area_label.setObjectName(u"drop_area_label")
        self.drop_area_label.setLineWidth(1)
        self.drop_area_label.setMidLineWidth(0)
        self.drop_area_label.setAlignment(Qt.AlignHCenter|Qt.AlignTop)
        self.drop_area_label.setIndent(0)

        self.verticalLayout_11.addWidget(self.drop_area_label)

        self.verticalLayout_12.addLayout(self.verticalLayout_11)

        self.verticalLayout_14 = QVBoxLayout()
        self.verticalLayout_14.setSpacing(0)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.label_2 = QLabel(self.drop_area_frame)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignHCenter|Qt.AlignTop)
        self.label_2.setWordWrap(False)
        self.label_2.setIndent(0)

        self.verticalLayout_14.addWidget(self.label_2)

        self.verticalLayout_12.addLayout(self.verticalLayout_14)

        self.instructions_label = QLabel(self.drop_area_frame)
        self.instructions_label.setObjectName(u"instructions_label")
        self.instructions_label.setAlignment(Qt.AlignCenter)
        self.instructions_label.setMargin(15)
        self.instructions_label.setIndent(0)

        self.verticalLayout_12.addWidget(self.instructions_label)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_12.addItem(self.verticalSpacer_6)

        self.verticalLayout_2.addWidget(self.drop_area_frame)

        self.stackedWidget.addWidget(self.drop_page)
        self.project_list_page = QWidget()
        self.project_list_page.setObjectName(u"project_list_page")
        self.verticalLayout_10 = QVBoxLayout(self.project_list_page)
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setSpacing(12)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(12, 4, -1, 4)
        self.importing_edl_label_2 = QLabel(self.project_list_page)
        self.importing_edl_label_2.setObjectName(u"importing_edl_label_2")
        self.importing_edl_label_2.setMinimumSize(QSize(200, 0))
        self.importing_edl_label_2.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_10.addWidget(self.importing_edl_label_2)

        self.select_project_label = QLabel(self.project_list_page)
        self.select_project_label.setObjectName(u"select_project_label")
        self.select_project_label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_10.addWidget(self.select_project_label)

        self.projects_search_line_edit = SearchWidget(self.project_list_page)
        self.projects_search_line_edit.setObjectName(u"projects_search_line_edit")
        sizePolicy.setHeightForWidth(self.projects_search_line_edit.sizePolicy().hasHeightForWidth())
        self.projects_search_line_edit.setSizePolicy(sizePolicy)
        self.projects_search_line_edit.setMinimumSize(QSize(200, 30))
        self.projects_search_line_edit.setLayoutDirection(Qt.RightToLeft)
        self.projects_search_line_edit.setCursorPosition(0)
        self.projects_search_line_edit.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_10.addWidget(self.projects_search_line_edit)

        self.project_page_settings_button = QPushButton(self.project_list_page)
        self.project_page_settings_button.setObjectName(u"project_page_settings_button")
        self.project_page_settings_button.setMaximumSize(QSize(22, 20))
        self.project_page_settings_button.setIcon(icon1)
        self.project_page_settings_button.setIconSize(QSize(22, 20))
        self.project_page_settings_button.setFlat(True)

        self.horizontalLayout_10.addWidget(self.project_page_settings_button)

        self.horizontalLayout_10.setStretch(1, 1)

        self.verticalLayout_10.addLayout(self.horizontalLayout_10)

        self.project_scroll_area = QScrollArea(self.project_list_page)
        self.project_scroll_area.setObjectName(u"project_scroll_area")
        self.project_scroll_area.setWidgetResizable(True)
        self.project_area = QWidget()
        self.project_area.setObjectName(u"project_area")
        self.project_area.setGeometry(QRect(0, 0, 964, 462))
        self.project_grid = QGridLayout(self.project_area)
        self.project_grid.setSpacing(2)
        self.project_grid.setContentsMargins(2, 2, 2, 2)
        self.project_grid.setObjectName(u"project_grid")
        self.verticalSpacer_11 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.project_grid.addItem(self.verticalSpacer_11, 0, 0, 1, 2)

        self.project_scroll_area.setWidget(self.project_area)

        self.verticalLayout_10.addWidget(self.project_scroll_area)

        self.stackedWidget.addWidget(self.project_list_page)
        self.entity_types_page = QWidget()
        self.entity_types_page.setObjectName(u"entity_types_page")
        self.verticalLayout_8 = QVBoxLayout(self.entity_types_page)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(12, -1, 0, -1)
        self.entity_picker_title_label = QLabel(self.entity_types_page)
        self.entity_picker_title_label.setObjectName(u"entity_picker_title_label")
        self.entity_picker_title_label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_2.addWidget(self.entity_picker_title_label)

        self.horizontalLayout_2.setStretch(0, 1)

        self.verticalLayout_8.addLayout(self.horizontalLayout_2)

        self.stackedWidget.addWidget(self.entity_types_page)
        self.entities_list_page = QWidget()
        self.entities_list_page.setObjectName(u"entities_list_page")
        sizePolicy.setHeightForWidth(self.entities_list_page.sizePolicy().hasHeightForWidth())
        self.entities_list_page.setSizePolicy(sizePolicy)
        self.entities_list_page.setMinimumSize(QSize(0, 0))
        self.verticalLayout_3 = QVBoxLayout(self.entities_list_page)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(12, 0, 12, 0)
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setSpacing(12)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.horizontalLayout_7.setContentsMargins(0, 4, 0, 4)
        self.entity_buttons_layout = QHBoxLayout()
        self.entity_buttons_layout.setSpacing(5)
        self.entity_buttons_layout.setObjectName(u"entity_buttons_layout")

        self.horizontalLayout_7.addLayout(self.entity_buttons_layout)

        self.entities_title_label = QLabel(self.entities_list_page)
        self.entities_title_label.setObjectName(u"entities_title_label")
        self.entities_title_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_7.addWidget(self.entities_title_label)

        self.horizontalSpacer_10 = QSpacerItem(155, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_10)

        self.entities_search_line_edit = SearchWidget(self.entities_list_page)
        self.entities_search_line_edit.setObjectName(u"entities_search_line_edit")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.entities_search_line_edit.sizePolicy().hasHeightForWidth())
        self.entities_search_line_edit.setSizePolicy(sizePolicy1)
        self.entities_search_line_edit.setMinimumSize(QSize(200, 30))
        self.entities_search_line_edit.setBaseSize(QSize(0, 0))
        self.entities_search_line_edit.setLayoutDirection(Qt.RightToLeft)
        self.entities_search_line_edit.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_7.addWidget(self.entities_search_line_edit)

        self.entities_page_settings_button = QPushButton(self.entities_list_page)
        self.entities_page_settings_button.setObjectName(u"entities_page_settings_button")
        self.entities_page_settings_button.setMaximumSize(QSize(22, 20))
        self.entities_page_settings_button.setIcon(icon1)
        self.entities_page_settings_button.setIconSize(QSize(22, 20))
        self.entities_page_settings_button.setFlat(True)

        self.horizontalLayout_7.addWidget(self.entities_page_settings_button)

        self.horizontalLayout_7.setStretch(1, 1)

        self.verticalLayout_3.addLayout(self.horizontalLayout_7)

        self.entity_scroll_area = QScrollArea(self.entities_list_page)
        self.entity_scroll_area.setObjectName(u"entity_scroll_area")
        self.entity_scroll_area.setWidgetResizable(True)
        self.entity_area = QWidget()
        self.entity_area.setObjectName(u"entity_area")
        self.entity_area.setGeometry(QRect(0, 0, 98, 28))
        self.entity_area.setStyleSheet(u"")
        self.horizontalLayout_5 = QHBoxLayout(self.entity_area)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.entities_type_stacked_widget = QStackedWidget(self.entity_area)
        self.entities_type_stacked_widget.setObjectName(u"entities_type_stacked_widget")
        self.page_1 = QWidget()
        self.page_1.setObjectName(u"page_1")
        self.gridLayout = QGridLayout(self.page_1)
        self.gridLayout.setSpacing(2)
        self.gridLayout.setContentsMargins(2, 2, 2, 2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalSpacer = QSpacerItem(20, 398, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 0, 0, 1, 1)

        self.entities_type_stacked_widget.addWidget(self.page_1)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.gridLayout_3 = QGridLayout(self.page_2)
        self.gridLayout_3.setSpacing(2)
        self.gridLayout_3.setContentsMargins(2, 2, 2, 2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.verticalSpacer_12 = QSpacerItem(20, 398, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_12, 0, 0, 1, 1)

        self.entities_type_stacked_widget.addWidget(self.page_2)
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.gridLayout_4 = QGridLayout(self.page_3)
        self.gridLayout_4.setSpacing(2)
        self.gridLayout_4.setContentsMargins(2, 2, 2, 2)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.verticalSpacer_13 = QSpacerItem(20, 398, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer_13, 0, 0, 1, 1)

        self.entities_type_stacked_widget.addWidget(self.page_3)
        self.page_4 = QWidget()
        self.page_4.setObjectName(u"page_4")
        self.gridLayout_5 = QGridLayout(self.page_4)
        self.gridLayout_5.setSpacing(2)
        self.gridLayout_5.setContentsMargins(2, 2, 2, 2)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.verticalSpacer_14 = QSpacerItem(20, 398, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_5.addItem(self.verticalSpacer_14, 0, 0, 1, 1)

        self.entities_type_stacked_widget.addWidget(self.page_4)
        self.page_5 = QWidget()
        self.page_5.setObjectName(u"page_5")
        self.gridLayout_6 = QGridLayout(self.page_5)
        self.gridLayout_6.setSpacing(2)
        self.gridLayout_6.setContentsMargins(2, 2, 2, 2)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.verticalSpacer_15 = QSpacerItem(20, 398, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_6.addItem(self.verticalSpacer_15, 0, 0, 1, 1)

        self.entities_type_stacked_widget.addWidget(self.page_5)

        self.horizontalLayout_5.addWidget(self.entities_type_stacked_widget)

        self.entity_scroll_area.setWidget(self.entity_area)

        self.verticalLayout_3.addWidget(self.entity_scroll_area)

        self.stackedWidget.addWidget(self.entities_list_page)
        self.cut_list_page = QWidget()
        self.cut_list_page.setObjectName(u"cut_list_page")
        self.verticalLayout_6 = QVBoxLayout(self.cut_list_page)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(12, 0, 12, 0)
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setSpacing(12)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(12, 4, 0, 4)
        self.selected_entity_label = QLabel(self.cut_list_page)
        self.selected_entity_label.setObjectName(u"selected_entity_label")
        sizePolicy1.setHeightForWidth(self.selected_entity_label.sizePolicy().hasHeightForWidth())
        self.selected_entity_label.setSizePolicy(sizePolicy1)
        self.selected_entity_label.setMinimumSize(QSize(200, 0))

        self.horizontalLayout_6.addWidget(self.selected_entity_label)

        self.horizontalSpacer_6 = QSpacerItem(90, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_6)

        self.cuts_title_label = QLabel(self.cut_list_page)
        self.cuts_title_label.setObjectName(u"cuts_title_label")
        self.cuts_title_label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_6.addWidget(self.cuts_title_label)

        self.cuts_sort_button = QPushButton(self.cut_list_page)
        self.cuts_sort_button.setObjectName(u"cuts_sort_button")
        sizePolicy1.setHeightForWidth(self.cuts_sort_button.sizePolicy().hasHeightForWidth())
        self.cuts_sort_button.setSizePolicy(sizePolicy1)
        self.cuts_sort_button.setMinimumSize(QSize(90, 0))
        self.cuts_sort_button.setBaseSize(QSize(0, 0))
        self.cuts_sort_button.setFlat(True)

        self.horizontalLayout_6.addWidget(self.cuts_sort_button)

        self.search_line_edit = SearchWidget(self.cut_list_page)
        self.search_line_edit.setObjectName(u"search_line_edit")
        sizePolicy1.setHeightForWidth(self.search_line_edit.sizePolicy().hasHeightForWidth())
        self.search_line_edit.setSizePolicy(sizePolicy1)
        self.search_line_edit.setMinimumSize(QSize(200, 30))
        self.search_line_edit.setLayoutDirection(Qt.RightToLeft)
        self.search_line_edit.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_6.addWidget(self.search_line_edit)

        self.cut_list_page_settings_button = QPushButton(self.cut_list_page)
        self.cut_list_page_settings_button.setObjectName(u"cut_list_page_settings_button")
        self.cut_list_page_settings_button.setMaximumSize(QSize(22, 20))
        self.cut_list_page_settings_button.setIcon(icon1)
        self.cut_list_page_settings_button.setIconSize(QSize(22, 22))
        self.cut_list_page_settings_button.setFlat(True)

        self.horizontalLayout_6.addWidget(self.cut_list_page_settings_button)

        self.horizontalLayout_6.setStretch(2, 1)

        self.verticalLayout_6.addLayout(self.horizontalLayout_6)

        self.scrollArea_3 = QScrollArea(self.cut_list_page)
        self.scrollArea_3.setObjectName(u"scrollArea_3")
        self.scrollArea_3.setWidgetResizable(True)
        self.cuts_area = QWidget()
        self.cuts_area.setObjectName(u"cuts_area")
        self.cuts_area.setGeometry(QRect(0, 0, 98, 28))
        self.cuts_grid = QGridLayout(self.cuts_area)
        self.cuts_grid.setSpacing(2)
        self.cuts_grid.setContentsMargins(2, 2, 2, 2)
        self.cuts_grid.setObjectName(u"cuts_grid")
        self.verticalSpacer_5 = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.cuts_grid.addItem(self.verticalSpacer_5, 1, 0, 1, 1)

        self.scrollArea_3.setWidget(self.cuts_area)

        self.verticalLayout_6.addWidget(self.scrollArea_3)

        self.stackedWidget.addWidget(self.cut_list_page)
        self.cut_summary_page = QWidget()
        self.cut_summary_page.setObjectName(u"cut_summary_page")
        self.verticalLayout_4 = QVBoxLayout(self.cut_summary_page)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.cut_summary_selectors_frame = QFrame(self.cut_summary_page)
        self.cut_summary_selectors_frame.setObjectName(u"cut_summary_selectors_frame")
        self.cut_summary_selectors_frame.setFrameShape(QFrame.StyledPanel)
        self.cut_summary_selectors_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.cut_summary_selectors_frame)
        self.horizontalLayout_8.setSpacing(12)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.total_button = SelectorButton(self.cut_summary_selectors_frame)
        self.total_button.setObjectName(u"total_button")
        sizePolicy1.setHeightForWidth(self.total_button.sizePolicy().hasHeightForWidth())
        self.total_button.setSizePolicy(sizePolicy1)
        self.total_button.setMinimumSize(QSize(70, 20))
        self.total_button.setBaseSize(QSize(0, 70))
        self.total_button.setCheckable(True)
        self.total_button.setChecked(True)
        self.total_button.setAutoExclusive(True)
        self.total_button.setFlat(True)

        self.horizontalLayout_8.addWidget(self.total_button)

        self.new_select_button = SelectorButton(self.cut_summary_selectors_frame)
        self.new_select_button.setObjectName(u"new_select_button")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.new_select_button.sizePolicy().hasHeightForWidth())
        self.new_select_button.setSizePolicy(sizePolicy2)
        self.new_select_button.setBaseSize(QSize(0, 70))
        self.new_select_button.setCheckable(True)
        self.new_select_button.setChecked(False)
        self.new_select_button.setAutoExclusive(True)
        self.new_select_button.setFlat(True)

        self.horizontalLayout_8.addWidget(self.new_select_button)

        self.omitted_select_button = SelectorButton(self.cut_summary_selectors_frame)
        self.omitted_select_button.setObjectName(u"omitted_select_button")
        sizePolicy2.setHeightForWidth(self.omitted_select_button.sizePolicy().hasHeightForWidth())
        self.omitted_select_button.setSizePolicy(sizePolicy2)
        self.omitted_select_button.setBaseSize(QSize(0, 70))
        self.omitted_select_button.setCheckable(True)
        self.omitted_select_button.setAutoExclusive(True)
        self.omitted_select_button.setFlat(True)

        self.horizontalLayout_8.addWidget(self.omitted_select_button)

        self.reinstated_select_button = SelectorButton(self.cut_summary_selectors_frame)
        self.reinstated_select_button.setObjectName(u"reinstated_select_button")
        sizePolicy2.setHeightForWidth(self.reinstated_select_button.sizePolicy().hasHeightForWidth())
        self.reinstated_select_button.setSizePolicy(sizePolicy2)
        self.reinstated_select_button.setBaseSize(QSize(0, 70))
        self.reinstated_select_button.setCheckable(True)
        self.reinstated_select_button.setAutoExclusive(True)
        self.reinstated_select_button.setFlat(True)

        self.horizontalLayout_8.addWidget(self.reinstated_select_button)

        self.cut_change_select_button = SelectorButton(self.cut_summary_selectors_frame)
        self.cut_change_select_button.setObjectName(u"cut_change_select_button")
        sizePolicy2.setHeightForWidth(self.cut_change_select_button.sizePolicy().hasHeightForWidth())
        self.cut_change_select_button.setSizePolicy(sizePolicy2)
        self.cut_change_select_button.setBaseSize(QSize(0, 70))
        self.cut_change_select_button.setCheckable(True)
        self.cut_change_select_button.setAutoExclusive(True)
        self.cut_change_select_button.setFlat(True)

        self.horizontalLayout_8.addWidget(self.cut_change_select_button)

        self.rescan_select_button = SelectorButton(self.cut_summary_selectors_frame)
        self.rescan_select_button.setObjectName(u"rescan_select_button")
        sizePolicy2.setHeightForWidth(self.rescan_select_button.sizePolicy().hasHeightForWidth())
        self.rescan_select_button.setSizePolicy(sizePolicy2)
        self.rescan_select_button.setBaseSize(QSize(0, 70))
        self.rescan_select_button.setCheckable(True)
        self.rescan_select_button.setAutoExclusive(True)
        self.rescan_select_button.setFlat(True)

        self.horizontalLayout_8.addWidget(self.rescan_select_button)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_2)

        self.only_vfx_check_box = QCheckBox(self.cut_summary_selectors_frame)
        self.only_vfx_check_box.setObjectName(u"only_vfx_check_box")
        sizePolicy3 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.only_vfx_check_box.sizePolicy().hasHeightForWidth())
        self.only_vfx_check_box.setSizePolicy(sizePolicy3)

        self.horizontalLayout_8.addWidget(self.only_vfx_check_box)

        self.horizontalSpacer_11 = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_11)

        self.cut_summary_page_settings_button = QPushButton(self.cut_summary_selectors_frame)
        self.cut_summary_page_settings_button.setObjectName(u"cut_summary_page_settings_button")
        self.cut_summary_page_settings_button.setMaximumSize(QSize(22, 20))
        self.cut_summary_page_settings_button.setIcon(icon1)
        self.cut_summary_page_settings_button.setIconSize(QSize(22, 20))
        self.cut_summary_page_settings_button.setFlat(True)

        self.horizontalLayout_8.addWidget(self.cut_summary_page_settings_button)

        self.horizontalLayout_8.setStretch(6, 1)

        self.verticalLayout_4.addWidget(self.cut_summary_selectors_frame)

        self.line_2 = QFrame(self.cut_summary_page)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_4.addWidget(self.line_2)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(12, -1, 12, -1)
        self.cut_summary_title_label = QLabel(self.cut_summary_page)
        self.cut_summary_title_label.setObjectName(u"cut_summary_title_label")
        self.cut_summary_title_label.setMinimumSize(QSize(0, 30))
        self.cut_summary_title_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_7.addWidget(self.cut_summary_title_label)

        self.scrollArea_2 = QScrollArea(self.cut_summary_page)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setWidgetResizable(True)
        self.cut_summary_widgets = QWidget()
        self.cut_summary_widgets.setObjectName(u"cut_summary_widgets")
        self.cut_summary_widgets.setGeometry(QRect(0, 0, 964, 400))
        self.cutsummary_list = QVBoxLayout(self.cut_summary_widgets)
        self.cutsummary_list.setSpacing(2)
        self.cutsummary_list.setContentsMargins(2, 2, 2, 2)
        self.cutsummary_list.setObjectName(u"cutsummary_list")
        self.verticalSpacer_2 = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Preferred)

        self.cutsummary_list.addItem(self.verticalSpacer_2)

        self.scrollArea_2.setWidget(self.cut_summary_widgets)

        self.verticalLayout_7.addWidget(self.scrollArea_2)

        self.verticalLayout_4.addLayout(self.verticalLayout_7)

        self.stackedWidget.addWidget(self.cut_summary_page)
        self.progress_page = QWidget()
        self.progress_page.setObjectName(u"progress_page")
        self.gridLayout_2 = QGridLayout(self.progress_page)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_7, 2, 0, 1, 1)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_8, 2, 2, 1, 1)

        self.progress_bar = QProgressBar(self.progress_page)
        self.progress_bar.setObjectName(u"progress_bar")
        sizePolicy.setHeightForWidth(self.progress_bar.sizePolicy().hasHeightForWidth())
        self.progress_bar.setSizePolicy(sizePolicy)
        self.progress_bar.setMaximumSize(QSize(16777215, 16777215))
        self.progress_bar.setValue(24)
        self.progress_bar.setTextVisible(False)

        self.gridLayout_2.addWidget(self.progress_bar, 2, 1, 1, 1)

        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_8, 4, 1, 1, 1)

        self.verticalSpacer_9 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_9, 0, 1, 1, 1)

        self.progress_bar_label = QLabel(self.progress_page)
        self.progress_bar_label.setObjectName(u"progress_bar_label")
        self.progress_bar_label.setWordWrap(True)

        self.gridLayout_2.addWidget(self.progress_bar_label, 3, 1, 1, 1)

        self.progress_screen_title_label = QLabel(self.progress_page)
        self.progress_screen_title_label.setObjectName(u"progress_screen_title_label")

        self.gridLayout_2.addWidget(self.progress_screen_title_label, 1, 1, 1, 1)

        self.gridLayout_2.setColumnStretch(0, 1)
        self.gridLayout_2.setColumnStretch(1, 3)
        self.gridLayout_2.setColumnStretch(2, 1)
        self.stackedWidget.addWidget(self.progress_page)
        self.success_page = QWidget()
        self.success_page.setObjectName(u"success_page")
        self.horizontalLayout_3 = QHBoxLayout(self.success_page)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_4)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(-1, -1, -1, 40)
        self.label = QLabel(self.success_page)
        self.label.setObjectName(u"label")
        sizePolicy4 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy4)
        self.label.setMaximumSize(QSize(100, 100))
        self.label.setPixmap(QPixmap(u":/tk_multi_importcut/check_mark.png"))
        self.label.setScaledContents(True)
        self.label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_4.addWidget(self.label)

        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.success_label = QLabel(self.success_page)
        self.success_label.setObjectName(u"success_label")
        self.success_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.success_label)

        self.edl_imported_label = QLabel(self.success_page)
        self.edl_imported_label.setObjectName(u"edl_imported_label")
        self.edl_imported_label.setAlignment(Qt.AlignCenter)
        self.edl_imported_label.setMargin(5)

        self.verticalLayout.addWidget(self.edl_imported_label)

        self.verticalLayout_15 = QVBoxLayout()
        self.verticalLayout_15.setSpacing(0)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(-1, 30, -1, -1)
        self.shotgun_button = QPushButton(self.success_page)
        self.shotgun_button.setObjectName(u"shotgun_button")
        self.shotgun_button.setMinimumSize(QSize(50, 30))
        self.shotgun_button.setMaximumSize(QSize(1000, 16777215))
        self.shotgun_button.setFlat(False)

        self.verticalLayout_15.addWidget(self.shotgun_button)

        self.verticalLayout.addLayout(self.verticalLayout_15)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_3)

        self.horizontalLayout_3.addLayout(self.verticalLayout)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_4)

        self.stackedWidget.addWidget(self.success_page)

        self.main_layout.addWidget(self.stackedWidget)

        self.feedback_label = QLabel(Dialog)
        self.feedback_label.setObjectName(u"feedback_label")
        self.feedback_label.setFrameShape(QFrame.NoFrame)
        self.feedback_label.setFrameShadow(QFrame.Plain)
        self.feedback_label.setWordWrap(True)
        self.feedback_label.setMargin(0)
        self.feedback_label.setIndent(10)
        self.feedback_label.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.main_layout.addWidget(self.feedback_label)

        self.line = QFrame(Dialog)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.main_layout.addWidget(self.line)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(12, 0, 12, 12)
        self.back_button = QPushButton(Dialog)
        self.back_button.setObjectName(u"back_button")
        icon2 = QIcon()
        icon2.addFile(u":/tk_multi_importcut/left_arrow.png", QSize(), QIcon.Normal, QIcon.Off)
        self.back_button.setIcon(icon2)
        self.back_button.setFlat(True)

        self.horizontalLayout.addWidget(self.back_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.create_entity_button = QPushButton(Dialog)
        self.create_entity_button.setObjectName(u"create_entity_button")
        self.create_entity_button.setIconSize(QSize(16, 16))

        self.horizontalLayout.addWidget(self.create_entity_button)

        self.cancel_button = QPushButton(Dialog)
        self.cancel_button.setObjectName(u"cancel_button")

        self.horizontalLayout.addWidget(self.cancel_button)

        self.next_button = QPushButton(Dialog)
        self.next_button.setObjectName(u"next_button")
        self.next_button.setEnabled(False)

        self.horizontalLayout.addWidget(self.next_button)

        self.reset_button = QPushButton(Dialog)
        self.reset_button.setObjectName(u"reset_button")

        self.horizontalLayout.addWidget(self.reset_button)

        self.email_button = QPushButton(Dialog)
        self.email_button.setObjectName(u"email_button")

        self.horizontalLayout.addWidget(self.email_button)

        self.submit_button = QPushButton(Dialog)
        self.submit_button.setObjectName(u"submit_button")

        self.horizontalLayout.addWidget(self.submit_button)

        self.skip_button = QPushButton(Dialog)
        self.skip_button.setObjectName(u"skip_button")

        self.horizontalLayout.addWidget(self.skip_button)

        self.select_button = QPushButton(Dialog)
        self.select_button.setObjectName(u"select_button")

        self.horizontalLayout.addWidget(self.select_button)

        self.horizontalLayout.setStretch(1, 1)

        self.main_layout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)

        self.stackedWidget.setCurrentIndex(1)
        self.entities_type_stacked_widget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.help_button.setText("")
        self.drop_page_settings_button.setText("")
        self.edl_added_icon.setText("")
        self.mov_added_icon.setText("")
        self.file_added_label.setText(QCoreApplication.translate("Dialog", u"testing", None))
        self.drop_area_icon_label.setText("")
        self.drop_area_label.setText(QCoreApplication.translate("Dialog", u"DRAG & DROP", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"EDL & MOV", None))
        self.instructions_label.setText(QCoreApplication.translate("Dialog", u"Import Cut EDL and optional MOV.", None))
        self.importing_edl_label_2.setText(QCoreApplication.translate("Dialog", u"Treating blah...", None))
        self.select_project_label.setText(QCoreApplication.translate("Dialog", u"Select Project", None))
        self.projects_search_line_edit.setText("")
        self.projects_search_line_edit.setPlaceholderText(QCoreApplication.translate("Dialog", u"Search Projects", None))
        self.project_page_settings_button.setText("")
        self.entity_picker_title_label.setText(QCoreApplication.translate("Dialog", u"This screen is never shown as this step is now combined with the Entities screen (next screen).\n"
"This screen is kept so we have a direct match between internal steps and screens", None))
        self.entities_title_label.setText(QCoreApplication.translate("Dialog", u"Select Link for Cut", None))
        self.entities_search_line_edit.setPlaceholderText(QCoreApplication.translate("Dialog", u"Search Sequences", None))
        self.entities_page_settings_button.setText("")
        self.selected_entity_label.setText("")
        self.cuts_title_label.setText(QCoreApplication.translate("Dialog", u"Compare to Previous Cut", None))
        self.cuts_sort_button.setText(QCoreApplication.translate("Dialog", u"Sort ...", None))
        self.search_line_edit.setPlaceholderText(QCoreApplication.translate("Dialog", u"Search Cut", None))
        self.cut_list_page_settings_button.setText("")
        self.total_button.setText(QCoreApplication.translate("Dialog", u"Total", None))
        self.new_select_button.setText(QCoreApplication.translate("Dialog", u"New", None))
        self.omitted_select_button.setText(QCoreApplication.translate("Dialog", u"Omitted", None))
        self.reinstated_select_button.setText(QCoreApplication.translate("Dialog", u"Reinstated", None))
        self.cut_change_select_button.setText(QCoreApplication.translate("Dialog", u"Cut Changes", None))
        self.rescan_select_button.setText(QCoreApplication.translate("Dialog", u"Rescan Needed", None))
        self.only_vfx_check_box.setText(QCoreApplication.translate("Dialog", u"Hide Non-VFX Shots", None))
        self.cut_summary_page_settings_button.setText("")
        self.cut_summary_title_label.setText("")
        self.progress_bar_label.setText("")
        self.progress_screen_title_label.setText(QCoreApplication.translate("Dialog", u"Importing ....", None))
        self.label.setText("")
        self.success_label.setText(QCoreApplication.translate("Dialog", u"CUT IMPORTED", None))
        self.edl_imported_label.setText(QCoreApplication.translate("Dialog", u"EDL_file_name", None))
        self.shotgun_button.setText(QCoreApplication.translate("Dialog", u"View in Flow Production Tracking", None))
        self.feedback_label.setText("")
        self.back_button.setText(QCoreApplication.translate("Dialog", u"Back", None))
        self.create_entity_button.setText(QCoreApplication.translate("Dialog", u"New Entity", None))
        self.cancel_button.setText(QCoreApplication.translate("Dialog", u"Close", None))
        self.next_button.setText(QCoreApplication.translate("Dialog", u"Next", None))
        self.reset_button.setText(QCoreApplication.translate("Dialog", u"Reset", None))
        self.email_button.setText(QCoreApplication.translate("Dialog", u"Email Summary", None))
        self.submit_button.setText(QCoreApplication.translate("Dialog", u"Import Cut", None))
        self.skip_button.setText(QCoreApplication.translate("Dialog", u"Skip", None))
        self.select_button.setText(QCoreApplication.translate("Dialog", u"Select", None))
    # retranslateUi
