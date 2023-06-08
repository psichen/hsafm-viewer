import os
import sys
import re
import datetime
import numpy as np
import shutil
import tifffile
from skimage import io
from hsafm_base import HSAFM
import pyqtgraph as pg
pg.setConfigOptions(imageAxisOrder='row-major')
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QListWidget, QLabel, QSlider, QGridLayout, QHBoxLayout, QVBoxLayout, QFileDialog
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction

def bind_key(k):
    def decorator(func):
        def wrapper(self, **kwargs):
            keys = {
                    'j':Qt.Key.Key_J,
                    'k':Qt.Key.Key_K,
                    'h':Qt.Key.Key_H,
                    'l':Qt.Key.Key_L,
                    'w':Qt.Key.Key_W,
                    'b':Qt.Key.Key_B,
                    'v':Qt.Key.Key_V,
                    'z':Qt.Key.Key_Z,
                    ':':Qt.Key.Key_Colon,
                    'space':Qt.Key.Key_Space,
                    '$':Qt.Key.Key_Dollar,
                    '^':Qt.Key.Key_AsciiCircum,
                    '[':Qt.Key.Key_BracketLeft,
                    ']':Qt.Key.Key_BracketRight,
                    }
            if keys[k] in kwargs['keyPressed']:
                func(self, **kwargs)
        return wrapper
    return decorator

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HS-AFM viewer")
        self.resize(1100, 800)
        self.fps = 10
        self.play_stat = 0
        self.autoLevel = 1
        self.keyPressed = []

        lut = [
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [1,0,0],
            [2,0,0],
            [4,0,0],
            [4,0,0],
            [5,0,0],
            [6,0,0],
            [7,0,0],
            [8,0,0],
            [9,0,0],
            [10,0,0],
            [12,0,0],
            [13,0,0],
            [14,0,0],
            [15,0,0],
            [16,0,0],
            [17,0,0],
            [18,0,0],
            [19,0,0],
            [21,0,0],
            [22,0,0],
            [23,0,0],
            [23,0,0],
            [24,0,0],
            [25,0,0],
            [26,0,0],
            [27,0,0],
            [29,0,0],
            [30,0,0],
            [31,0,0],
            [32,0,0],
            [33,0,0],
            [34,0,0],
            [35,0,0],
            [36,0,0],
            [38,0,0],
            [39,0,0],
            [40,0,0],
            [41,0,0],
            [42,0,0],
            [42,0,0],
            [43,0,0],
            [44,0,0],
            [46,0,0],
            [47,0,0],
            [48,0,0],
            [49,0,0],
            [50,0,0],
            [51,0,0],
            [52,0,0],
            [53,0,0],
            [55,0,0],
            [56,0,0],
            [57,0,0],
            [58,0,0],
            [59,0,0],
            [60,0,0],
            [61,0,0],
            [61,0,0],
            [63,0,0],
            [64,0,0],
            [65,0,0],
            [66,0,0],
            [67,0,0],
            [68,0,0],
            [69,0,0],
            [70,0,0],
            [72,0,0],
            [73,0,0],
            [74,0,0],
            [75,0,0],
            [76,0,0],
            [77,0,0],
            [78,0,0],
            [80,0,0],
            [81,0,0],
            [81,0,0],
            [82,0,0],
            [83,0,0],
            [84,0,0],
            [85,0,0],
            [86,0,0],
            [87,1,0],
            [89,3,0],
            [90,5,0],
            [91,7,0],
            [92,8,0],
            [93,10,0],
            [94,12,0],
            [95,14,0],
            [96,15,0],
            [98,17,0],
            [99,19,0],
            [100,21,0],
            [100,21,0],
            [101,22,0],
            [102,24,0],
            [103,26,0],
            [104,28,0],
            [106,29,0],
            [107,31,0],
            [108,33,0],
            [109,34,0],
            [110,36,0],
            [111,38,0],
            [112,40,0],
            [113,41,0],
            [115,43,0],
            [116,45,0],
            [117,47,0],
            [118,48,0],
            [119,50,0],
            [119,50,0],
            [120,52,0],
            [121,54,0],
            [123,55,0],
            [124,57,0],
            [125,59,0],
            [126,60,0],
            [127,62,0],
            [128,64,0],
            [129,66,0],
            [130,67,0],
            [132,69,0],
            [133,71,0],
            [134,73,0],
            [135,74,0],
            [136,76,0],
            [137,78,0],
            [138,80,0],
            [138,80,0],
            [140,81,0],
            [141,83,0],
            [142,85,0],
            [143,86,0],
            [144,88,0],
            [145,90,0],
            [146,92,0],
            [147,93,0],
            [149,95,0],
            [150,97,0],
            [151,99,0],
            [152,100,0],
            [153,102,0],
            [154,104,0],
            [155,106,0],
            [157,107,0],
            [158,109,0],
            [158,109,0],
            [159,111,0],
            [160,112,0],
            [161,114,2],
            [162,116,6],
            [163,118,9],
            [164,119,12],
            [166,121,15],
            [167,123,18],
            [168,125,21],
            [169,126,24],
            [170,128,27],
            [171,130,30],
            [172,132,33],
            [173,133,36],
            [175,135,40],
            [176,137,43],
            [177,139,46],
            [177,139,46],
            [178,140,49],
            [179,142,52],
            [180,144,55],
            [181,145,58],
            [183,147,61],
            [184,149,64],
            [185,151,67],
            [186,152,70],
            [187,154,74],
            [188,156,77],
            [189,158,80],
            [190,159,83],
            [192,161,86],
            [193,163,89],
            [194,165,92],
            [195,166,95],
            [196,168,98],
            [196,168,98],
            [197,170,101],
            [198,171,104],
            [200,173,108],
            [201,175,111],
            [202,177,114],
            [203,178,117],
            [204,180,120],
            [205,182,123],
            [206,184,126],
            [207,185,129],
            [209,187,132],
            [210,189,135],
            [211,191,138],
            [212,192,141],
            [213,194,145],
            [214,196,148],
            [215,197,151],
            [215,197,151],
            [217,199,154],
            [218,201,157],
            [219,203,160],
            [220,204,163],
            [221,206,166],
            [222,208,169],
            [223,210,172],
            [224,211,175],
            [226,213,179],
            [227,215,182],
            [228,217,185],
            [229,218,188],
            [230,220,191],
            [231,222,194],
            [232,223,197],
            [234,225,200],
            [235,227,203],
            [235,227,203],
            [236,229,206],
            [237,230,209],
            [238,232,213],
            [239,234,216],
            [240,236,219],
            [241,237,222],
            [243,239,225],
            [244,241,228],
            [245,243,231],
            [246,244,234],
            [247,246,237],
            [248,248,240],
            [249,249,243],
            [250,251,246],
            [252,253,250],
            [253,255,253],
            ]
        cmap = pg.ColorMap(pos=None, color=lut)

        # central widget
        cw = QWidget()
        layout_main = QHBoxLayout()

        # left widget for file list
        layout_left = QVBoxLayout()
        self.lst_files = QListWidget()

        self.msg = QLabel('cheatsheet\n\n'
                          'select folder\t:\n'
                          'next file\t\t j\n'
                          'previous file\t k\n'
                          'toggle level\t v\n'
                          'toggle play\t space\n'
                          'next frame\t l\n'
                          'previous frame\t h\n'
                          'jump forwards\t w\n'
                          'jump backwards\t b\n'
                          'go to head\t ^\n'
                          'go to end\t $\n'
                          'x10 forwards\t ]\n'
                          'x10 backwards\t [\n'
                          'save\t\t z\n'
                          )
        self.status = QLabel('')

        self.lst_files.setMaximumWidth(200)
        self.lst_files.setMaximumHeight(300)
        self.msg.setMaximumWidth(200)
        self.status.setMaximumWidth(200)

        layout_left.addWidget(self.lst_files)
        layout_left.addWidget(self.msg)
        layout_left.addWidget(self.status)

        # right widget for viewing images
        layout_right = QGridLayout()
        layout_right.setSpacing(0)
        self.view = pg.GraphicsView()
        self.vb = pg.ViewBox(enableMenu=False)
        self.img = pg.ImageItem()
        self.vb.addItem(self.img)
        self.vb.setAspectLocked()
        self.view.setCentralItem(self.vb)
        layout_right.addWidget(self.view, 0,0,3,3)

        self.hist = pg.HistogramLUTWidget()
        self.hist.setImageItem(self.img)
        self.hist.gradient.setColorMap(cmap)
        self.hist.setMaximumWidth(100)
        layout_right.addWidget(self.hist, 0,3)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        layout_right.addWidget(self.slider, 3,0)

        self.index = QLabel()
        layout_right.addWidget(self.index, 3,3)

        # init UI
        self.setCentralWidget(cw)
        cw.setLayout(layout_main)
        layout_main.addLayout(layout_left)
        layout_main.addLayout(layout_right)
        self.view.setFocus()

        # signals and slots
        self.lst_files.currentItemChanged.connect(self.update)
        self.slider.valueChanged.connect(self.update)
        self.timer = QTimer()
        self.timer.timeout.connect(self.change_frame)
        self.view.scene().sigMouseMoved.connect(self.mouseMoved)

    def keyPressEvent(self, e):
        if not e.isAutoRepeat():
            self.keyPressed.append(e.key())
            if not hasattr(self, 'hsafm') and e.key() != Qt.Key.Key_Colon:
                self.status.setText('select folder!')
            else:
                self.action(self.keyPressed)

    def keyReleaseEvent(self, e):
        self.keyPressed.clear()
        if not e.isAutoRepeat():
            if e.key() in [Qt.Key.Key_BracketLeft, Qt.Key.Key_BracketRight]:
                self.stop_accelerated()

    @bind_key(':')
    def select_folder(self, keyPressed):
        self.keyPressed.clear()
        cwd = QFileDialog.getExistingDirectory(self)
        if cwd:
            os.chdir(cwd)
            self.lst_files.clear()
            self.lst_files.addItems([f for f in os.listdir(cwd) if f.endswith(".asd") and not f.startswith("._")])
            self.lst_files.sortItems()
            self.lst_files.setCurrentRow(0)

    @bind_key('j')
    def next_file(self, keyPressed):
        if self.lst_files.currentRow() < self.lst_files.count()-1:
            self.lst_files.setCurrentRow(self.lst_files.currentRow()+1)

    @bind_key('k')
    def prev_file(self, keyPressed):
        if self.lst_files.currentRow() > 0:
            self.lst_files.setCurrentRow(self.lst_files.currentRow()-1)

    def update(self):
        if self.lst_files.currentItem():
            if isinstance(self.sender(), QListWidget):
                file_path = os.path.join(os.getcwd(), self.lst_files.currentItem().text())
                self.hsafm = HSAFM(file_path)

                rec_datetime = datetime.datetime(
                        self.hsafm.yearRec,
                        self.hsafm.monthRec,
                        self.hsafm.dayRec,
                        self.hsafm.hourRec,
                        self.hsafm.minuteRec,
                        self.hsafm.secondRec,
                        )
                rec_duration = datetime.timedelta(milliseconds=self.hsafm.frameAcqTime*self.hsafm.frameNumber[-1])
                rec_datetime -= rec_duration

                self.msg.setText(
                        f"scan range:\t{self.hsafm.xScanRange} x {self.hsafm.yScanRange} nm\n"
                        f"pixels:\t\t{self.hsafm.xPixel} x {self.hsafm.yPixel}\n"
                        f"date:\t\t{rec_datetime.date()}\n"
                        f"time:\t\t{rec_datetime.time()}\n"
                        f"record duration:\t{rec_duration}\n"
                        f"time resolution:\t{self.hsafm.frameAcqTime/1000} s\n"
                        f"comment:\n{self.hsafm.comment}"
                        )

                self.f_curr = 0
                self.f_max = self.hsafm.height.shape[0]-1
                self.slider.setValue(0)
                self.slider.setMinimum(0)
                self.slider.setMaximum(self.f_max)
                self.hist.setHistogramRange(np.min(self.hsafm.height), np.max(self.hsafm.height))
                self.index.setText(f"0/{self.f_max}")

            elif isinstance(self.sender(), QSlider):
                self.f_curr = self.slider.value()
                self.index.setText(f"{self.f_curr}/{self.f_max}")

            if self.autoLevel:
                self.img.clear()
                # self.img.setImage(self.hsafm.height[self.f_curr])
                self.img.setImage(np.flip(self.hsafm.height[self.f_curr], axis=0))
                lvls = np.quantile(self.hsafm.height[self.f_curr], [.005,.995])
                self.hist.setLevels(*lvls)
            else:
                lvls = self.img.getLevels()
                self.img.clear()
                self.img.setImage(np.flip(self.hsafm.height[self.f_curr], axis=0))
                # self.img.setImage(self.hsafm.height[self.f_curr])
                self.hist.setLevels(*lvls)

            self.view.setFocus()

    def change_frame(self):
        self.f_curr = self.slider.value()

        if self.fps>0:
            if self.f_curr == self.f_max:
                self.f_curr = 0
            else:
                self.f_curr += 1
        elif self.fps<0:
            if self.f_curr == 0:
                self.f_curr = self.f_max
            else:
                self.f_curr -= 1
        self.slider.setValue(self.f_curr)

    @bind_key('l')
    def next_frame(self, keyPressed):
        if self.f_curr < self.f_max:
            self.f_curr += 1
        self.slider.setValue(self.f_curr)

    @bind_key('h')
    def prev_frame(self, keyPressed):
        if self.f_curr > 0:
            self.f_curr -= 1
        self.slider.setValue(self.f_curr)

    @bind_key('v')
    def level(self, keyPressed):
        self.autoLevel = 0 if self.autoLevel else 1

    @bind_key('space')
    def play(self, keyPressed):
        self.play_stat = 0 if self.play_stat else 1
        if self.play_stat:
            self.timer.start(abs(int(1000/self.fps)))
        else:
            self.timer.stop()

    @bind_key('w')
    def jump_forward(self, keyPressed):
        f_step = int(self.f_max/5)
        if self.f_curr+f_step > self.f_max:
            self.f_curr = self.f_max
        else:
            self.f_curr += f_step
        self.slider.setValue(self.f_curr)

    @bind_key('b')
    def jump_backward(self, keyPressed):
        f_step = int(self.f_max/5)
        if self.f_curr-f_step < 0:
            self.f_curr = 0
        else:
            self.f_curr -= f_step
        self.slider.setValue(self.f_curr)

    @bind_key('^')
    def go_head(self, keyPressed):
        self.slider.setValue(0)

    @bind_key('$')
    def go_end(self, keyPressed):
        self.slider.setValue(self.f_max)

    @bind_key(']')
    def accelerated_forward(self, keyPressed):
        self.fps = 100
        self.play_stat = 1
        self.timer.start(abs(int(1000/self.fps)))

    @bind_key('[')
    def accelerated_backward(self, keyPressed):
        self.fps = -100
        self.play_stat = 1
        self.timer.start(abs(int(1000/self.fps)))

    def stop_accelerated(self):
        self.fps = 10
        self.play_stat = 0
        self.timer.stop()

    @bind_key('z')
    def save(self, keyPressed):
        save_dir = os.path.join(os.getcwd(), 'selected files')
        save_name = re.search(r"(.*).asd$", self.lst_files.currentItem().text()).groups()[0]

        if not os.path.exists(os.path.join(save_dir, save_name)):
            os.makedirs(os.path.join(save_dir, save_name))

        shutil.copy(os.path.join(os.getcwd(), self.lst_files.currentItem().text()), save_dir)
        tifffile.imwrite(f"{save_dir}/{save_name}/{save_name}.tif", self.hsafm.height, imagej=True, resolution=(self.hsafm.xPixel/self.hsafm.xScanRange, self.hsafm.yPixel/self.hsafm.yScanRange), metadata={'axes':'ZYX', 'unit':'nm', 'finterval':self.hsafm.frameAcqTime/1000})
        self.status.setText('saved!')

    def action(self, keyPressed):
        self.select_folder(keyPressed=keyPressed)
        self.next_file(keyPressed=keyPressed)
        self.prev_file(keyPressed=keyPressed)
        self.next_frame(keyPressed=keyPressed)
        self.prev_frame(keyPressed=keyPressed)
        self.level(keyPressed=keyPressed)
        self.play(keyPressed=keyPressed)
        self.jump_forward(keyPressed=keyPressed)
        self.jump_backward(keyPressed=keyPressed)
        self.go_head(keyPressed=keyPressed)
        self.go_end(keyPressed=keyPressed)
        self.accelerated_forward(keyPressed=keyPressed)
        self.accelerated_backward(keyPressed=keyPressed)
        self.save(keyPressed=keyPressed)

    def mouseMoved(self, e):
        if hasattr(self, 'hsafm'):
            if self.img.sceneBoundingRect().contains(e):
                mouse_point = self.vb.mapSceneToView(e)
                row_max, col_max = self.hsafm.height[self.f_curr].shape
                row = int(row_max-1-mouse_point.y())
                col = int(mouse_point.x())
                height = self.hsafm.height[self.f_curr, row, col]
                self.status.setText('[%d, %d]\nheight:\t%0.2f' % (col, row, height))
            else:
                self.status.setText('')
        else:
            self.status.setText('')


if __name__ == "__main__":
    app = QApplication([])
    win = Window()
    win.show()
    sys.exit(app.exec())
