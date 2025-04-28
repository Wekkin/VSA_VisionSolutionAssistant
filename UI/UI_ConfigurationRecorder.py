from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QLineEdit, QFileDialog, QMessageBox, QHeaderView, QApplication, QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import sys
import csv

CAMERA_MODELS = ["海康工业相机", "大华工业相机", "巴斯勒工业相机"]
LENS_MODELS = ["8mm定焦镜头", "12mm变焦镜头", "16mm定焦镜头"]
LIGHT_MODELS = ["环形光源", "条形光源", "面光源"]

class ConfigurationRecorder(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background:#f5f6fa;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)
        # 顶部标题和按钮区
        title_bar = QHBoxLayout()
        title = QLabel("配置记录")
        title.setStyleSheet("font-size:22px;font-weight:bold;")
        title_bar.addWidget(title)
        title_bar.addStretch()
        db_btn = QPushButton("数据库管理")
        db_btn.setToolTip("点击进入数据库物品库维护页面")
        db_btn.setStyleSheet("border:1px solid #1890ff;color:#1890ff;background:white;padding:6px 18px;border-radius:4px;")
        title_bar.addWidget(db_btn)
        main_layout.addLayout(title_bar)
        # 工具栏
        tool_bar = QHBoxLayout()
        add_btn = QPushButton("+ 添加工位配置")
        add_btn.setStyleSheet("background:#1890ff;color:white;padding:8px 24px;border-radius:4px;font-weight:bold;")
        add_btn.clicked.connect(self.add_row)
        tool_bar.addWidget(add_btn)
        tool_bar.addStretch()
        import_btn = QPushButton(QIcon(), "导入配置")
        import_btn.setStyleSheet("background:white;color:#1890ff;border:1px solid #1890ff;padding:6px 16px;border-radius:4px;")
        import_btn.clicked.connect(self.import_config)
        export_btn = QPushButton(QIcon(), "导出配置")
        export_btn.setStyleSheet("background:white;color:#1890ff;border:1px solid #1890ff;padding:6px 16px;border-radius:4px;margin-left:8px;")
        export_btn.clicked.connect(self.export_config)
        tool_bar.addWidget(import_btn)
        tool_bar.addWidget(export_btn)
        main_layout.addLayout(tool_bar)
        # 卡片式表格区
        card = QWidget()
        card.setStyleSheet("background:white;border-radius:12px;padding:16px 8px 8px 8px;box-shadow:0 2px 8px #e8e8e8;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(8, 8, 8, 8)
        # 表格
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "工位编号", "相机型号", "镜头型号", "光源型号", "分辨率(px)", "视野(mm)", "工作距离(mm)", "操作"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet('''
            QTableWidget {border:none; font-size:10px;}
            QHeaderView::section {background:#fafafa;font-weight:bold;font-size:10px;}
            QTableWidget::item {padding: 8px;}
        ''')
        self.table.verticalHeader().setDefaultSectionSize(60)  # 行高
        card_layout.addWidget(self.table)
        main_layout.addWidget(card)
        # 初始化数据
        self.load_demo_data()

    def load_demo_data(self):
        demo = [
            ["WP001", "海康工业相机", "8mm定焦镜头", "环形光源", "1920x1080", "200", "300"],
            ["WP002", "大华工业相机", "12mm变焦镜头", "条形光源", "2448x2048", "150", "400"],
            ["WP003", "巴斯勒工业相机", "16mm定焦镜头", "面光源", "3072x2048", "180", "350"]
        ]
        for row in demo:
            self.add_row(row)

    def add_row(self, data=None):
        row = self.table.rowCount()
        self.table.insertRow(row)
        # 工位编号
        item = QTableWidgetItem(data[0] if data else "")
        self.table.setItem(row, 0, item)
        # 相机型号
        camera = QComboBox()
        camera.addItems(CAMERA_MODELS)
        if data: camera.setCurrentText(data[1])
        camera.setEditable(True)
        self.table.setCellWidget(row, 1, camera)
        # 镜头型号
        lens = QComboBox()
        lens.addItems(LENS_MODELS)
        if data: lens.setCurrentText(data[2])
        lens.setEditable(True)
        self.table.setCellWidget(row, 2, lens)
        # 光源型号
        light = QComboBox()
        light.addItems(LIGHT_MODELS)
        if data: light.setCurrentText(data[3])
        light.setEditable(True)
        self.table.setCellWidget(row, 3, light)
        # 分辨率
        res = QLineEdit(data[4] if data else "")
        self.table.setCellWidget(row, 4, res)
        # 视野
        fov = QLineEdit(data[5] if data else "")
        self.table.setCellWidget(row, 5, fov)
        # 工作距离
        dist = QLineEdit(data[6] if data else "")
        self.table.setCellWidget(row, 6, dist)
        # 操作栏
        op_widget = QWidget()
        op_layout = QHBoxLayout(op_widget)
        op_layout.setContentsMargins(0,0,0,0)
        edit_btn = QPushButton()
        edit_btn.setIcon(QIcon.fromTheme("edit"))
        edit_btn.setToolTip("编辑")
        edit_btn.setFixedSize(24,24)
        edit_btn.setStyleSheet("border:none;")
        del_btn = QPushButton()
        del_btn.setIcon(QIcon.fromTheme("delete"))
        del_btn.setToolTip("删除")
        del_btn.setFixedSize(24,24)
        del_btn.setStyleSheet("border:none;")
        del_btn.clicked.connect(lambda: self.table.removeRow(row))
        op_layout.addWidget(edit_btn)
        op_layout.addWidget(del_btn)
        op_layout.addStretch()
        self.table.setCellWidget(row, 7, op_widget)

    def import_config(self):
        path, _ = QFileDialog.getOpenFileName(self, "导入配置", "", "Excel/CSV Files (*.csv *.xls *.xlsx)")
        if not path:
            return
        # 这里只做CSV演示
        if path.endswith('.csv'):
            try:
                with open(path, newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader)  # 跳过表头
                    for row in reader:
                        if len(row) >= 7:
                            self.add_row(row[:7])
                QMessageBox.information(self, "导入成功", "配置导入成功！")
            except Exception as e:
                QMessageBox.warning(self, "导入失败", f"导入失败: {e}")
        else:
            QMessageBox.warning(self, "暂不支持", "目前仅支持CSV导入演示")

    def export_config(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出配置", "config.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["工位编号", "相机型号", "镜头型号", "光源型号", "分辨率(px)", "视野(mm)", "工作距离(mm)"])
                for row in range(self.table.rowCount()):
                    data = [
                        self.table.item(row, 0).text() if self.table.item(row, 0) else "",
                        self.table.cellWidget(row, 1).currentText(),
                        self.table.cellWidget(row, 2).currentText(),
                        self.table.cellWidget(row, 3).currentText(),
                        self.table.cellWidget(row, 4).text(),
                        self.table.cellWidget(row, 5).text(),
                        self.table.cellWidget(row, 6).text()
                    ]
                    writer.writerow(data)
            QMessageBox.information(self, "导出成功", "配置导出成功！")
        except Exception as e:
            QMessageBox.warning(self, "导出失败", f"导出失败: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ConfigurationRecorder()
    win.setWindowTitle('配置记录')
    win.resize(1100, 600)
    win.show()
    sys.exit(app.exec_())
