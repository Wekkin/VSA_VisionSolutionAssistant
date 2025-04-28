from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QFrame, QListWidget, QListWidgetItem, QApplication, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
import sys, os

class FileUploadCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet('''
            QFrame {border:2px dashed #d9d9d9; border-radius:12px; background:#fff;}
            QPushButton {background:#222; color:white; border-radius:4px; padding:8px 24px;}
            QPushButton:hover {background:#1890ff;}
        ''')
        self.setAcceptDrops(True)
        self.file_path = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        self.icon = QLabel()
        self.icon.setPixmap(QPixmap(':/icons/upload.png').scaled(48,48,Qt.KeepAspectRatio) if QIcon.hasThemeIcon('upload') else QPixmap())
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setText('\n⬆')
        self.icon.setStyleSheet('font-size:40px;color:#bfbfbf;')
        layout.addWidget(self.icon)
        self.tip = QLabel('拖拽结构图到此处，或点击上传\n支持 PNG、JPG、PDF 格式')
        self.tip.setAlignment(Qt.AlignCenter)
        self.tip.setStyleSheet('color:#888;font-size:15px;')
        layout.addWidget(self.tip)
        self.upload_btn = QPushButton('选择文件上传')
        self.upload_btn.clicked.connect(self.open_file)
        layout.addWidget(self.upload_btn)
        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setStyleSheet('margin-top:12px;')
        layout.addWidget(self.preview)
        self.del_btn = QPushButton('删除文件')
        self.del_btn.setStyleSheet('background:#f5f5f5;color:#ff4d4f;')
        self.del_btn.clicked.connect(self.delete_file)
        self.del_btn.hide()
        layout.addWidget(self.del_btn)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, '选择结构图', '', 'Images (*.png *.jpg *.jpeg);;PDF Files (*.pdf)')
        if path:
            self.show_file(path)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path.lower().endswith(('.png','.jpg','.jpeg','.pdf')):
                self.show_file(path)
            else:
                QMessageBox.warning(self, '格式错误', '仅支持PNG/JPG/PDF文件')

    def show_file(self, path):
        self.file_path = path
        fname = os.path.basename(path)
        fsize = os.path.getsize(path)
        size_str = f'{fsize//1024} KB'
        if path.lower().endswith(('.png','.jpg','.jpeg')):
            pix = QPixmap(path).scaled(120,90,Qt.KeepAspectRatio)
            self.preview.setPixmap(pix)
        else:
            self.preview.setPixmap(QPixmap())
            self.preview.setText('PDF文件: '+fname)
        self.tip.setText(f'{fname} ({size_str})')
        self.del_btn.show()

    def delete_file(self):
        self.file_path = None
        self.preview.clear()
        self.tip.setText('拖拽结构图到此处，或点击上传\n支持 PNG、JPG、PDF 格式')
        self.del_btn.hide()

class PlaceholderCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet('QFrame {border:2px dashed #d9d9d9; border-radius:12px; background:#fff;}')
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        # 右上角按钮
        btn_bar = QHBoxLayout()
        btn_bar.addStretch()
        self.edit_btn = QPushButton('进入布局编辑器')
        self.edit_btn.setEnabled(False)
        self.edit_btn.setStyleSheet('background:#f5f5f5;color:#bfbfbf;border-radius:4px;padding:6px 18px;')
        btn_bar.addWidget(self.edit_btn)
        layout.addLayout(btn_bar)
        # 占位图标和文字
        icon = QLabel('''<div style="font-size:48px;color:#bfbfbf;">&#x229E;</div>''')
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)
        tip = QLabel('功能开发中，未来用于模块布局可视化分析')
        tip.setAlignment(Qt.AlignCenter)
        tip.setStyleSheet('color:#888;font-size:16px;margin-top:8px;')
        layout.addWidget(tip)
        layout.addStretch()

class IntegrationAnalyzer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setStyleSheet('background:#fafbfc;')
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(18)
        # 顶部标题
        title_bar = QHBoxLayout()
        title = QLabel('集成分析模块')
        title.setStyleSheet('font-size:20px;font-weight:bold;')
        title_bar.addWidget(title)
        title_bar.addStretch()
        feedback_btn = QPushButton('意见反馈')
        feedback_btn.setStyleSheet('background:#fafafa;color:#888;border-radius:4px;padding:6px 18px;')
        title_bar.addWidget(feedback_btn)
        main_layout.addLayout(title_bar)
        # 副标题
        subtitle = QLabel('用于视觉系统工位集成分析与布局规划')
        subtitle.setStyleSheet('color:#888;font-size:14px;margin-bottom:8px;')
        main_layout.addWidget(subtitle)
        # 上传卡片
        upload_card = FileUploadCard()
        upload_card.setFixedHeight(220)
        main_layout.addWidget(upload_card)
        # 占位可视化卡片
        placeholder = PlaceholderCard()
        placeholder.setFixedHeight(260)
        main_layout.addWidget(placeholder)
        # 说明
        info = QLabel('''<span style="color:#888;">当前为集成分析模块基础功能，更多可视化分析功能正在开发中，敬请期待。</span>''')
        info.setStyleSheet('margin-top:12px;')
        main_layout.addWidget(info)
        main_layout.addStretch()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = IntegrationAnalyzer()
    win.setWindowTitle('集成分析模块')
    win.resize(900, 700)
    win.show()
    sys.exit(app.exec_())
