'''
This file contains main code of program: Educational software for planning regime of HPP. NRU MPEI, Moscow, Russia.
Version: v.1.2
Last update 29.06.2019
Developed on PyQt5 v5.6; Python 3.5
Autor: Alexander Sysoev (AlexShepa)
'''

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (QLineF, QPointF, QRectF, Qt)
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem,
                             QGridLayout, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QGraphicsRectItem, QInputDialog)
from PyQt5.QtGui import QPainter, QBrush
from window_bone import UiMainWindow
import xlsxwriter
import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from initial_data import initial_data


class MyFirstGuiProgram(QtWidgets.QMainWindow, UiMainWindow):
    int_data = initial_data(QtWidgets.QMainWindow)
    number_of_RP = int_data['Number of CP'] + 1
    z_max = int_data['Mark max']
    z_min = int_data['Mark min']
    z_start = int_data['Mark start']
    q_pritok = int_data['Rate']
    t_days = int_data['Time in days']
    losses = int_data['Rate losses']
    dh = int_data['Head losses']
    variant = 1
    station_info = 'Votkinskaya HPP on Kama river. NPU = %s m, UMO = %s m. Начальная отметка = %s m.' % (
        z_max, z_min, z_start[str(variant)])
    margin_top = 15
    margin_left = 0
    graph_height_px = 320
    margin_right = 35
    deltaY = graph_height_px / 10
    deltaZ = (z_max - z_min) / 10
    restrictions = int_data['Restrictions']
    working_characteristic = int_data['Work characteristics']
    UiMainWindow.errors_in_calculations = int_data['Errors in calc']
    long_term_head_change_permission = False
    resized = QtCore.pyqtSignal()
    tmp_log_write = True

    def __init__(self, parent=None):
        self.result_list = []
        self.regime_list = []
        self.regime_rect_list = []
        self.regime_dict_middle = {}
        self.regime_rect_dict_middle = {}
        self.middle_term_calculation = False
        QtWidgets.QMainWindow.__init__(self, parent=parent)
        self.setup_ui(self)
        self.action_file_export.triggered.connect(lambda: self.excel_export())
        self.revert_calculcation.clicked.connect(lambda: self.revert_calculation_longterm())
        self.scene = QtWidgets.QGraphicsScene()
        self.scene_middle = QtWidgets.QGraphicsScene()
        self.graphics_view.setScene(self.scene)
        self.graphics_view_tab2.setScene(self.scene_middle)
        self.form_report.clicked.connect(lambda: self.excel_export())
        self.resized.connect(self.change_size_function)
        self.action_settings_default_window_size.triggered.connect(lambda: self.resize(1024, 800))
        self.action_about_program.triggered.connect(lambda: self.about_program())
        self.action_settings_write_in_file.setCheckable(True)
        self.action_settings_write_in_file.triggered.connect(lambda: self.cancel_write_down())
        self.action_settings_used_restrictions.triggered.connect(lambda: self.used_restrictions())
        # ----- end -----

        # Axes
        graph_width_px = self.graphics_view.width() - self.margin_right
        self.deltaX = deltaX = int(graph_width_px) / int(self.number_of_RP)  # Distance on X between lines
        graph_width_px_middle = self.graphics_view_tab2.width() - self.margin_right
        self.deltaX_middle = int(graph_width_px_middle) / 4  # Distance on X between lines - middleterm
        self.calculcation_indicator.setMinimum(1)
        self.calculcation_indicator.valueChanged.connect(
            lambda: self.addInputTextToListbox(self.scene, deltaX))  # Draw cursor when change CP
        self.calculcation_indicator.valueChanged.connect(lambda: self.future_rate(self.calculcation_indicator.value()))
        self.calculcation_indicator.setMaximum(1)
        self.addInputTextToListbox(self.scene, deltaX)  # Draw first cursor
        self.graph_height_px = self.graphics_view.height() - 80

        # Draw station regime - longterm
        self.insert_mark.returnPressed.connect((lambda: self.draw_regime(self.scene, 'mark')))
        self.insert_rate.returnPressed.connect((lambda: self.draw_regime(self.scene, 'rate')))
        self.start_calculcation.clicked.connect((lambda: self.draw_regime(self.scene, 'button')))

        # Take table - longterm
        self.result_table.setColumnCount(self.number_of_RP)
        self.result_table.setHorizontalHeaderLabels([str(i) for i in range(0, self.number_of_RP)])
        self.result_table.setRowCount(3)
        self.result_table.setVerticalHeaderLabels(["Q, m³/s", "Z, m", "H, m"])
        self.result_table.cellActivated.connect(self.activated_from_table)
        self.result_table.currentItemChanged.connect(self.current_head)
        self.result_table.currentCellChanged.connect(self.entered)
        self.long_term_head_item = None
        self.result_table.itemChanged.connect(self.item_changed)
        self.result_table.resizeColumnsToContents()

        self.model = QtGui.QStandardItemModel(3, 1)
        self.selModel = QtCore.QItemSelectionModel(self.model)
        self.long_term_head_change_permission = True
        item_start = QtWidgets.QTableWidgetItem(str(self.z_start[str(self.variant)]))
        self.result_table.setItem(1, 0, item_start)
        empty_cell = QtWidgets.QTableWidgetItem('-')
        self.result_table.setItem(0, 0, empty_cell)
        empty_cell = QtWidgets.QTableWidgetItem('-')
        self.result_table.setItem(2, 0, empty_cell)
        self.result_table.resizeColumnsToContents()
        self.station_info_browser.setFontWeight(400)
        self.editIndex = QModelIndex()
        text = '<span style="font-weight: 400">%s</span>' % (self.int_data['Station info'])
        self.station_info_browser.setHtml(text)
        self.future_rate(self.calculcation_indicator.value())
        self.middle_rate(1)
        self.long_term_head_change_permission = False
        self.deltaX = (self.graphics_view.width() - self.margin_right) / int(self.number_of_RP)

        # ---MIDDLETERM---

        # Set combobox for middleterm
        text = '<span style="font-weight: 400">%s</span>' % (self.int_data['Errors in calc'])
        self.restrictions_info_browser_tab_2.setHtml(text)
        self.start_period_tab_2.addItems(['0'])
        self.end_period_tab_2.addItem(str(self.start_period_tab_2.currentIndex() + 3))
        self.choose_line_tab_2.addItems(['A', 'B', 'C'])

        # Activate functions after change of initial period with combobox
        self.start_period_tab_2.currentIndexChanged.connect(lambda: self.middleterm_change_of_period())

        # Draw coordinate net - middleterm
        self.draw_coordinate_net(self.scene_middle, int(self.end_period_tab_2.currentText()) + 1,
                                 self.graphics_view_tab2)
        self.draw_dispatch_graph(self.scene_middle, 4, self.graphics_view_tab2)
        self.add_zones(self.scene_middle, 4, self.graphics_view_tab2)

        self.insert_mark_tab_2.returnPressed.connect(
            (lambda: self.draw_regime_middle(self.scene_middle, 'mark')))
        self.insert_rate_tab_2.returnPressed.connect(
            (lambda: self.draw_regime_middle(self.scene_middle, 'rate')))
        self.start_calculcation_tab_2.clicked.connect(
            (lambda: self.draw_regime_middle(self.scene_middle, 'button')))

        self.choose_line_tab_2.currentTextChanged.connect(lambda: self.table_selection_change())

        self.result_table_tab_2.setColumnCount(11)
        self.result_table_tab_2.setHorizontalHeaderLabels([
            "CP", "Line", "Qicn, m³/s", "Zubs, m", "Zube, m", "Zlb, m", "H, m", 'Qhpp, m³/s', 'N, MVt', 'E, kVt*h',
            'Approve'
        ])
        self.result_table_tab_2.setRowCount(39)
        self.result_table_tab_2.resizeColumnsToContents()
        # Enter line names
        item = QtWidgets.QTableWidgetItem('A')
        self.result_table_tab_2.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem('A-1')
        self.result_table_tab_2.setItem(1, 1, item)
        item = QtWidgets.QTableWidgetItem('A-1-1')
        self.result_table_tab_2.setItem(2, 1, item)
        self.btn_A11 = QtWidgets.QPushButton()
        self.btn_A11.setText('Approve line A-1-1')
        self.btn_A11.setEnabled(False)
        self.result_table_tab_2.setCellWidget(2, 10, self.btn_A11)
        self.btn_A11.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_A11.text()))
        item = QtWidgets.QTableWidgetItem('A-1-2')
        self.result_table_tab_2.setItem(3, 1, item)
        self.btn_A12 = QtWidgets.QPushButton()
        self.btn_A12.setText('Approve line A-1-2')
        self.btn_A12.setEnabled(False)
        self.result_table_tab_2.setCellWidget(3, 10, self.btn_A12)
        self.btn_A12.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_A12.text()))
        item = QtWidgets.QTableWidgetItem('A-1-3')
        self.result_table_tab_2.setItem(4, 1, item)
        self.btn_A13 = QtWidgets.QPushButton()
        self.btn_A13.setText('Approve line A-1-3')
        self.btn_A13.setEnabled(False)
        self.result_table_tab_2.setCellWidget(4, 10, self.btn_A13)
        self.btn_A13.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_A13.text()))
        item = QtWidgets.QTableWidgetItem('A-2')
        self.result_table_tab_2.setItem(5, 1, item)
        item = QtWidgets.QTableWidgetItem('A-2-1')
        self.result_table_tab_2.setItem(6, 1, item)
        self.btn_A21 = QtWidgets.QPushButton()
        self.btn_A21.setText('Approve line A-2-1')
        self.btn_A21.setEnabled(False)
        self.result_table_tab_2.setCellWidget(6, 10, self.btn_A21)
        self.btn_A21.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_A21.text()))
        item = QtWidgets.QTableWidgetItem('A-2-2')
        self.result_table_tab_2.setItem(7, 1, item)
        self.btn_A22 = QtWidgets.QPushButton()
        self.btn_A22.setText('Approve line A-2-2')
        self.btn_A22.setEnabled(False)
        self.result_table_tab_2.setCellWidget(7, 10, self.btn_A22)
        self.btn_A22.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_A22.text()))
        item = QtWidgets.QTableWidgetItem('A-2-3')
        self.result_table_tab_2.setItem(8, 1, item)
        self.btn_A23 = QtWidgets.QPushButton()
        self.btn_A23.setText('Approve line A-2-3')
        self.btn_A23.setEnabled(False)
        self.result_table_tab_2.setCellWidget(8, 10, self.btn_A23)
        self.btn_A23.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_A23.text()))
        item = QtWidgets.QTableWidgetItem('A-3')
        self.result_table_tab_2.setItem(9, 1, item)
        item = QtWidgets.QTableWidgetItem('A-3-1')
        self.result_table_tab_2.setItem(10, 1, item)
        self.result_table_tab_2.setItem(10, 1, item)
        self.btn_A31 = QtWidgets.QPushButton()
        self.btn_A31.setText('Approve line A-3-1')
        self.btn_A31.setEnabled(False)
        self.result_table_tab_2.setCellWidget(10, 10, self.btn_A31)
        self.btn_A31.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_A31.text()))
        item = QtWidgets.QTableWidgetItem('A-3-2')
        self.result_table_tab_2.setItem(11, 1, item)
        self.btn_A32 = QtWidgets.QPushButton()
        self.btn_A32.setText('Approve line A-3-2')
        self.btn_A32.setEnabled(False)
        self.result_table_tab_2.setCellWidget(11, 10, self.btn_A32)
        self.btn_A32.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_A32.text()))
        item = QtWidgets.QTableWidgetItem('A-3-3')
        self.result_table_tab_2.setItem(12, 1, item)
        self.btn_A33 = QtWidgets.QPushButton()
        self.btn_A33.setText('Approve line A-3-3')
        self.btn_A33.setEnabled(False)
        self.result_table_tab_2.setCellWidget(12, 10, self.btn_A33)
        self.btn_A33.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_A33.text()))
        item = QtWidgets.QTableWidgetItem('B')
        self.result_table_tab_2.setItem(13, 1, item)
        item = QtWidgets.QTableWidgetItem('B-1')
        self.result_table_tab_2.setItem(14, 1, item)
        item = QtWidgets.QTableWidgetItem('B-1-1')
        self.result_table_tab_2.setItem(15, 1, item)
        self.btn_B11 = QtWidgets.QPushButton()
        self.btn_B11.setText('Approve line B-1-1')
        self.btn_B11.setEnabled(False)
        self.result_table_tab_2.setCellWidget(15, 10, self.btn_B11)
        self.btn_B11.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_B11.text()))
        item = QtWidgets.QTableWidgetItem('B-1-2')
        self.result_table_tab_2.setItem(16, 1, item)
        self.btn_B12 = QtWidgets.QPushButton()
        self.btn_B12.setText('Approve line B-1-2')
        self.btn_B12.setEnabled(False)
        self.result_table_tab_2.setCellWidget(16, 10, self.btn_B12)
        self.btn_B12.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_B12.text()))
        item = QtWidgets.QTableWidgetItem('B-1-3')
        self.result_table_tab_2.setItem(17, 1, item)
        self.btn_B13 = QtWidgets.QPushButton()
        self.btn_B13.setText('Approve line B-1-3')
        self.btn_B13.setEnabled(False)
        self.result_table_tab_2.setCellWidget(17, 10, self.btn_B13)
        self.btn_B13.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_B13.text()))
        item = QtWidgets.QTableWidgetItem('B-2')
        self.result_table_tab_2.setItem(18, 1, item)
        item = QtWidgets.QTableWidgetItem('B-2-1')
        self.result_table_tab_2.setItem(19, 1, item)
        self.btn_B21 = QtWidgets.QPushButton()
        self.btn_B21.setText('Approve line B-2-1')
        self.btn_B21.setEnabled(False)
        self.result_table_tab_2.setCellWidget(19, 10, self.btn_B21)
        self.btn_B21.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_B21.text()))
        item = QtWidgets.QTableWidgetItem('B-2-2')
        self.result_table_tab_2.setItem(20, 1, item)
        self.btn_B22 = QtWidgets.QPushButton()
        self.btn_B22.setText('Approve line B-2-2')
        self.btn_B22.setEnabled(False)
        self.result_table_tab_2.setCellWidget(20, 10, self.btn_B22)
        self.btn_B22.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_B22.text()))
        item = QtWidgets.QTableWidgetItem('B-2-3')
        self.result_table_tab_2.setItem(21, 1, item)
        self.btn_B23 = QtWidgets.QPushButton()
        self.btn_B23.setText('Approve line B-2-3')
        self.btn_B23.setEnabled(False)
        self.result_table_tab_2.setCellWidget(21, 10, self.btn_B23)
        self.btn_B23.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_B23.text()))
        item = QtWidgets.QTableWidgetItem('B-3')
        self.result_table_tab_2.setItem(22, 1, item)
        item = QtWidgets.QTableWidgetItem('B-3-1')
        self.result_table_tab_2.setItem(23, 1, item)
        self.btn_B31 = QtWidgets.QPushButton()
        self.btn_B31.setText('Approve line B-3-1')
        self.btn_B31.setEnabled(False)
        self.result_table_tab_2.setCellWidget(23, 10, self.btn_B31)
        self.btn_B31.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_B31.text()))
        item = QtWidgets.QTableWidgetItem('B-3-2')
        self.result_table_tab_2.setItem(24, 1, item)
        self.btn_B32 = QtWidgets.QPushButton()
        self.btn_B32.setText('Approve line B-3-2')
        self.btn_B32.setEnabled(False)
        self.result_table_tab_2.setCellWidget(24, 10, self.btn_B32)
        self.btn_B32.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_B32.text()))
        item = QtWidgets.QTableWidgetItem('B-3-3')
        self.result_table_tab_2.setItem(25, 1, item)
        self.btn_B33 = QtWidgets.QPushButton()
        self.btn_B33.setText('Approve line B-3-3')
        self.btn_B33.setEnabled(False)
        self.result_table_tab_2.setCellWidget(25, 10, self.btn_B33)
        self.btn_B33.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_B33.text()))
        item = QtWidgets.QTableWidgetItem('C')
        self.result_table_tab_2.setItem(26, 1, item)
        item = QtWidgets.QTableWidgetItem('C-1')
        self.result_table_tab_2.setItem(27, 1, item)
        item = QtWidgets.QTableWidgetItem('C-1-1')
        self.result_table_tab_2.setItem(28, 1, item)
        self.btn_C11 = QtWidgets.QPushButton()
        self.btn_C11.setText('Approve line C-1-1')
        self.btn_C11.setEnabled(False)
        self.result_table_tab_2.setCellWidget(28, 10, self.btn_C11)
        self.btn_C11.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_C11.text()))
        item = QtWidgets.QTableWidgetItem('C-1-2')
        self.result_table_tab_2.setItem(29, 1, item)
        self.btn_C12 = QtWidgets.QPushButton()
        self.btn_C12.setText('Approve line C-1-2')
        self.btn_C12.setEnabled(False)
        self.result_table_tab_2.setCellWidget(29, 10, self.btn_C12)
        self.btn_C12.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_C12.text()))
        item = QtWidgets.QTableWidgetItem('C-1-3')
        self.result_table_tab_2.setItem(30, 1, item)
        self.btn_C13 = QtWidgets.QPushButton()
        self.btn_C13.setText('Approve line C-1-3')
        self.btn_C13.setEnabled(False)
        self.result_table_tab_2.setCellWidget(30, 10, self.btn_C13)
        self.btn_C13.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_C13.text()))
        item = QtWidgets.QTableWidgetItem('C-2')
        self.result_table_tab_2.setItem(31, 1, item)
        item = QtWidgets.QTableWidgetItem('C-2-1')
        self.result_table_tab_2.setItem(32, 1, item)
        self.btn_C21 = QtWidgets.QPushButton()
        self.btn_C21.setText('Approve line C-2-1')
        self.btn_C21.setEnabled(False)
        self.result_table_tab_2.setCellWidget(32, 10, self.btn_C21)
        self.btn_C21.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_C21.text()))
        item = QtWidgets.QTableWidgetItem('C-2-2')
        self.result_table_tab_2.setItem(33, 1, item)
        self.btn_C22 = QtWidgets.QPushButton()
        self.btn_C22.setText('Approve line C-2-2')
        self.btn_C22.setEnabled(False)
        self.result_table_tab_2.setCellWidget(33, 10, self.btn_C22)
        self.btn_C22.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_C22.text()))
        item = QtWidgets.QTableWidgetItem('C-2-3')
        self.result_table_tab_2.setItem(34, 1, item)
        self.btn_C23 = QtWidgets.QPushButton()
        self.btn_C23.setText('Approve line C-2-3')
        self.btn_C23.setEnabled(False)
        self.result_table_tab_2.setCellWidget(34, 10, self.btn_C23)
        self.btn_C23.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_C23.text()))
        item = QtWidgets.QTableWidgetItem('C-3')
        self.result_table_tab_2.setItem(35, 1, item)
        item = QtWidgets.QTableWidgetItem('C-3-1')
        self.result_table_tab_2.setItem(36, 1, item)
        self.btn_C31 = QtWidgets.QPushButton()
        self.btn_C31.setText('Approve line C-3-1')
        self.btn_C31.setEnabled(False)
        self.result_table_tab_2.setCellWidget(36, 10, self.btn_C31)
        self.btn_C31.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_C31.text()))
        item = QtWidgets.QTableWidgetItem('C-3-2')
        self.result_table_tab_2.setItem(37, 1, item)
        self.btn_C32 = QtWidgets.QPushButton()
        self.btn_C32.setText('Approve line C-3-2')
        self.btn_C32.setEnabled(False)
        self.result_table_tab_2.setCellWidget(37, 10, self.btn_C32)
        self.btn_C32.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_C32.text()))
        item = QtWidgets.QTableWidgetItem('C-3-3')
        self.result_table_tab_2.setItem(38, 1, item)
        self.btn_C33 = QtWidgets.QPushButton()
        self.btn_C33.setText('Approve line C-3-3')
        self.btn_C33.setEnabled(False)
        self.result_table_tab_2.setCellWidget(38, 10, self.btn_C33)
        self.btn_C33.clicked.connect(lambda: self.approve_line_from_middleterm(self.btn_C33.text()))
        self.result_table_tab_2.resizeColumnsToContents()
        # End enter line names
        # Create index dictionary
        self.middle_line_index = {
            'A': 0, 'A-1': 1, 'A-1-1': 2, 'A-1-2': 3, 'A-1-3': 4, 'A-2': 5, 'A-2-1': 6, 'A-2-2': 7, 'A-2-3': 8,
            'A-3': 9, 'A-3-1': 10, 'A-3-2': 11, 'A-3-3': 12, 'B': 13, 'B-1': 14, 'B-1-1': 15, 'B-1-2': 16, 'B-1-3': 17,
            'B-2': 18, 'B-2-1': 19, 'B-2-2': 20, 'B-2-3': 21, 'B-3': 22, 'B-3-1': 23, 'B-3-2': 24, 'B-3-3': 25,
            'C': 26, 'C-1': 27, 'C-1-1': 28, 'C-1-2': 29, 'C-1-3': 30, 'C-2': 31, 'C-2-1': 32, 'C-2-2': 33,
            'C-2-3': 34, 'C-3': 35, 'C-3-1': 36, 'C-3-2': 37, 'C-3-3': 38}

        self.middle_btn_names = {
            'A-1-1': self.btn_A11, 'A-1-2': self.btn_A12, 'A-1-3': self.btn_A13, 'A-2-1': self.btn_A21,
            'A-2-2': self.btn_A22, 'A-2-3': self.btn_A23, 'A-3-1': self.btn_A31, 'A-3-2': self.btn_A32,
            'A-3-3': self.btn_A33, 'B-1-1': self.btn_B11, 'B-1-2': self.btn_B12, 'B-1-3': self.btn_B13,
            'B-2-1': self.btn_B21, 'B-2-2': self.btn_B22, 'B-2-3': self.btn_B23, 'B-3-1': self.btn_B31,
            'B-3-2': self.btn_B32, 'B-3-3': self.btn_B33, 'C-1-1': self.btn_C11, 'C-1-2': self.btn_C12,
            'C-1-3': self.btn_C13, 'C-2-1': self.btn_C21, 'C-2-2': self.btn_C22, 'C-2-3': self.btn_C23,
            'C-3-1': self.btn_C31, 'C-3-2': self.btn_C32, 'C-3-3': self.btn_C33}

        for i in self.menu_3_variant.actions():
            i.setCheckable(True)
        self.action.setChecked(True)
        self.action.triggered.connect(lambda: self.change_of_variant('1'))
        self.action_2.triggered.connect(lambda: self.change_of_variant('2'))
        self.action_3.triggered.connect(lambda: self.change_of_variant('3'))
        self.action_4.triggered.connect(lambda: self.change_of_variant('4'))
        self.action_5.triggered.connect(lambda: self.change_of_variant('5'))
        self.action_6.triggered.connect(lambda: self.change_of_variant('6'))
        self.action_7.triggered.connect(lambda: self.change_of_variant('7'))
        self.action_8.triggered.connect(lambda: self.change_of_variant('8'))
        self.action_9.triggered.connect(lambda: self.change_of_variant('9'))
        self.action_10.triggered.connect(lambda: self.change_of_variant('10'))
        self.action_11.triggered.connect(lambda: self.change_of_variant('11'))
        self.action_12.triggered.connect(lambda: self.change_of_variant('12'))
        self.action_13.triggered.connect(lambda: self.change_of_variant('13'))
        self.action_14.triggered.connect(lambda: self.change_of_variant('14'))
        self.action_15.triggered.connect(lambda: self.change_of_variant('15'))
        self.action_16.triggered.connect(lambda: self.change_of_variant('16'))
        self.action_17.triggered.connect(lambda: self.change_of_variant('17'))
        self.action_18.triggered.connect(lambda: self.change_of_variant('18'))
        self.action_19.triggered.connect(lambda: self.change_of_variant('19'))
        self.action_20.triggered.connect(lambda: self.change_of_variant('20'))
        self.action_21.triggered.connect(lambda: self.change_of_variant('21'))
        self.action_22.triggered.connect(lambda: self.change_of_variant('22'))
        self.action_23.triggered.connect(lambda: self.change_of_variant('23'))
        self.action_24.triggered.connect(lambda: self.change_of_variant('24'))
        self.action_25.triggered.connect(lambda: self.change_of_variant('25'))
        self.action_26.triggered.connect(lambda: self.change_of_variant('26'))
        self.action_27.triggered.connect(lambda: self.change_of_variant('27'))
        self.action_28.triggered.connect(lambda: self.change_of_variant('28'))
        self.action_29.triggered.connect(lambda: self.change_of_variant('29'))
        self.action_30.triggered.connect(lambda: self.change_of_variant('30'))
        self.action_31.triggered.connect(lambda: self.change_of_variant('31'))
        self.action_32.triggered.connect(lambda: self.change_of_variant('32'))
        self.action_33.triggered.connect(lambda: self.change_of_variant('33'))
        self.action_34.triggered.connect(lambda: self.change_of_variant('34'))
        self.action_35.triggered.connect(lambda: self.change_of_variant('35'))

        self.menu_action_indexes = {
            '1': self.action, '2': self.action_2, '3': self.action_3, '4': self.action_4,
            '5': self.action_5, '6': self.action_6, '7': self.action_7, '8': self.action_8, '9': self.action_9,
            '10': self.action_10, '11': self.action_11, '12': self.action_12, '13': self.action_13,
            '14': self.action_14, '15': self.action_15, '16': self.action_16, '17': self.action_17,
            '18': self.action_18, '19': self.action_19, '20': self.action_20, '21': self.action_21,
            '22': self.action_22, '23': self.action_23, '24': self.action_24, '25': self.action_25,
            '26': self.action_26, '27': self.action_27, '28': self.action_28, '29': self.action_29,
            '30': self.action_30, '31': self.action_31, '32': self.action_32, '33': self.action_33,
            '34': self.action_34, '35': self.action_35}

        self.tmp_log_write_down()

    # Setting for restrictions
    def used_restrictions(self):
        self.restriction_array = self.restrictions
        self.restriction_window = QtWidgets.QDialog(self)
        self.restriction_window.setMinimumSize(400, 80 + 20 * len(self.restriction_array))
        self.restriction_window.resize(400, 50 + 20 * len(self.restriction_array))
        self.restriction_window.setWindowTitle('Restriction settings')
        hello_text = QtWidgets.QGroupBox(self.restriction_window)
        font = QtGui.QFont()
        font.setBold(False)
        font.setPointSize(8)
        font.setWeight(5)
        hello_text.setFont(font)
        hello_text.setGeometry(QtCore.QRect(10, 10, 380, 30 + 20 * len(self.restriction_array)))
        hello_text.setTitle("Choose restrictions to use:")
        self.check_boxes_list = []
        for index, value in enumerate(self.restriction_array):
            ch_box = QtWidgets.QCheckBox(value[0], hello_text)
            ch_box.move(20, 25 + 20 * index)
            if value[6]:
                ch_box.toggle()
            ch_box.stateChanged.connect(lambda: self.change_of_restriction())
            self.check_boxes_list.append(ch_box)
        accept_button = QtWidgets.QPushButton(self.restriction_window)
        accept_button.setGeometry(310, self.restriction_window.height() - 35, 80, 25)
        accept_button.setText('Accept')
        accept_button.clicked.connect(lambda: self.accept_change_of_restrictions())
        self.restriction_window.show()

    # Function omit change of checkbox
    def change_of_restriction(self):
        for i in range(len(self.check_boxes_list)):
            if self.check_boxes_list[i].isChecked() is False:
                self.restriction_array[i][6] = False

    # A function of receiving a change to the list of restrictions
    def accept_change_of_restrictions(self):
        self.restrictions = self.restriction_array
        if self.calculcation_indicator.maximum() > 1:
            self.calculcation_indicator.setValue(1)
            self.insert_rate.insert(self.result_table.item(0, 1).text())
            self.draw_regime(self.scene, 'rate')
        self.restriction_window.close()

    def resizeEvent(self, event):
        self.resized.emit()
        return super(MyFirstGuiProgram, self).resizeEvent(event)

    def add_zones(self, scene, number_of_RP, view):
        graph = self.dispatch_graph()
        graph_width_px = view.width() - self.margin_right
        deltaX = int(graph_width_px) / int(number_of_RP)  # The distance X between the lines
        if deltaX < 45.47:
            deltaX = 45.476190476190474
        if scene == self.scene:  # For longterm
            for i in range(len(graph) - 1):
                zone_path = QtGui.QPainterPath()
                line_name_1 = 'Line %s' % (str(i + 1))
                line_1 = graph[line_name_1]
                line_name_2 = 'Line %s' % (str(i + 2))
                line_2 = graph[line_name_2]
                if view.width():
                    zone_path.moveTo((self.margin_left + 0 * deltaX), self.from_absolute_to_relative(
                        line_1[0]))
                    for j in range(number_of_RP):
                        zone_path.lineTo((self.margin_left + j * deltaX), self.from_absolute_to_relative(line_1[j]))
                    zone_path.lineTo((self.margin_left + (number_of_RP - 1) * deltaX), self.from_absolute_to_relative(
                        line_2[number_of_RP - 1]))
                    for k in range(number_of_RP - 1, -1, -1):
                        zone_path.lineTo((self.margin_left + k * deltaX), self.from_absolute_to_relative(line_2[k]))
                    zone_path.closeSubpath()
                    pen_rec = QtGui.QPen(QtCore.Qt.black)
                    pen_rec.setWidth(2)
                    if line_name_2 == 'Line 2':
                        brush = QBrush(Qt.FDiagPattern)
                        brush.setColor(QtGui.QColor(255, 0, 0, 127))
                        scene.addPath(zone_path, pen_rec, brush)
                    elif line_name_2 == 'Line 3':
                        brush = QBrush(Qt.Dense6Pattern)
                        brush.setColor(QtGui.QColor(217, 0, 255, 255))
                        scene.addPath(zone_path, pen_rec, brush)
                    elif line_name_2 == 'Line 4':
                        brush = QBrush(Qt.DiagCrossPattern)
                        brush.setColor(QtGui.QColor(245, 161, 144, 255))
                        scene.addPath(zone_path, pen_rec, brush)
                    elif line_name_2 == 'Line 5':
                        brush = QBrush(Qt.Dense5Pattern)
                        brush.setColor(QtGui.QColor(230, 80, 0, 127))
                        scene.addPath(zone_path, pen_rec, brush)
                    elif line_name_2 == 'Line 6':
                        brush = QBrush(Qt.CrossPattern)
                        brush.setColor(QtGui.QColor(235, 255, 20, 255))
                        scene.addPath(zone_path, pen_rec, brush)
                    elif line_name_2 == 'Line 7':
                        brush = QBrush(Qt.BDiagPattern)
                        brush.setColor(QtGui.QColor(20, 157, 255, 255))
                        scene.addPath(zone_path, pen_rec, brush)
        else:  # For middleterm
            for i in range(len(graph) - 1):
                zone_path = QtGui.QPainterPath()
                line_name_1 = 'Line %s' % (str(i + 1))
                line_1 = graph[line_name_1]
                line_name_2 = 'Line %s' % (str(i + 2))
                line_2 = graph[line_name_2]
                if view.width():
                    zone_path.moveTo((self.margin_left + 0 * deltaX), self.from_absolute_to_relative_middle(
                        line_1[int(self.start_period_tab_2.currentText())]))
                    for j in range(number_of_RP):
                        zone_path.lineTo((self.margin_left + j * deltaX), self.from_absolute_to_relative_middle(
                            line_1[j + int(self.start_period_tab_2.currentText())]))
                    zone_path.lineTo((self.margin_left + 3 * deltaX), self.from_absolute_to_relative_middle(
                        line_2[int(self.end_period_tab_2.currentText())]))
                    for k in range(number_of_RP - 1, -1, -1):
                        zone_path.lineTo((self.margin_left + k * deltaX), self.from_absolute_to_relative_middle(
                            line_2[int(self.start_period_tab_2.currentText()) + k]))
                    zone_path.closeSubpath()
                    pen_rec = QtGui.QPen(QtCore.Qt.black)
                    pen_rec.setWidth(2)
                    if line_name_2 == 'Line 2':
                        brush = QBrush(Qt.FDiagPattern)
                        brush.setColor(QtGui.QColor(255, 0, 0, 127))
                        scene.addPath(zone_path, pen_rec, brush)
                    elif line_name_2 == 'Line 3':
                        brush = QBrush(Qt.Dense6Pattern)
                        brush.setColor(QtGui.QColor(190, 61, 245, 127))
                        scene.addPath(zone_path, pen_rec, brush)
                    elif line_name_2 == 'Line 4':
                        brush = QBrush(Qt.DiagCrossPattern)
                        brush.setColor(QtGui.QColor(245, 161, 144, 255))
                        scene.addPath(zone_path, pen_rec, brush)
                    elif line_name_2 == 'Line 5':
                        brush = QBrush(Qt.Dense5Pattern)
                        brush.setColor(QtGui.QColor(230, 80, 0, 127))
                        scene.addPath(zone_path, pen_rec, brush)
                    elif line_name_2 == 'Line 6':
                        brush = QBrush(Qt.CrossPattern)
                        brush.setColor(QtGui.QColor(235, 255, 20, 255))
                        scene.addPath(zone_path, pen_rec, brush)
                    elif line_name_2 == 'Line 7':
                        brush = QBrush(Qt.BDiagPattern)
                        brush.setColor(QtGui.QColor(20, 157, 255, 255))
                        scene.addPath(zone_path, pen_rec, brush)

    # Function responsible for changing the calculation option
    def change_of_variant(self, variant_new):
        if len(self.result_list) > 0:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Question)
            msg.setWindowTitle("Variant change")
            msg.setText("On variant change, all results will be lost! Continue?")
            okButton = msg.addButton('Yes', QtWidgets.QMessageBox.AcceptRole)
            msg.addButton('No', QtWidgets.QMessageBox.RejectRole)
            msg.exec()
            if msg.clickedButton() == okButton:
                self.start_period_tab_2.setCurrentIndex(0)
                self.choose_line_tab_2.setCurrentIndex(0)
                old_variant = self.menu_action_indexes[str(self.variant)]
                old_variant.setChecked(False)
                new_variant = self.menu_action_indexes[variant_new]
                new_variant.setChecked(True)
                self.variant = int(variant_new)
                file = open('EducationalSoftware.tmp', 'r')
                lines = file.readlines()
                file.close()
                file_new = open('EducationalSoftware.tmp', 'w')
                file_new.write(lines[0])
                file_new.write(str(self.variant) + '\n')

                file_new.close()
                self.result_list = []
                self.regime_list = []
                self.regime_rect_list = []
                self.end_period_tab_2.removeItem(0)
                self.end_period_tab_2.addItem(str(self.start_period_tab_2.currentIndex() + 3))
                for i in range(1, self.start_period_tab_2.count()):
                    self.start_period_tab_2.removeItem(1)
                for l in range(self.choose_line_tab_2.count() - 1):
                    try:
                        self.choose_line_tab_2.removeItem(1)
                    except:
                        pass
                self.choose_line_tab_2.addItems(['B', 'C'])
                for items in self.scene.items():
                    try:
                        if str(items.pen().color().red()) == '255':
                            self.scene.removeItem(items)
                    except:
                        pass
                for items in self.scene_middle.items():
                    try:
                        if str(items.pen().color().red()) == '255':
                            self.scene_middle.removeItem(items)
                        elif str(items.pen().color().name()) == '#ff00ff':
                            self.scene_middle.removeItem(items)
                        elif str(items.pen().color().name()) == '#00ffff':
                            self.scene_middle.removeItem(items)
                        elif str(items.pen().color().green()) == '255':
                            self.scene_middle.removeItem(items)
                    except:
                        pass

                pen_rec = QtGui.QPen(QtCore.Qt.red)
                pen_rec.setWidth(4)
                rect_start = QtCore.QRectF(self.margin_left - 1.5,
                                           self.from_absolute_to_relative(self.z_start[str(self.variant)]) - 1.5, 3, 3)
                self.scene.addRect(rect_start, pen_rec)
                pen_rec = QtGui.QPen(QtCore.Qt.red)
                pen_rec.setWidth(4)
                rect_start = QtCore.QRectF(self.margin_left - 1.5,
                                           self.from_absolute_to_relative_middle(self.z_start[str(self.variant)]) - 1.5,
                                           3, 3)
                self.scene_middle.addRect(rect_start, pen_rec)
                self.long_term_head_change_permission = True
                self.result_table.item(1, 0).setText(str(self.z_start[str(self.variant)]))
                self.station_info = 'Votkinskaya HPP on Kama river. NPU = %s m, UMO = %s m. Начальная отметка = %s m.' % (
                    self.z_max, self.z_min, self.z_start[str(self.variant)])
                max = self.calculcation_indicator.maximum()
                self.calculcation_indicator.setMaximum(1)
                self.future_rate(self.calculcation_indicator.value())
                for j in range(1, max):
                    for l in range(0, 3):
                        self.result_table.item(l, j).setText('')
                self.long_term_head_change_permission = False
                for l in range(40):
                    if self.result_table_tab_2.item(l, 0) is not None:
                        self.result_table_tab_2.item(l, 0).setText('')
                    for k in range(8):
                        if self.result_table_tab_2.item(l, k + 2) is not None:
                            self.result_table_tab_2.item(l, k + 2).setText('')
                if self.restrictions_info_browser.toPlainText() == 'No errors during calculation':
                    pass
                else:
                    self.restrictions_info_browser.setText('No errors during calculation')
                self.restrictions_info_browser_tab_2.setText('No errors during calculation')
                if self.tmp_log_write:
                    if self.tmp_log_write:
                        file = open('EducationalSoftware.tmp', 'r')
                        data = file.readlines()
                        file.close()
                        file_new = open('EducationalSoftware.tmp', 'w')
                        file_new.write(data[0])
                        file_new.write(data[1])
                        file_new.close()
                return 'End'
            else:
                new_variant = self.menu_action_indexes[variant_new]
                new_variant.setChecked(False)
        else:
            old_variant = self.menu_action_indexes[str(self.variant)]
            old_variant.setChecked(False)
            new_variant = self.menu_action_indexes[variant_new]
            new_variant.setChecked(True)
            self.variant = int(variant_new)
            file = open('EducationalSoftware.tmp', 'r')
            lines = file.readlines()
            file.close()
            file_new = open('EducationalSoftware.tmp', 'w')
            file_new.write(lines[0])
            file_new.write(str(self.variant) + '\n')

            file_new.close()
            for items in self.scene.items():
                try:
                    if str(items.pen().color().red()) == '255':
                        self.scene.removeItem(items)
                except:
                    pass
            for items in self.scene_middle.items():
                try:
                    if str(items.pen().color().red()) == '255':
                        self.scene_middle.removeItem(items)
                except:
                    pass
            pen_rec = QtGui.QPen(QtCore.Qt.red)
            pen_rec.setWidth(4)
            rect_start = QtCore.QRectF(self.margin_left - 1.5,
                                       self.from_absolute_to_relative(self.z_start[str(self.variant)]) - 1.5, 3, 3)
            self.scene.addRect(rect_start, pen_rec)
            pen_rec = QtGui.QPen(QtCore.Qt.red)
            pen_rec.setWidth(4)
            rect_start = QtCore.QRectF(self.margin_left - 1.5,
                                       self.from_absolute_to_relative_middle(self.z_start[str(self.variant)]) - 1.5, 3,
                                       3)
            self.scene_middle.addRect(rect_start, pen_rec)
            self.long_term_head_change_permission = True
            self.result_table.item(1, 0).setText(str(self.z_start[str(self.variant)]))
            self.long_term_head_change_permission = False
            self.station_info = 'Votkinskaya HPP on Kama river. NPU = %s m, UMO = %s m. Начальная отметка = %s m.' % (
                self.z_max, self.z_min, self.z_start[str(self.variant)])
            self.future_rate(self.calculcation_indicator.value())

    # Revert calculation function
    def revert_calculation_longterm(self):
        # print('revert-calculation-started')
        if len(self.result_list) > 0:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Question)
            msg.setWindowTitle("Cancel calculation")
            msg.setText("You really want to cancel result of last calculation?")
            okButton = msg.addButton('Yes', QtWidgets.QMessageBox.AcceptRole)
            msg.addButton('No', QtWidgets.QMessageBox.RejectRole)
            msg.exec()
            if msg.clickedButton() == okButton:
                max = self.calculcation_indicator.maximum()
                if int(self.end_period_tab_2.currentText()) >= (max - 1):
                    if int(self.start_period_tab_2.currentText()) == (max - 1):
                        self.start_period_tab_2.setCurrentIndex(self.start_period_tab_2.currentIndex() - 1)
                    else:
                        pass
                    if self.result_table_tab_2.item(2, 0) is not None and self.result_table_tab_2.item(2,
                                                                                                       0).text() != '':
                        line_revert = 'A-1-1'
                        self.result_table_tab_2.item(2, 0).setText('')
                        for i in range(8):
                            self.result_table_tab_2.item(2, i + 2).setText('')
                        if self.regime_rect_dict_middle.get(line_revert) is not None:
                            try:
                                self.scene_middle.removeItem(self.regime_rect_dict_middle.pop(line_revert))
                                self.scene_middle.removeItem(self.regime_dict_middle.pop(line_revert))
                            except:
                                pass
                    elif self.result_table_tab_2.item(1, 0) is not None and self.result_table_tab_2.item(1,
                                                                                                         0).text() != '':
                        line_revert = 'A-1'
                        self.result_table_tab_2.item(1, 0).setText('')
                        for i in range(8):
                            self.result_table_tab_2.item(1, i + 2).setText('')
                        if self.regime_rect_dict_middle.get(line_revert) is not None:
                            try:
                                self.scene_middle.removeItem(self.regime_rect_dict_middle.pop(line_revert))
                                self.scene_middle.removeItem(self.regime_dict_middle.pop(line_revert))
                            except:
                                pass
                    elif self.result_table_tab_2.item(0, 0) is not None and self.result_table_tab_2.item(0,
                                                                                                         0).text() != '':
                        line_revert = 'A'
                        self.result_table_tab_2.item(0, 0).setText('')
                        for i in range(8):
                            self.result_table_tab_2.item(0, i + 2).setText('')
                        if self.regime_rect_dict_middle.get(line_revert) is not None:
                            try:
                                self.scene_middle.removeItem(self.regime_rect_dict_middle.pop(line_revert))
                                self.scene_middle.removeItem(self.regime_dict_middle.pop(line_revert))
                            except:
                                pass
                    self.start_period_tab_2.removeItem(max - 1)
                self.long_term_head_change_permission = True
                for i in range(3):
                    self.result_table.item(i, max - 1).setText('')
                self.result_list.pop()
                self.calculcation_indicator.setMaximum(max - 1)
                graph = self.regime_rect_list.pop()
                self.scene.removeItem(graph)
                graph = self.regime_list.pop()
                self.scene.removeItem(graph)
                if self.tmp_log_write:
                    file = open('EducationalSoftware.tmp', 'r')
                    data = file.readlines()
                    file.close()
                    data.pop()
                    file_new = open('EducationalSoftware.tmp', 'w')
                    for line in data:
                        file_new.write(line)
                    file_new.close()
                if max - 1 > 1:
                    self.restrictions_info_browser.clear()
                    self.restrictions_info_browser.setText('No errors during calculation')
                    self.calculcation_indicator.setValue(self.calculcation_indicator.minimum())
                    self.insert_mark.insert(self.result_table.item(1, self.calculcation_indicator.minimum()).text())
                    self.draw_regime(self.scene, 'mark')
                else:
                    self.restrictions_info_browser.clear()
                    self.restrictions_info_browser.setFontWeight(400)
                    self.restrictions_info_browser.setText('No errors during calculation')

    # Revert write to file function
    def cancel_write_down(self):
        if self.action_settings_write_in_file.isChecked():
            self.tmp_log_write = True
            tmp_file = open('EducationalSoftware.tmp', 'w')
            tmp_file.write(str(self.tmp_log_write) + '\n')
            tmp_file.write(str(self.variant) + '\n')
            tmp_file.close()
        else:
            self.tmp_log_write = False
            tmp_file = open('EducationalSoftware.tmp', 'w')
            tmp_file.write(str(self.tmp_log_write) + '\n')
            tmp_file.write(str(self.variant) + '\n')
            tmp_file.close()

    # Write to file
    def tmp_log_write_down(self):
        try:
            tmp_file = open('EducationalSoftware.tmp', 'r')
            info = tmp_file.read().splitlines()
            self.change_of_variant(info[1])
            if info[0] == 'True' and len(info[2]) > 0:
                self.action_settings_write_in_file.setChecked(True)
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Question)
                msg.setWindowTitle("Restore data")
                msg.setText("You really want to restore data?")
                okButton = msg.addButton('Yes', QtWidgets.QMessageBox.AcceptRole)
                msg.addButton('No', QtWidgets.QMessageBox.RejectRole)
                msg.exec()
                if msg.clickedButton() == okButton:
                    for i in range(len(info) - 2):
                        self.insert_rate.insert(str(info[i + 2]))
                        self.draw_regime(self.scene, 'rate')
                    tmp_file.close()
                else:
                    tmp_file.close()
                    file_new = open('EducationalSoftware.tmp', 'w')
                    file_new.write(info[0] + '\n')
                    file_new.write(info[1] + '\n')
                    file_new.close()
        except:
            tmp_file = open('EducationalSoftware.tmp', 'w')
            self.action_settings_write_in_file.setChecked(True)
            tmp_file.write(str(self.tmp_log_write) + '\n')
            tmp_file.write(str(self.variant) + '\n')
            tmp_file.close()

    # Resize window size
    def change_size_function(self):
        prog_width = 1024
        prog_height = 800
        delta_width = prog_width - self.width()
        delta_height = prog_height - self.height()
        self.tab_widget.setGeometry(QtCore.QRect(10, 25, 1010 - delta_width, 750 - delta_height))
        self.graphics_view.setGeometry(QtCore.QRect(10, 170, (990 - delta_width), (400 - delta_height)))
        self.result_table.setGeometry(QtCore.QRect(10, 600 - delta_height, 990 - delta_width, 120))
        self.restrictions_info_browser.setGeometry(QtCore.QRect(10, 80, 620 - delta_width, 60))
        self.line.setGeometry(QtCore.QRect(10, 65, 620 - delta_width, 16))
        self.station_info_browser.setGeometry(QtCore.QRect(10, 15, 620 - delta_width, 50))
        self.group_box_station_info_and_restr.setGeometry(QtCore.QRect(10, 10, 640 - delta_width, 150))
        self.group_box.setGeometry(QtCore.QRect(660 - delta_width, 10, 340, 150))
        self.label_table.setGeometry(QtCore.QRect(10, 575 - delta_height, 500, 20))
        # Среднесрочный
        if delta_width > 0:
            self.graphics_view_tab2.setGeometry(QtCore.QRect(10, 10, 520 - delta_width / 2, 400))
            self.group_box_station_info_and_restr_tab_2.setGeometry(QtCore.QRect(540 - delta_width / 2, 135, 450, 150))
            self.group_box_line_tab_2.setGeometry(QtCore.QRect(540 - delta_width / 2, 10, 450, 120))
            self.group_box_tab_2.setGeometry(QtCore.QRect(540 - delta_width / 2, 290, 450, 120))
        else:
            self.graphics_view_tab2.setGeometry(QtCore.QRect(10, 10, 520 - delta_width, 400))
            self.group_box_station_info_and_restr_tab_2.setGeometry(QtCore.QRect(540 - delta_width, 135, 450, 150))
            self.group_box_line_tab_2.setGeometry(QtCore.QRect(540 - delta_width, 10, 450, 120))
            self.group_box_tab_2.setGeometry(QtCore.QRect(540 - delta_width, 290, 450, 120))
        if delta_height < 0:
            self.result_table_tab_2.setGeometry(QtCore.QRect(10, 430, 960, 280 - delta_height))
        elif delta_height >= 0:
            self.result_table_tab_2.setGeometry(QtCore.QRect(10, 430, 960, 280 - delta_height))

        self.deltaX = (self.graphics_view.width() - self.margin_right) / int(self.number_of_RP)  # Расстояние по X
        if self.deltaX <= 45.476190476190474:
            self.deltaX = 45.476190476190474
        var = 0
        if delta_width < 0 and delta_height >= 0:
            var = 1
        elif delta_width >= 0 and delta_height >= 0:
            var = 2
        elif delta_width >= 0 and delta_height < 0:
            var = 3
        elif delta_width < 0 and delta_height < 0:
            var = 4
        if var == 1 or var == 2:
            self.graph_height_px = 320
        elif var == 3 or var == 4:
            self.graph_height_px = self.graphics_view.height() - 80
        self.scene.clear()
        self.draw_coordinate_net(self.scene, self.number_of_RP, self.graphics_view)
        self.draw_dispatch_graph(self.scene, self.number_of_RP, self.graphics_view)
        self.add_zones(self.scene, self.number_of_RP, self.graphics_view)
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        try:
            if self.result_table.item(1, 1).text():
                self.regime_list = []
                self.regime_rect_list = []
                self.calculcation_indicator.setValue(1)
                self.insert_mark.clear()
                self.insert_mark.insert(self.result_table.item(1, 1).text())
                self.draw_regime(self.scene, 'mark')
        except:
            pass

    # Remember head to restore it if necessary
    def current_head(self, current):
        try:
            current.row()
            if current.row() == 2:
                self.long_term_head_item = current.text()
        except:
            pass

    # Rewrite table when combobox change
    def combo_box_change(self):
        for i in range(3):
            for j in range(10):
                if j == 1:
                    pass
                else:
                    try:
                        item = self.result_table_tab_2.item(i, j)
                        item.setText('')
                    except:
                        pass
        if int(self.start_period_tab_2.currentText()) < len(self.result_list):
            if (len(self.result_list) - int(self.start_period_tab_2.currentText())) > 3:
                range_middle = 3
            else:
                range_middle = (len(self.result_list) - int(self.start_period_tab_2.currentText()))
            for k in range(range_middle):
                item = QtWidgets.QTableWidgetItem(str(int(self.start_period_tab_2.currentText()) + k + 1))
                self.result_table_tab_2.setItem(k, 0, item)
                for l in range(len(self.result_list[0])):
                    item = QtWidgets.QTableWidgetItem(
                        str(self.result_list[int(self.start_period_tab_2.currentText()) + k][l]))
                    self.result_table_tab_2.setItem(k, 2 + l, item)
            for i in range(self.choose_line_tab_2.count() - 1):
                self.choose_line_tab_2.removeItem(1)
            if range_middle == 3 or range_middle == 2:
                self.choose_line_tab_2.addItems(['A-1', 'A-1-1', 'A-1-2', 'A-1-3', 'A-2', 'A-3', 'B', 'C'])
            elif range_middle == 1:
                self.choose_line_tab_2.addItems(['A-1', 'A-2', 'A-3', 'B', 'C'])
            else:
                self.choose_line_tab_2.addItems(['B', 'C'])

    # Function for trace about change in table for longterm
    def item_changed(self, item):
        if item.row() == 2 and (self.long_term_head_change_permission is False):
            QtWidgets.QMessageBox.warning(self, "Error", "Change of HPP's head is prohibited!")
            head_item = QtWidgets.QTableWidgetItem(self.long_term_head_item)
            self.long_term_head_change_permission = True
            self.result_table.setItem(2, item.column(), head_item)
            self.long_term_head_change_permission = False
        elif item.column() == 0 and (self.long_term_head_change_permission is False):
            QtWidgets.QMessageBox.information(self, "Error", "You can't change initial data!")
            head_item = QtWidgets.QTableWidgetItem('-')
            self.long_term_head_change_permission = True
            self.result_table.setItem(2, 0, head_item)
            head_item = QtWidgets.QTableWidgetItem('-')
            self.result_table.setItem(0, 0, head_item)
            item_start = QtWidgets.QTableWidgetItem(str(self.z_start[str(self.variant)]))
            self.result_table.setItem(1, 0, item_start)
            self.long_term_head_change_permission = False

    # Activate calculation when change table value
    def activated_from_table(self, row, column):
        if self.result_table.item(row, column) is None or self.result_table.item(row, column).text() == '':
            QtWidgets.QMessageBox.warning(self, "Error", "No data input!")
        else:
            if row == 1:

                try:
                    mark = float(self.result_table.item(row, column).text())
                except ValueError:
                    QtWidgets.QMessageBox.information(self, "Error",
                                                      "Float values must be separated by point!/Wrong input format!")
                    return 'Error'
                self.insert_mark.clear()
                self.insert_mark.insert(str(mark))
                self.draw_regime(self.scene, 'mark')
                self.result_table.setCurrentCell(row, column + 1)
            if row == 0:
                try:
                    rate = int(self.result_table.item(row, column).text())
                except ValueError:
                    QtWidgets.QMessageBox.information(self, "Error",
                                                      "Float values must be separated by point!/Wrong input format!")
                    return 'Ass'
                self.insert_rate.clear()
                self.insert_rate.insert(str(rate))
                self.draw_regime(self.scene, 'rate')
                self.result_table.setCurrentCell(row, column + 1)

    def entered(self, row, col):
        if self.calculcation_indicator.maximum() >= (col):
            self.calculcation_indicator.setValue(col)

    # Draw coordinate net and prepare for draw dispatch graph.
    def draw_coordinate_net(self, scene, number_of_RP, view):
        pen = QtGui.QPen(QtCore.Qt.gray)  # Назначаем перо
        graph_width_px = view.width() - self.margin_right
        deltaX = int(graph_width_px) / int(number_of_RP)
        deltaY = int(self.graph_height_px) / 10
        if deltaX <= 45.476190476190474 or deltaY < 32:
            deltaX = 45.476190476190474
        deltaZ = (self.z_max - self.z_min) / 10
        # Draw lines parallel Y
        if view.width() == 520:  # 520 - width of view in middleterm
            for i in range(4):
                r = QtCore.QLineF((self.margin_left + i * deltaX), self.margin_top, (self.margin_left + i * deltaX),
                                  self.graph_height_px + self.margin_top)
                scene.addLine(r, pen)
                # Signature for CP
                item_for_RP = scene.addText(str(int(self.start_period_tab_2.currentText()) + i))
                item_for_RP.setPos((self.margin_left + i * deltaX) - 8, self.graph_height_px + self.margin_top + 1)

            start_period = int(self.start_period_tab_2.currentText())
            try:
                z_ = self.result_table.item(1, start_period).text()
                pen_rec = QtGui.QPen(QtCore.Qt.red)
                pen_rec.setWidth(4)
                if scene == self.scene:
                    rect_start = QtCore.QRectF(self.margin_left - 1.5, self.from_absolute_to_relative(z_) - 1.5, 3, 3)
                    self.rect_start_name = scene.addRect(rect_start, pen_rec)
                else:
                    rect_start = QtCore.QRectF(self.margin_left - 1.5, self.from_absolute_to_relative_middle(z_) - 1.5,
                                               3, 3)
                    self.rect_start_name = scene.addRect(rect_start, pen_rec)
            except:
                pen_rec = QtGui.QPen(QtCore.Qt.red)
                pen_rec.setWidth(4)
                if scene == self.scene:
                    rect_start = QtCore.QRectF(self.margin_left - 1.5,
                                               self.from_absolute_to_relative(self.z_start[str(self.variant)]) - 1.5,
                                               3, 3)
                    self.rect_start_name = scene.addRect(rect_start, pen_rec)
                else:
                    rect_start = QtCore.QRectF(self.margin_left - 1.5,
                                               self.from_absolute_to_relative_middle(
                                                   self.z_start[str(self.variant)]) - 1.5, 3, 3)
                    self.rect_start_name = scene.addRect(rect_start, pen_rec)

        else:
            for i in range(number_of_RP):
                r = QtCore.QLineF((self.margin_left + i * deltaX), self.margin_top, (self.margin_left + i * deltaX),
                                  self.graph_height_px + self.margin_top)
                scene.addLine(r, pen)
                # Signature for CP
                item_for_RP = scene.addText(str(i))
                item_for_RP.setPos((self.margin_left + i * deltaX) - 8, self.graph_height_px + self.margin_top + 1)
            pen_rec = QtGui.QPen(QtCore.Qt.red)
            pen_rec.setWidth(4)
            rect_start = QtCore.QRectF(self.margin_left - 1.5,
                                       self.from_absolute_to_relative(self.z_start[str(self.variant)]) - 1.5, 3, 3)
            scene.addRect(rect_start, pen_rec)

        # Draw lines parallel X
        for i in range(11):
            if i == 10 or i == 0:
                pen.setWidth(2)
            else:
                pen.setWidth(1)
            r = QtCore.QLineF(self.margin_left, (self.margin_top + i * deltaY), deltaX * (number_of_RP - 1),
                              (self.margin_top + i * deltaY))

            scene.addLine(r, pen)
            mark = scene.addText(str(self.z_max - deltaZ * i))
            mark.setPos(-35, (self.margin_top + i * deltaY) - 10)
        mark_txt = scene.addText('Zub, м')
        mark_txt.setPos(-25, -15)

        text_rp = QtWidgets.QGraphicsSimpleTextItem()
        text_rp.setText('Calculation period')
        a = scene.addText(text_rp.text())
        a.setPos(graph_width_px / 2.5, self.graph_height_px + self.margin_top + 25)
        text_head = QtWidgets.QGraphicsSimpleTextItem()
        text_head.setText('Dispatch graph')
        a = scene.addText(text_head.text())
        a.setPos(graph_width_px / 2.5, - self.margin_top + 5)

    # Draw dispatch graph
    def draw_dispatch_graph(self, scene, number_of_RP, view):
        pen_graph = QtGui.QPen(QtCore.Qt.blue)
        graph = self.dispatch_graph()
        graph_width_px = view.width() - self.margin_right
        deltaX = int(graph_width_px) / int(number_of_RP)  # Расстояние по X между прямыми
        if deltaX < 45.47:
            deltaX = 45.476190476190474
        for i in range(len(graph)):
            line_name = 'Line %s' % (str(i + 1))
            line = graph[line_name]
            if view.width() == 520:
                for j in range(number_of_RP - 1):
                    if scene == self.scene:
                        r = QtCore.QLineF((self.margin_left + j * deltaX), self.from_absolute_to_relative(
                            line[int(self.start_period_tab_2.currentText()) + j]),
                                          (self.margin_left + (j + 1) * deltaX), self.from_absolute_to_relative(
                                line[int(self.start_period_tab_2.currentText()) + j + 1]))
                        scene.addLine(r, pen_graph)
                    else:
                        r = QtCore.QLineF((self.margin_left + j * deltaX), self.from_absolute_to_relative_middle(
                            line[int(self.start_period_tab_2.currentText()) + j]),
                                          (self.margin_left + (j + 1) * deltaX), self.from_absolute_to_relative_middle(
                                line[int(self.start_period_tab_2.currentText()) + j + 1]))
                        scene.addLine(r, pen_graph)
            else:
                if scene == self.scene:
                    for j in range(number_of_RP - 1):
                        r = QtCore.QLineF((self.margin_left + j * deltaX), self.from_absolute_to_relative(line[j]),
                                          (self.margin_left + (j + 1) * deltaX),
                                          self.from_absolute_to_relative(line[j + 1]))
                        scene.addLine(r, pen_graph)
                else:
                    for j in range(number_of_RP - 1):
                        r = QtCore.QLineF((self.margin_left + j * deltaX),
                                          self.from_absolute_to_relative_middle(line[j]),
                                          (self.margin_left + (j + 1) * deltaX),
                                          self.from_absolute_to_relative_middle(line[j + 1]))
                        scene.addLine(r, pen_graph)

    # Function for draw regime HPP in middleterm when change of start period
    def middle_additional_regime(self):
        max = self.calculcation_indicator.maximum()
        count = 0
        delta = max - int(self.start_period_tab_2.currentText())
        if delta >= 3:
            count = 3
        elif delta == 2:
            count = 2
        elif delta <= 1:
            count = 0
        for i in range(0, delta):
            if self.result_table.item(1, int(self.start_period_tab_2.currentText()) + i + 1) is not None:
                if str(self.result_table.item(1, int(self.start_period_tab_2.currentText()) + i + 1).text()) != '':
                    self.draw_regime_middle_from_longterm(
                        start_period=(int(self.start_period_tab_2.currentText()) + i + 1),
                        start_mark=float(
                            self.result_table.item(1, int(self.start_period_tab_2.currentText()) + i).text()),
                        end_mark=float(
                            self.result_table.item(1, int(self.start_period_tab_2.currentText()) + 1 + i).text()))
    #  Print info about future rates and periods
    def future_rate(self, number_of_RP):
        self.station_info_browser.clear()
        text = '<span style="font-weight: 400">%s</span>' % (self.station_info)
        self.station_info_browser.setHtml(text)
        if ((self.number_of_RP) - number_of_RP) >= 3:
            rp = 'Current calculation period: %s, future rates:' % (number_of_RP)
            self.station_info_browser.append(rp)
            rate = '<p style="font-weight:400">Q<sub>%s</sub> = %s m<sup>3</sup>/s; Q<sub>%s</sub> = %s m<sup>3</sup>/s; Q<sub>%s</sub> = %s m<sup>3</sup>/s;</p>' % (
                number_of_RP, self.q_pritok[str(self.variant)][number_of_RP - 1] + self.losses[str(self.variant)][number_of_RP - 1], number_of_RP + 1,
                self.q_pritok[str(self.variant)][number_of_RP] + self.losses[str(self.variant)][number_of_RP],
                number_of_RP + 2, self.q_pritok[str(self.variant)][number_of_RP + 1] + self.losses[str(self.variant)][number_of_RP + 1])
            self.station_info_browser.append(rate)
        elif ((self.number_of_RP) - number_of_RP) == 2:
            rp = 'Current calculation period: %s, future rates:' % (number_of_RP)
            self.station_info_browser.append(rp)
            rate = '<p style="font-weight:400">Q<sub>%s</sub> = %s m<sup>3</sup>/s; Q<sub>%s</sub> = %s m<sup>3</sup>/s;</p>' % (
                number_of_RP, self.q_pritok[str(self.variant)][number_of_RP - 1] + self.losses[str(self.variant)][number_of_RP - 1], number_of_RP + 1,
                self.q_pritok[str(self.variant)][number_of_RP] + self.losses[str(self.variant)][number_of_RP])
            self.station_info_browser.append(rate)
        elif ((self.number_of_RP) - number_of_RP) == 1 or ((self.number_of_RP - 1) - number_of_RP) == 0:
            rp = 'Current calculation period: %s, future rate:' % (number_of_RP)
            self.station_info_browser.append(rp)
            rate = '<p style="font-weight:400">Q<sub>%s</sub> = %s m<sup>3</sup>/s;</p>' % (
                number_of_RP, self.q_pritok[str(self.variant)][number_of_RP - 1] + self.losses[str(self.variant)][number_of_RP - 1])
            self.station_info_browser.append(rate)

    # Info about rates for middleterm
    def middle_rate(self, number_of_RP):
        self.station_info_browser_tab_2.clear()
        rp = 'Future rates:'
        self.station_info_browser_tab_2.append(rp)
        rate = '<p style="font-weight:400">Q<sub>%s</sub> = %s m<sup>3</sup>/s; Q<sub>%s</sub> = %s m<sup>3</sup>/s; Q<sub>%s</sub> = %s m<sup>3</sup>/s;</p>' % (
            number_of_RP, self.q_pritok[str(self.variant)][number_of_RP - 1], number_of_RP + 1,
            self.q_pritok[str(self.variant)][number_of_RP],
            number_of_RP + 2, self.q_pritok[str(self.variant)][number_of_RP + 1])
        self.station_info_browser_tab_2.append(rate)

    def edit(self, index, trigger, event):
        self.editIndex = index
        return super().edit(index, trigger, event)

    def draw_regime(self, scene, iniciator):
        type_count = ''
        start_period = self.calculcation_indicator.value()
        start_mark = float(self.result_table.item(1, int(start_period) - 1).text())
        q_pritok = self.q_pritok[str(self.variant)][int(start_period) - 1] + self.losses[str(self.variant)][int(start_period) - 1]
        time = self.t_days[int(start_period) - 1] * 86400
        if iniciator == 'button':
            end_mark = self.insert_mark.displayText()
            q_hpp = self.insert_mark.displayText()
            if end_mark:
                type_count = 'straight'
            else:
                type_count = 'reverse'
        elif iniciator == 'mark':
            type_count = 'straight'
        elif iniciator == 'rate':
            type_count = 'reverse'
        if type_count == 'straight':
            try:
                float(self.insert_mark.displayText())
            except ValueError:
                QtWidgets.QMessageBox.information(self, "Error",
                                                  "Float values must be separated by point!/Wrong input format!")
                return 'Error'
            if (float(self.insert_mark.displayText()) > 89) or (float(self.insert_mark.displayText()) < 82):
                QtWidgets.QMessageBox.information(self, "Error",
                                                  "Mark is out of approved range!")
                return 'TooBig'
            end_mark = self.insert_mark.displayText()
            volume_start = self.connection_curve_vb('Z', mark=float(start_mark))
            volume_end = self.connection_curve_vb('Z', mark=float(end_mark))
            delta_w = volume_end - volume_start
            q_reservior = (delta_w * (10 ** 6)) / (time)
            q_hpp = q_pritok - q_reservior
            z_middle = (float(start_mark) + float(end_mark)) / 2
            z_lower_bief = self.connection_curve_nb('Q', rate=(q_hpp + 10))
            head = z_middle - z_lower_bief - self.dh
            power = (9.81 * q_hpp * head * self.get_efficiency(head)) / 1000
            production = (power * (time / (60 * 60))) / (10 ** 3)
            if (float(q_hpp) > 25000) or (float(q_hpp) < 250):
                QtWidgets.QMessageBox.information(self, "Error", "Rate is out of approved range!")
                return 'Error'
        else:
            try:
                int(self.insert_rate.displayText())
            except ValueError:
                QtWidgets.QMessageBox.information(self, "Error",
                                                  "Float values must be separated by point!/Wrong input format!")
                return 'Error'
            if (float(self.insert_rate.displayText()) > 25000) or (float(self.insert_rate.displayText()) < 250):
                QtWidgets.QMessageBox.information(self, "Error", "Rate is out of approved range!")
                return 'Error'
            q_hpp = int(self.insert_rate.displayText())
            volume_start = self.connection_curve_vb('Z', mark=float(start_mark))
            q_reservior = q_pritok - q_hpp
            delta_w = (q_reservior * time) / (10 ** 6)
            volume_end = delta_w + volume_start
            end_mark = self.connection_curve_vb('V', volume=int(volume_end))
            z_middle = (float(start_mark) + float(end_mark)) / 2
            z_lower_bief = self.connection_curve_nb('Q', rate=(q_hpp + 10))
            head = z_middle - z_lower_bief - self.dh
            power = (9.81 * q_hpp * head * self.get_efficiency(head)) / 1000
            production = (power * (time / (60 * 60))) / (10 ** 3)
            if (float(end_mark) > 89) or (float(end_mark) < 82):
                QtWidgets.QMessageBox.information(self, "Error", "Mark is out of approved range!")
                return 'Error'
        period_result = [q_pritok, start_mark]

        if type_count == 'straight':
            end_mark_formatted = float(end_mark)
        else:
            end_mark_formatted = float("{0:.2f}".format(end_mark))

        period_result.append(end_mark_formatted)
        z_lower_bief_formatted = float("{0:.2f}".format(z_lower_bief))

        period_result.append(z_lower_bief_formatted)
        head_formatted = float("{0:.2f}".format(head))
        period_result.append(head_formatted)
        q_hpp_formatted = float("{0:.2f}".format(q_hpp))
        period_result.append(q_hpp_formatted)
        power_formatted = float("{0:.2f}".format(power))
        period_result.append(power_formatted)
        production_formatted = float("{0:.2f}".format(production))
        period_result.append(production_formatted)
        if self.tmp_log_write:  # Write in tmp-file
            file = open('EducationalSoftware.tmp', 'r')
            data = file.readlines()
            file.close()
            if len(data) - 2 >= start_period:
                data[start_period + 1] = str(int(q_hpp_formatted)) + '\n'
            else:
                data.append(str(int(q_hpp_formatted)) + '\n')
            file_new = open('EducationalSoftware.tmp', 'w')
            for line in data:
                file_new.write(line)
            file_new.close()

        if len(self.result_list) <= (start_period - 1):
            self.result_list.append(period_result)
        else:
            self.result_list[start_period - 1] = period_result

        line_start = self.dispatch_graph_intersect(float(start_mark), start_period - 1)
        line_end = self.dispatch_graph_intersect(float(end_mark), start_period)
        error_graph_intersect = True  # Intersect with dispatch graph
        for elem in line_start:
            if elem in line_end:
                error_graph_intersect = False
                break

        rates = self.dispatch_graph_rates(line=line_end, period=start_period)
        error_in_graph_rates = False
        if (int(q_hpp) >= rates[0]) and (int(q_hpp) <= rates[1]):
            pass
        else:
            error_in_graph_rates = True
        if self.restrictions_info_browser.toPlainText() == 'No errors during calculation':
            pass
        else:
            errors_in_calc_text = self.restrictions_info_browser.toPlainText().split('\n')
            self.restrictions_info_browser.clear()
            self.restrictions_info_browser.setFontWeight(400)
            what_to_find = 'in %s' % (start_period)
            for j in range(len(errors_in_calc_text)):
                if errors_in_calc_text[j].find(what_to_find) >= 0:
                    pass
                else:
                    self.restrictions_info_browser.append(errors_in_calc_text[j])
            if len(self.restrictions_info_browser.toPlainText()) == 0:
                self.restrictions_info_browser.setText('No errors during calculation')

        if error_in_graph_rates:
            if self.restrictions_info_browser.toPlainText() == 'No errors during calculation':
                self.restrictions_info_browser.setFontWeight(400)
                self.restrictions_info_browser.setText(
                    'Rate disparity of dispatch zone in %s calculation period' % (start_period))
            else:
                self.restrictions_info_browser.setFontWeight(400)
                self.restrictions_info_browser.append(
                    'Rate disparity of dispatch zone in %s calculation period' % (start_period))

        if error_graph_intersect:
            if self.restrictions_info_browser.toPlainText() == 'No errors during calculation':
                self.restrictions_info_browser.setFontWeight(400)
                self.restrictions_info_browser.setText(
                    'Intersection of dispatch graph in %s calculation period' % (start_period))
            else:
                self.restrictions_info_browser.setFontWeight(400)
                self.restrictions_info_browser.append(
                    'Intersection of dispatch graph in %s calculation period' % (start_period))

        # Check on restrictions
        err_restr = []
        for restr in self.restrictions:
            if restr[6]:
                if (restr[2] <= start_period) and (restr[3] >= start_period):
                    if restr[1] == 'Z':
                        if restr[5] == '<=':
                            restr_mark = (float(end_mark) <= restr[4])
                            if restr_mark == False:
                                err_restr.append(restr[0])
                        elif restr[5] == '>=':
                            restr_mark = (float(end_mark) >= restr[4])
                            if restr_mark == False:
                                err_restr.append(restr[0])
                        elif restr[5] == '=':
                            restr_mark = (float(end_mark) == restr[4])
                            if restr_mark == False:
                                err_restr.append(restr[0])
                    elif restr[1] == 'Q':
                        if restr[5] == '<=':
                            restr_mark = (int(q_hpp) <= restr[4])
                            if restr_mark == False:
                                err_restr.append(restr[0])
                        elif restr[5] == '>=':
                            restr_mark = (int(q_hpp) >= restr[4])
                            if restr_mark == False:
                                err_restr.append(restr[0])
                        elif restr[5] == '=':
                            restr_mark = (int(q_hpp) == restr[4])
                            if restr_mark == False:
                                err_restr.append(restr[0])
                    elif restr[1] == 'H':
                        if restr[5] == '<=':
                            restr_mark = (float(head) <= restr[4])
                            if restr_mark == False:
                                err_restr.append(restr[0])
                        elif restr[5] == '>=':
                            restr_mark = (float(head) >= restr[4])
                            if restr_mark == False:
                                err_restr.append(restr[0])
                        elif restr[5] == '=':
                            restr_mark = (float(head) == restr[4])
                            if restr_mark == False:
                                err_restr.append(restr[0])

        if len(err_restr) > 0:
            for i in err_restr:
                if self.restrictions_info_browser.toPlainText() == 'No errors during calculation':
                    self.restrictions_info_browser.setFontWeight(400)
                    self.restrictions_info_browser.setText(
                        'Noncompliance with restriction: %s in %s calculation period' % (i, start_period))
                else:
                    self.restrictions_info_browser.setFontWeight(400)
                    self.restrictions_info_browser.append(
                        'Noncompliance with restriction: %s in %s calculation period' % (i, start_period))
            self.restrictions_info_browser.toPlainText()

        # Draw regime
        pen_1 = QtGui.QPen(QtCore.Qt.red)
        pen_1.setWidth(3)
        r = QtCore.QLineF((int(start_period) * self.deltaX - self.deltaX), self.from_absolute_to_relative(start_mark),
                          ((int(start_period) + 1) * self.deltaX - self.deltaX),
                          self.from_absolute_to_relative(end_mark))
        line = scene.addLine(r, pen_1)
        pen_rec = QtGui.QPen(QtCore.Qt.red)
        pen_rec.setWidth(4)
        rect_start = QtCore.QRectF(((int(start_period) + 1) * self.deltaX - self.deltaX) - 1.5,
                                   self.from_absolute_to_relative(end_mark) - 1.5, 3, 3)
        rect = scene.addRect(rect_start, pen_rec)
        change = False
        if (self.result_table.item(0, self.calculcation_indicator.value()) is not None) and (
                self.result_table.item(1, self.calculcation_indicator.value()) is not None):
            change = True
            if len(self.regime_list) < self.calculcation_indicator.value():
                self.regime_list.append(line)
                self.regime_rect_list.append(rect)
            else:
                item = self.result_table.item(1, self.calculcation_indicator.value()).text()  # Get old mark
                try:
                    scene.removeItem(self.regime_list[self.calculcation_indicator.value() - 1])  # Delete old mark
                    self.regime_list[self.calculcation_indicator.value() - 1] = line
                except:
                    pass
                try:
                    scene.removeItem(
                        self.regime_rect_list[self.calculcation_indicator.value() - 1])  # Delete rectangle
                    self.regime_rect_list[self.calculcation_indicator.value() - 1] = rect
                except:
                    pass
        else:
            self.regime_list.append(line)
            self.regime_rect_list.append(rect)
        self.draw_regime_middle_from_longterm(start_period=start_period, start_mark=start_mark, end_mark=end_mark,
                                              change=change)
        # Table
        self.long_term_head_change_permission = True
        if type_count == 'straight':
            item = QtWidgets.QTableWidgetItem(str(float((end_mark))))
        else:
            item = QtWidgets.QTableWidgetItem(str(float("{0:.2f}".format(end_mark))))
        self.result_table.setItem(1, int(start_period), item)
        item_q_hpp = QtWidgets.QTableWidgetItem(str(int(q_hpp)))
        self.result_table.setItem(0, int(start_period), item_q_hpp)
        item_head = QtWidgets.QTableWidgetItem(str(float("{0:.2f}".format(head))))
        self.result_table.setItem(2, int(start_period), item_head)
        self.result_table.resizeColumnsToContents()
        if (int(self.end_period_tab_2.currentText())) >= start_period:
            item_rp = QtWidgets.QTableWidgetItem(str(start_period))
            self.result_table_tab_2.setItem(start_period - 1 - int(self.start_period_tab_2.currentText()), 0, item_rp)
            item_q_pritok = QtWidgets.QTableWidgetItem(str(int(self.result_list[start_period - 1][0])))
            self.result_table_tab_2.setItem(start_period - 1 - int(self.start_period_tab_2.currentText()), 2,
                                            item_q_pritok)
            item_z_start = QtWidgets.QTableWidgetItem(str(float(self.result_list[start_period - 1][1])))
            self.result_table_tab_2.setItem(start_period - 1 - int(self.start_period_tab_2.currentText()), 3,
                                            item_z_start)
            if type_count == 'straight':
                item_z_end = QtWidgets.QTableWidgetItem(str(float((self.result_list[start_period - 1][2]))))
            else:
                item_z_end = QtWidgets.QTableWidgetItem(
                    str(float("{0:.2f}".format(self.result_list[start_period - 1][2]))))
            self.result_table_tab_2.setItem(start_period - 1 - int(self.start_period_tab_2.currentText()), 4,
                                            item_z_end)
            item_z_lower_bief = QtWidgets.QTableWidgetItem(
                str(float("{0:.2f}".format(self.result_list[start_period - 1][3]))))
            self.result_table_tab_2.setItem(start_period - 1 - int(self.start_period_tab_2.currentText()), 5,
                                            item_z_lower_bief)
            item_head = QtWidgets.QTableWidgetItem(str(float("{0:.2f}".format(self.result_list[start_period - 1][4]))))
            self.result_table_tab_2.setItem(start_period - 1 - int(self.start_period_tab_2.currentText()), 6,
                                            item_head)
            item_q_hpp = QtWidgets.QTableWidgetItem(str(int(self.result_list[start_period - 1][5])))
            self.result_table_tab_2.setItem(start_period - 1 - int(self.start_period_tab_2.currentText()), 7,
                                            item_q_hpp)
            item_power = QtWidgets.QTableWidgetItem(str(float("{0:.2f}".format(self.result_list[start_period - 1][6]))))
            self.result_table_tab_2.setItem(start_period - 1 - int(self.start_period_tab_2.currentText()), 8,
                                            item_power)
            item_production = QtWidgets.QTableWidgetItem(
                str(float("{0:.2f}".format(self.result_list[start_period - 1][7]))))
            self.result_table_tab_2.setItem(start_period - 1 - int(self.start_period_tab_2.currentText()), 9,
                                            item_production)
            self.editIndex = QModelIndex()
            self.result_table_tab_2.resizeColumnsToContents()

        self.long_term_head_change_permission = False
        tmp = int(self.calculcation_indicator.text())
        self.calculcation_indicator.setMaximum(tmp + 1)
        if self.start_period_tab_2.count() <= (
        int(self.calculcation_indicator.text())) and self.start_period_tab_2.count() <= 17:
            self.start_period_tab_2.addItem(str(int(self.calculcation_indicator.text())))
        per_old = int(self.calculcation_indicator.text())
        per_new = per_old + 1
        self.calculcation_indicator.cleanText()
        self.calculcation_indicator.setValue(per_new)
        self.insert_rate.clear()
        self.insert_mark.clear()
        self.editIndex = QModelIndex()
        self.future_rate(self.calculcation_indicator.value())
        if (self.result_table.item(1, self.calculcation_indicator.value()) is not None) and change and len(
                self.result_table.item(1, self.calculcation_indicator.value()).text()) >= 1:
            mark = float(self.result_table.item(1, self.calculcation_indicator.value()).text())
            self.insert_mark.clear()
            self.insert_mark.insert(str(mark))
            self.draw_regime(self.scene, 'mark')

    # Draw middleterm regime
    def draw_regime_middle(self, scene, iniciator):
        self.middle_term_calculation = True
        type_count = ''
        start_period = 0
        start_mark = 0
        length_line_name = len(self.choose_line_tab_2.currentText())
        if length_line_name == 1:
            start_period = int(self.start_period_tab_2.currentText()) + 1
            start_mark = float(self.result_table.item(1, int(start_period) - 1).text())
        elif length_line_name == 3:
            start_period = int(self.start_period_tab_2.currentText()) + 2
            start_mark = float(
                self.result_table_tab_2.item(
                    self.middle_line_index[self.choose_line_tab_2.currentText()[0]],
                    4).text())
        elif length_line_name == 5:
            start_period = int(self.start_period_tab_2.currentText()) + 3

            start_mark = float(
                self.result_table_tab_2.item(
                    self.middle_line_index[self.choose_line_tab_2.currentText()[0:3]],
                    4).text())
        q_pritok = self.q_pritok[str(self.variant)][int(start_period) - 1] + self.losses[str(self.variant)][int(start_period) - 1]
        time = self.t_days[int(start_period) - 1] * 86400
        if iniciator == 'button':
            end_mark = self.insert_mark_tab_2.displayText()
            q_hpp = self.insert_rate_tab_2.displayText()
            if end_mark:
                type_count = 'straight'
            else:
                type_count = 'reverse'
        elif iniciator == 'mark':
            type_count = 'straight'
        elif iniciator == 'rate':
            type_count = 'reverse'
        if type_count == 'straight':
            try:
                float(self.insert_mark_tab_2.displayText())
            except ValueError:
                QtWidgets.QMessageBox.information(self, "Error",
                                                  "Float values must be separated by point!/Wrong input format!")
                return 'Error'
            if (float(self.insert_mark_tab_2.displayText()) > 92.0) or (
                    float(self.insert_mark_tab_2.displayText()) < 82.0):
                QtWidgets.QMessageBox.information(self, "Error", "Mark is out of approved range!")
                return 'TooBig'

            end_mark = self.insert_mark_tab_2.displayText()
            volume_start = self.connection_curve_vb('Z', mark=float(start_mark))
            volume_end = self.connection_curve_vb('Z', mark=float(end_mark))
            delta_w = volume_end - volume_start
            q_reservior = (delta_w * (10 ** 6)) / (time)
            q_hpp = q_pritok - q_reservior
            z_middle = (float(start_mark) + float(end_mark)) / 2
            z_lower_bief = self.connection_curve_nb('Q', rate=(q_hpp + 10))
            head = z_middle - z_lower_bief - self.dh
            power = (9.81 * q_hpp * head * self.get_efficiency(head)) / 1000
            production = (power * (time / (60 * 60))) / (10 ** 3)
        else:
            try:
                int(self.insert_rate_tab_2.displayText())
            except ValueError:
                QtWidgets.QMessageBox.information(self, "Error",
                                                  "Float values must be separated by point!/Wrong input format!")
                return 'Error'
            if (float(self.insert_rate_tab_2.displayText()) > 25000) or (
                    float(self.insert_rate_tab_2.displayText()) < 250):
                QtWidgets.QMessageBox.information(self, "Error", "Rate is out of approved range!")
            q_hpp = int(self.insert_rate_tab_2.displayText())
            volume_start = self.connection_curve_vb('Z', mark=float(start_mark))
            q_reservior = q_pritok - q_hpp
            delta_w = (q_reservior * time) / (10 ** 6)
            volume_end = delta_w + volume_start
            end_mark = self.connection_curve_vb('V', volume=int(volume_end))
            z_middle = (float(start_mark) + float(end_mark)) / 2
            z_lower_bief = self.connection_curve_nb('Q', rate=(q_hpp + 10))
            head = z_middle - z_lower_bief - self.dh
            power = (9.81 * q_hpp * head * self.get_efficiency(head)) / 1000
            production = (power * (time / (60 * 60))) / (10 ** 3)
        if length_line_name == 5:
            btn_name = self.middle_btn_names[self.choose_line_tab_2.currentText()]
            btn_name.setEnabled(True)

        period_result = [q_pritok, start_mark]
        if type_count == 'straight':
            end_mark_formatted = float(end_mark)
        else:
            end_mark_formatted = float("{0:.2f}".format(end_mark))

        period_result.append(end_mark_formatted)
        z_lower_bief_formatted = float("{0:.2f}".format(z_lower_bief))

        period_result.append(z_lower_bief_formatted)
        head_formatted = float("{0:.2f}".format(head))
        period_result.append(head_formatted)
        q_hpp_formatted = float("{0:.2f}".format(q_hpp))
        period_result.append(q_hpp_formatted)
        power_formatted = float("{0:.2f}".format(power))
        period_result.append(power_formatted)
        production_formatted = float("{0:.2f}".format(production))
        period_result.append(production_formatted)
        line_start = self.dispatch_graph_intersect(float(start_mark), start_period - 1)
        line_end = self.dispatch_graph_intersect(float(end_mark), start_period)
        error_graph_intersect = True  # Intersect with graph
        error_restrictions = True
        for elem in line_start:
            if elem in line_end:
                error_graph_intersect = False
                break
        rates = self.dispatch_graph_rates(line=line_end, period=start_period)
        error_in_graph_rates = False
        if (int(q_hpp) >= rates[0]) and (int(q_hpp) <= rates[1]):
            pass
        else:
            error_in_graph_rates = True

        if self.restrictions_info_browser_tab_2.toPlainText() == 'No errors during calculation':
            pass
        else:
            errors_in_calc_text = self.restrictions_info_browser_tab_2.toPlainText().split('\n')
            self.restrictions_info_browser_tab_2.clear()
            self.restrictions_info_browser_tab_2.setFontWeight(400)
            what_to_find = 'Line %s' % (self.choose_line_tab_2.currentText())
            for j in range(len(errors_in_calc_text)):
                if errors_in_calc_text[j].find(what_to_find) >= 0:
                    pass
                else:
                    self.restrictions_info_browser_tab_2.append(errors_in_calc_text[j])
            if len(self.restrictions_info_browser_tab_2.toPlainText()) == 0:
                self.restrictions_info_browser_tab_2.setText('No errors during calculation')
        if error_graph_intersect:
            if self.restrictions_info_browser_tab_2.toPlainText() == 'No errors during calculation':
                self.restrictions_info_browser_tab_2.setFontWeight(400)
                self.restrictions_info_browser_tab_2.setText(
                    'Line %s. Intersection of dispatch graph in %s calculation period' % (
                        self.choose_line_tab_2.currentText(), start_period))
            else:
                self.restrictions_info_browser_tab_2.setFontWeight(400)
                self.restrictions_info_browser_tab_2.append(
                    'Line %s. Intersection of dispatch graph in %s calculation period' % (
                        self.choose_line_tab_2.currentText(), start_period))
        if error_in_graph_rates:
            if self.restrictions_info_browser_tab_2.toPlainText() == 'No errors during calculation':
                self.restrictions_info_browser_tab_2.setFontWeight(400)
                self.restrictions_info_browser_tab_2.setText(
                    'Line %s. Rate disparity of dispatch zone in %s calculation period' % (
                        self.choose_line_tab_2.currentText(), start_period))
            else:
                self.restrictions_info_browser_tab_2.setFontWeight(400)
                self.restrictions_info_browser_tab_2.append(
                    'Line %s. Rate disparity of dispatch zone in %s calculation period' % (
                        self.choose_line_tab_2.currentText(), start_period))

        # Rectrictions check
        err_restr = []
        for restr in self.restrictions:
            if (restr[2] <= start_period) and (restr[3] >= start_period):
                if restr[1] == 'Z':
                    if restr[5] == '<=':
                        restr_mark = (float(end_mark) <= restr[4])
                        if restr_mark == False:
                            err_restr.append(restr[0])
                    elif restr[5] == '>=':
                        restr_mark = (float(end_mark) >= restr[4])
                        if restr_mark == False:
                            err_restr.append(restr[0])
                    elif restr[5] == '=':
                        restr_mark = (float(end_mark) == restr[4])
                        if restr_mark == False:
                            err_restr.append(restr[0])
                elif restr[1] == 'Q':
                    if restr[5] == '<=':
                        restr_mark = (int(q_hpp) <= restr[4])
                        if restr_mark == False:
                            err_restr.append(restr[0])
                    elif restr[5] == '>=':
                        restr_mark = (int(q_hpp) >= restr[4])
                        if restr_mark == False:
                            err_restr.append(restr[0])
                    elif restr[5] == '=':
                        restr_mark = (int(q_hpp) == restr[4])
                        if restr_mark == False:
                            err_restr.append(restr[0])
                elif restr[1] == 'H':
                    if restr[5] == '<=':
                        restr_mark = (float(head) <= restr[4])
                        if restr_mark == False:
                            err_restr.append(restr[0])
                    elif restr[5] == '>=':
                        restr_mark = (float(head) >= restr[4])
                        if restr_mark == False:
                            err_restr.append(restr[0])
                    elif restr[5] == '=':
                        restr_mark = (float(head) == restr[4])
                        if restr_mark == False:
                            err_restr.append(restr[0])
        if len(err_restr) > 0:
            for i in err_restr:
                if self.restrictions_info_browser_tab_2.toPlainText() == 'No errors during calculation':
                    self.restrictions_info_browser_tab_2.setFontWeight(400)
                    self.restrictions_info_browser_tab_2.setText(
                        'Line %s. Noncompliance with restriction: %s in %s calculation period' % (
                            self.choose_line_tab_2.currentText(), i, start_period))
                else:
                    self.restrictions_info_browser_tab_2.setFontWeight(400)
                    self.restrictions_info_browser_tab_2.append(
                        'Line %s. Noncompliance with restriction: %s in %s calculation period' % (
                            self.choose_line_tab_2.currentText(), i, start_period))
            text = self.restrictions_info_browser_tab_2.toPlainText()
            text = text.split('\n')
        pen = QtGui.QPen(QtCore.Qt.red)
        pen_rec = QtGui.QPen(QtCore.Qt.red)
        pen_rec.setWidth(4)
        if self.choose_line_tab_2.currentText()[0] == 'A':
            pen = QtGui.QPen(QtCore.Qt.green)
            pen_rec = QtGui.QPen(QtCore.Qt.green)
        elif self.choose_line_tab_2.currentText()[0] == 'B':
            pen = QtGui.QPen(QtCore.Qt.magenta)
            pen_rec = QtGui.QPen(QtCore.Qt.magenta)
        elif self.choose_line_tab_2.currentText()[0] == 'C':
            pen = QtGui.QPen(QtCore.Qt.cyan)
            pen_rec = QtGui.QPen(QtCore.Qt.cyan)

        pen.setWidth(2)
        r = QtCore.QLineF(((int(start_period) - int(
            self.start_period_tab_2.currentText())) * self.deltaX_middle - self.deltaX_middle),
                          self.from_absolute_to_relative_middle(start_mark),
                          ((int(start_period) - int(
                              self.start_period_tab_2.currentText()) + 1) * self.deltaX_middle - self.deltaX_middle),
                          self.from_absolute_to_relative_middle(end_mark))
        line = scene.addLine(r, pen)
        leng = len(self.regime_list)
        rect_start = QtCore.QRectF(
            ((int(start_period) - int(
                self.start_period_tab_2.currentText()) + 1) * self.deltaX_middle - self.deltaX_middle) - 1.5,
            self.from_absolute_to_relative_middle(end_mark) - int(self.start_period_tab_2.currentText()) - 1.5, 3, 3)
        rect = scene.addRect(rect_start, pen_rec)

        change = False
        if (self.result_table_tab_2.item(self.middle_line_index[self.choose_line_tab_2.currentText()],
                                         2) is not None) and len(
            self.result_table_tab_2.item(self.middle_line_index[self.choose_line_tab_2.currentText()],
                                         2).text()) > 1:
            change = True
            item = self.result_table_tab_2.item(
                self.middle_line_index[self.choose_line_tab_2.currentText()], 3).text()  # Получаем старую отметку
            scene.removeItem(
                self.regime_dict_middle.get(self.choose_line_tab_2.currentText()))  # Удаляем старую линию
            self.regime_dict_middle.update({self.choose_line_tab_2.currentText(): line})
            scene.removeItem(self.regime_rect_dict_middle.get(
                self.choose_line_tab_2.currentText()))  # Удаляем прямоугольник
            self.regime_rect_dict_middle.update({self.choose_line_tab_2.currentText(): rect})
        else:
            self.regime_dict_middle.update({self.choose_line_tab_2.currentText(): line})
            self.regime_rect_dict_middle.update({self.choose_line_tab_2.currentText(): rect})

        if (int(self.end_period_tab_2.currentText())) >= start_period:
            print('TRUE')
        item_rp = QtWidgets.QTableWidgetItem(str(start_period))
        self.result_table_tab_2.setItem(self.middle_line_index[self.choose_line_tab_2.currentText()], 0,
                                        item_rp)
        item_q_pritok = QtWidgets.QTableWidgetItem(str(int(period_result[0])))
        self.result_table_tab_2.setItem(self.middle_line_index[self.choose_line_tab_2.currentText()], 2,
                                        item_q_pritok)
        item_z_start = QtWidgets.QTableWidgetItem(str(float(period_result[1])))
        self.result_table_tab_2.setItem(self.middle_line_index[self.choose_line_tab_2.currentText()], 3,
                                        item_z_start)
        if type_count == 'straight':
            item_z_end = QtWidgets.QTableWidgetItem(str(float((period_result[2]))))
        else:
            item_z_end = QtWidgets.QTableWidgetItem(
                str(float("{0:.2f}".format(period_result[2]))))
        self.result_table_tab_2.setItem(self.middle_line_index[self.choose_line_tab_2.currentText()], 4,
                                        item_z_end)
        item_z_lower_bief = QtWidgets.QTableWidgetItem(
            str(float("{0:.2f}".format(period_result[3]))))
        self.result_table_tab_2.setItem(self.middle_line_index[self.choose_line_tab_2.currentText()], 5,
                                        item_z_lower_bief)
        item_head = QtWidgets.QTableWidgetItem(str(float("{0:.2f}".format(period_result[4]))))
        self.result_table_tab_2.setItem(self.middle_line_index[self.choose_line_tab_2.currentText()], 6,
                                        item_head)
        item_q_hpp = QtWidgets.QTableWidgetItem(str(int(period_result[5])))
        self.result_table_tab_2.setItem(self.middle_line_index[self.choose_line_tab_2.currentText()], 7,
                                        item_q_hpp)
        item_power = QtWidgets.QTableWidgetItem(str(float("{0:.2f}".format(period_result[6]))))
        self.result_table_tab_2.setItem(self.middle_line_index[self.choose_line_tab_2.currentText()], 8,
                                        item_power)
        item_production = QtWidgets.QTableWidgetItem(
            str(float("{0:.2f}".format(period_result[7]))))
        self.result_table_tab_2.setItem(self.middle_line_index[self.choose_line_tab_2.currentText()], 9,
                                        item_production)
        self.editIndex = QModelIndex()
        self.result_table_tab_2.resizeColumnsToContents()
        self.insert_rate_tab_2.clear()
        self.insert_mark_tab_2.clear()

        self.editIndex = QModelIndex()
        if len(self.choose_line_tab_2.currentText()) == 1:
            line_name = self.choose_line_tab_2.currentText()  # линия
            indx = self.middle_line_index[line_name]
            added_line = self.result_table_tab_2.item(indx + 1, 1).text()
            if self.choose_line_tab_2.findText(added_line) == -1:
                self.choose_line_tab_2.insertItem(self.choose_line_tab_2.currentIndex() + 1,
                                                  added_line)
                added_line = self.result_table_tab_2.item(indx + 5, 1).text()
                self.choose_line_tab_2.insertItem(self.choose_line_tab_2.currentIndex() + 2,
                                                  added_line)
                added_line = self.result_table_tab_2.item(indx + 9, 1).text()
                self.choose_line_tab_2.insertItem(self.choose_line_tab_2.currentIndex() + 3,
                                                  added_line)
        elif len(self.choose_line_tab_2.currentText()) == 3:
            line_name = self.choose_line_tab_2.currentText()  # линия
            indx = self.middle_line_index[line_name]
            added_line = self.result_table_tab_2.item(indx + 1, 1).text()
            if self.choose_line_tab_2.findText(added_line) == -1:
                self.choose_line_tab_2.insertItem(self.choose_line_tab_2.currentIndex() + 1,
                                                  added_line)
                added_line = self.result_table_tab_2.item(indx + 2, 1).text()
                self.choose_line_tab_2.insertItem(self.choose_line_tab_2.currentIndex() + 2,
                                                  added_line)
                added_line = self.result_table_tab_2.item(indx + 3, 1).text()
                self.choose_line_tab_2.insertItem(self.choose_line_tab_2.currentIndex() + 3,
                                                  added_line)
        self.choose_line_tab_2.setSizeAdjustPolicy(0)
        changed_line_name = self.choose_line_tab_2.currentText()

        if len(self.choose_line_tab_2.currentText()) < 5:
            try:
                self.choose_line_tab_2.setCurrentIndex(
                    self.choose_line_tab_2.currentIndex() + 1)
            except:
                pass

        if (self.result_table_tab_2.item(self.middle_line_index[self.choose_line_tab_2.currentText()],
                                         2) is not None) and change and len(self.choose_line_tab_2.currentText()) < 5:
            for k in range(3):
                if self.result_table_tab_2.item(self.middle_line_index[changed_line_name + '-' + str(k + 1)],
                                                4) is not None:
                    mark = float(
                        self.result_table_tab_2.item(self.middle_line_index[changed_line_name + '-' + str(k + 1)],
                                                     4).text())
                    self.insert_mark_tab_2.clear()
                    self.insert_mark_tab_2.insert(str(mark))
                    line_indx = self.choose_line_tab_2.findText(changed_line_name + '-' + str(k + 1))
                    self.choose_line_tab_2.setCurrentIndex(line_indx)
                    self.draw_regime_middle(self.scene_middle, 'mark')
        elif (self.result_table_tab_2.item(self.middle_line_index[self.choose_line_tab_2.currentText()],
                                           2) is not None) and change and len(
            self.choose_line_tab_2.currentText()) == 5:
            for l in range(3):
                try:
                    if self.result_table_tab_2.item(self.middle_line_index[changed_line_name + '-' + str(l + 1)],
                                                    4) is not None:
                        mark = float(
                            self.result_table_tab_2.item(self.middle_line_index[changed_line_name + '-' + str(l + 1)],
                                                         4).text())
                        self.insert_mark_tab_2.clear()
                        self.insert_mark_tab_2.insert(str(mark))
                        line_indx = self.choose_line_tab_2.findText(changed_line_name + '-' + str(l + 1))
                        self.choose_line_tab_2.setCurrentIndex(line_indx)
                        self.draw_regime_middle(self.scene_middle, 'mark')
                except:
                    pass

    # Calculation when CP change in middleterm
    def middleterm_change_of_period(self):
        self.end_period_tab_2.removeItem(0)
        self.end_period_tab_2.addItem(str(self.start_period_tab_2.currentIndex() + 3))
        if self.middle_term_calculation:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Question)
            msg.setWindowTitle("Change of calculation period")
            msg.setText("On calculation period change, all results will be lost! Continue?")
            okButton = msg.addButton('Yes', QtWidgets.QMessageBox.AcceptRole)
            msg.addButton('No', QtWidgets.QMessageBox.RejectRole)
            msg.exec()
            if msg.clickedButton() == okButton:
                self.scene_middle.clear()
                self.draw_coordinate_net(self.scene_middle, 4, self.graphics_view_tab2)
                self.draw_dispatch_graph(self.scene_middle, 4, self.graphics_view_tab2)
                self.add_zones(self.scene_middle, 4, self.graphics_view_tab2)
                self.middle_rate(int(self.start_period_tab_2.currentText()) + 1)
                self.middle_additional_regime()
                self.combo_box_change()
                self.table_middle_term_clearance()
                self.middle_term_calculation = False
                self.restrictions_info_browser_tab_2.setText('No errors during calculation')
                return 'End'
        else:
            self.scene_middle.clear()
            self.draw_coordinate_net(self.scene_middle, 4, self.graphics_view_tab2)
            self.draw_dispatch_graph(self.scene_middle, 4, self.graphics_view_tab2)
            self.add_zones(self.scene_middle, 4, self.graphics_view_tab2)
            self.middle_rate(int(self.start_period_tab_2.currentText()) + 1)
            self.combo_box_change()
            self.middle_additional_regime()
            return 'End'

    # Clear table when CP chagne
    def table_middle_term_clearance(self):
        for i in range(3, 38):
            for j in range(10):
                if j == 1:
                    pass
                else:
                    try:
                        item = self.result_table_tab_2.item(i, j)
                        item.setText('')
                        # self.result_table_tab_2.removeItem(item)
                    except:
                        pass
        for i in self.middle_btn_names.values():
            try:
                i.setEnabled(False)
            except:
                pass

    # Approve line from middleterm with influence on longterm
    def approve_line_from_middleterm(self, linename):
        if linename != ('A-1-1') or self.middle_btn_names.get('A-1-1').isEnabled():
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setWindowTitle("Approve line")
            msg.setText("On line approvement results of line A-1-1 will be lost! Continue?")
            okButton = msg.addButton('Yes', QtWidgets.QMessageBox.AcceptRole)
            msg.addButton('No', QtWidgets.QMessageBox.RejectRole)
            msg.exec()
            if msg.clickedButton() == okButton:
                z_end_1 = self.result_table_tab_2.item(self.middle_line_index[linename[16]], 4).text()
                z_end_2 = self.result_table_tab_2.item(self.middle_line_index[linename[16:19]], 4).text()
                z_end_3 = self.result_table_tab_2.item(self.middle_line_index[linename[16:]], 4).text()
                for i in range(3):
                    if i == 0:
                        self.calculcation_indicator.setValue(int(self.start_period_tab_2.currentText()) + 1 + i)
                        self.insert_mark.clear()
                        self.insert_mark.insert(z_end_1)
                        self.draw_regime(self.scene, 'mark')
                    elif i == 1:
                        self.calculcation_indicator.setValue(int(self.start_period_tab_2.currentText()) + 1 + i)
                        self.insert_mark.clear()
                        self.insert_mark.insert(z_end_2)
                        self.draw_regime(self.scene, 'mark')
                    elif i == 2:
                        self.calculcation_indicator.setValue(int(self.start_period_tab_2.currentText()) + 1 + i)
                        self.insert_mark.clear()
                        self.insert_mark.insert(z_end_3)
                        self.draw_regime(self.scene, 'mark')

    # Get efficiency from work characteristic
    def get_efficiency(self, head):
        work_dict = self.working_characteristic
        heads_list = work_dict.keys()
        heads_list = sorted(heads_list, reverse=True)
        efficiency_list = work_dict.values()
        efficiency_list = sorted(efficiency_list, reverse=True)
        for i in range(0, len(heads_list)):
            if (head > float(heads_list[i])) and (i == 0):
                efficiency = efficiency_list[i] + (
                        (efficiency_list[i] - efficiency_list[i + 1]) * (head - float(heads_list[i]))) / (
                                     float(heads_list[i]) - float(heads_list[i + 1]))
                return efficiency / 100
            elif (head > float(heads_list[i])) and (i > 0):
                efficiency = efficiency_list[i] + (
                        (efficiency_list[i - 1] - efficiency_list[i]) * (head - float(heads_list[i]))) / (
                                     float(heads_list[i - 1]) - float(heads_list[i]))
                return efficiency / 100
            elif (head < float(heads_list[i])) and (i == (len(heads_list) - 1)):
                efficiency = efficiency_list[i] + (
                        (efficiency_list[i - 1] - efficiency_list[i]) * (head - float(heads_list[i]))) / (
                                     float(heads_list[i - 1]) - float(heads_list[i]))
                return efficiency / 100

    def draw_regime_middle_from_longterm(self, start_period=0, start_mark=0.0, end_mark=0.0, change=False):
        scene = self.scene_middle
        delta = self.deltaX_middle
        if int(start_period) > int(self.end_period_tab_2.currentText()) or int(start_period) <= int(
                self.start_period_tab_2.currentText()):
            if int(start_period) == int(self.start_period_tab_2.currentText()):
                pass
                try:
                    self.scene_middle.removeItem(self.rect_start_name)
                except:
                    pass
        else:
            pen = QtGui.QPen(QtCore.Qt.red)
            pen.setWidth(3)
            r = QtCore.QLineF(((int(start_period) - int(self.start_period_tab_2.currentText())) * delta - delta),
                              self.from_absolute_to_relative_middle(start_mark),
                              ((int(start_period) - int(self.start_period_tab_2.currentText()) + 1) * delta - delta),
                              self.from_absolute_to_relative_middle(end_mark))
            line_middle = scene.addLine(r, pen)

            pen_rec = QtGui.QPen(QtCore.Qt.red)
            pen_rec.setWidth(4)
            rect_start = QtCore.QRectF(
                ((int(start_period) - int(self.start_period_tab_2.currentText()) + 1) * delta - delta) - 1.5,
                self.from_absolute_to_relative_middle(end_mark) - 1.5, 3, 3)
            rect_middle = scene.addRect(rect_start, pen_rec)
            if (int(start_period) - int(self.start_period_tab_2.currentText())) == 1:
                line_name = 'A'
            elif (int(start_period) - int(self.start_period_tab_2.currentText())) == 2:
                line_name = 'A-1'
            elif (int(start_period) - int(self.start_period_tab_2.currentText())) == 3:
                line_name = 'A-1-1'
            if change:
                item = self.result_table.item(1, self.calculcation_indicator.value()).text()  # Получаем старую отметку
                try:
                    scene.removeItem(self.regime_dict_middle.get(line_name))  # Удаляем старую линию
                    self.regime_dict_middle.update({line_name: line_middle})
                    scene.removeItem(self.regime_rect_dict_middle.get(line_name))  # Удаляем прямоугольник
                    self.regime_rect_dict_middle.update({line_name: rect_middle})
                except:
                    pass
            else:
                self.regime_dict_middle.update({line_name: line_middle})
                self.regime_rect_dict_middle.update({line_name: rect_middle})
            if (int(start_period) - int(self.start_period_tab_2.currentText())) == 1:
                line_name = 'A'  # линия
                indx = self.middle_line_index[line_name]
                added_line = self.result_table_tab_2.item(indx + 1, 1).text()
                if self.choose_line_tab_2.findText(added_line) == -1:
                    indx_of_current_line = self.choose_line_tab_2.findText(line_name)
                    self.choose_line_tab_2.insertItem(indx_of_current_line + 1,
                                                      added_line)
                    added_line = self.result_table_tab_2.item(indx + 5, 1).text()
                    self.choose_line_tab_2.insertItem(indx_of_current_line + 2,
                                                      added_line)
                    added_line = self.result_table_tab_2.item(indx + 9, 1).text()
                    self.choose_line_tab_2.insertItem(indx_of_current_line + 3,
                                                      added_line)
            elif (int(start_period) - int(self.start_period_tab_2.currentText())) == 2:
                line_name = 'A-1'  # линия
                indx = self.middle_line_index[line_name]
                added_line = self.result_table_tab_2.item(indx + 1, 1).text()
                if self.choose_line_tab_2.findText(added_line) == -1:
                    indx_of_current_line = self.choose_line_tab_2.findText(line_name)
                    self.choose_line_tab_2.insertItem(indx_of_current_line + 1, added_line)
                    added_line = self.result_table_tab_2.item(indx + 2, 1).text()
                    self.choose_line_tab_2.insertItem(indx_of_current_line + 2, added_line)
                    added_line = self.result_table_tab_2.item(indx + 3, 1).text()
                    self.choose_line_tab_2.insertItem(indx_of_current_line + 3, added_line)
            self.restrictions_info_browser_tab_2.clear()
            if self.restrictions_info_browser.toPlainText() != 'No errors during calculation':
                self.restrictions_info_browser_tab_2.setFontWeight(400)
                txt = self.restrictions_info_browser.toPlainText()
                restrictions_proh = []
                previous_value = 0
                for x in range(0, len(txt)):
                    if txt[x] == '\n':
                        restrictions_proh.append(txt[previous_value:x])
                        previous_value = x + 1
                restrictions_proh.append(txt[previous_value:])
                what_to_find = 'in %s' % start_period
                for l in restrictions_proh:
                    if (int(start_period) - int(self.start_period_tab_2.currentText())) == 1:
                        line_name = 'A'
                        l = 'Longterm. ' + l
                        if self.restrictions_info_browser_tab_2.toPlainText() == 'No errors during calculation':
                            self.restrictions_info_browser_tab_2.setText(l)
                        else:
                            self.restrictions_info_browser_tab_2.append(l)
                    elif (int(start_period) - int(self.start_period_tab_2.currentText())) == 2:
                        what_to_find = 'in %s' % (start_period - 1)
                        index = l.find(what_to_find)
                        if index >= 0 and (l[index + len(what_to_find)] == ' '):
                            line_name = 'A'
                            l = 'Longterm. ' + l
                            if self.restrictions_info_browser_tab_2.toPlainText() == 'No errors during calculation':
                                self.restrictions_info_browser_tab_2.setText(l)
                            else:
                                self.restrictions_info_browser_tab_2.append(l)
                        what_to_find = 'in %s' % start_period
                        index = l.find(what_to_find)
                        if index >= 0 and (l[index + len(what_to_find)] == ' '):
                            line_name = 'A-1'
                            l = 'Longterm.' + l
                            if self.restrictions_info_browser_tab_2.toPlainText() == 'No errors during calculation':
                                self.restrictions_info_browser_tab_2.setText(l)
                            else:
                                self.restrictions_info_browser_tab_2.append(l)
                    elif (int(start_period) - int(self.start_period_tab_2.currentText())) == 3:
                        what_to_find = 'in %s' % (start_period - 2)
                        index = l.find(what_to_find)
                        if index >= 0 and (l[index + len(what_to_find)] == ' '):
                            line_name = 'A'
                            l = 'Longterm. ' + l
                            if self.restrictions_info_browser_tab_2.toPlainText() == 'No errors during calculation':
                                self.restrictions_info_browser_tab_2.setText(l)
                            else:
                                self.restrictions_info_browser_tab_2.append(l)
                        what_to_find = 'in %s' % (start_period - 1)
                        index = l.find(what_to_find)
                        if index >= 0 and (l[index + len(what_to_find)] == ' '):
                            line_name = 'A-1'
                            l = 'Longterm. ' + l
                            if self.restrictions_info_browser_tab_2.toPlainText() == 'No errors during calculation':
                                self.restrictions_info_browser_tab_2.setText(l)
                            else:
                                self.restrictions_info_browser_tab_2.append(l)
                        what_to_find = 'in %s' % (start_period)
                        index = l.find(what_to_find)
                        if index >= 0 and (l[index + len(what_to_find)] == ' '):
                            # line_name = 'A-1-1'
                            l = 'Longterm. ' + l
                            if self.restrictions_info_browser_tab_2.toPlainText() == 'No errors during calculation':
                                self.restrictions_info_browser_tab_2.setText(l)
                            else:
                                self.restrictions_info_browser_tab_2.append(l)
                if len(self.restrictions_info_browser_tab_2.toPlainText()) < 1:
                    self.restrictions_info_browser_tab_2.setFontWeight(400)
                    self.restrictions_info_browser_tab_2.setText('No errors during calculation')

    def excel_export(self):
        file_name = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Excel file', 'Regime calculation',
                                                         'Excel files (*.xlsx)')
        if file_name == ('', ''): return
        try:
            workbook = xlsxwriter.Workbook(file_name[0])
            cell_format = workbook.add_format()
            cell_format.set_text_wrap()
            cell_format.set_center_across()
            cell_format.set_bottom()
            cell_format.set_top()
            cell_format.set_left()
            cell_format.set_right()
            cell_format.set_align('vcenter')
            cell_format.set_align('center')
            headers_format = workbook.add_format()
            headers_format.set_bold()
            headers_format.set_text_wrap()
            headers_format.set_bottom()
            headers_format.set_top()
            headers_format.set_left()
            headers_format.set_right()
            headers_format.set_align('vcenter')
            headers_format.set_align('center')
            worksheet = workbook.add_worksheet('Page')
            bold = workbook.add_format({'bold': True})
            headers = ['Number of RP', 'Days', 'Rate', 'Mark of UB start.', 'Mark of UB start.', 'Mark of LB', 'Head',
                       'Rate in LB', 'Power', 'Energy']
            labels = ['-', '-', 'm³/s', 'm', 'm', 'm', 'm', 'm³/s', 'MVt', 'kVt.h']
            for i in range(len(headers)):
                worksheet.merge_range(0, i, 1, i, headers[i], headers_format)
                worksheet.write(2, i, labels[i], cell_format)
            result = self.result_list
            days = self.t_days
            pritok = self.q_pritok[str(self.variant)]
            for j in range(len(result)):
                worksheet.write(j + 3, 0, j + 1, cell_format)
                worksheet.write(j + 3, 1, days[j], cell_format)
                for k in range(len(result[j])):
                    worksheet.write(j + 3, k + 2, result[j][k], cell_format)
            restrictions = self.restrictions_info_browser.toPlainText().splitlines()
            worksheet.write('A25', 'Calculation error:')
            for i in range(len(restrictions)):
                worksheet.write('A%s' % (26 + i), restrictions[i])
            # Save regime
            self.scene.clearSelection()
            self.scene.setSceneRect(self.scene.itemsBoundingRect())
            image = QImage(self.scene.sceneRect().size().toSize(), QImage.Format_A2RGB30_Premultiplied)
            image.fill(QtCore.Qt.white)
            painter = QPainter(image)
            self.scene.render(painter)
            image.save("regime.png")
            painter.end()
            worksheet.insert_image('L2', 'regime.png')
            workbook.close()
            os.remove('regime.png')
        except:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Can't write a file. Probably it is open or in use!")

    # Convert from metres to scene pixels.
    def from_absolute_to_relative(self, mark):
        mark = float(mark)
        mark_in_px = ((self.graph_height_px) * (self.z_max - mark) / (self.z_max - self.z_min)) + self.margin_top
        return mark_in_px

    # Convert from scene pixels to metres.
    def from_relative_to_absolute(self, px):
        px_in_mark = self.z_max - (((self.z_max - self.z_min) * (px - self.margin_top)) / ((self.graph_height_px)))
        return px_in_mark

    # Convert from metres to scene pixels - middleterm
    def from_absolute_to_relative_middle(self, mark):
        graph_height_px = 320
        mark = float(mark)
        mark_in_px = ((graph_height_px) * (self.z_max - mark) / (self.z_max - self.z_min)) + self.margin_top
        return mark_in_px

        # Convert from scene pixels to metres - middleterm
    def from_relative_to_absolute_middle(self, px):
        graph_height_px = 320
        px_in_mark = self.z_max - (((self.z_max - self.z_min) * (px - self.margin_top)) / ((graph_height_px)))
        return px_in_mark

    # Find intersects
    def dispatch_graph_intersect(self, mark, start_period):
        graph = self.dispatch_graph()
        for i in range(len(graph)):
            line_name = 'Line %s' % (str(i + 1))
            line = graph[line_name]
            delta = float(mark) - line[start_period]
            if abs(delta) <= 0.02:
                for j in list(reversed(range(i, len(graph)))):
                    line_name_end = 'Line %s' % (str(j + 1))
                    line = graph[line_name_end]
                    delta = float(mark) - line[start_period]
                    if abs(delta) <= 0.05:
                        return [i for i in range(int(line_name[-1]), int(line_name_end[-1]) + 2)]
            elif float(mark) <= float(line[start_period]):
                return [int(line_name[-1])]

    # Put cursor on dispatch graph
    def addInputTextToListbox(self, scene, deltaX):
        pen_period = QtGui.QPen(QtCore.Qt.red)
        pen_period.setStyle(Qt.DashLine)
        pen_period.setDashPattern([10, 5])
        pen_period.setWidth(3)
        y = self.calculcation_indicator.text()
        for items in scene.items():
            try:
                if str(items.pen().color().red()) == '255' and items.pen().style() == 6:
                    scene.removeItem(items)
            except:
                pass
        r = QtCore.QLineF((int(y) * self.deltaX - self.deltaX), self.margin_top, (int(y) * self.deltaX - self.deltaX),
                          self.graph_height_px + self.margin_top)
        line = scene.addLine(r, pen_period)

    # Focus on changed line.
    def table_selection_change(self):
        item = self.result_table_tab_2.item(self.middle_line_index[self.choose_line_tab_2.currentText()], 1)
        item.setSelected(True)
        self.result_table_tab_2.scrollToItem(item)

    # Real dispatch graph
    def dispatch_graph(self):
        line_1 = [84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84]
        line_2 = [85.15, 85, 84.95, 84.95, 84.9, 85.07, 85.9, 86.25, 86.5, 86.57, 86.6, 86.56, 86.46, 86.32, 86.28,
                  86.28, 86.24, 86.18, 86.04, 85.87, 85.15]
        line_3 = [85.24, 85, 84.95, 84.95, 84.9, 85.29, 86.61, 87.2, 87.35, 87.5, 87.67, 87.64, 87.5, 87.38, 87.31,
                  87.31, 87.22, 87.13, 86.75, 86.39, 85.24]
        line_4 = [85.24, 85, 85.5, 85.95, 86.43, 87.42, 87.85, 88.07, 88.21, 88.25, 88.25, 88.18, 87.93, 87.6, 87.49,
                  87.49, 87.33, 87.13, 86.75, 86.39, 85.25]
        line_5 = [85.7, 85, 86.22, 86.75, 87.25, 88, 88.7, 89, 89, 89, 89, 89, 89, 89, 89, 89, 88.9, 88.8, 88.38, 87.92,
                  85.7]
        line_6 = [85.67, 86.6, 87.38, 88, 88.44, 88.8, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 85.67]
        line_7 = [89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89]
        graph = {
            'Line 1': line_1,
            'Line 2': line_2,
            'Line 3': line_3,
            'Line 4': line_4,
            'Line 5': line_5,
            'Line 6': line_6,
            'Line 7': line_7
        }
        return graph

    # Rates of zones
    def dispatch_graph_rates(self, line, period):
        line_1 = [380, 420]
        if period <= 2:
            line_2 = [570, 630]
        elif period <= 14:
            line_2 = [870, 1300]
        else:
            line_2 = [570, 630]
        line_3 = [1000, 1180]
        line_4 = [1200, 1380]
        line_5 = [1200, 1480]
        line_6 = [2400, 7100]
        line_7 = [9700, 19600]
        line_8 = [18800, 21670]
        rates = {'1': line_1, '2': line_2, '3': line_3, '4': line_4, '5': line_5,
                 '6': line_6, '7': line_7, '8': line_8
                 }
        max_min_rates = []
        if len(line) > 1:
            min_line = rates.get(str(line[0]))[0]
            max_min_rates.append(min_line)
            max_line = rates.get(str(line[-1]))[1]
            max_min_rates.append(max_line)
        else:
            min_line = rates.get(str(line[0]))[0]
            max_min_rates.append(min_line)
            max_line = rates.get(str(line[0]))[1]
            max_min_rates.append(max_line)
        return max_min_rates

    # Curve for lower bief
    def curve_nb(self):
        curve = {
            '65.5': 1000,
            '65.66': 1100,
            '65.83': 1200,
            '65.98': 1300,
            '66.14': 1400,
            '66.28': 1500,
            '67.07': 2050,
            '67.55': 2500,
            '68.12': 3000,
            '68.65': 3500,
            '69.15': 4000,
            '69.6': 4500,
            '70.1': 5100,
            '71.53': 6850,
            '72.0': 7500,
            '72.84': 8800,
            '74.93': 13700,
            '75.6': 16000,
            '76.82': 22500

        }
        return curve

    # Curve for upper bief
    def curve_vb(self):
        curve = {
            '80': 2600,
            '81': 3073,
            '82': 3616,
            '83': 4230,
            '84': 4910,
            '85': 5661,
            '86': 6474,
            '87': 7359,
            '88': 8325,
            '89': 9363,
            '90': 10463
        }
        return curve

    # Get values from curve of LB
    def connection_curve_nb(self, type_of_insert, mark=0.0, rate=0.0):
        curve = self.curve_nb()
        keys = list(curve.keys())
        values = list(curve.values())
        keys.sort()
        values.sort()
        if type_of_insert == 'Z':
            for i in range(1, len(keys)):
                if mark <= float(keys[i]):
                    rate_from_mark = curve[keys[i - 1]] + (
                            ((mark - float(keys[i - 1])) * (curve[keys[i]] - curve[keys[i - 1]])) / (
                            float(keys[i]) - float(keys[i - 1])))
                    return rate_from_mark
                elif i == (len(keys) - 1):
                    rate_from_mark = curve[keys[i - 1]] + (
                            ((mark - float(keys[i - 1])) * (curve[keys[i]] - curve[keys[i - 1]])) / (
                            float(keys[i]) - float(keys[i - 1])))
                    return rate_from_mark
        else:
            for i in range(1, len(values)):
                if rate <= values[i]:
                    mark_from_rate = float(keys[i - 1]) + (
                            ((rate - float(curve[keys[i - 1]])) * (float(keys[i]) - float(keys[i - 1]))) / (
                            float(curve[keys[i]]) - float(curve[keys[i - 1]])))
                    return mark_from_rate
                elif i == (len(values) - 1):
                    mark_from_rate = curve[keys[i - 1]] + (
                            ((mark - float(keys[i - 1])) * (curve[keys[i]] - curve[keys[i - 1]])) / (
                            float(keys[i]) - float(keys[i - 1])))
                    return mark_from_rate

    # Get values from curve of UB
    def connection_curve_vb(self, type_of_insert, mark=0.0, volume=0):
        curve = self.curve_vb()
        keys = list(curve.keys())
        values = list(curve.values())
        keys.sort()
        values.sort()
        if type_of_insert == 'Z':
            for i in range(1, len(keys)):
                if mark <= float(keys[i]):
                    volume_from_mark = curve[keys[i - 1]] + (
                            ((mark - float(keys[i - 1])) * (curve[keys[i]] - curve[keys[i - 1]])) / (
                            float(keys[i]) - float(keys[i - 1])))
                    return volume_from_mark
                elif i == (len(keys) - 1):
                    volume_from_mark = curve[keys[i - 1]] + (
                            ((mark - float(keys[i - 1])) * (curve[keys[i]] - curve[keys[i - 1]])) / (
                            float(keys[i]) - float(keys[i - 1])))
                    return volume_from_mark
        else:
            for i in range(1, len(values)):
                if volume <= values[i]:
                    mark_from_volume = float(keys[i - 1]) + (
                            ((volume - float(curve[keys[i - 1]])) * (float(keys[i]) - float(keys[i - 1]))) / (
                        float(curve[keys[i]]) - float(curve[keys[i - 1]])))
                    return mark_from_volume
                elif i == (len(values) - 1):
                    mark_from_volume = curve[keys[i - 1]] + (
                            ((volume - float(keys[i - 1])) * (curve[keys[i]] - curve[keys[i - 1]])) / (
                            float(keys[i]) - float(keys[i - 1])))
                    return mark_from_volume

    # About prog
    def about_program(self):
        info_new = QtWidgets.QMessageBox(self)
        info_new.setWindowTitle('About')
        info_new.setText("This programm was created for making calculations of longterm and middleterm regimes of HPP.<br>"
                         "The program is intended for use by students and teachers of the Department"
                         "Renewables of  \"MPEI\", Moscow, Russia.<br>"
                         "Program developed of Python 3.5 with library PyQt v5.6 and xlswriter v1.1.5.<br>"
                         "Version: 1.1. Last update: 29.05.2019;<br>"
                         "Author: Sysoev Alexander; e-mail: <a href='mailto:sasha_sysoev@mail.ru?subject=Educational package'>sasha_sysoev@mail.ru</a>")
        info_new.setTextFormat(1)
        info_new.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MyFirstGuiProgram()
    w.setWindowTitle("Calculation regime of HPP")
    w.show()
    sys.exit(app.exec_())
