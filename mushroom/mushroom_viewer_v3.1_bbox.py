import datetime
import json
import time
import sys
import cv2
import os
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PIL import ImageFont, ImageDraw, Image

APP_NAME = "[BBox] 버섯 라벨링 저작도구"
APP_VERSION = "Ver1.0"

class MushroomMain(QMainWindow):
    json_data = []
    image_data = []
    job_type = 'BBox'
    current_index = 0

    select_object_list = -1
    open_path = None

    MUSHROOM_TYPE = ['mushroom']
    MUSHROOM_TYPE_KOR = ['버섯']

    #이미지 크기가 큰 경우 조절을 위한 변수, 크기와 반비례
    IMAGE_SCALE = 2

    new_segmentaion_list = []

    COLOR_LIST = [(255, 0, 0)]

    COLOR = [
        (0, 255, 255), (255, 0, 255), (0, 0, 255),
        (255, 255, 0), (255, 0, 255), (0, 255, 0), (255, 255, 255), (0, 0, 0)
    ]

    isPressed = False
    select_category = -1

    def __init__(self, *args, **kwargs):
        super(MushroomMain, self).__init__(*args, **kwargs)
        self.setWindowTitle(APP_NAME + " " + APP_VERSION)

        self.main_groupbox = QtWidgets.QGroupBox()
        self.setCentralWidget(self.main_groupbox)
        self.setWindowIcon(QtGui.QIcon('./icon/favicon-32x32.png'))
        self.main_layout = QtWidgets.QGridLayout(self.main_groupbox)

        menubar = self.menuBar()
        menu_folder_open = menubar.addMenu("파일")
        menu_open_folder = QAction("폴더열기", self)
        menu_open_folder.triggered.connect(self.open_folder)
        menu_exit_program = QAction("종료", self)
        menu_exit_program.triggered.connect(qApp.exit)
        menu_folder_open.addAction(menu_open_folder)
        menu_folder_open.addAction(menu_exit_program)

        self.label_title = QtWidgets.QLabel(APP_NAME)
        self.label_title.setFixedHeight(50)

        self.image_label = QLabel()
        self.image_label.setFixedSize(540, 960)
        
        self.object_groupbox = QtWidgets.QGroupBox()
        self.object_groupbox.setFixedHeight(40)
        self.object_area_layout = QtWidgets.QHBoxLayout(self.object_groupbox)
        
        for idx, one_data in enumerate(self.MUSHROOM_TYPE_KOR):
            mushroom_button = QPushButton(one_data + '(' + str(idx+1) + ')') 
            
            mushroom_button.setFixedWidth(100)
            mushroom_button.setFixedHeight(20)
            mushroom_button.pressed.connect(self.categories_pressed)
            mushroom_button.toggled.connect(self.categories_toggled)
            mushroom_button.setCheckable(True)
            mushroom_button.setStyleSheet("font-weight:bold; color:black;")
            mushroom_button.setObjectName(f'mushroom{idx}')

            self.object_area_layout.addWidget(mushroom_button)

        self.object_area_layout.setAlignment(QtCore.Qt.AlignLeft)

        self.control_groupbox = QtWidgets.QGroupBox()
        self.control_groupbox.setFixedHeight(50)
        self.control_area_layout = QtWidgets.QGridLayout(self.control_groupbox)
        
        self.prev_btn = QPushButton()
        self.prev_btn.setEnabled(False)
        self.prev_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowLeft))
        self.prev_btn.clicked.connect(self.prev_action)
        
        self.next_btn = QPushButton()
        self.next_btn.setEnabled(False)
        self.next_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        self.next_btn.clicked.connect(self.next_action)
        
        self.control_area_layout.addWidget(self.prev_btn, 0, 0)
        self.control_area_layout.addWidget(self.next_btn, 0, 1)

        self.job_groupbox = QtWidgets.QGroupBox()
        self.job_area_layout = QtWidgets.QGridLayout(self.job_groupbox)

        self.job_all_label = QLabel('버섯 Object List')
        self.job_all_label.setFixedSize(350, 50)
        
        self.job_area_layout.addWidget(self.job_all_label, 0, 0)
        self.job_area_layout.setAlignment(QtCore.Qt.AlignTop)
        self.job_all_label.setStyleSheet("QLabel{border:1px solid white; background-color:#2C87F0; color:white; font-size:13pt; font-weight:bold; margin:3px 0px 3px 0px; padding:0px 12px 0px 12px}")
        
        self.main_layout.addWidget(self.label_title, 0, 1, 1, 1)
        self.main_layout.addWidget(self.object_groupbox, 1, 1, 1, 1)
        self.main_layout.addWidget(self.image_label, 2, 1, 1, 1)
        self.main_layout.addWidget(self.control_groupbox, 3, 1, 1, 1)
        self.main_layout.addWidget(self.job_groupbox, 1, 2, 3, 1)
        
        self.label_title.setStyleSheet("QLabel{color:black; font-size:17pt; font-weight:bold; margin: 12px 0px 12px 0px;}")
        self.image_label.setStyleSheet("QLabel{background-color:white;}")

        self.image_label.mousePressEvent = self.getBeginMouse
        self.image_label.mouseMoveEvent = self.getDragMouse
        self.image_label.mouseReleaseEvent = self.getStopMouse
        
        self.statusbar = QtWidgets.QStatusBar(self)                 # 하단 상태바
        self.lbl_json_dataset = QtWidgets.QLabel('데이터셋 : ')
        self.lbl_json_dataset_value = QtWidgets.QLabel('')
        self.lbl_json_file_name = QtWidgets.QLabel('파일명 : ')
        self.lbl_json_file_name.hide()
        self.lbl_json_file_name_value = QtWidgets.QLabel('')
        self.lbl_json_file_name_value.hide()
        self.lbl_json_index = QtWidgets.QLabel('인덱스 : ')
        self.lbl_json_index.hide()
        self.lbl_json_index_value = QtWidgets.QLabel()
        self.lbl_json_index_value.hide()

        self.statusbar.addWidget(self.lbl_json_dataset)
        self.statusbar.addWidget(self.lbl_json_dataset_value)
        self.statusbar.addWidget(self.lbl_json_file_name)
        self.statusbar.addWidget(self.lbl_json_file_name_value)
        self.statusbar.addWidget(self.lbl_json_index)
        self.statusbar.addWidget(self.lbl_json_index_value)

        self.setStatusBar(self.statusbar)
        
        self.move(100, 0)


    def hangulFilePathImageRead(self, filePath):
        #파일스트림으로 불러오기
        stream = open(filePath.encode("utf-8"), "rb")
        #스트림 버퍼에 담긴 데이터를 바이트로 추출하기
        bytes = bytearray(stream.read())
        #바이트를 수정에 용이한 넘파이 배열로 변환
        numpyArray = np.asarray(bytes, dtype=np.uint8)

        return cv2.imdecode(numpyArray, cv2.IMREAD_UNCHANGED)


    def is_json_key_present(self, check_json_data, key):
        try:
            buf = check_json_data[key]
        except KeyError:
            return False
        return True


    def prev_action(self):
        # 데이터 저장 체크
        if not self.check_save():
            return

        go_index = self.current_index - 1
        if go_index < 0:
            QtWidgets.QMessageBox.warning(self, "알림", "이전 데이터가 없습니다.")
        else:
            self.setData(go_index)
            self.select_object_list = -1

    def next_action(self):        
        # 데이터 저장 체크
        if not self.check_save():
            return

        go_index = self.current_index + 1
        if go_index > len(self.json_data):
            QtWidgets.QMessageBox.warning(self, "알림", "다음 데이터가 없습니다.")
        else:
            self.setData(go_index)
            self.select_object_list = -1


    # 폴더 열기
    def open_folder(self):
        self.json_data = []
        self.open_path = str(QFileDialog.getExistingDirectory(self, "이미지 파일이 있는 곳을 지정해주세요.", "./tool_mushroom/data"))
        print(self.open_path)
        try: 
            file_list = os.listdir(self.open_path)
        except FileNotFoundError:
            return

        for file in file_list:
            file_full = os.path.join(self.open_path, file)
            file_head, file_ext = os.path.splitext(file_full)

            if '.jpg' == file_ext:
                file_path, file_name = os.path.split(file_head)
                json_file_name = file_head + '.json'

                one_load_json = {'json_file': '', 'data': ''}
                init_json = {
                    "INFO": {
                        "DATASET_NAME": "스마트팜 통합데이터 (버섯)",
                        "DATASET_DETAIL": "(스마트팜 통합데이터_버섯)",
                        "VERSION": "1.0",
                        "LICENSE": "",
                        "CREATE_DATE_TIME": datetime.datetime.now().strftime('%Y-%m-%d %X'),
                        "CONTRIBUTOR": "",
                        "URL": "",
                        "CATEGORY_NAME": "버섯"
                    },
                    "IMAGE": {
                        "IMAGE_URL": "",
                        "IMAGE_FILE_NAME": file_name + '.jpg',
                        "WIDTH": 1080,
                        "HEIGHT": 1920,
                        "ANNOTATION_COUNT": 0
                    },
                    "ANNOTATION_INFO": [                        
                    ],
                    "META": {
                        "DBYHS_SPCHCKN": None,
                        "DBYHS_NORMALITY_ALTERNATIVE": True,
                        "IP_CAMERA_ID": None,
                        "WIND_SPEED": None,
                        "AIR_VELOCITY": None,
                        "TEMPERATURE": None,
                        "HUMIDITY": None,
                        "ILLUMINATION_INTENSITY": None,
                        "CARBON_DIOXIDE": None,
                        "GUIDELINE": None,
                        "IMAGE_CREATE_DATE": "",
                        "IMAGE_CREATE_TIME": "",
                        "IMAGE_CREATE_DAY_OF_WEEK": "",
                        "STIPE_LENGTH": None,
                        "STIPE_THICKNESS": None,
                        "PILEUS_DIAMETER": None,
                        "PILEUS_THICKNESS": None,
                        "GROSS_WEIGHT": None
                    }
                }
                
                one_load_json['json_file'] = json_file_name
                one_load_json['data'] = init_json
                    
                self.json_data.append(one_load_json)

        if len(self.json_data) == 0:
            # json 데이터 없을 경우
            QtWidgets.QMessageBox.warning(self, "알림", "현재 선택한 폴더에는 json 파일이 없습니다.")
            return

        self.total_count = len(self.json_data)

        self.lbl_json_file_name.show()
        self.lbl_json_file_name_value.show()
        self.lbl_json_index.show()
        self.lbl_json_index_value.show()
        
        self.setData(0)


    def setData(self, index):
        self.job_all_label.setEnabled(True)
        data_info = self.json_data[index]['data']
        image_info = data_info['IMAGE']

        category_name = data_info['INFO']['CATEGORY_NAME']
        image_file = image_info['IMAGE_FILE_NAME']

        # self.label_title.setText(data_info['INFO']['DATASET_NAME'] + ' 뷰어')
        #상태 표시줄 변경
        self.lbl_json_dataset_value.setText(data_info['INFO']['DATASET_NAME'])
        self.lbl_json_file_name_value.setText(image_file)
        self.lbl_json_index_value.setText(str(index + 1) + " / " + str(self.total_count))
        
        self.current_index = index

        file_name = os.path.join(self.open_path, image_file)
        
        c_image = self.hangulFilePathImageRead(file_name)
        c_image = cv2.cvtColor(c_image, cv2.COLOR_BGR2RGB)
        c_h, c_w, c_c = c_image.shape

        # 기존에 선택된 리스트 삭제
        if self.job_area_layout.count() > 1:
            for i in range(self.job_area_layout.count() - 1, 0, -1):
                self.job_area_layout.itemAt(i).widget().setParent(None)

        for idx, annotation_data in enumerate(data_info['ANNOTATION_INFO']):
            c_image = self.getBoxImage(category_name, c_image, idx, annotation_data)

        q_image = QtGui.QImage(c_image.data, c_w, c_h, c_w * c_c, QtGui.QImage.Format_RGB888)
        p_ixmap = QtGui.QPixmap.fromImage(q_image)
        p_ixmap = p_ixmap.scaled(int(p_ixmap.width() / self.IMAGE_SCALE), int(p_ixmap.height() / self.IMAGE_SCALE))
        
        self.image_label.setPixmap(p_ixmap)
        self.image_label.resize(p_ixmap.width(), p_ixmap.height())

        self.image_label.show()
        self.current_image = c_image

        if self.current_index == 0:
            self.prev_btn.setEnabled(False)
        else:
            self.prev_btn.setEnabled(True)

        if self.current_index + 1 == len(self.json_data):
            self.next_btn.setEnabled(False)
        else:
            self.next_btn.setEnabled(True)


    def getBoxImage(self, category_name, c_image, idx, annotation_data):
        self.job_type = 'BBox'
        category_text = str(idx + 1) + ' - ' + category_name
            
            # BBox
        x1 = int(annotation_data['BOUNDING_BOX_X_COORDINATE'])
        y1 = int(annotation_data['BOUNDING_BOX_Y_COORDINATE'])
        x2 = int(annotation_data['BOUNDING_BOX_WIDTH'])
        y2 = int(annotation_data['BOUNDING_BOX_HEIGHT'])
            
        c_image = cv2.rectangle(c_image, (x1, y1), (x2+x1, y2+y1), (255,255,255), 5)

        if self.select_object_list == idx:
                # c_image = cv2.rectangle(c_image, (x1, y1), (x2+x1, y2+y1), (0,0,0), 5)
            c_image = cv2.rectangle(c_image, (x1, y1), (x2+x1, y2+y1), (26,109,255), 5)

        img_pil = Image.fromarray(cv2.cvtColor(c_image, cv2.COLOR_BGR2RGB))
        img_draw = ImageDraw.Draw(img_pil)
        img_draw.text((x1, y1+5), category_text, font=ImageFont.truetype('./fonts/gulim.ttc', 45), stroke_width=1, fill=(0, 255, 255))
        c_image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

            # 버섯 Object 리스트 관련
        select_groupbox = QtWidgets.QGroupBox()
        select_groupbox.setObjectName((f'mushroomGroupbox{idx}'))

        select_groupbox.setStyleSheet("QGroupBox{border:1px solid black;}")

        select_area_layout = QtWidgets.QGridLayout(select_groupbox)

        one_label = QtWidgets.QLabel(category_text)
        one_text_label = QtWidgets.QLabel(str(x2) + ' x ' + str(y2))
        one_box_button = QtWidgets.QPushButton()
        one_trash_button = QtWidgets.QPushButton()

        one_box_button.setFixedWidth(45)
        one_trash_button.setFixedWidth(45)

        one_box_button.setIcon(QtGui.QIcon('./icon/box.png'))
        one_box_button.clicked.connect(lambda _, i=idx: self.box_select(i))

        one_trash_button.setIcon(QtGui.QIcon('./icon/trash_icon.png'))
        one_trash_button.clicked.connect(lambda _, i=idx: self.box_delete(i))

        select_area_layout.addWidget(one_label, 0, 0)
        select_area_layout.addWidget(one_text_label, 0, 1)
        select_area_layout.addWidget(one_box_button, 0, 2)
        select_area_layout.addWidget(one_trash_button, 0, 3)

        self.job_area_layout.addWidget(select_groupbox)
        self.job_area_layout.setAlignment(QtCore.Qt.AlignTop)
        return c_image


    def getBeginMouse(self, event):
        #마우스 좌클릭 & 유효한 카테고리 & 바운딩 박스 작업인 경우
        if event.button() == QtCore.Qt.LeftButton and self.select_category >= 0 and self.job_type == 'BBox':
            self.isPressed = True
            self.begin = event.pos()

    def getDragMouse(self, event):
        if self.select_category >= 0 and self.isPressed and self.job_type == 'BBox':
            self.end = event.pos()
            try:
                self.drawBbox(self.current_image.copy())
            except AttributeError:
                return
        

    def getStopMouse(self, event):
        if self.select_category >= 0 and self.isPressed and self.job_type == 'BBox':
            if self.begin == event.pos():
                return
            try:
                self.drawBbox(self.current_image)
            except AttributeError:
                return

            new_bbox = {}
            new_bbox['ID'] = 1
            new_bbox['BOUNDING_BOX_X_COORDINATE'] = min(self.begin.x(), self.end.x()) * self.IMAGE_SCALE
            new_bbox['BOUNDING_BOX_Y_COORDINATE'] = min(self.begin.y(), self.end.y()) * self.IMAGE_SCALE
            new_bbox['BOUNDING_BOX_WIDTH'] = (max(self.begin.x(), self.end.x()) - min(self.begin.x(), self.end.x())) * self.IMAGE_SCALE
            new_bbox['SEGMENTATION'] = None
            new_bbox['BOUNDING_BOX_HEIGHT'] = (max(self.begin.y(), self.end.y()) - min(self.begin.y(), self.end.y())) * self.IMAGE_SCALE
            new_bbox['SEGMENTATION_AREA_TOTAL'] = None
            new_bbox['CROWDSOURSING_OPERATION_ALTERNATIVE'] = None

            self.json_data[self.current_index]['data']['ANNOTATION_INFO'].append(new_bbox)

            self.setData(self.current_index)

            self.isPressed = False
            self.begin = QtCore.QPoint()
            self.end = QtCore.QPoint()
            

    def drawBbox(self, image):
        # BBox
        x1 = self.begin.x() * self.IMAGE_SCALE
        y1 = self.begin.y() * self.IMAGE_SCALE
        x2 = self.end.x() * self.IMAGE_SCALE
        y2 = self.end.y() * self.IMAGE_SCALE

        c_h, c_w, c_c = image.shape
        
        c_image = cv2.rectangle(image, (x1, y1), (x2, y2), (255,255,255), 5)
        img_pil = Image.fromarray(cv2.cvtColor(c_image, cv2.COLOR_BGR2RGB))
        img_draw = ImageDraw.Draw(img_pil)
        font_size = 45
        image_text = 'new'
        img_draw.text((abs(x1 + x2 - font_size * len(image_text) // 2) // 2, abs(y1 + y2 - font_size) // 2), image_text, font=ImageFont.truetype('./fonts/gulim.ttc', font_size), stroke_width=1, fill=(0, 255, 255))
        c_image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

        q_image = QtGui.QImage(c_image.data, c_w, c_h, c_w * c_c, QtGui.QImage.Format_RGB888)
        p_ixmap = QtGui.QPixmap.fromImage(q_image)
        p_ixmap = p_ixmap.scaled(p_ixmap.width() / self.IMAGE_SCALE, p_ixmap.height() / self.IMAGE_SCALE)
        
        self.image_label.setPixmap(p_ixmap)
    

    def box_select(self, idx):
        self.select_object_list = idx
        self.setData(self.current_index)


    def box_delete(self, idx):
        self.json_data[self.current_index]['data']['ANNOTATION_INFO'].pop(idx)
        self.setData(self.current_index)
        
       
    def categories_pressed(self):
        for idx, one_data in enumerate(self.MUSHROOM_TYPE_KOR):
            if self.findChild(QtWidgets.QPushButton, f"mushroom{idx}").isChecked():
                self.findChild(QtWidgets.QPushButton, f"mushroom{idx}").setChecked(False)
                self.findChild(QtWidgets.QPushButton, f"mushroom{idx}").setStyleSheet("font-weight:bold; color:black;")


    def categories_toggled(self):
        for idx, one_data in enumerate(self.MUSHROOM_TYPE_KOR):
            if self.findChild(QtWidgets.QPushButton, f"mushroom{idx}").isChecked() and self.select_category != idx:
                self.findChild(QtWidgets.QPushButton, f"mushroom{idx}").setStyleSheet("font-weight:bold; color:white;" "background-color:rgb%s" % str(self.COLOR_LIST[idx]))
                self.select_category = idx

            elif  self.findChild(QtWidgets.QPushButton, f"mushroom{idx}").isChecked() and self.select_category == idx:
                self.findChild(QtWidgets.QPushButton, f"mushroom{idx}").setChecked(False)
                self.select_category = -1


    def check_save(self):
        # 저장 체크
        if len(self.json_data[self.current_index]['data']['ANNOTATION_INFO']) < 1:
            QtWidgets.QMessageBox.warning(self, '필수입력사항 확인', '선택된 객체가 없습니다.', QtWidgets.QMessageBox.Ok)
            return False

        return True


if __name__ == '__main__':
    # 이미지 파일만 Read 해서 Bbox 그리는 용도 (단순 그리기, 저장 기능 없음)
    app = QtWidgets.QApplication(sys.argv)
    ui = MushroomMain()
    ui.show()

    app.installEventFilter(ui)
    sys.exit(app.exec_())
    