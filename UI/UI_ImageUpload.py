from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QListWidgetItem, QPushButton, QLabel, QFileDialog,
                             QScrollArea, QMessageBox, QInputDialog, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
import os
import json
import shutil

class ImageUploader(QWidget):
    def __init__(self, project_path, parent=None):
        super().__init__(parent)
        self.project_path = project_path
        self.current_station = None
        self.station_images = {}  # 存储工位和图片的对应关系
        self.initUI()
        
    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(16)  # 增加组件之间的间距
        
        # 左侧工位列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 工位列表标题
        station_label = QLabel("工位列表")
        station_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
                color: #262626;
            }
        """)
        left_layout.addWidget(station_label)
        
        # 工位列表
        self.station_list = QListWidget()
        self.station_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e8e8e8;
                border-radius: 4px;
                background: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background: #e6f7ff;
                color: #1890ff;
            }
            QListWidget::item:hover {
                background: #f5f5f5;
            }
        """)
        
        # 添加默认工位
        for i in range(1, 6):
            item = QListWidgetItem(f"工位{i}")
            self.station_list.addItem(item)
        
        # 添加工位按钮
        add_station_btn = QPushButton("+ 添加工位")
        add_station_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #1890ff;
                border: none;
                padding: 8px;
                text-align: left;
            }
            QPushButton:hover {
                color: #40a9ff;
            }
        """)
        add_station_btn.clicked.connect(self.addStation)
        
        left_layout.addWidget(self.station_list)
        left_layout.addWidget(add_station_btn)
        
        # 设置左侧工位列表的固定宽度
        left_widget.setFixedWidth(200)
        
        # 中间预览区域
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        middle_layout.setContentsMargins(0, 0, 0, 0)
        
        # 预览区标题
        preview_label = QLabel("图片预览")
        preview_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
                color: #262626;
            }
        """)
        middle_layout.addWidget(preview_label)
        
        # 预览区
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e8e8e8;
                border-radius: 4px;
                background: white;
            }
        """)
        
        self.preview_widget = QWidget()
        self.preview_layout = QVBoxLayout(self.preview_widget)
        self.preview_layout.setAlignment(Qt.AlignCenter)
        
        # 添加引导文字
        self.guide_label = QLabel("上传实验测试时对应工位的工位布局图片")
        self.guide_label.setStyleSheet("""
            QLabel {
                color: #8c8c8c;
                font-size: 14px;
            }
        """)
        self.guide_label.setAlignment(Qt.AlignCenter)
        self.preview_layout.addWidget(self.guide_label)
        
        self.preview_scroll.setWidget(self.preview_widget)
        middle_layout.addWidget(self.preview_scroll)
        
        # 右侧功能区
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 功能区标题
        function_label = QLabel("功能区")
        function_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
                color: #262626;
            }
        """)
        right_layout.addWidget(function_label)
        
        # 功能按钮容器
        button_container = QFrame()
        button_container.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e8e8e8;
                border-radius: 4px;
                padding: 16px;
            }
        """)
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(12)
        
        # 上传按钮
        self.upload_btn = QPushButton("上传图片")
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background: #1890ff;
                color: white;
                padding: 12px;
                border-radius: 4px;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #40a9ff;
            }
            QPushButton:disabled {
                background: #d9d9d9;
            }
        """)
        self.upload_btn.clicked.connect(self.uploadImages)
        self.upload_btn.setEnabled(False)
        
        # 删除按钮
        self.delete_btn = QPushButton("删除选中图片")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background: #ff4d4f;
                color: white;
                padding: 12px;
                border-radius: 4px;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #ff7875;
            }
            QPushButton:disabled {
                background: #d9d9d9;
            }
        """)
        self.delete_btn.clicked.connect(self.deleteSelectedImages)
        self.delete_btn.setEnabled(False)
        
        # 完成按钮
        self.finish_btn = QPushButton("完成")
        self.finish_btn.setStyleSheet("""
            QPushButton {
                background: #52c41a;
                color: white;
                padding: 12px;
                border-radius: 4px;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #73d13d;
            }
            QPushButton:disabled {
                background: #d9d9d9;
            }
        """)
        self.finish_btn.clicked.connect(self.saveStationImages)
        self.finish_btn.setEnabled(False)
        
        button_layout.addWidget(self.upload_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.finish_btn)
        
        right_layout.addWidget(button_container)
        right_layout.addStretch()
        
        # 设置右侧功能区的固定宽度
        right_widget.setFixedWidth(200)
        
        # 添加所有部件到主布局
        layout.addWidget(left_widget)
        layout.addWidget(middle_widget, stretch=1)  # 让中间区域可以伸展
        layout.addWidget(right_widget)
        
        # 连接工位选择信号
        self.station_list.currentItemChanged.connect(self.onStationSelected)
        
    def addStation(self):
        """添加新工位"""
        current_count = self.station_list.count()
        new_station = QListWidgetItem(f"工位{current_count + 1}")
        self.station_list.addItem(new_station)
        
    def onStationSelected(self, current, previous):
        """工位选择变化时的处理"""
        if current:
            self.current_station = current.text()
            self.upload_btn.setEnabled(True)
            # 显示当前工位的图片
            self.showStationImages(self.current_station)
        else:
            self.current_station = None
            self.upload_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            
    def uploadImages(self):
        """上传图片"""
        if not self.current_station:
            return
            
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if files:
            # 确保存储目录存在
            station_dir = os.path.join(self.project_path, "station_images", self.current_station)
            os.makedirs(station_dir, exist_ok=True)
            
            # 复制图片到项目目录
            for file_path in files:
                file_name = os.path.basename(file_path)
                target_path = os.path.join(station_dir, file_name)
                shutil.copy2(file_path, target_path)
                
                # 更新存储的图片信息
                if self.current_station not in self.station_images:
                    self.station_images[self.current_station] = []
                self.station_images[self.current_station].append(target_path)
            
            # 更新预览
            self.showStationImages(self.current_station)
            self.finish_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
            
    def showStationImages(self, station):
        """显示工位的图片"""
        # 先从布局中移除引导标签（但不删除它）
        self.preview_layout.removeWidget(self.guide_label)
        
        # 清除现有的预览
        while self.preview_layout.count():
            item = self.preview_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # 如果有该工位的图片，显示它们
        if station in self.station_images and self.station_images[station]:
            for image_path in self.station_images[station]:
                # 创建图片预览
                preview = QLabel()
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaled(
                    QSize(600, 400),  # 增大预览图片尺寸
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                preview.setPixmap(scaled_pixmap)
                preview.setStyleSheet("""
                    QLabel {
                        border: 1px solid #e8e8e8;
                        border-radius: 4px;
                        padding: 4px;
                        margin: 4px;
                        background: white;
                    }
                """)
                preview.setAlignment(Qt.AlignCenter)
                self.preview_layout.addWidget(preview)
            
            self.guide_label.hide()
            self.delete_btn.setEnabled(True)
        else:
            # 显示引导文字
            self.guide_label.show()
            self.delete_btn.setEnabled(False)
            self.preview_layout.addWidget(self.guide_label)
            
        self.preview_layout.addStretch()
        
    def deleteSelectedImages(self):
        """删除当前工位的所有图片"""
        if not self.current_station or self.current_station not in self.station_images:
            return
            
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除工位 {self.current_station} 的所有图片吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 删除文件
            station_dir = os.path.join(self.project_path, "station_images", self.current_station)
            if os.path.exists(station_dir):
                shutil.rmtree(station_dir)
            
            # 清除存储的信息
            self.station_images.pop(self.current_station, None)
            
            # 更新预览
            self.showStationImages(self.current_station)
            
            if not self.station_images:
                self.finish_btn.setEnabled(False)
        
    def saveStationImages(self):
        """保存工位图片信息"""
        if not self.station_images:
            return
            
        # 保存工位和图片的对应关系
        save_data = {}
        for station, images in self.station_images.items():
            # 只保存相对路径
            relative_paths = [os.path.relpath(path, self.project_path) for path in images]
            save_data[station] = relative_paths
            
        # 保存到 JSON 文件
        save_path = os.path.join(self.project_path, "station_images.json")
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
            
        QMessageBox.information(self, "成功", "工位图片信息保存成功！") 