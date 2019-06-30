# -*- coding: utf-8 -*-
'''
This file contains formation code of program: Educational software for planning regime of HPP. NRU MPEI, Moscow, Russia.
Version: v.1.2
Last update 29.06.2019
Developed on PyQt5 v5.6; Python 3.5
Autor: Alexander Sysoev (AlexShepa)
'''
from PyQt5 import QtCore, QtGui, QtWidgets


class UiMainWindow(object):
    station_info = 'Station info'  # Default text for text fields
    errors_in_calculations = 'No errors during calculation'  # Default text for text fields

    def setup_ui(self, main_window):  # Function of forming the appearance of the program
        # Window size
        main_window.setMinimumSize(QtCore.QSize(800, 620))
        main_window.setMaximumSize(QtCore.QSize(1280, 1024))
        main_window.resize(1024, 800)  # Default

        # Add widgets to window
        self.centralwidget = QtWidgets.QWidget(main_window)  # Main widget
        self.tab_widget = QtWidgets.QTabWidget(self.centralwidget)  # Add widget for different tabs
        self.tab_widget.setGeometry(QtCore.QRect(10, 10, 1010, 750))  # Default size in px

        # Adding tabs
        # All refers to tab - longterm regime. tab_2 - middleterm.
        self.tab = QtWidgets.QWidget()
        self.tab_widget.addTab(self.tab, "Longterm regime")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_widget.addTab(self.tab_2, "Middleterm regime")
        self.tab_widget.setCurrentIndex(0)

        # --LONGTERM REGIME OF CALCULATION --
        # Groupbox for input data
        self.group_box = QtWidgets.QGroupBox(self.tab)
        self.group_box.setGeometry(QtCore.QRect(660, 10, 340, 150))
        # Default font
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(8)
        font.setWeight(75)
        self.group_box.setFont(font)

        # Rate for end of calculation period(CP)
        self.insert_mark = QtWidgets.QLineEdit(self.group_box)
        self.insert_mark.setGeometry(QtCore.QRect(190, 20, 80, 25))

        # A text explanation for the mark
        self.output = QtWidgets.QLabel(self.group_box)
        self.output.setGeometry(QtCore.QRect(10, 20, 150, 25))
        self.output.setText("End mark UB, m:")

        # Rate in LB
        self.insert_rate = QtWidgets.QLineEdit(self.group_box)
        self.insert_rate.setGeometry(QtCore.QRect(190, 55, 80, 25))

        # A text explanation for the rate
        self.output = QtWidgets.QLabel(self.group_box)
        self.output.setGeometry(QtCore.QRect(10, 55, 185, 25))
        self.output.setText("Rate in lover bief, m³/s :")

        # Spinbox with explanations about current CP.
        self.calculcation_indicator = QtWidgets.QSpinBox(self.group_box)
        self.calculcation_indicator.setGeometry(QtCore.QRect(190, 90, 80, 25))

        # A text explanation for spinbox
        self.output = QtWidgets.QLabel(self.group_box)
        self.output.setGeometry(QtCore.QRect(10, 90, 150, 25))
        self.output.setText("Calculation period:")

        # Button to start calculation
        self.start_calculcation = QtWidgets.QPushButton(self.group_box)
        self.start_calculcation.setGeometry(QtCore.QRect(10, 120, 100, 25))

        # Button to revert calculation
        self.revert_calculcation = QtWidgets.QPushButton(self.group_box)
        self.revert_calculcation.setGeometry(QtCore.QRect(235, 120, 100, 25))

        # Button to get report
        self.form_report = QtWidgets.QPushButton(self.group_box)
        self.form_report.setGeometry(QtCore.QRect(125, 120, 100, 25))

        # ---MIDDLETERM REGIME---
        # Groupbox for input data
        self.group_box_tab_2 = QtWidgets.QGroupBox(self.tab_2)
        self.group_box_tab_2.setGeometry(QtCore.QRect(540, 290, 450, 120))

        # Default font
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.group_box_tab_2.setFont(font)

        # Rate for end of calculation period(CP)
        self.insert_mark_tab_2 = QtWidgets.QLineEdit(self.group_box_tab_2)
        self.insert_mark_tab_2.setGeometry(QtCore.QRect(190, 20, 80, 25))

        # A text explanation for the mark
        self.output_tab_2 = QtWidgets.QLabel(self.group_box_tab_2)
        self.output_tab_2.setGeometry(QtCore.QRect(10, 20, 150, 25))
        self.output_tab_2.setText("End mark UB, m:")

        # Rate in LB
        self.insert_rate_tab_2 = QtWidgets.QLineEdit(self.group_box_tab_2)
        self.insert_rate_tab_2.setGeometry(QtCore.QRect(190, 55, 80, 25))

        # A text explanation for the rate
        self.output_tab_2 = QtWidgets.QLabel(self.group_box_tab_2)
        self.output_tab_2.setGeometry(QtCore.QRect(10, 55, 185, 25))
        self.output_tab_2.setText("Rate in lover bief, m³/s :")

        # Button to start calculation
        self.start_calculcation_tab_2 = QtWidgets.QPushButton(self.group_box_tab_2)
        self.start_calculcation_tab_2.setGeometry(QtCore.QRect(10, 90, 100, 25))

        # MIDDLETERM - CHOOSE LINE
        # Groupbox for CP and calculation line(CL)
        self.group_box_line_tab_2 = QtWidgets.QGroupBox(self.tab_2)
        self.group_box_line_tab_2.setGeometry(QtCore.QRect(540, 10, 450, 120))

        # Default font
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.group_box_line_tab_2.setFont(font)

        # A text explanation for start period
        self.start_period_label_tab_2 = QtWidgets.QLabel(self.group_box_line_tab_2)
        self.start_period_label_tab_2.setGeometry(QtCore.QRect(10, 15, 150, 25))
        self.start_period_label_tab_2.setText("Start period")

        # Choose menu for start period
        self.start_period_tab_2 = QtWidgets.QComboBox(self.group_box_line_tab_2)
        self.start_period_tab_2.setGeometry(QtCore.QRect(10, 35, 50, 25))

        # A text explanation for end period
        self.end_period_label_tab_2 = QtWidgets.QLabel(self.group_box_line_tab_2)
        self.end_period_label_tab_2.setGeometry(QtCore.QRect(200, 15, 185, 25))
        self.end_period_label_tab_2.setText("End period")

        # Choose menu for end peiod. With one option. Done this for style
        self.end_period_tab_2 = QtWidgets.QComboBox(self.group_box_line_tab_2)
        self.end_period_tab_2.setGeometry(QtCore.QRect(200, 35, 50, 25))

        # A text explanation for chosen line
        self.choose_line_label_tab_2 = QtWidgets.QLabel(self.group_box_line_tab_2)
        self.choose_line_label_tab_2.setGeometry(QtCore.QRect(10, 70, 185, 25))
        self.choose_line_label_tab_2.setText("Calculation line:")

        # Choose menu for CL
        self.choose_line_tab_2 = QtWidgets.QComboBox(self.group_box_line_tab_2)
        self.choose_line_tab_2.setGeometry(QtCore.QRect(120, 70, 50, 25))

        # Graphic view for HPP regime and all graphic part
        self.graphics_view = QtWidgets.QGraphicsView(self.tab)
        self.graphics_view.setGeometry(QtCore.QRect(10, 170, 990, 400))

        # Graphic view for HPP regime and all graphic part - middleterm
        self.graphics_view_tab2 = QtWidgets.QGraphicsView(self.tab_2)
        self.graphics_view_tab2.setGeometry(QtCore.QRect(10, 10, 520, 400))

        # Groupbox for station and restrictions info
        self.group_box_station_info_and_restr = QtWidgets.QGroupBox(self.tab)
        self.group_box_station_info_and_restr.setGeometry(QtCore.QRect(10, 10, 640, 150))

        # Default font
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(8)
        font.setWeight(75)
        self.group_box_station_info_and_restr.setFont(font)

        # Text browser - for station info and future rate
        self.station_info_browser = QtWidgets.QTextBrowser(self.group_box_station_info_and_restr)
        self.station_info_browser.setGeometry(QtCore.QRect(10, 15, 620, 50))

        # Between browser line
        self.line = QtWidgets.QFrame(self.group_box_station_info_and_restr)
        self.line.setGeometry(QtCore.QRect(10, 65, 620, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)

        # Text browser - for restrictions info
        self.restrictions_info_browser = QtWidgets.QTextBrowser(self.group_box_station_info_and_restr)
        self.restrictions_info_browser.setGeometry(QtCore.QRect(10, 80, 620, 60))

        # --- MIDDLETERM ----

        # Groupbox for station and restrictions info
        self.group_box_station_info_and_restr_tab_2 = QtWidgets.QGroupBox(self.tab_2)
        self.group_box_station_info_and_restr_tab_2.setGeometry(QtCore.QRect(540, 135, 450, 150))

        # Default font
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.group_box_station_info_and_restr_tab_2.setFont(font)

        # Text browser - for station info and future rate
        self.station_info_browser_tab_2 = QtWidgets.QTextBrowser(self.group_box_station_info_and_restr_tab_2)
        self.station_info_browser_tab_2.setGeometry(QtCore.QRect(10, 15, 430, 35))

        # Text browser - for restrictions info
        self.restrictions_info_browser_tab_2 = QtWidgets.QTextBrowser(self.group_box_station_info_and_restr_tab_2)
        self.restrictions_info_browser_tab_2.setGeometry(QtCore.QRect(10, 65, 430, 80))

        # Between browser line
        self.line_tab_2 = QtWidgets.QFrame(self.group_box_station_info_and_restr_tab_2)
        self.line_tab_2.setGeometry(QtCore.QRect(10, 50, 430, 16))
        self.line_tab_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_tab_2.setFrameShadow(QtWidgets.QFrame.Sunken)

        # Result table

        # A text explanation for result
        self.label_table = QtWidgets.QLabel(self.tab)
        self.label_table.setGeometry(QtCore.QRect(10, 575, 500, 20))
        self.label_table.setFont(font)
        self.label_table.setText("Interim calculation results:")

        # Result table
        self.result_table = QtWidgets.QTableWidget(self.tab)
        self.result_table.setGeometry(QtCore.QRect(10, 600, 990, 120))
        self.label_table_tab_2 = QtWidgets.QLabel(self.tab_2)
        self.label_table_tab_2.setGeometry(QtCore.QRect(10, 410, 500, 20))
        self.label_table_tab_2.setFont(font)
        self.label_table_tab_2.setText("Interim calculation results:")
        # Result table. Middleterm
        self.result_table_tab_2 = QtWidgets.QTableWidget(self.tab_2)
        self.result_table_tab_2.setGeometry(QtCore.QRect(10, 430, 960, 280))

        # Program menubar
        self.menubar = QtWidgets.QMenuBar(main_window)
        main_window.setMenuBar(self.menubar)
        main_window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1280, 21))

        # Menu 1. File - export data to Excel.
        self.menu_1_file = QtWidgets.QMenu(self.menubar)
        self.action_file_export = QtWidgets.QAction(main_window)
        self.menu_1_file.addAction(self.action_file_export)
        self.menubar.addAction(self.menu_1_file.menuAction())

        # Menu 2. Settings. Write to tmp. Default window size.
        # List of used restrictions.
        self.menu_2_settings = QtWidgets.QMenu(self.menubar)
        self.action_settings_write_in_file = QtWidgets.QAction(main_window)
        self.menu_2_settings.addAction(self.action_settings_write_in_file)
        self.action_settings_default_window_size = QtWidgets.QAction(main_window)
        self.menu_2_settings.addAction(self.action_settings_default_window_size)
        self.menubar.addAction(self.menu_2_settings.menuAction())
        self.action_settings_used_restrictions = QtWidgets.QAction(main_window)
        self.menu_2_settings.addAction(self.action_settings_used_restrictions)
        self.menubar.addAction(self.menu_2_settings.menuAction())

        # Menu 3. Choose variant.
        self.menu_3_variant = QtWidgets.QMenu(self.menubar)
        self.action = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action)
        self.action_2 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_2)
        self.action_3 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_3)
        self.action_4 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_4)
        self.action_5 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_5)
        self.action_6 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_6)
        self.action_7 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_7)
        self.action_8 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_8)
        self.action_9 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_9)
        self.action_10 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_10)
        self.action_11 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_11)
        self.action_12 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_12)
        self.action_13 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_13)
        self.action_14 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_14)
        self.action_15 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_15)
        self.action_16 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_16)
        self.action_17 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_17)
        self.action_18 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_18)
        self.action_19 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_19)
        self.action_20 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_20)
        self.action_21 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_21)
        self.action_22 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_22)
        self.action_23 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_23)
        self.action_24 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_24)
        self.action_25 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_25)
        self.action_26 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_26)
        self.action_27 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_27)
        self.action_28 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_28)
        self.action_29 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_29)
        self.action_30 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_30)
        self.action_31 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_31)
        self.action_32 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_32)
        self.action_33 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_33)
        self.action_34 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_34)
        self.action_35 = QtWidgets.QAction(main_window)
        self.menu_3_variant.addAction(self.action_35)
        self.menubar.addAction(self.menu_3_variant.menuAction())

        # Menu 4. Program info.
        self.menu_4_about = QtWidgets.QMenu(self.menubar)
        self.action_about_program = QtWidgets.QAction(main_window)
        self.menu_4_about.addAction(self.action_about_program)
        self.menubar.addAction(self.menu_4_about.menuAction())

        self.retranslateUi(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "main_window"))
        self.station_info_browser.setHtml(_translate("main_window",
                                            "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                            "p, li { white-space: pre-wrap; }\n"
                                            "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
                                            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%s</p></body></html>" % (
                                                self.station_info)))
        self.restrictions_info_browser.setHtml(_translate("main_window",
                                              "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                              "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                              "p, li { white-space: pre-wrap; }\n"
                                              "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
                                              "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%s</p></body></html>" % (
                                                  self.errors_in_calculations)))
        self.station_info_browser_tab_2.setHtml(_translate("main_window",
                                                  "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                                  "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                                  "p, li { white-space: pre-wrap; }\n"
                                                  "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
                                                  "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%s</p></body></html>" % (
                                                      self.errors_in_calculations)))

        self.menu_1_file.setTitle(_translate("main_window", "File"))
        self.action_file_export.setText(_translate("main_window", "Export results"))
        self.menu_2_settings.setTitle(_translate("main_window", "Settings"))
        self.action_settings_write_in_file.setText(_translate("main_window", "Write in file"))
        self.action_settings_default_window_size.setText(_translate("main_window", "Default window size"))
        self.action_settings_used_restrictions.setText(_translate("main_window", "Used restrictions"))
        self.menu_3_variant.setTitle(_translate("main_window", "Calculation variant"))
        self.action.setText(_translate("main_window", "Variant 1"))
        self.action_2.setText(_translate("main_window", "Variant 2"))
        self.action_3.setText(_translate("main_window", "Variant 3"))
        self.action_4.setText(_translate("main_window", "Variant 4"))
        self.action_5.setText(_translate("main_window", "Variant 5"))
        self.action_6.setText(_translate("main_window", "Variant 6"))
        self.action_7.setText(_translate("main_window", "Variant 7"))
        self.action_8.setText(_translate("main_window", "Variant 8"))
        self.action_9.setText(_translate("main_window", "Variant 9"))
        self.action_10.setText(_translate("main_window", "Variant 10"))
        self.action_11.setText(_translate("main_window", "Variant 11"))
        self.action_12.setText(_translate("main_window", "Variant 12"))
        self.action_13.setText(_translate("main_window", "Variant 13"))
        self.action_14.setText(_translate("main_window", "Variant 14"))
        self.action_15.setText(_translate("main_window", "Variant 15"))
        self.action_16.setText(_translate("main_window", "Variant 16"))
        self.action_17.setText(_translate("main_window", "Variant 17"))
        self.action_18.setText(_translate("main_window", "Variant 18"))
        self.action_19.setText(_translate("main_window", "Variant 19"))
        self.action_20.setText(_translate("main_window", "Variant 20"))
        self.action_21.setText(_translate("main_window", "Variant 21"))
        self.action_22.setText(_translate("main_window", "Variant 22"))
        self.action_23.setText(_translate("main_window", "Variant 23"))
        self.action_24.setText(_translate("main_window", "Variant 24"))
        self.action_25.setText(_translate("main_window", "Variant 25"))
        self.action_26.setText(_translate("main_window", "Variant 26"))
        self.action_27.setText(_translate("main_window", "Variant 27"))
        self.action_28.setText(_translate("main_window", "Variant 28"))
        self.action_29.setText(_translate("main_window", "Variant 29"))
        self.action_30.setText(_translate("main_window", "Variant 30"))
        self.action_31.setText(_translate("main_window", "Variant 31"))
        self.action_32.setText(_translate("main_window", "Variant 32"))
        self.action_33.setText(_translate("main_window", "Variant 33"))
        self.action_34.setText(_translate("main_window", "Variant 34"))
        self.action_35.setText(_translate("main_window", "Variant 35"))
        self.menu_4_about.setTitle(_translate("main_window", "Help"))
        self.action_about_program.setText(_translate("main_window", "About program"))
        self.start_calculcation.setText(_translate("main_window", "Accept"))
        self.form_report.setText(_translate("main_window", "Report"))
        self.revert_calculcation.setText(_translate("main_window", "Cancel"))
        self.start_calculcation_tab_2.setText(_translate("main_window", "Accept"))
        self.group_box_station_info_and_restr.setTitle(_translate("main_window", "Station info and restrictions:"))
        self.group_box_station_info_and_restr_tab_2.setTitle(_translate("main_window", "Station info and restrictions:"))
        self.group_box.setTitle(_translate("main_window", "Calculation:"))
        self.group_box_line_tab_2.setTitle(_translate("main_window", "Middleterm regime:"))
        self.group_box_tab_2.setTitle(_translate("main_window", "Calculation:"))
