from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLabel, QSpinBox, 
                             QLineEdit, QMessageBox, QHeaderView, QInputDialog)
from PyQt5.QtCore import Qt
import os

class DefectMatrixGenerator(QWidget):
    def __init__(self, project_path, parent=None):
        super().__init__(parent)
        self.project_path = project_path
        self.defect_table = None
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # 区域和缺陷数量设置部分
        config_layout = QHBoxLayout()
        
        # 缺陷类型数量设置（行）
        defect_layout = QHBoxLayout()
        defect_label = QLabel("缺陷类型数量：")
        self.defect_spin = QSpinBox()
        self.defect_spin.setRange(1, 100)
        self.defect_spin.setValue(1)
        defect_layout.addWidget(defect_label)
        defect_layout.addWidget(self.defect_spin)
        
        # 区域数量设置（列）
        area_layout = QHBoxLayout()
        area_label = QLabel("区域数量：")
        self.area_spin = QSpinBox()
        self.area_spin.setRange(1, 100)
        self.area_spin.setValue(1)
        area_layout.addWidget(area_label)
        area_layout.addWidget(self.area_spin)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 生成表格按钮
        self.generate_btn = QPushButton("生成矩阵表格")
        self.generate_btn.clicked.connect(self.generateTable)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background: #1890ff;
                color: white;
                padding: 6px 16px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background: #40a9ff;
            }
        """)
        
        # 保存按钮
        self.save_btn = QPushButton("保存并生成文件夹")
        self.save_btn.clicked.connect(self.saveAndCreateFolders)
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #52c41a;
                color: white;
                padding: 6px 16px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background: #73d13d;
            }
            QPushButton:disabled {
                background: #d9d9d9;
            }
        """)
        
        button_layout.addWidget(self.generate_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addStretch()
        
        config_layout.addLayout(defect_layout)  # 先添加缺陷类型（行）
        config_layout.addLayout(area_layout)    # 再添加区域（列）
        config_layout.addLayout(button_layout)
        
        layout.addLayout(config_layout)
        
        # 表格部分
        self.defect_table = QTableWidget(0, 0)
        self.defect_table.setHorizontalHeaderLabels([])
        self.defect_table.setVerticalHeaderLabels([])
        self.defect_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 允许双击编辑表头
        self.defect_table.horizontalHeader().sectionDoubleClicked.connect(self.editColumnHeader)
        self.defect_table.verticalHeader().sectionDoubleClicked.connect(self.editRowHeader)
        
        # 设置表头样式
        header_style = """
            QHeaderView::section {
                background-color: #fafafa;
                padding: 4px;
                border: 1px solid #f0f0f0;
                font-weight: bold;
            }
            QHeaderView::section:hover {
                background-color: #f0f0f0;
            }
        """
        self.defect_table.horizontalHeader().setStyleSheet(header_style)
        self.defect_table.verticalHeader().setStyleSheet(header_style)
        
        layout.addWidget(self.defect_table)
        
    def editColumnHeader(self, column):
        """编辑列表头（区域名称）"""
        current_text = self.defect_table.horizontalHeaderItem(column).text()
        new_text, ok = QInputDialog.getText(
            self, 
            "编辑区域名称", 
            "请输入区域名称：",
            text=current_text
        )
        if ok and new_text:
            self.defect_table.setHorizontalHeaderItem(column, QTableWidgetItem(new_text))
            
    def editRowHeader(self, row):
        """编辑行表头（缺陷类型名称）"""
        current_text = self.defect_table.verticalHeaderItem(row).text()
        new_text, ok = QInputDialog.getText(
            self, 
            "编辑缺陷类型名称", 
            "请输入缺陷类型名称：",
            text=current_text
        )
        if ok and new_text:
            self.defect_table.setVerticalHeaderItem(row, QTableWidgetItem(new_text))
        
    def generateTable(self):
        rows = self.defect_spin.value()  # 缺陷类型数量（行）
        cols = self.area_spin.value()    # 区域数量（列）
        
        self.defect_table.setRowCount(rows)
        self.defect_table.setColumnCount(cols)
        
        # 设置列标题（区域）
        for i in range(cols):
            self.defect_table.setHorizontalHeaderItem(i, QTableWidgetItem(f"区域{i+1}"))
        
        # 设置行标题（缺陷类型）
        for i in range(rows):
            self.defect_table.setVerticalHeaderItem(i, QTableWidgetItem(f"缺陷{i+1}"))
            
        # 初始化表格内容（默认全选）
        for i in range(rows):
            for j in range(cols):
                item = QTableWidgetItem()
                item.setCheckState(Qt.Checked)  # 默认选中
                self.defect_table.setItem(i, j, item)
        
        self.save_btn.setEnabled(True)
        
    def saveAndCreateFolders(self):
        if not self.defect_table:
            return
            
        rows = self.defect_table.rowCount()
        cols = self.defect_table.columnCount()
        
        # 获取所有缺陷类型和区域名称
        defects = []  # 行（缺陷类型）
        areas = []    # 列（区域）
        
        for i in range(rows):
            defect_name = self.defect_table.verticalHeaderItem(i).text()
            defects.append(defect_name)
            
        for j in range(cols):
            area_name = self.defect_table.horizontalHeaderItem(j).text()
            areas.append(area_name)
            
        # 创建文件夹
        defects_base_dir = os.path.join(self.project_path, "defects")
        if not os.path.exists(defects_base_dir):
            os.makedirs(defects_base_dir)
            
        # 根据选中的组合创建文件夹
        created_folders = []
        for i in range(rows):
            for j in range(cols):
                item = self.defect_table.item(i, j)
                if item.checkState() == Qt.Checked:
                    folder_name = f"{areas[j]}_{defects[i]}"  # 区域_缺陷
                    folder_path = os.path.join(defects_base_dir, folder_name)
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                        created_folders.append(folder_name)
        
        if created_folders:
            QMessageBox.information(self, "成功", f"已创建以下缺陷文件夹：\n{chr(10).join(created_folders)}")
        else:
            QMessageBox.warning(self, "警告", "没有选中任何缺陷组合！") 