import os
from entity.file import File

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