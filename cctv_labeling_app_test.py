#pytest .\CCTV_Labeling\cctv_labeling_app_test.py
#pytest --cov-report term --cov=[coverage .\CCTV_Labeling\cctv_labeling_app_test.py]
import pytest

import cctv_labeling_app

AVAIL_DIR_OFFSET = './test_images'
UNAVAIL_DIR_OFFSET = './unavail_dir'
AVAIL_SCALE_OFFSET = 920


@pytest.fixture
def app(qtbot):
    test_cctv_app = cctv_labeling_app.LabelingMain()
    qtbot.addWidget(test_cctv_app)

    return test_cctv_app

def test_initValue(app):
    app.initValue(100, AVAIL_DIR_OFFSET, 1)
    assert len(app.file_name_list) > 0

def test_initValue2(app):
    app.initValue(0, UNAVAIL_DIR_OFFSET, 2)
    assert len(app.file_name_list) == 0

def test_initImageAndData(app):
    app.initValue(100, AVAIL_DIR_OFFSET, 1)
    app.initImageAndData(10000, AVAIL_DIR_OFFSET, 2, app.getFileList(AVAIL_DIR_OFFSET))
    assert app.actual_people_count_groupbox.isVisible()

def test_initImageAndData2(app):
    app.initValue(AVAIL_SCALE_OFFSET, AVAIL_DIR_OFFSET, 3)
    app.initImageAndData(500, AVAIL_DIR_OFFSET, 3, app.getFileList(AVAIL_DIR_OFFSET))
    assert app.predict_dumping_yn_groupbox.isVisible()

def test_title(app):
    assert app.windowTitle() == 'CCTV_Verification'

def test_prevBtnAction(app):
    app.initValue(AVAIL_SCALE_OFFSET, AVAIL_DIR_OFFSET, 1)
    app.prevBtnAction(app.width_scale, AVAIL_DIR_OFFSET, 2, app.test_num, app.getFileList(AVAIL_DIR_OFFSET))
    assert app.file_index == 1

def test_prevBtnAction2(app):
    app.initValue(AVAIL_SCALE_OFFSET, AVAIL_DIR_OFFSET, 1)
    app.prevBtnAction(app.width_scale, AVAIL_DIR_OFFSET, 100, app.test_num, app.getFileList(AVAIL_DIR_OFFSET))
    assert app.file_index == 99

def test_nextBtnAction(app):
    app.initValue(AVAIL_SCALE_OFFSET, AVAIL_DIR_OFFSET, 1)
    app.nextBtnAction(app.width_scale, AVAIL_DIR_OFFSET, 2, app.test_num, app.getFileList(AVAIL_DIR_OFFSET))
    assert app.file_index == 3

def test_getFileList(app):
    assert len(app.getFileList(AVAIL_DIR_OFFSET)) > 0

def test_getFileList2(app):
    assert len(app.getFileList(UNAVAIL_DIR_OFFSET)) == 0

def test_calcConfusionMatrixValue(app):
    assert True