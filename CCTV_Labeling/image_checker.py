import os
import shutil
import sys
import cv2

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *

APP_NAME = "이미지 결과 확인"

class ImageChecker(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.index = 0
        self.event_stack = []
        self.delete_stack = []
        self.save_stack = []
        self.window_size = QtCore.QSize(1920, 1080)
        self.default_image_pixmap = QtGui.QImage(1600, 900, QtGui.QImage.Format_RGB888)
        self.default_image_pixmap.fill(QtGui.qRgb(255, 255, 255))
        self.image_folder = Folder()
        self.save_folder = Folder()
        self.initView()
        self.show()
        
    def initView(self):
        self.setWindowTitle(APP_NAME)
        self.resize(self.window_size)
        self.showMaximized()

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

        self.menubar = self.menuBar()
        self.menu_open = self.menubar.addMenu("파일")
        self.menu_open_folder = QAction("폴더 열기", self)
        self.menu_open_folder.triggered.connect(lambda: self.updateImageFolder(self.image_folder, str(QFileDialog.getExistingDirectory(self, "이미지 폴더 불러오기"))))
        self.menu_open.addAction(self.menu_open_folder)
        self.menu_open_save_folder = QAction("저장 폴더 지정", self)
        self.menu_open_save_folder.triggered.connect(lambda: self.openSaveFolder(self.save_folder))
        self.menu_open.addAction(self.menu_open_save_folder)

        self.image_label = QLabel()
        self.image_label.setPixmap(QtGui.QPixmap(self.default_image_pixmap))
        self.main_layout.addWidget(self.image_label, 0, QtCore.Qt.AlignCenter)

    def setStatusBar(self, file_list, index):
        self.lbl_folder_path.show()
        self.lbl_folder_path_value.setText(file_list[index].folder_path)
        self.lbl_folder_path_value.show()
        self.lbl_file_name.show()
        self.lbl_file_name_value.setText(file_list[index].file_name)
        self.lbl_file_name_value.show()
        self.lbl_index.show()
        self.lbl_index_value.setText(str(index+1) + '/' + str(len(file_list)))
        self.lbl_index_value.show()

    def updateImageFolder(self, image_folder, folder_path):
        image_folder.updateFiles(folder_path)
        self.showImage(image_folder.file_list, 0)
        self.index = 0
        self.event_stack = []
        self.delete_stack = []
        self.save_stack = []

    def openSaveFolder(self, folder):
        folder_path = str(QFileDialog.getExistingDirectory(self, "복사 폴더 불러오기"))
        folder.folder_path = folder_path

    def showImage(self, file_list, index):
        if len(file_list) == 0:
            self.image_label.setPixmap(QtGui.QPixmap(self.default_image_pixmap))
            QMessageBox.warning(self, '알림', '폴더에 사진이 없습니다.')
        else:
            self.image_label.setPixmap(self.readImage(file_list[index]).scaledToWidth(1600))
            self.setStatusBar(file_list, index)

    def readImage(self, file):
        image = cv2.imread(os.path.join(file.folder_path, file.file_name))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_height, image_width, image_bytesPerPixel = image.shape
        image_Qimage = QtGui.QImage(image.data, image_width, image_height, image_width * image_bytesPerPixel, QtGui.QImage.Format_RGB888)
        image_pixmap = QtGui.QPixmap.fromImage(image_Qimage)
        return image_pixmap

    def removeImage(self, file_list, index):
        try:
            os.remove(os.path.join(file_list[index].folder_path, file_list[index].file_name))
        except:
            QMessageBox.warning(self, '오류', '사진 삭제에 실패했습니다.')
        file_list = file_list[:index] + file_list[index + 1:]
        self.image_folder.file_list = file_list
        if index >= len(file_list):
            self.index = len(file_list)-1
            self.showImage(file_list, len(file_list)-1)
        else:
            self.showImage(file_list, index)

    def copyImage(self, file_list, index, save_folder):
        if save_folder.folder_path == "":
            QMessageBox.warning(self, '알림', '복사할 폴더를 선택해주세요.')
            self.openSaveFolder(save_folder)
        try:
            shutil.copyfile(os.path.join(file_list[index].folder_path, file_list[index].file_name), os.path.join(save_folder.folder_path, file_list[index].file_name))
        except:
            QMessageBox.warning(self, '오류', '사진 복사에 실패했습니다.')

    def prevAction(self, file_list, index):
        self.showImage(file_list, index - 1)

    def nextAction(self, file_list, index):
        self.showImage(file_list, index + 1)

    def deleteAction(self, file_list, index):
        self.removeImage(file_list, index)

    def copyAction(self, file_list, index, save_folder):
        self.copyImage(file_list, index, save_folder)

    def undoAction(self, file_list, index, save_folder, event_stack, delete_stack, save_stack):
        if not event_stack:
            return

        past_event = event_stack.pop()
        if past_event == QtCore.Qt.Key_Left:
            if self.index < len(self.image_folder.file_list) - 1:
                self.nextAction(self.image_folder.file_list, self.index)
                self.index += 1
        elif past_event == QtCore.Qt.Key_Right:
            if self.index > 0:
                self.prevAction(self.image_folder.file_list, self.index)
                self.index -= 1
        elif past_event == QtCore.Qt.Key_D or past_event == QtCore.Qt.Key_Delete:
            file, image = delete_stack.pop()
            cv2.imwrite(os.path.join(file.folder_path, file.file_name), image)
            file_list.append(file)
            file_list.sort(key= lambda file: file.file_name)
            self.index = file_list.index(file)
            self.showImage(file_list, file_list.index(file))
        elif past_event == QtCore.Qt.Key_S or past_event == QtCore.Qt.Key_Insert:
            file = save_stack.pop()
            save_folder.set_file_list(save_folder.folder_path)
            if os.path.isfile(os.path.join(save_folder.folder_path, file.file_name)):
                os.remove(os.path.join(save_folder.folder_path, file.file_name))

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
        elif e.key() == QtCore.Qt.Key_Left:
            if self.index > 0:
                self.prevAction(self.image_folder.file_list, self.index)
                self.index -= 1
                self.event_stack.append(e.key())
        elif e.key() == QtCore.Qt.Key_Right:
            if self.index < len(self.image_folder.file_list) - 1:
                self.nextAction(self.image_folder.file_list, self.index)
                self.index += 1
                self.event_stack.append(e.key())
        elif e.key() == QtCore.Qt.Key_D or e.key() == QtCore.Qt.Key_Delete:
            delete_image = cv2.imread(os.path.join(self.image_folder.file_list[self.index].folder_path, self.image_folder.file_list[self.index].file_name))
            self.delete_stack.append((self.image_folder.file_list[self.index], delete_image))
            self.event_stack.append(e.key())
            try:
                self.deleteAction(self.image_folder.file_list, self.index)
            except:
                self.delete_stack.pop()
                self.event_stack.pop()
        elif e.key() == QtCore.Qt.Key_S or e.key() == QtCore.Qt.Key_Insert:
            self.save_stack.append(self.image_folder.file_list[self.index])
            self.event_stack.append(e.key())
            try:
                self.copyAction(self.image_folder.file_list, self.index, self.save_folder)
            except:
                self.save_stack.pop()
                self.event_stack.pop()
        elif e.key() == QtCore.Qt.Key_R:
            self.undoAction(self.image_folder.file_list, self.index, self.save_folder, self.event_stack, self.delete_stack, self.save_stack)

class Folder():
    def __init__(self, folder_path = "", file_list = []) -> None:
        self.folder_path = folder_path
        self.file_list = file_list
    
    def updateFiles(self, folder_path):
        self.folder_path = folder_path
        self.set_file_list(folder_path)

    def set_file_list(self, folder_path):
        try: 
            file_list = os.listdir(folder_path)
        except FileNotFoundError:
            return []
        image_list = []
        for file_name in file_list:
            _, file_ext =  os.path.splitext(file_name)
            if file_ext != '.jpg':
                continue
            file_name = File(folder_path, file_name)
            image_list.append(file_name)
        
        self.file_list = sorted(image_list, key = lambda file : file.file_name)

class File():
    def __init__(self, folder_path, file_name) -> None:
        self.folder_path = folder_path
        self.file_name = file_name

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageChecker()
    app.installEventFilter(window)
    sys.exit(app.exec_())