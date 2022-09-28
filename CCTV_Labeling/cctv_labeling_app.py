from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *

import sys
import os

APP_NAME = 'CCTV_Verification_Test'

class LabelingMain(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.folder_path = ""
        self.file_index = 0
        self.scale = 2
        self.initUI()

    def initUI(self):
        self.setWindowTitle(APP_NAME)
        self.resize(1920, 1080)
        self.showMaximized()

        self.menubar = self.menuBar()
        self.menu_open = self.menubar.addMenu("파일")
        self.menu_open_folder = QAction("폴더 열기", self)
        self.menu_open_folder.triggered.connect(lambda: self.setImageScaledByIndex((self.scale), self.getFolderPathByOpenDir(), 0))
        self.menu_open.addAction(self.menu_open_folder)

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

        self.statusbar.addWidget(self.lbl_folder_path)
        self.statusbar.addWidget(self.lbl_folder_path_value)
        self.statusbar.addWidget(self.lbl_file_name)
        self.statusbar.addWidget(self.lbl_file_name_value)
        self.statusbar.addWidget(self.lbl_index)
        self.statusbar.addWidget(self.lbl_index_value)

        self.main_groupbox = QGroupBox()
        self.setCentralWidget(self.main_groupbox)
        self.main_layout = QVBoxLayout(self.main_groupbox)

        self.image_layout = QHBoxLayout()
        self.actual_image_label = QLabel()
        self.actual_image_label.setPixmap(QtGui.QPixmap("test.jpg").scaledToWidth(960))
        self.actual_image_label.setMargin(3)
        self.image_layout.addWidget(self.actual_image_label)
        self.predict_image_label = QLabel()
        self.predict_image_label.setPixmap(QtGui.QPixmap("test.jpg").scaledToWidth(960))
        self.predict_image_label.setMargin(3)
        self.image_layout.addWidget(self.predict_image_label)
        self.main_layout.addLayout(self.image_layout)

        self.prev_btn = QPushButton()
        self.prev_btn.setEnabled(False)
        self.prev_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowLeft))
        self.prev_btn.clicked.connect(lambda: self.prevBtnAction(self.scale, self.folder_path, self.file_index))

        self.next_btn = QPushButton()
        self.next_btn.setEnabled(False)
        self.next_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        self.next_btn.clicked.connect(lambda: self.nextBtnAction(self.scale, self.folder_path, self.file_index))

        self.control_button_layout = QHBoxLayout()
        self.control_button_layout.addWidget(self.prev_btn)
        self.control_button_layout.addWidget(self.next_btn)
        self.main_layout.addLayout(self.control_button_layout)

        self.main_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.show()

    """
        사진 폴더 열기 기능관련 함수
    """
    def setImageScaledByIndex(self, scale, folder_path, index):
        pixmap = QtGui.QPixmap(self.getFilePathByIndex(folder_path, index))
        pixmap = pixmap.scaled(int(pixmap.width() / scale), int(pixmap.height() / scale))
        self.actual_image_label.setPixmap(pixmap)
        self.folder_path = folder_path

    def setActualImage(self):
    
    def setPredictImage(self):
        

    def getFilePathByIndex(self, folder_path, index):
        try: 
            file_list = os.listdir(folder_path)
        except FileNotFoundError:
            return
        file_name_list = []

        for file in file_list:
            file_name, file_ext = os.path.splitext(file)
            if file_ext == '.jpg':
                file_name_list.append(file_name)

        if index == 0:
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(True)
        elif index == len(file_name_list) - 1:
            self.prev_btn.setEnabled(True)
            self.next_btn.setEnabled(False)
        else:
            self.prev_btn.setEnabled(True)
            self.next_btn.setEnabled(True)
        
        return folder_path + '/' + file_name_list[index] + '.jpg'

    def prevBtnAction(self, scale, folder_path, index):
        self.setImageScaledByIndex(scale, folder_path, index-1)
        self.file_index = index - 1

    def nextBtnAction(self, scale, folder_path, index):
        self.setImageScaledByIndex(scale, folder_path, index+1)
        self.file_index = index + 1


    def getFolderPathByOpenDir(self):
        return str(QFileDialog.getExistingDirectory(self, "사진 폴더 불러오기"))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LabelingMain()
    app.installEventFilter(window)
    sys.exit(app.exec_())