from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *

class ImageCheckerView(QMainWindow):
    key_event_signal = QtCore.pyqtSignal(int)

    def __init__(self, APP_NAME):
        super().__init__()
        # self.window_size = QtCore.QSize(1920, 1080)
        self.default_image_pixmap = QtGui.QImage(1600, 900, QtGui.QImage.Format_RGB888)
        self.default_image_pixmap.fill(QtGui.qRgb(255, 255, 255))

        self.setWindowTitle(APP_NAME)
        # self.resize(self.window_size)
        self.showMaximized()

        self.menubar = self.menuBar()
        self.menu_open = self.menubar.addMenu("파일")
        self.menu_open_folder = QAction("폴더 열기", self)
        self.menu_open.addAction(self.menu_open_folder)
        self.menu_open_save_folder = QAction("저장 폴더 지정", self)
        self.menu_open.addAction(self.menu_open_save_folder)

        self.main_groupbox = QGroupBox()
        self.setCentralWidget(self.main_groupbox)
        self.main_layout = QVBoxLayout(self.main_groupbox)

        self.image_label = QLabel()
        self.image_label.setPixmap(QtGui.QPixmap(self.default_image_pixmap))
        self.main_layout.addWidget(self.image_label, 0, QtCore.Qt.AlignCenter)

        self.statusbar = self.statusBar()
        self.lbl_folder_path = QLabel('폴더 위치: ')
        self.lbl_folder_path.hide()
        self.lbl_folder_path_value = QLabel('')
        self.lbl_folder_path_value.hide()
        self.lbl_file_name = QLabel('파일명: ')
        self.lbl_file_name.hide()
        self.lbl_file_name_value = QLabel('')
        self.lbl_file_name_value.hide()
        self.lbl_index = QLabel('번호: ')
        self.lbl_index.hide()
        self.lbl_index_value = QLabel('')
        self.lbl_index_value.hide()
        self.lbl_iscopied = QLabel('')
        self.lbl_iscopied.hide()

        self.statusbar.addWidget(self.lbl_folder_path)
        self.statusbar.addWidget(self.lbl_folder_path_value)
        self.statusbar.addWidget(self.lbl_file_name)
        self.statusbar.addWidget(self.lbl_file_name_value)
        self.statusbar.addWidget(self.lbl_index)
        self.statusbar.addWidget(self.lbl_index_value)
        self.statusbar.addWidget(self.lbl_iscopied)

    def keyPressEvent(self, e):
        self.key_event_signal.emit(e.key())
