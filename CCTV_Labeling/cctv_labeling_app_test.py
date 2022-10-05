#run pytest .\CCTV_Labeling\cctv_labeling_app_test.py
import pytest

import cctv_labeling_app

@pytest.fixture
def app(qtbot):
    test_cctv_app = cctv_labeling_app.LabelingMain()
    qtbot.addWidget(test_cctv_app)

    return test_cctv_app

def test_title(app):
    assert app.windowTitle() == 'CCTV_Verification'

def test_lbl_folder_path_value(app):
    assert app.lbl_folder_path_value.text() == './test_images'

def test_prevBtnAction(app):
    app.file_index = 2
    app.prevBtnAction(app.width_scale, app.folder_path, app.file_index, app.test_num)
    assert app.file_index == 1

def test_nextBtnAction(app):
    app.file_index = 2
    app.nextBtnAction(app.width_scale, app.folder_path, app.file_index, app.test_num)
    assert app.file_index == 3

