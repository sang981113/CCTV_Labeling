from bdb import checkfuncname
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *

import sys
import os

APP_NAME = 'CCTV_Verification'

class LabelingMain(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.folder_path = ""
        self.file_index = 0
        self.width_scale = 960
        self.initUI()

    def initUI(self):
        self.setWindowTitle(APP_NAME)
        self.resize(1920, 1080)
        self.showMaximized()

        self.menubar = self.menuBar()
        self.menu_open = self.menubar.addMenu("파일")
        self.menu_open_folder = QAction("폴더 열기", self)
        self.menu_open_folder.triggered.connect(lambda: self.setScaledImage((self.width_scale), self.getFolderPathByOpenDir(), 0))
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
        self.actual_image_label.setPixmap(QtGui.QPixmap("screen.png").scaledToWidth(self.width_scale))
        self.actual_image_label.setMargin(3)
        self.image_layout.addWidget(self.actual_image_label)
        self.predict_image_label = QLabel()
        self.predict_image_label.setPixmap(QtGui.QPixmap("screen.png").scaledToWidth(self.width_scale))
        self.predict_image_label.setMargin(3)
        self.image_layout.addWidget(self.predict_image_label)
        self.main_layout.addLayout(self.image_layout)

        self.prev_btn = QPushButton()
        self.prev_btn.setEnabled(False)
        self.prev_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowLeft))
        self.prev_btn.clicked.connect(lambda: self.prevBtnAction(self.width_scale, self.folder_path, self.file_index))

        self.next_btn = QPushButton()
        self.next_btn.setEnabled(False)
        self.next_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        self.next_btn.clicked.connect(lambda: self.nextBtnAction(self.width_scale, self.folder_path, self.file_index))

        self.control_button_layout = QHBoxLayout()
        self.control_button_layout.addWidget(self.prev_btn)
        self.control_button_layout.addWidget(self.next_btn)
        self.main_layout.addLayout(self.control_button_layout)

        self.main_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.show()

    """
        사진 폴더 열기 기능관련 함수
    """
    def getFolderPathByOpenDir(self):
        folder_path = str(QFileDialog.getExistingDirectory(self, "이미지 폴더 불러오기"))
        try: 
            file_list = os.listdir(folder_path)
        except FileNotFoundError:
            return
        self.predict_file_name_list = self.getFileNameList(True, file_list)
        self.actual_file_name_list = self.getFileNameList(False, file_list)

        self.file_name_list = self.getSameNameList(self.getFileNameList(True, file_list), self.getFileNameList(False, file_list))
        if len(self.file_name_list) == 0:
            return

        return folder_path

    def setScaledImage(self, scale, folder_path, index):
        if folder_path == None:
            QMessageBox.warning(self, '알림', '사용할 수 없는 폴더입니다.')
            return
        self.setImage(scale, folder_path, index, False)
        self.setImage(scale, folder_path, index, True)
        self.folder_path = folder_path
        
    def setImage(self, scale, folder_path, index, isPredict):
        pixmap = QtGui.QPixmap(self.getFilePath(folder_path, index, isPredict))
        pixmap = pixmap.scaledToWidth(scale)

        if index == 0 and self.file_count > 1:
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(True)
        elif index == 0 and self.file_count <= 1:
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
        elif index == self.file_count - 1:
            self.prev_btn.setEnabled(True)
            self.next_btn.setEnabled(False)
        else:
            self.prev_btn.setEnabled(True)
            self.next_btn.setEnabled(True)

        if isPredict:
            self.predict_image_label.setPixmap(pixmap)
        else:
            self.actual_image_label.setPixmap(pixmap)
        
    def getFilePath(self, folder_path, index, isPredict):
        self.file_count = len(self.file_name_list)
        if isPredict:
            return folder_path + '/res_' + self.file_name_list[index] + '.jpg'
        else:
            return folder_path + '/save_' + self.file_name_list[index] + '.jpg'

    def getSameNameList(self, predict_file_name_list, actual_file_name_list):
        same_name_list = []
        for i in range(len(predict_file_name_list)):
            if predict_file_name_list[i].split('_', maxsplit=1)[1] == actual_file_name_list[i].split('_', maxsplit=1)[1]:
                same_name_list.append(predict_file_name_list[i].split('_', maxsplit=1)[1])
        return same_name_list


    def getFileNameList(self, isPredict, file_list):
        file_name_list = []
        for file in file_list:
            file_name, file_ext = os.path.splitext(file)
            if file_ext == '.jpg' and not isPredict:
                if not file_name.startswith('save'):
                    continue
                file_name_list.append(file_name)
            elif file_ext == '.jpg' and isPredict:
                if not file_name.startswith('res'):
                    continue
                file_name_list.append(file_name)

        return file_name_list

    def prevBtnAction(self, scale, folder_path, index):
        self.setScaledImage(scale, folder_path, index-1)
        self.file_index = index - 1

    def nextBtnAction(self, scale, folder_path, index):
        self.setScaledImage(scale, folder_path, index+1)
        self.file_index = index + 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LabelingMain()
    app.installEventFilter(window)
    sys.exit(app.exec_())