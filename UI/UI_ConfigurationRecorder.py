from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QLineEdit, QFileDialog, QMessageBox, QHeaderView, QApplication, QAbstractItemView,
    QDialog, QTableView, QCompleter
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QColor, QFont
import sys
import csv
import pandas as pd
import traceback
from utils.logger import Logger
from utils.path_utils import get_resource_path

CAMERA_MODELS = ["海康工业相机", "大华工业相机", "巴斯勒工业相机"]
LENS_MODELS = ["8mm定焦镜头", "12mm变焦镜头", "16mm定焦镜头"]
LIGHT_MODELS = ["环形光源", "条形光源", "面光源"]

class ERPDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ERP数据查看")
        self.setMinimumSize(1000, 600)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # 创建表格
        self.table = QTableView()
        self.table.setStyleSheet("""
            QTableView {
                border: none;
                background: white;
                gridline-color: #f0f0f0;
            }
            QTableView::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QHeaderView::section {
                background: #fafafa;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #e8e8e8;
                font-weight: bold;
            }
        """)
        
        # 加载ERP数据
        try:
            df = pd.read_csv(get_resource_path('src/ERP.csv'))
            model = QStandardItemModel(df.shape[0], df.shape[1])
            model.setHorizontalHeaderLabels(df.columns)
            for row in range(df.shape[0]):
                for col in range(df.shape[1]):
                    item = QStandardItem(str(df.iat[row, col]))
                    model.setItem(row, col, item)
            self.table.setModel(model)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载ERP数据失败: {str(e)}")
            
        layout.addWidget(self.table)

class ConfigurationRecorder(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = Logger()
        # 读取ERP数据，提取相机和镜头型号
        self.erp_camera_models, self.erp_lens_models = self.load_erp_models()
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background:#f5f6fa;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)
        
        # 顶部标题
        title = QLabel("配置记录")
        title.setStyleSheet("font-size:22px;font-weight:bold;")
        main_layout.addWidget(title)
        
        # 卡片式表格区
        card = QWidget()
        card.setStyleSheet("background:white;border-radius:12px;padding:16px 8px 8px 8px;box-shadow:0 2px 8px #e8e8e8;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(8, 8, 8, 8)
        
        # 多级表头内容
        group_headers = [
            ("相机配置", 3),
            ("缺陷分布", 1),
            ("视野(mm)", 2),
            ("景深", 1),
            ("光圈", 1),
            ("曝光时间", 1),
            ("物料光源距离", 1),
            ("工作距离", 1),
            ("物料尺寸(mm)", 3),
            ("像素大小(mm)", 2),
            ("飞拍速度(mm/s)", 2),
            ("图像节拍", 1),
            ("打光方式", 1),
            ("拍照方式", 1)
        ]
        sub_headers = [
            "相机", "镜头", "微距调节", "区域", "长", "宽", "DOF(mm)", "F", "(ms)", "(mm)", "(mm)",
            "长", "宽", "高", "水平", "垂直", "水平", "垂直", "(s)", "通道", "次", "飞拍or定拍"
        ]
        col_count = sum([span for _, span in group_headers])
        
        # 创建两行表头的表格
        self.table = QTableWidget(0, col_count)
        self.table.setRowCount(0)
        self.table.setColumnCount(col_count)
        self.table.setSpan(0, 0, 1, col_count)  # 先合并首行，后面再拆分
        self.table.setStyleSheet('''
            QTableWidget {border:none; font-size:10px;}
            QHeaderView::section {background:#fafafa;font-weight:bold;font-size:10px;}
            QTableWidget::item {padding: 8px;}
        ''')
        self.table.verticalHeader().setDefaultSectionSize(60)
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 设置相机和镜头列宽及自适应
        self.table.setColumnWidth(0, 220)
        self.table.setColumnWidth(1, 220)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        # 设置多级表头
        self.table.setRowCount(2)
        bold_font = QFont()
        bold_font.setBold(True)
        for i, (text, span) in enumerate(group_headers):
            col = sum([s for _, s in group_headers[:i]])
            self.table.setSpan(0, col, 1, span)
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(QColor("#e3f2fd"))  # 柔和淡蓝色
            item.setFont(bold_font)
            self.table.setItem(0, col, item)
        for i, text in enumerate(sub_headers):
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(QColor("#e8f5e9"))  # 柔和淡绿色
            item.setFont(bold_font)
            self.table.setItem(1, i, item)
        self.table.setVerticalHeaderLabels(["", ""])
        card_layout.addWidget(self.table)
        main_layout.addWidget(card)
        
        # 底部按钮区域
        button_bar = QHBoxLayout()
        button_bar.setContentsMargins(0, 0, 0, 0)
        
        # 添加工位配置按钮
        add_btn = QPushButton("+ 添加工位配置")
        add_btn.setFixedHeight(30)
        add_btn.setStyleSheet("""
            QPushButton {
                background:#1890ff;
                color:white;
                padding:0 24px;
                border-radius:4px;
                font-weight:bold;
            }
            QPushButton:hover {
                background:#40a9ff;
            }
        """)
        add_btn.clicked.connect(self.add_row)
        button_bar.addWidget(add_btn)
        
        # 减少工位配置按钮
        remove_btn = QPushButton("- 减少工位配置")
        remove_btn.setFixedHeight(30)
        remove_btn.setStyleSheet("""
            QPushButton {
                background:#ff7875;
                color:white;
                padding:0 24px;
                border-radius:4px;
                font-weight:bold;
            }
            QPushButton:hover {
                background:#ffb3b3;
            }
        """)
        remove_btn.clicked.connect(self.remove_row)
        button_bar.addWidget(remove_btn)
        
        button_bar.addStretch()
        
        # 右侧按钮组
        right_buttons = QHBoxLayout()
        right_buttons.setSpacing(8)
        
        # ERP数据按钮
        erp_btn = QPushButton("ERP数据")
        erp_btn.setFixedHeight(30)
        erp_btn.setStyleSheet("""
            QPushButton {
                background:white;
                color:#1890ff;
                border:1px solid #1890ff;
                padding:0 16px;
                border-radius:4px;
            }
            QPushButton:hover {
                background:#e6f7ff;
            }
        """)
        erp_btn.clicked.connect(self.show_erp_data)
        
        # 数据库管理按钮
        db_btn = QPushButton("数据库管理")
        db_btn.setFixedHeight(30)
        db_btn.setToolTip("点击进入数据库物品库维护页面")
        db_btn.setStyleSheet("""
            QPushButton {
                border:1px solid #1890ff;
                color:#1890ff;
                background:white;
                padding:0 18px;
                border-radius:4px;
            }
            QPushButton:hover {
                background:#e6f7ff;
            }
        """)
        
        # 导入配置按钮
        import_btn = QPushButton("导入配置")
        import_btn.setFixedHeight(30)
        import_btn.setStyleSheet("""
            QPushButton {
                background:white;
                color:#1890ff;
                border:1px solid #1890ff;
                padding:0 16px;
                border-radius:4px;
            }
            QPushButton:hover {
                background:#e6f7ff;
            }
        """)
        import_btn.clicked.connect(self.import_config)
        
        # 导出配置按钮
        export_btn = QPushButton("导出配置")
        export_btn.setFixedHeight(30)
        export_btn.setStyleSheet("""
            QPushButton {
                background:white;
                color:#1890ff;
                border:1px solid #1890ff;
                padding:0 16px;
                border-radius:4px;
            }
            QPushButton:hover {
                background:#e6f7ff;
            }
        """)
        export_btn.clicked.connect(self.export_config)
        
        # 添加右侧按钮
        right_buttons.addWidget(erp_btn)
        right_buttons.addWidget(db_btn)
        right_buttons.addWidget(import_btn)
        right_buttons.addWidget(export_btn)
        
        button_bar.addLayout(right_buttons)
        main_layout.addLayout(button_bar)
        
        # 初始化只显示一行
        self.add_row()

    def load_demo_data(self):
        demo = [
            ["WP001", "海康工业相机", "8mm定焦镜头", "环形光源", "1920x1080", "200", "300"],
            ["WP002", "大华工业相机", "12mm变焦镜头", "条形光源", "2448x2048", "150", "400"],
            ["WP003", "巴斯勒工业相机", "16mm定焦镜头", "面光源", "3072x2048", "180", "350"]
        ]
        for row in demo:
            self.add_row(row)

    def load_erp_models(self):
        camera_models = []
        lens_models = []
        try:
            df = pd.read_csv(get_resource_path('src/ERP.csv'))
            camera_models = sorted(set(df.loc[df['名称'].astype(str).str.contains('工业相机'), '规格型号'].dropna().astype(str)))
            lens_models = sorted(set(df.loc[df['名称'].astype(str).str.contains('镜头'), '规格型号'].dropna().astype(str)))
        except Exception as e:
            pass  # 读取失败则用空列表
        return camera_models, lens_models

    def add_row(self, data=None):
        try:
            self.logger.info(f"[配置记录] 添加工位配置行, data={data}")
        row = self.table.rowCount()
        self.table.insertRow(row)
        font_css = "font-size:14px; min-width:120px;"
        # 相机 QLineEdit + QCompleter
        camera_edit = QLineEdit(data[0] if data else "")
        camera_edit.setStyleSheet(font_css)
        camera_completer = QCompleter(self.erp_camera_models)
        camera_completer.setCaseSensitivity(Qt.CaseInsensitive)
        camera_edit.setCompleter(camera_completer)
        self.table.setCellWidget(row, 0, camera_edit)
        # 镜头 QLineEdit + QCompleter
        lens_edit = QLineEdit(data[1] if data else "")
        lens_edit.setStyleSheet(font_css)
        lens_completer = QCompleter(self.erp_lens_models)
        lens_completer.setCaseSensitivity(Qt.CaseInsensitive)
        lens_edit.setCompleter(lens_completer)
        self.table.setCellWidget(row, 1, lens_edit)
        # 其余列全部为QLineEdit
        editors = [camera_edit, lens_edit]
        for col in range(2, self.table.columnCount()):
            val = data[col] if data and len(data) > col else ""
            edit = QLineEdit(val)
            edit.setStyleSheet(font_css)
            self.table.setCellWidget(row, col, edit)
            editors.append(edit)
        # 公式自动计算逻辑
        def update_all_auto_fields():
            camera = camera_edit.text().strip()
            try:
                fov_len = float(editors[4].text())  # 视野长
                fov_wid = float(editors[5].text())  # 视野宽
                exposure = float(editors[8].text())  # 曝光时间(ms)
                mat_len = float(editors[11].text())  # 物料尺寸长
            except ValueError:
                editors[14].setText("")
                editors[15].setText("")
                editors[16].setText("")
                editors[17].setText("")
                editors[18].setText("")
                return
            # 像素大小
            if camera == 'a2A2448-75ucBAC':
                px_len = fov_len / 2448
                px_wid = fov_wid / 2048
                speed_h = fov_len / 2448 / exposure * 1000 * 2.56 if exposure > 0 else 0
                speed_v = fov_wid / 2048 / exposure * 1000 * 2.56 if exposure > 0 else 0
            elif camera == 'a2A4096-30ucBAC':
                px_len = fov_len / 4096
                px_wid = fov_wid / 3000
                speed_h = fov_len / 4096 / exposure * 1000 * 2.56 if exposure > 0 else 0
                speed_v = fov_wid / 3000 / exposure * 1000 * 2.56 if exposure > 0 else 0
            else:
                editors[14].setText("")
                editors[15].setText("")
                editors[16].setText("")
                editors[17].setText("")
                editors[18].setText("")
                return
            editors[14].setText(f"{px_len:.5f}")  # 像素大小水平
            editors[15].setText(f"{px_wid:.5f}")  # 像素大小垂直
            editors[16].setText(f"{speed_h:.2f}")  # 飞拍速度水平
            editors[17].setText(f"{speed_v:.2f}")  # 飞拍速度垂直
            # 图像节拍
            if speed_h > 0:
                image_cycle = mat_len / speed_h
                editors[18].setText(f"{image_cycle:.2f}")
            else:
                editors[18].setText("")
        # 绑定信号，确保实时联动
        camera_edit.textChanged.connect(update_all_auto_fields)
        editors[4].textChanged.connect(update_all_auto_fields)  # 视野长
        editors[5].textChanged.connect(update_all_auto_fields)  # 视野宽
        editors[8].textChanged.connect(update_all_auto_fields)  # 曝光时间
        editors[11].textChanged.connect(update_all_auto_fields) # 物料尺寸长
        except Exception as e:
            tb = traceback.format_exc()
            self.logger.error(f"[配置记录] 添加工位配置行异常: {str(e)}\n{tb}")

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
                self.logger.info(f"[配置记录] 导入配置成功: {path}")
                QMessageBox.information(self, "导入成功", "配置导入成功！")
            except Exception as e:
                tb = traceback.format_exc()
                self.logger.error(f"[配置记录] 导入配置失败: {str(e)}\n{tb}")
                QMessageBox.warning(self, "导入失败", f"导入失败: {e}")
        else:
            self.logger.warning(f"[配置记录] 暂不支持的导入格式: {path}")
            QMessageBox.warning(self, "暂不支持", "目前仅支持CSV导入演示")

    def export_config(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出配置", "config.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # 写表头
                headers = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(1, col)
                    headers.append(item.text() if item else "")
                writer.writerow(headers)
                # 写数据
                for row in range(2, self.table.rowCount()):
                    data = []
                    for col in range(self.table.columnCount()):
                        widget = self.table.cellWidget(row, col)
                        if widget is not None:
                            if hasattr(widget, 'text'):
                                data.append(widget.text())
                            elif hasattr(widget, 'currentText'):
                                data.append(widget.currentText())
                            else:
                                data.append("")
                        else:
                            item = self.table.item(row, col)
                            data.append(item.text() if item else "")
                    writer.writerow(data)
            self.logger.info(f"[配置记录] 导出配置成功: {path}")
            QMessageBox.information(self, "导出成功", "配置导出成功！")
        except Exception as e:
            tb = traceback.format_exc()
            self.logger.error(f"[配置记录] 导出配置失败: {str(e)}\n{tb}")
            QMessageBox.warning(self, "导出失败", f"导出失败: {e}")

    def show_erp_data(self):
        """显示ERP数据对话框"""
        dialog = ERPDialog(self)
        dialog.exec_()

    def remove_row(self):
        if self.table.rowCount() > 1:
            self.table.removeRow(self.table.rowCount() - 1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ConfigurationRecorder()
    win.setWindowTitle('配置记录')
    win.resize(1100, 600)
    win.show()
    sys.exit(app.exec_())
