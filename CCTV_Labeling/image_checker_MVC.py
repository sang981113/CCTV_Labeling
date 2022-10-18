import os
import sys
import cv2

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *

APP_NAME = "이미지 결과 확인"

class ImageCheckerView(QMainWindow):
    key_event_signal = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.window_size = QtCore.QSize(1920, 1080)
        self.default_image_pixmap = QtGui.QImage(1600, 900, QtGui.QImage.Format_RGB888)
        self.default_image_pixmap.fill(QtGui.qRgb(255, 255, 255))

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
        self.menu_open.addAction(self.menu_open_folder)

        self.image_label = QLabel()
        self.image_label.setPixmap(QtGui.QPixmap(self.default_image_pixmap))
        self.main_layout.addWidget(self.image_label, 0, QtCore.Qt.AlignCenter)

    def keyPressEvent(self, e):
        self.key_event_signal.emit(e.key())

class ImageCheckerController():
    def __init__(self) -> None:
        self._app = QApplication(sys.argv)
        self._view = ImageCheckerView()
        self.index = 0
        self.folder = Folder()

        self._view.menu_open_folder.triggered.connect(lambda: self.openFolder())
        self._view.key_event_signal.connect(self.key_press_event)

    def key_press_event(self, key):
        if key == QtCore.Qt.Key_Escape:
            self.close()
        elif key == QtCore.Qt.Key_Left:
            self.prevAction(self.folder.file_list, self.index)
        elif key == QtCore.Qt.Key_Right:
            self.nextAction(self.folder.file_list, self.index)
        elif key == QtCore.Qt.Key_D:
            self.deleteAction(self.folder.file_list, self.index)

    def run(self):
        self._view.setFocus()
        self._view.show()
        self._app.exec_()

    def setStatusBar(self, file_list, index):
        self._view.lbl_folder_path.show()
        self._view.lbl_folder_path_value.setText(file_list[index].folder_path)
        self._view.lbl_folder_path_value.show()
        self._view.lbl_file_name.show()
        self._view.lbl_file_name_value.setText(file_list[index].file_name)
        self._view.lbl_file_name_value.show()
        self._view.lbl_index.show()
        self._view.lbl_index_value.setText(str(index+1) + '/' + str(len(file_list)))
        self._view.lbl_index_value.show()

    def openFolder(self):
        folder_path = str(QFileDialog.getExistingDirectory(self._view, "이미지 폴더 불러오기"))
        self.folder.updateFiles(folder_path)
        self.showImage(self.folder.file_list, 0)
        self.index = 0

    def showImage(self, file_list, index):
        if len(file_list) == 0:
            self._view.image_label.setPixmap(QtGui.QPixmap(self._view.default_image_pixmap))
            QMessageBox.warning(self._view, '알림', '폴더에 사진이 없습니다.')
        else:
            self._view.image_label.setPixmap(self.readImage(file_list[index]).scaledToWidth(1600))
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
            QMessageBox.warning(self._view, '오류', '사진 삭제에 실패했습니다.')
        file_list = file_list[:index] + file_list[index + 1:]
        self.folder.file_list = file_list
        if index >= len(file_list):
            self.prevAction(file_list, len(file_list))
        else:
            self.showImage(file_list, index)

    def prevAction(self, file_list, index):
        if index > 0:
            self.showImage(file_list, index - 1)
            self.index -= 1

    def nextAction(self, file_list, index):
        if index < len(file_list) - 1:
            self.showImage(file_list, index + 1)
            self.index += 1

    def deleteAction(self, file_list, index):
        self.removeImage(file_list, index)


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
    image_checker_controller = ImageCheckerController()
    sys.exit(image_checker_controller.run())