from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *

import sys
import os
import json
import cv2

from enum import Enum

APP_NAME = 'CCTV_Verification'
DIR_OFFSET = './test_images'
ACTUAL_OFFSET = 'save'
ACTUAL_JSON_OFFSET = 'json'
BOX_OFFSET = 'box'
PREDICT_OFFSET = 'res'
FILE_SPLITER = '_'
IMAGE_EXT_OFFSET = '.jpg'
DATA_EXT_OFFSET = '.json'
JSON_MODE = True
TEST_NAME_LIST = ['사람 검출 검출률(정밀도, precision)',
                    '사람 검출 신뢰도(재현률, recall)',
                    '투기행위 인식률(정확도, accuracy)']
ACTUAL_COLOR = (0, 255, 0)


class ImageType(Enum):
    ACTUAL = 1
    BOX = 2
    PREDICT = 3
    

class LabelingMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.folder_path = ""
        self.file_index = 0
        self.width_scale = 940
        self.test_num = 1
        self.file_name_list = []
        self.window_size = QtCore.QSize(1920, 1080)
        self.default_pixmap = QtGui.QImage(1920, 1080, QtGui.QImage.Format_RGB888)
        self.default_pixmap.fill(QtGui.qRgb(255, 255, 255))
        self.initUI()

    def initUI(self):
        self.setWindowTitle(APP_NAME)
        self.resize(self.window_size)
        self.showMaximized()

        self.menubar = self.menuBar()
        self.menu_open = self.menubar.addMenu("파일")
        self.menu_open_folder = QAction("폴더 열기", self)
        self.menu_open_folder.triggered.connect(lambda: self.initImageAndData(self.width_scale, self.getFolderPathByFileDialog(), self.test_num))
        # self.log_open = self.menubar.addMenu("로그")
        # self.log_open_folder = QAction("로그 보기", self)
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

        self.test_name_label = QLabel()
        self.test_name_label.setStyleSheet("QLabel{font-size:20pt; font-weight:bold; padding:0px 0px 15px 0px}")
        self.test_name_label.setVisible(False)
        self.main_layout.addWidget(self.test_name_label)

        self.top_text_data_layout = QHBoxLayout()
        self.main_layout.addLayout(self.top_text_data_layout)

        self.json_data_layout = QVBoxLayout()

        def initJsonGroupBox(text_label, value_label):
            groupbox = QGroupBox()
            groupbox.setStyleSheet("QGroupBox{border:1px solid black}")
            groupbox.setVisible(False)
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
        self.precision_value_label = QLabel()
        self.precision_groupbox = initJsonGroupBox(QLabel("Precision: "), self.precision_value_label)
        self.recall_value_label = QLabel()
        self.recall_groupbox = initJsonGroupBox(QLabel("Recall: "), self.recall_value_label)
        self.accuracy_value_label = QLabel()
        self.accuracy_groupbox = initJsonGroupBox(QLabel("Accuracy: "), self.accuracy_value_label)

        self.json_data_layout.addWidget(self.actual_people_count_groupbox)
        self.json_data_layout.addWidget(self.predict_people_count_groupbox)
        self.json_data_layout.addWidget(self.actual_dumping_yn_groupbox)
        self.json_data_layout.addWidget(self.predict_dumping_yn_groupbox)
        self.json_data_layout.addWidget(self.precision_groupbox)
        self.json_data_layout.addWidget(self.recall_groupbox)
        self.json_data_layout.addWidget(self.accuracy_groupbox)
        self.json_data_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.top_text_data_layout.addLayout(self.json_data_layout)

        self.confusion_matrix_layout = QGridLayout()
        def initConfusionMatrixGroupBox(text_label, value_label):
            groupbox = QGroupBox()
            groupbox.setStyleSheet("QGroupBox{border:1px solid black}")
            groupbox.setVisible(False)
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
        self.actual_image_layout = QVBoxLayout()
        self.actual_info_label = QLabel("Actual Image")
        self.actual_info_label.setAlignment(QtCore.Qt.AlignCenter)
        self.actual_info_label.setStyleSheet("QLabel{font-size:20pt; font-weight:bold; padding:10px 0px 10px 0px}")
        self.actual_image_layout.addWidget(self.actual_info_label)
        self.actual_image_label = QLabel()
        self.actual_image_label.setPixmap(QtGui.QPixmap(self.default_pixmap).scaledToWidth(self.width_scale))
        self.actual_image_label.setMargin(3)
        self.actual_image_layout.addWidget(self.actual_image_label)
        self.image_layout.addLayout(self.actual_image_layout)

        self.predict_image_layout = QVBoxLayout()
        self.predict_info_label = QLabel("Predict Image")
        self.predict_info_label.setAlignment(QtCore.Qt.AlignCenter)
        self.predict_info_label.setStyleSheet("QLabel{font-size:20pt; font-weight:bold; padding:10px 0px 10px 0px}")
        self.predict_image_layout.addWidget(self.predict_info_label)
        self.predict_image_label = QLabel()
        self.predict_image_label.setPixmap(QtGui.QPixmap(self.default_pixmap).scaledToWidth(self.width_scale))
        self.predict_image_label.setMargin(3)
        self.predict_image_layout.addWidget(self.predict_image_label)
        self.image_layout.addLayout(self.predict_image_layout)
        self.main_layout.addLayout(self.image_layout)

        self.button_control_layout = QVBoxLayout()
        self.prev_next_btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton()
        self.prev_btn.setEnabled(False)
        self.prev_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowLeft))
        self.prev_btn.clicked.connect(lambda: self.prevBtnAction(self.width_scale, self.folder_path, self.file_index, self.test_num))
        self.prev_next_btn_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton()
        self.next_btn.setEnabled(False)
        self.next_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        self.next_btn.clicked.connect(lambda: self.nextBtnAction(self.width_scale, self.folder_path, self.file_index, self.test_num))
        self.prev_next_btn_layout.addWidget(self.next_btn)
        self.button_control_layout.addLayout(self.prev_next_btn_layout)
        self.main_layout.addLayout(self.button_control_layout)

        self.test_btn_layout = QHBoxLayout()
        self.next_test_btn = QPushButton('다음 테스트')
        self.next_test_btn.setVisible(False)
        self.next_test_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
        self.next_test_btn.clicked.connect(lambda: self.nextTestBtnAction(self.width_scale, self.folder_path, self.test_num))
        self.test_btn_layout.setAlignment(QtCore.Qt.AlignRight)
        self.test_btn_layout.addWidget(self.next_test_btn)
        self.button_control_layout.addLayout(self.test_btn_layout)
        self.main_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.show()

        self.folder_path = DIR_OFFSET
        self.file_name_list = self.getFileList(DIR_OFFSET)
        if len(self.file_name_list) > 0:
            self.initImageAndData(self.width_scale, DIR_OFFSET, self.test_num)


    def getFolderPathByFileDialog(self):
        folder_path = str(QFileDialog.getExistingDirectory(self, "이미지 폴더 불러오기"))
        if len(self.getFileList(folder_path)) != 0:
            self.file_name_list = self.getFileList(folder_path)
            self.folder_path = folder_path
            self.test_num = 1
            self.file_index = 0
            return folder_path
        else:
            return


    def getFileList(self, folder_path):
        try: 
            file_list = os.listdir(folder_path)
        except FileNotFoundError:
            return []

        box_file_name_list = self.getFileNameList(ImageType.BOX, IMAGE_EXT_OFFSET, file_list)

        if JSON_MODE == True:
            actual_file_name_list = self.getSameNameList(self.getFileNameList(ImageType.ACTUAL, IMAGE_EXT_OFFSET, file_list), self.getFileNameList(ImageType.ACTUAL, DATA_EXT_OFFSET, file_list))
            predict_file_name_list = self.getSameNameList(self.getFileNameList(ImageType.PREDICT, IMAGE_EXT_OFFSET, file_list), self.getFileNameList(ImageType.PREDICT, DATA_EXT_OFFSET, file_list))
        else:
            actual_file_name_list = self.getFileNameList(ImageType.ACTUAL, IMAGE_EXT_OFFSET, file_list)
            predict_file_name_list = self.getFileNameList(ImageType.PREDICT, IMAGE_EXT_OFFSET, file_list)

        return self.getMatchedImageList(predict_file_name_list, actual_file_name_list, box_file_name_list)


    def initImageAndData(self, scale, folder_path, test_num):
        """
            Keyword arguments
            scale: use for setImage scale with width
            folder_path: initial value or get from getFolderPathByDir
            test_num: the index of test
        """
        if folder_path == None:
            # if selected cancel in the getFolderPathByDir
            return

        if len(self.file_name_list) == 0:
            QMessageBox.information(self, '알림', '표시할 수 있는 사진이 없습니다.')
            return

        if test_num == 1:
            self.actual_people_count_groupbox.setVisible(True)
            self.predict_people_count_groupbox.setVisible(True)
            self.actual_dumping_yn_groupbox.setVisible(False)
            self.predict_dumping_yn_groupbox.setVisible(False)
            self.precision_groupbox.setVisible(True)
            self.recall_groupbox.setVisible(False)
            self.accuracy_groupbox.setVisible(False)
        elif test_num == 2:
            self.actual_people_count_groupbox.setVisible(True)
            self.predict_people_count_groupbox.setVisible(True)
            self.actual_dumping_yn_groupbox.setVisible(False)
            self.predict_dumping_yn_groupbox.setVisible(False)
            self.precision_groupbox.setVisible(False)
            self.recall_groupbox.setVisible(True)
            self.accuracy_groupbox.setVisible(False)
        elif test_num == 3:
            self.actual_people_count_groupbox.setVisible(False)
            self.predict_people_count_groupbox.setVisible(False)
            self.actual_dumping_yn_groupbox.setVisible(True)
            self.predict_dumping_yn_groupbox.setVisible(True)
            self.precision_groupbox.setVisible(False)
            self.recall_groupbox.setVisible(False)
            self.accuracy_groupbox.setVisible(True)
        else:
            QMessageBox.information(self, '알림', '테스트를 완료하셨습니다.')
            return

        self.file_index = 0
        self.setImageAndData(scale, folder_path, 0, test_num)
        self.test_name_label.setVisible(True)
        self.test_name_label.setText(str(test_num) + '. ' + TEST_NAME_LIST[test_num - 1])
        self.true_positive_groupbox.setVisible(True)
        self.false_negative_groupbox.setVisible(True)
        self.false_positive_groupbox.setVisible(True)
        self.true_negative_groupbox.setVisible(True)

        if JSON_MODE == False:
            self.actual_people_count_groupbox.setVisible(False)
            self.predict_people_count_groupbox.setVisible(False)
            self.actual_dumping_yn_groupbox.setVisible(False)
            self.predict_dumping_yn_groupbox.setVisible(False)
            self.precision_groupbox.setVisible(False)
            self.recall_groupbox.setVisible(False)
            self.accuracy_groupbox.setVisible(False)
            self.true_positive_groupbox.setVisible(False)
            self.false_negative_groupbox.setVisible(False)
            self.false_positive_groupbox.setVisible(False)
            self.true_negative_groupbox.setVisible(False)

        self.setFocus()



    def setImageAndData(self, scale, folder_path, index, test_num):
        if test_num > len(TEST_NAME_LIST):
            return

        if index == 0 and len(self.file_name_list) > 1:
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(True)
            self.next_test_btn.setVisible(False)
        elif index == 0 and len(self.file_name_list) <= 1:
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            self.next_test_btn.setVisible(False)
        elif index == len(self.file_name_list) - 1:
            self.prev_btn.setEnabled(True)
            self.next_btn.setEnabled(False)
            self.next_test_btn.setVisible(True)
        elif index > 0 and index < len(self.file_name_list) - 1:
            self.prev_btn.setEnabled(True)
            self.next_btn.setEnabled(True)
            self.next_test_btn.setVisible(False)
        else:
            return

        self.setScaledImage(scale, folder_path, index, test_num)
        if JSON_MODE == True:
            self.setJsonData(folder_path, index)
            self.setConfusionMatrixValue(folder_path, test_num)


    def setScaledImage(self, scale, folder_path, index, test_num):
        """
            Keyword arguments
            scale: use for setImage scale with width
            index: order of image
        """
        with open(self.getFilePath(folder_path , self.file_name_list[index], ImageType.ACTUAL, DATA_EXT_OFFSET)) as f:
            actual_json = json.load(f)
        image = cv2.imread(self.getFilePath(folder_path, self.file_name_list[index], ImageType.ACTUAL, IMAGE_EXT_OFFSET), cv2.IMREAD_UNCHANGED)
        image = self.drawBBox(image, actual_json['people'])
        image_height, image_width, image_bytesPerPixel = image.shape
        actual_image = QtGui.QImage(image.data, image_width, image_height, image_width * image_bytesPerPixel, QtGui.QImage.Format_RGB888)
        actual_image_pixmap = QtGui.QPixmap.fromImage(actual_image).scaledToWidth(scale)

        if test_num == 1 or test_num == 2:
            self.actual_image_label.setPixmap(actual_image_pixmap)
            self.predict_image_label.setPixmap(QtGui.QPixmap(self.getFilePath(folder_path, self.file_name_list[index], ImageType.BOX, IMAGE_EXT_OFFSET)).scaledToWidth(scale))
            self.setStatusBar(folder_path, index, ImageType.BOX)
        elif test_num == 3:
            self.actual_image_label.setPixmap(actual_image_pixmap)
            self.predict_image_label.setPixmap(QtGui.QPixmap(self.getFilePath(folder_path, self.file_name_list[index], ImageType.PREDICT, IMAGE_EXT_OFFSET)).scaledToWidth(scale))
            self.setStatusBar(folder_path, index, ImageType.PREDICT)
        else:
            return

    
    def drawBBox(self, image, person_list):
        for person in person_list:
            cv2.rectangle(image, (person['box'][0], person['box'][1]), (person['box'][2], person['box'][3]), ACTUAL_COLOR, 2)
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


    def setStatusBar(self, folder_path, index, image_type):
        self.lbl_folder_path.show()
        self.lbl_folder_path_value.setText(folder_path)
        self.lbl_folder_path_value.show()
        self.lbl_file_name.show()
        self.lbl_file_name_value.setText(self.getFileName(self.file_name_list[index], ImageType.ACTUAL, IMAGE_EXT_OFFSET) + ', ' + self.getFileName(self.file_name_list[index], image_type, IMAGE_EXT_OFFSET))
        self.lbl_file_name_value.show()
        self.lbl_index.show()
        self.lbl_index_value.setText(str(index+1))
        self.lbl_index_value.show()


    def setJsonData(self, folder_path, index):
        def getDumping_yn(json):
            dumping_str = ''
            for person in json['people']:
                dumping_str = dumping_str + person['dumping_yn']
            return dumping_str
        with open(self.getFilePath(folder_path , self.file_name_list[index], ImageType.ACTUAL, DATA_EXT_OFFSET)) as f:
            actual_json = json.load(f)
        with open(self.getFilePath(folder_path , self.file_name_list[index], ImageType.PREDICT, DATA_EXT_OFFSET)) as f:
            predict_json = json.load(f)

        self.actual_people_count_value_label.setText(str(len(actual_json['people'])))
        self.actual_dumping_yn_value_label.setText(str(getDumping_yn(actual_json)))
        self.predict_people_count_value_label.setText(str(len(predict_json['people'])))
        self.predict_dumping_yn_value_label.setText(str(getDumping_yn(predict_json)))


    def setConfusionMatrixValue(self, folder_path, test_num):
        true_positive = 0
        false_negative = 0
        false_positive = 0
        true_negative = 0

        def getIOU(box1, box2):
            # box = (x1, y1, x2, y2)
            box1_area = (box1[2] - box1[0] + 1) * (box1[3] - box1[1] + 1)
            box2_area = (box2[2] - box2[0] + 1) * (box2[3] - box2[1] + 1)

            # obtain x1, y1, x2, y2 of the intersection
            x1 = max(box1[0], box2[0])
            y1 = max(box1[1], box2[1])
            x2 = min(box1[2], box2[2])
            y2 = min(box1[3], box2[3])

            # compute the width and height of the intersection
            w = max(0, x2 - x1 + 1)
            h = max(0, y2 - y1 + 1)

            inter = w * h
            iou = inter / (box1_area + box2_area - inter)
            return iou

        if test_num == 1 or test_num == 2:
            for file_name in self.file_name_list:
                with open(self.getFilePath(folder_path , file_name, ImageType.ACTUAL, DATA_EXT_OFFSET)) as f:
                    actual_json = json.load(f)
                with open(self.getFilePath(folder_path , file_name, ImageType.PREDICT, DATA_EXT_OFFSET)) as f:
                    predict_json = json.load(f)
                actual_people = actual_json['people']
                predict_people = predict_json['people']
                for actual_person in actual_people:
                    iou_list = []
                    for predict_person in predict_people:
                        if getIOU(actual_person['box'], predict_person['box']) > 0.5:
                            iou_list.append(getIOU(actual_person['box'], predict_person['box']))
                    if len(iou_list) > 0:
                        # people detected and should reject improper person
                        del predict_people[iou_list.index(max(iou_list))]
                        true_positive += 1
                    else:
                        false_negative += 1
                false_positive += len(predict_people)
                if len(actual_people) == 0 and len(predict_people) == 0:
                    true_negative += 1
                        
        elif test_num == 3:
            for file_name in self.file_name_list:
                with open(self.getFilePath(folder_path , file_name, ImageType.ACTUAL, DATA_EXT_OFFSET)) as f:
                    actual_json = json.load(f)
                with open(self.getFilePath(folder_path , file_name, ImageType.PREDICT, DATA_EXT_OFFSET)) as f:
                    predict_json = json.load(f)
                actual_people = actual_json['people']
                predict_people = predict_json['people']
                for actual_person in actual_people:
                    iou_list = []
                    for predict_person in predict_people:
                        if getIOU(actual_person['box'], predict_person['box']) > 0.5:
                            iou_list.append(getIOU(actual_person['box'], predict_person['box']))
                    if len(iou_list) > 0:
                        # people detected and should reject improper person
                        if actual_person['dumping_yn'] == 'Y' and predict_people[iou_list.index(max(iou_list))]['dumping_yn'] == 'Y':
                            true_positive += 1
                        elif actual_person['dumping_yn'] == 'Y' and predict_people[iou_list.index(max(iou_list))]['dumping_yn'] == 'N':
                            false_negative += 1
                        elif actual_person['dumping_yn'] == 'N' and predict_people[iou_list.index(max(iou_list))]['dumping_yn'] == 'Y':
                            false_positive += 1
                        elif actual_person['dumping_yn'] == 'N' and predict_people[iou_list.index(max(iou_list))]['dumping_yn'] == 'N':
                            true_negative += 1
                        del predict_people[iou_list.index(max(iou_list))]
                    else:
                        false_negative += 1
                false_negative += len(predict_people)
                if len(actual_people) == 0 and len(predict_people) == 0:
                    true_negative += 1
        else:
            return

        self.true_positive_value_label.setText(str(true_positive))
        self.false_negative_value_label.setText(str(false_negative))
        self.false_positive_value_label.setText(str(false_positive))
        self.true_negative_value_label.setText(str(true_negative))
        try:
            self.precision_value_label.setText(str(true_positive / (true_positive + false_positive)))
        except ZeroDivisionError:
            self.precision_value_label.setText(str(true_positive) + '/' + str(true_positive + false_positive))
        try:
            self.recall_value_label.setText(str(true_positive / (true_positive + false_negative)))
        except ZeroDivisionError:
            self.recall_value_label.setText(str(true_positive) + '/' + str(true_positive + false_negative))
        try:
            self.accuracy_value_label.setText(str((true_positive + true_negative) / (true_positive + false_positive + false_negative + true_negative)))
        except ZeroDivisionError:
            self.accuracy_value_label.setText(str(true_positive + true_negative) + '/' + str(true_positive + false_positive + false_negative + true_negative))
        

    def getFilePath(self, folder_path, file_name, image_type, file_ext_offset):
        return folder_path + '/' + self.getFileName(file_name, image_type, file_ext_offset)

    
    def getFileName(self, file_name, image_type, file_ext_offset):
        if image_type == ImageType.ACTUAL:
            return ACTUAL_OFFSET + FILE_SPLITER + file_name + file_ext_offset
        elif image_type == ImageType.BOX:
            return BOX_OFFSET + FILE_SPLITER + file_name + file_ext_offset
        elif image_type == ImageType.PREDICT:
            return PREDICT_OFFSET + FILE_SPLITER + file_name + file_ext_offset


    def getMatchedImageList(self, *list_tuple):
        matched_list = []
        first_flag = 1
        for file_name_list in list_tuple:
            temp_list = []
            for file in file_name_list:
                temp_list.append(file.split(FILE_SPLITER, maxsplit=1)[1])
            if first_flag == 1:
                matched_list = temp_list
                first_flag == 0
            else:
                matched_list = list(set(matched_list) & set(temp_list))

        return sorted(matched_list)


    def getFileNameList(self, image_type, file_ext_offset, file_list):
        file_name_list = []
        for file in file_list:
            file_name, file_ext = os.path.splitext(file)
            if file_ext == file_ext_offset and image_type == ImageType.ACTUAL:
                if not file_name.startswith(ACTUAL_OFFSET):
                    continue
                file_name_list.append(file_name)
            elif file_ext == file_ext_offset and image_type == ImageType.PREDICT:
                if file_name.startswith(PREDICT_OFFSET):
                    file_name_list.append(file_name)
            elif file_ext == file_ext_offset and image_type == ImageType.BOX:
                if file_name.startswith(BOX_OFFSET):
                    file_name_list.append(file_name)
            
        return file_name_list


    def getSameNameList(self, file_list1, file_list2):
        return sorted(list(set(file_list1) & set(file_list2)))


    def prevBtnAction(self, scale, folder_path, index, test_num):
        self.setImageAndData(scale, folder_path, index-1, test_num)
        self.file_index = index - 1
        self.setFocus()


    def nextBtnAction(self, scale, folder_path, index, test_num):
        self.setImageAndData(scale, folder_path, index+1, test_num)
        self.file_index = index + 1
        self.setFocus()


    def nextTestBtnAction(self, scale, folder_path, test_num):
        self.initImageAndData(scale, folder_path, test_num+1)
        self.test_num = self.test_num + 1
        self.setFocus()


    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
        elif e.key() == QtCore.Qt.Key_Left and self.prev_btn.isEnabled():
            self.prevBtnAction(self.width_scale, self.folder_path, self.file_index, self.test_num)
        elif e.key() == QtCore.Qt.Key_Right and self.next_btn.isEnabled():
            self.nextBtnAction(self.width_scale, self.folder_path, self.file_index, self.test_num)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LabelingMain()
    app.installEventFilter(window)
    sys.exit(app.exec_())