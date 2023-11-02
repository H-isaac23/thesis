import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QApplication, QLabel, QPushButton, QVBoxLayout, \
    QHBoxLayout

class Widget(QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        self.width = 1280
        self.height = 720

        self.setFixedHeight(self.height)
        self.setFixedWidth(self.width)
        self.setContentsMargins(0, 0, 0, 0)

        ### Header
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_widget.setContentsMargins(0, 0, 0, 0)

        file_label = QLabel("FILE NAME")
        status_label = QLabel("STATUS")
        file_label.setContentsMargins(0, 0, 0, 0)
        status_label.setContentsMargins(0, 0, 0, 0)

        header_layout.addWidget(file_label)
        header_layout.addWidget(status_label)

        header_widget.setLayout(header_layout)

        ### PDF list widget

        pdf_widget = QListWidget()
        pdf_widget.setObjectName("pdf-widget")
        for i in range(20):
            item = QListWidgetItem(f"Item {i}")
            item.setTextAlignment(Qt.AlignCenter)
            pdf_widget.addItem(item)

        #### Button container
        button_container = QWidget()

        button_layout = QVBoxLayout()
        start_button = QPushButton("START")
        clear_button = QPushButton("CLEAR")
        start_button.setObjectName("start-button")
        clear_button.setObjectName("clear-button")

        button_layout.addWidget(start_button)
        button_layout.addWidget(clear_button)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_container.setLayout(button_layout)

        ### sidebar container

        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(header_widget, 1)
        sidebar_layout.addWidget(pdf_widget, 10)
        sidebar_layout.addWidget(button_container, 2)

        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebar-widget")
        sidebar_widget.setLayout(sidebar_layout)

        ### Putting it all together

        browse_button = QPushButton("Browse")
        browse_button.setObjectName("browse-button")

        content_layout = QVBoxLayout()
        content_layout.addWidget(browse_button)
        content_layout.setContentsMargins(0, 0, 0, 0)
        main_widget = QWidget()
        main_widget.setLayout(content_layout)

        layout = QHBoxLayout()
        layout.addWidget(main_widget, 3)
        layout.addWidget(sidebar_widget, 1)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication()

    w = Widget()
    w.show()

    with open("style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    sys.exit(app.exec())