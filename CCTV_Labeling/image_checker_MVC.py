import os
import sys
import cv2
import shutil

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *

APP_NAME = "이미지 결과 확인"

class ImageCheckerView(QMainWindow):
    key_event_signal = QtCore.pyqtSignal(int)

    def __init__(self):
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

class ImageCheckerController():
    def __init__(self) -> None:
        self._app = QApplication(sys.argv)
        self._view = ImageCheckerView()
        self.folder = Folder()
        self.folder.save_folder = Folder("", [], 0, [], Folder())

        self._view.menu_open_folder.triggered.connect(lambda: self.open_folder(self.folder))
        self._view.menu_open_save_folder.triggered.connect(lambda: self.open_save_folder(self.folder))
        self._view.key_event_signal.connect(self.key_press_event)

    # for pytest
    def get_app(self):
        return self._app

    def key_press_event(self, key):
        if key == QtCore.Qt.Key_Escape:
            self._view.close()
        elif key == QtCore.Qt.Key_Left:
            if self.folder.index > 0:
                self.folder.index -= 1
                self.show_image(self.folder)
        elif key == QtCore.Qt.Key_Right:
            if self.folder.index < len(self.folder.file_list) - 1:
                self.folder.index += 1
                self.show_image(self.folder)
        elif key == QtCore.Qt.Key_D:
            self.delete_image(self.folder)
        elif key == QtCore.Qt.Key_R:
            self.cancel_delete(self.folder)
        elif key == QtCore.Qt.Key_S:
            self.save_image(self.folder)
        elif key == QtCore.Qt.Key_E:
            self.cancel_save(self.folder)

    def set_status_bar(self, folder):
        if len(folder.file_list) == 0:
            self._view.lbl_folder_path.hide()
            self._view.lbl_folder_path_value.hide()
            self._view.lbl_file_name.hide()
            self._view.lbl_file_name_value.hide()
            self._view.lbl_index.hide()
            self._view.lbl_index_value.hide()
            self._view.lbl_iscopied.hide()
        else:
            self._view.lbl_folder_path.show()
            self._view.lbl_folder_path_value.setText(folder.folder_path)
            self._view.lbl_folder_path_value.show()
            self._view.lbl_file_name.show()
            self._view.lbl_file_name_value.setText(folder.file_list[folder.index].file_name)
            self._view.lbl_file_name_value.show()
            self._view.lbl_index.show()
            self._view.lbl_index_value.setText(str(folder.index+1) + '/' + str(len(folder.file_list)))
            self._view.lbl_index_value.show()
            self.set_iscopied_label(folder)

    def set_iscopied_label(self, folder):
        self._view.lbl_iscopied.setText('')
        for save_file in folder.save_folder.file_list:
            if folder.file_list[folder.index].file_name == save_file.file_name:
                self._view.lbl_iscopied.setText('저장됨')
                break
        self._view.lbl_iscopied.show()

    def open_folder(self, folder):
        folder_path = str(QFileDialog.getExistingDirectory(self._view, "이미지 폴더 불러오기"))
        folder.updateFiles(folder_path)
        self.show_image(folder)

    def open_save_folder(self, folder):
        folder_path = str(QFileDialog.getExistingDirectory(self._view, "저장 폴더 불러오기"))
        save_folder = Folder()
        save_folder.updateFiles(folder_path)
        folder.save_folder = save_folder
        self.set_iscopied_label(folder)

    def show_image(self, folder):
        if len(folder.file_list) == 0:
            self._view.image_label.setPixmap(QtGui.QPixmap(self._view.default_image_pixmap))
            QMessageBox.information(self._view, '알림', '폴더에 사진이 없습니다.')
        else:
            self._view.image_label.setPixmap(self.read_image(folder).scaledToWidth(1600))
        self.set_status_bar(folder)

    def read_image(self, folder):
        try:
            image = cv2.imread(os.path.join(folder.folder_path, folder.file_list[folder.index].file_name))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        except:
            QMessageBox.warning(self._view, '오류', '사진을 가져오지 못했습니다.')
            return self._view.default_image_pixmap
        image_height, image_width, image_bytesPerPixel = image.shape
        image_Qimage = QtGui.QImage(image.data, image_width, image_height, image_width * image_bytesPerPixel, QtGui.QImage.Format_RGB888)
        image_pixmap = QtGui.QPixmap.fromImage(image_Qimage)
        return image_pixmap

    def delete_image(self, folder):
        delete_image = cv2.imread(os.path.join(folder.folder_path, folder.file_list[folder.index].file_name))
        folder.delete_backup.append((folder.file_list[folder.index], delete_image))
        try:
            os.remove(os.path.join(folder.folder_path, folder.file_list[folder.index].file_name))
        except:
            folder.delete_backup.pop()
            QMessageBox.warning(self._view, '오류', '사진 삭제에 실패했습니다.')
            return
        folder.file_list = folder.file_list[:folder.index] + folder.file_list[folder.index + 1:]
        if folder.index >= len(folder.file_list):
            folder.index -= 1
            self.show_image(folder)
        else:
            self.show_image(folder)

    def cancel_delete(self, folder):
        if len(folder.delete_backup) <= 0:
            return
        file, image = folder.delete_backup.pop()
        cv2.imwrite(os.path.join(folder.folder_path, file.file_name), image)
        folder.file_list.append(file)
        folder.file_list.sort(key = lambda file: file.file_name)
        folder.index = folder.file_list.index(file)
        self.show_image(folder)

    def save_image(self, folder):
        if folder.save_folder.folder_path == "":
            QMessageBox.information(self._view, '알림', '저장할 폴더를 선택해주세요.')
            self.open_save_folder(folder)
        try:
            shutil.copyfile(os.path.join(folder.folder_path, folder.file_list[folder.index].file_name), os.path.join(folder.save_folder.folder_path, folder.file_list[folder.index].file_name))
            if not folder.file_list[folder.index] in folder.save_folder.file_list:
                folder.save_folder.file_list.append(folder.file_list[folder.index])
        except:
            QMessageBox.warning(self._view, '오류', '사진 저장에 실패했습니다.')
        self.set_iscopied_label(folder)

    def cancel_save(self, folder):
        if len(folder.save_folder.file_list) <= 0:
            return
        try:
            os.remove(os.path.join(folder.save_folder.folder_path, folder.file_list[folder.index].file_name))
        except FileNotFoundError:
            return
        except:
            QMessageBox.warning(self._view, '오류', '저장된 사진을 삭제하지 못했습니다.')
            return
        for file in folder.save_folder.file_list:
            if file.file_name == folder.file_list[folder.index].file_name:
                del folder.save_folder.file_list[folder.save_folder.file_list.index(file)]
        self.set_iscopied_label(folder)

    def run(self):
        self._view.setFocus()
        self._view.show()
        self._app.exec_()

class Folder():
    def __init__(self, folder_path = "", file_list = [], index = 0, delete_backup = [], save_folder = None) -> None:
        self.folder_path = folder_path
        self.file_list = file_list
        self.index = index
        self.delete_backup = delete_backup
        self.save_folder = save_folder
    
    def updateFiles(self, folder_path):
        self.folder_path = folder_path
        self.set_file_list(folder_path)
        self.index = 0
        self.delete_backup = []

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
            file = File(file_name)
            image_list.append(file)
        
        self.file_list = sorted(image_list, key = lambda file : file.file_name)

class File():
    def __init__(self, file_name) -> None:
        self.file_name = file_name

if __name__ == '__main__':
    image_checker_controller = ImageCheckerController()
    sys.exit(image_checker_controller.run())