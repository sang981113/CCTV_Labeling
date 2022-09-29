from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *

import sys
import os
import json

APP_NAME = 'CCTV_Verification'
ACTUAL_OFFSET = 'save'
PREDICT_OFFSET = 'res'
IMAGE_EXT_OFFSET = '.jpg'
DATA_EXT_OFFSET = '.json'

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
        self.menu_open_folder.triggered.connect(lambda: self.initImageAndData(self.width_scale, self.getFolderPath()))
        self.log_open = self.menubar.addMenu("로그")
        self.log_open_folder = QAction("로그 보기", self)
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

        self.top_text_data_layout = QHBoxLayout()
        self.main_layout.addLayout(self.top_text_data_layout)

        self.json_data_layout = QVBoxLayout()

        def initJsonGroupBox(text_label, value_label):
            groupbox = QGroupBox()
            groupbox.setStyleSheet("QGroupBox{border:1px solid black}")
            layout = QGridLayout()
            groupbox.setLayout(layout)
            text_label.setStyleSheet("QLabel{font-size:15pt; font-weight:bold}")
            value_label.setStyleSheet("QLabel{font-size:15pt; font-weight:bold}")
            layout.addWidget(text_label, 0, 0, 1, 1)
            layout.addWidget(value_label, 0, 1, 1, 1)
            return groupbox

        self.actual_people_count_value_label = QLabel()
        self.actual_people_count_groupbox = initJsonGroupBox(QLabel("실제 사람 수: "), self.actual_people_count_value_label)
        self.predict_people_count_value_label = QLabel()
        self.predict_people_count_groupbox = initJsonGroupBox(QLabel("예측 사람 수: "), self.predict_people_count_value_label)
        self.actual_dumping_yn_value_label = QLabel()
        self.actual_dumping_yn_groupbox = initJsonGroupBox(QLabel("실제 투기 여부: "), self.actual_dumping_yn_value_label)
        self.predict_dumping_yn_value_label = QLabel()
        self.predict_dumping_yn_groupbox = initJsonGroupBox(QLabel("예측 투기 여부: "), self.predict_dumping_yn_value_label)

        self.json_data_layout.addWidget(self.actual_people_count_groupbox)
        self.json_data_layout.addWidget(self.predict_people_count_groupbox)
        self.json_data_layout.addWidget(self.actual_dumping_yn_groupbox)
        self.json_data_layout.addWidget(self.predict_dumping_yn_groupbox)
        self.json_data_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.top_text_data_layout.addLayout(self.json_data_layout)

        self.confusion_matrix_layout = QGridLayout()
        def initConfusionMatrixGroupBox(text_label, value_label):
            groupbox = QGroupBox()
            groupbox.setStyleSheet("QGroupBox{border:1px solid black}")
            layout = QGridLayout()
            groupbox.setLayout(layout)
            text_label.setStyleSheet("QLabel{font-size:20pt; font:Arial}")
            value_label.setStyleSheet("QLabel{font-size:20pt; font:Arial}")
            layout.addWidget(text_label, 0, 0, 1, 1)
            layout.addWidget(value_label, 0, 1, 1, 1)
            return groupbox

        self.true_positive_value_label = QLabel()
        self.true_positive_groupbox = initConfusionMatrixGroupBox(QLabel('True Positive: '), self.true_positive_value_label)
        self.false_negative_value_label = QLabel()
        self.false_negative_groupbox = initConfusionMatrixGroupBox(QLabel('False Negative: '), self.false_negative_value_label)
        self.false_positive_value_label = QLabel()
        self.false_positive_groupbox = initConfusionMatrixGroupBox(QLabel('False Positive: '), self.false_positive_value_label)
        self.true_negative_value_label = QLabel()
        self.true_negative_groupbox = initConfusionMatrixGroupBox(QLabel('True Negative: '), self.true_negative_value_label)
        self.confusion_matrix_layout.addWidget(self.true_positive_groupbox, 0, 0, 1, 1)
        self.confusion_matrix_layout.addWidget(self.false_negative_groupbox, 0, 2, 1, 1)
        self.confusion_matrix_layout.addWidget(self.false_positive_groupbox, 1, 0, 1, 1)
        self.confusion_matrix_layout.addWidget(self.true_negative_groupbox, 1, 2, 1, 1)
        self.confusion_matrix_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.top_text_data_layout.addLayout(self.confusion_matrix_layout)

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
        사진폴더 열기 관련 기능
    """
    def getFolderPath(self):
        folder_path = str(QFileDialog.getExistingDirectory(self, "이미지 폴더 불러오기"))
        try: 
            file_list = os.listdir(folder_path)
        except FileNotFoundError:
            return

        predict_file_name_list = self.getSameNameList(self.getFileNameList(True, IMAGE_EXT_OFFSET, file_list), self.getFileNameList(True, DATA_EXT_OFFSET, file_list))
        actual_file_name_list = self.getSameNameList(self.getFileNameList(False, IMAGE_EXT_OFFSET, file_list), self.getFileNameList(False, DATA_EXT_OFFSET, file_list))
        self.file_name_list = self.getMatchedImageList(predict_file_name_list, actual_file_name_list)
        self.file_count = len(self.file_name_list)
        if len(self.file_name_list) == 0:
            return
        self.folder_path = folder_path
        
        return folder_path

    def setConfusionMatrixValue(self):
        true_positive = 0
        false_negative = 0
        false_positive = 0
        true_negative = 0
        for file_name in self.file_name_list:
            with open('test_images/' + ACTUAL_OFFSET + '_' + file_name + DATA_EXT_OFFSET) as f:
                actual_json = json.load(f)
            with open('test_images/' + PREDICT_OFFSET + '_' + file_name + DATA_EXT_OFFSET) as f:
                predict_json = json.load(f)
            if actual_json['people'] == 0 and predict_json['people'] == 0:
                true_negative += 1
            elif actual_json['people'] == predict_json['people']:
                true_positive += 1
            elif actual_json['people'] > predict_json['people']:
                false_negative += 1
            elif actual_json['people'] < predict_json['people']:
                false_positive += 1
            else:
                continue
        self.true_positive_value_label.setText(str(true_positive))
        self.false_negative_value_label.setText(str(false_negative))
        self.false_positive_value_label.setText(str(false_positive))
        self.true_negative_value_label.setText(str(true_negative))

    def initImageAndData(self, scale, folder_path):
        self.setImageAndData(scale, folder_path, 0)
        self.setConfusionMatrixValue()

    def setImageAndData(self, scale, folder_path, index):
        if folder_path == None:
            QMessageBox.warning(self, '알림', '사용할 수 없는 폴더입니다.')
            return
        self.setScaledImage(scale, folder_path, index)
        self.setJsonData(index)

    """
        JSON 데이터 표시 관련 기능
    """
    def setJsonData(self, index):
        with open('test_images/' + ACTUAL_OFFSET + '_' + self.file_name_list[index] + DATA_EXT_OFFSET) as f:
            actual_json = json.load(f)
        with open('test_images/' + PREDICT_OFFSET + '_' + self.file_name_list[index] + DATA_EXT_OFFSET) as f:
            predict_json = json.load(f)

        self.actual_people_count_value_label.setText(str(actual_json['people']))
        self.actual_dumping_yn_value_label.setText(str(actual_json['dumping_yn']))
        self.predict_people_count_value_label.setText(str(predict_json['people']))
        self.predict_dumping_yn_value_label.setText(str(predict_json['dumping_yn']))

    """
        이미지 표시 관련 기능
    """
    def setScaledImage(self, scale, folder_path, index):
        self.setImage(scale, folder_path, index, False)
        self.setImage(scale, folder_path, index, True)

        if index == 0 and self.file_count > 1:
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(True)
        elif index == 0 and self.file_count <= 1:
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
        elif index >= self.file_count - 1:
            self.prev_btn.setEnabled(True)
            self.next_btn.setEnabled(False)
        else:
            self.prev_btn.setEnabled(True)
            self.next_btn.setEnabled(True)

        self.lbl_folder_path.show()
        self.lbl_folder_path_value.setText(folder_path)
        self.lbl_folder_path_value.show()
        self.lbl_file_name.show()
        self.lbl_file_name_value.setText(ACTUAL_OFFSET + '_' + self.file_name_list[index] + IMAGE_EXT_OFFSET + ', ' + PREDICT_OFFSET + '_' + self.file_name_list[index] + IMAGE_EXT_OFFSET)
        self.lbl_file_name_value.show()
        self.lbl_index.show()
        self.lbl_index_value.setText(str(index+1))
        self.lbl_index_value.show()
        
    def setImage(self, scale, folder_path, index, isPredict):
        pixmap = QtGui.QPixmap(self.getFilePath(folder_path, index, isPredict))
        pixmap = pixmap.scaledToWidth(scale)

        if isPredict:
            self.predict_image_label.setPixmap(pixmap)
        else:
            self.actual_image_label.setPixmap(pixmap)
        
    def getFilePath(self, folder_path, index, isPredict):
        if isPredict:
            return folder_path + '/' + PREDICT_OFFSET + '_' + self.file_name_list[index] + IMAGE_EXT_OFFSET
        else:
            return folder_path + '/' + ACTUAL_OFFSET + '_' + self.file_name_list[index] + IMAGE_EXT_OFFSET

    def getMatchedImageList(self, predict_file_name_list, actual_file_name_list):
        predict_name_list = []
        actual_name_list = []
        for file in predict_file_name_list:
            predict_name_list.append(file.split('_', maxsplit=1)[1])

        for file in actual_file_name_list:
            actual_name_list.append(file.split('_', maxsplit=1)[1])

        return list(set(predict_name_list) & set(actual_name_list))


    def getFileNameList(self, isPredict, file_ext_offset, file_list):
        file_name_list = []
        for file in file_list:
            file_name, file_ext = os.path.splitext(file)
            if file_ext == file_ext_offset and not isPredict:
                if not file_name.startswith(ACTUAL_OFFSET):
                    continue
                file_name_list.append(file_name)
            elif file_ext == file_ext_offset and isPredict:
                if not file_name.startswith(PREDICT_OFFSET):
                    continue
                file_name_list.append(file_name)
            elif file_ext == file_ext_offset and isPredict:
                if not file_name.startswith(PREDICT_OFFSET):
                    continue
                file_name_list.append(file_name)

        return file_name_list

    def getSameNameList(self, file_list1, file_list2):
        name_list1 = []
        name_list2 = []

        for file in file_list1:
            file_name, _ = os.path.splitext(file)
            name_list1.append(file_name)
        
        for file in file_list2:
            file_name, _ = os.path.splitext(file)
            name_list2.append(file_name)
        
        return list(set(name_list1) & set(name_list2))

    def prevBtnAction(self, scale, folder_path, index):
        self.setImageAndData(scale, folder_path, index-1)
        self.file_index = index - 1

    def nextBtnAction(self, scale, folder_path, index):
        self.setImageAndData(scale, folder_path, index+1)
        self.file_index = index + 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LabelingMain()
    app.installEventFilter(window)
    sys.exit(app.exec_())