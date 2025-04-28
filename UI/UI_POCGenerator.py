from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QFrame, QTextEdit, QFileDialog, QListWidget, QListWidgetItem, QComboBox, QGridLayout, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QIcon
import sys

class StepBar(QWidget):
    def __init__(self, steps, current_step=0, parent=None):
        super().__init__(parent)
        self.steps = steps
        self.current_step = current_step
        self.initUI()

    def setCurrentStep(self, idx):
        self.current_step = idx
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(0)
        for i, step in enumerate(self.steps):
            step_widget = QWidget()
            step_layout = QVBoxLayout(step_widget)
            step_layout.setContentsMargins(0, 0, 0, 0)
            # 圆形编号
            circle = QLabel(str(i+1) if i > self.current_step else '✓' if i < self.current_step else str(i+1))
            circle.setFixedSize(32, 32)
            circle.setAlignment(Qt.AlignCenter)
            circle.setFont(QFont('Arial', 14, QFont.Bold))
            if i < self.current_step:
                circle.setStyleSheet('background:#1890ff;color:white;border-radius:16px;border:2px solid #1890ff;')
            elif i == self.current_step:
                circle.setStyleSheet('background:white;color:#1890ff;border-radius:16px;border:2px solid #1890ff;')
            else:
                circle.setStyleSheet('background:#f0f2f5;color:#bfbfbf;border-radius:16px;border:2px solid #e8e8e8;')
            # 步骤名称
            label = QLabel(step)
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont('Arial', 10, QFont.Bold))
            if i == self.current_step:
                label.setStyleSheet('color:#1890ff;')
            elif i < self.current_step:
                label.setStyleSheet('color:#bfbfbf;')
            else:
                label.setStyleSheet('color:#bfbfbf;')
            step_layout.addWidget(circle)
            step_layout.addWidget(label)
            layout.addWidget(step_widget)
            # 连接线
            if i < len(self.steps) - 1:
                line = QFrame()
                line.setFixedHeight(2)
                line.setFixedWidth(40)
                line.setStyleSheet('background:#e8e8e8;')
                layout.addWidget(line)
        layout.addStretch()

class RFQCheckStep(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        # 步骤标题
        title = QLabel('RFQ完整性检查')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        layout.addWidget(title)
        # 关键字段区
        self.text = QTextEdit()
        self.text.setPlaceholderText('相机型号: XX-2000\n缺陷类型: 未填写\n检测距离: 500mm\n最小检测尺寸: 未填写\n图像分辨率: 4096x3000')
        self.text.setStyleSheet('font-size:14px;')
        layout.addWidget(self.text)
        # 编辑补充按钮
        edit_btn = QPushButton('编辑补充')
        edit_btn.setStyleSheet('background:#1890ff;color:white;padding:6px 16px;border-radius:4px;')
        layout.addWidget(edit_btn, alignment=Qt.AlignLeft)
        # 上传RFQ文件
        upload_btn = QPushButton('上传RFQ文件')
        upload_btn.setStyleSheet('background:#f0f2f5;color:#1890ff;padding:6px 16px;border-radius:4px;')
        upload_btn.clicked.connect(self.upload_file)
        layout.addWidget(upload_btn, alignment=Qt.AlignLeft)
        layout.addStretch()
    def upload_file(self):
        QFileDialog.getOpenFileName(self, '选择RFQ文件', '', 'PDF Files (*.pdf);;Excel Files (*.xls *.xlsx)')

class DefectMatrixStep(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        title = QLabel('缺陷矩阵生成')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        layout.addWidget(title)
        # 表格占位
        table = QLabel('缺陷类型与检测参数表格（示意）')
        table.setStyleSheet('background:#fafafa;border:1px solid #e8e8e8;padding:32px;border-radius:8px;')
        layout.addWidget(table)
        layout.addStretch()

class ImageUploadStep(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        # 左侧缺陷类型列表
        defect_list = QListWidget()
        for name in ['表面划伤','凹坑','气泡','异物']:
            item = QListWidgetItem(f'📁 {name}')
            defect_list.addItem(item)
        defect_list.setFixedWidth(120)
        layout.addWidget(defect_list)
        # 中间拖拽上传区
        upload_area = QLabel('拖拽图片到此上传')
        upload_area.setAlignment(Qt.AlignCenter)
        upload_area.setStyleSheet('background:#fafafa;border:2px dashed #bfbfbf;border-radius:8px;font-size:16px;')
        layout.addWidget(upload_area, stretch=1)
        # 右侧缩略图区
        thumb_area = QLabel('缩略图预览区')
        thumb_area.setAlignment(Qt.AlignTop)
        thumb_area.setStyleSheet('background:#f5f5f5;border-radius:8px;padding:8px;')
        thumb_area.setFixedWidth(180)
        layout.addWidget(thumb_area)

class LightConfigStep(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        title = QLabel('光照配置')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        layout.addWidget(title)
        form = QLabel('光源类型、角度、亮度等参数表单（示意）')
        form.setStyleSheet('background:#fafafa;border:1px solid #e8e8e8;padding:32px;border-radius:8px;')
        layout.addWidget(form)
        layout.addStretch()

class PPTGenStep(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        title = QLabel('自动生成PPT')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        layout.addWidget(title)
        # 模板选择
        template_box = QComboBox()
        template_box.addItems(['标准模板','简洁模板','深色模板'])
        layout.addWidget(template_box, alignment=Qt.AlignLeft)
        # 图片缩略图区
        thumbs = QHBoxLayout()
        for _ in range(3):
            thumb = QLabel('缩略图')
            thumb.setFixedSize(120,90)
            thumb.setStyleSheet('background:#fafafa;border:1px solid #e8e8e8;border-radius:8px;')
            thumbs.addWidget(thumb)
        layout.addLayout(thumbs)
        # 预览/导出按钮
        btns = QHBoxLayout()
        preview_btn = QPushButton('预览PPT')
        export_btn = QPushButton('导出PPT')
        preview_btn.setStyleSheet('background:#f0f2f5;color:#1890ff;padding:6px 16px;border-radius:4px;')
        export_btn.setStyleSheet('background:#1890ff;color:white;padding:6px 16px;border-radius:4px;')
        btns.addWidget(preview_btn)
        btns.addWidget(export_btn)
        btns.addStretch()
        layout.addLayout(btns)
        layout.addStretch()

class RiskNoteStep(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        title = QLabel('风险备注与标注')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        layout.addWidget(title)
        note = QTextEdit()
        note.setPlaceholderText('为每个缺陷类型添加风险说明、备注...')
        layout.addWidget(note)
        layout.addStretch()

class FolderCleanStep(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        title = QLabel('空文件夹清理')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        layout.addWidget(title)
        info = QLabel('自动检测并列出所有空文件夹，支持一键清理或手动选择删除。')
        info.setStyleSheet('background:#fafafa;border:1px solid #e8e8e8;padding:32px;border-radius:8px;')
        layout.addWidget(info)
        layout.addStretch()

class POCGenerator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.steps = [
            'RFQ完整性检查',
            '缺陷矩阵生成',
            '图片上传',
            '光照配置',
            '自动生成PPT',
            '风险备注与标注',
            '空文件夹清理'
        ]
        self.current_step = 0
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(24, 24, 24, 24)
        # 顶部步骤条
        self.step_bar = StepBar(self.steps, self.current_step)
        main_layout.addWidget(self.step_bar)
        # 内容区
        self.stack = QStackedWidget()
        self.pages = [
            RFQCheckStep(),
            DefectMatrixStep(),
            ImageUploadStep(),
            LightConfigStep(),
            PPTGenStep(),
            RiskNoteStep(),
            FolderCleanStep()
        ]
        for page in self.pages:
            self.stack.addWidget(page)
        main_layout.addWidget(self.stack, stretch=1)
        # 底部按钮区
        btn_bar = QHBoxLayout()
        self.prev_btn = QPushButton('上一步')
        self.next_btn = QPushButton('下一步')
        self.prev_btn.setStyleSheet('background:#f0f2f5;color:#1890ff;padding:8px 32px;border-radius:4px;')
        self.next_btn.setStyleSheet('background:#1890ff;color:white;padding:8px 32px;border-radius:4px;')
        self.prev_btn.clicked.connect(self.prev_step)
        self.next_btn.clicked.connect(self.next_step)
        btn_bar.addStretch()
        btn_bar.addWidget(self.prev_btn)
        btn_bar.addWidget(self.next_btn)
        main_layout.addLayout(btn_bar)
        self.update_btn_state()

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.stack.setCurrentIndex(self.current_step)
            self.step_bar.setCurrentStep(self.current_step)
            self.update_btn_state()

    def next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.stack.setCurrentIndex(self.current_step)
            self.step_bar.setCurrentStep(self.current_step)
            self.update_btn_state()

    def update_btn_state(self):
        self.prev_btn.setEnabled(self.current_step > 0)
        if self.current_step == len(self.steps) - 1:
            self.next_btn.setText('完成')
        else:
            self.next_btn.setText('下一步')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = POCGenerator()
    win.setWindowTitle('POC生成器')
    win.resize(1000, 700)
    win.show()
    sys.exit(app.exec_())
