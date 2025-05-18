import sys
import sqlite3
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'src', 'Camera.db')

class VisionSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('视觉选型计算器')
        self.setMinimumSize(1200, 700)
        self.cameras = []
        self.lenses = []
        self.init_ui()
        self.load_data()
        self.refresh_camera_box()
        self.refresh_lens_box()
        self.on_camera_changed()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        # 输入区
        input_layout = QHBoxLayout()
        # 相机选择
        input_layout.addWidget(QLabel('选择相机型号:'))
        self.camera_box = QComboBox()
        self.camera_box.currentIndexChanged.connect(self.on_camera_changed)
        input_layout.addWidget(self.camera_box)
        # 镜头规格选择
        input_layout.addWidget(QLabel('选择镜头规格:'))
        self.lens_box = QComboBox()
        self.lens_box.currentIndexChanged.connect(self.on_lens_changed)
        input_layout.addWidget(self.lens_box)
        # FOV输入
        input_layout.addWidget(QLabel('输入FOV长度(mm):'))
        self.fov_input = QLineEdit()
        self.fov_input.setPlaceholderText('如 51')
        self.fov_input.textChanged.connect(self.on_param_changed)
        input_layout.addWidget(self.fov_input)
        # 运动速度输入
        input_layout.addWidget(QLabel('运动速度(mm/s):'))
        self.speed_input = QLineEdit()
        self.speed_input.setPlaceholderText('如 200')
        self.speed_input.textChanged.connect(self.on_param_changed)
        input_layout.addWidget(self.speed_input)
        main_layout.addLayout(input_layout)
        # 参数显示区
        self.param_label = QLabel()
        self.param_label.setFont(QFont('Arial', 11))
        main_layout.addWidget(self.param_label)
        # 结果表格
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            '镜头型号', '焦距(mm)', 'WD', '接口', '工作距离范围', '是否匹配', '像素精度(μm)', '备注'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table, stretch=1)

    def load_data(self):
        # 读取数据库
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # 相机
        c.execute('SELECT Model, ChipSize, ChipWidth, ChipHeight, PixelWidth, PixelHeight, PixelSize, ChipType FROM Camera')
        self.cameras = c.fetchall()
        # 镜头
        c.execute('SELECT Model, FocalLength, WorkingDistance, Interface, MatchingChip FROM Lens')
        self.lenses = c.fetchall()
        conn.close()

    def refresh_camera_box(self):
        self.camera_box.clear()
        for cam in self.cameras:
            self.camera_box.addItem(cam[0])

    def refresh_lens_box(self):
        self.lens_box.clear()
        # 镜头规格可按MatchingChip去重
        specs = set()
        for lens in self.lenses:
            specs.add(lens[4])
        for spec in sorted(specs):
            self.lens_box.addItem(spec)

    def on_camera_changed(self):
        idx = self.camera_box.currentIndex()
        if idx < 0:
            return
        cam = self.cameras[idx]
        # 显示参数
        info = f"芯片尺寸: {cam[1]}  分辨率: {cam[4]}x{cam[5]}  像元: {cam[6]}μm  芯片类型: {cam[7]}"
        self.param_label.setText(info)
        self.on_param_changed()

    def on_lens_changed(self):
        self.on_param_changed()

    def on_param_changed(self):
        # 计算并刷新表格
        try:
            cam_idx = self.camera_box.currentIndex()
            lens_spec = self.lens_box.currentText()
            fov = float(self.fov_input.text()) if self.fov_input.text() else None
            speed = float(self.speed_input.text()) if self.speed_input.text() else None
            if cam_idx < 0 or not lens_spec or not fov:
                self.table.setRowCount(0)
                return
            cam = self.cameras[cam_idx]
            chip_width = float(cam[2])
            chip_height = float(cam[3])
            pixel_width = int(cam[4])
            pixel_height = int(cam[5])
            pixel_size = float(cam[6])
            # 放大倍率
            mag = chip_width / fov
            fov_w = chip_width / mag
            pixel_accuracy = fov / pixel_width * 1000  # μm/像素
            # 最大曝光时间
            max_exp = None
            if speed:
                max_exp = pixel_accuracy / speed
            # 过滤镜头
            lens_rows = []
            for lens in self.lenses:
                if lens[4] == lens_spec:
                    # 镜头型号, 焦距, WD, 接口, 工作距离范围, 是否匹配, 像素精度, 备注
                    match = '√' if mag < 1.2 else '×'
                    remark = ''
                    lens_rows.append([
                        lens[0], lens[1], lens[2], lens[3], lens[4], match, f'{pixel_accuracy:.3f}', remark
                    ])
            self.table.setRowCount(len(lens_rows))
            for i, row in enumerate(lens_rows):
                for j, val in enumerate(row):
                    item = QTableWidgetItem(str(val))
                    if row[5] == '√':
                        item.setBackground(QColor(200, 255, 200))
                    else:
                        item.setBackground(QColor(255, 200, 200))
                    self.table.setItem(i, j, item)
        except Exception as e:
            self.table.setRowCount(0)
            self.param_label.setText(f"参数错误: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = VisionSelector()
    win.show()
    sys.exit(app.exec_()) 