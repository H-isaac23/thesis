import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QApplication, QLabel, QPushButton, QVBoxLayout, \
    QHBoxLayout, QFileDialog, QAbstractItemView
from PySide6.QtGui import QIcon

class Widget(QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        self.width = 1280
        self.height = 720

        self.setFixedHeight(self.height)
        self.setFixedWidth(self.width)
        self.setContentsMargins(0, 0, 0, 0)

        self.filenames = []

        ### Header
        header_widget = QWidget()
        header_widget.setObjectName("header-widget")

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_widget.setContentsMargins(0, 0, 0, 0)

        file_label = QLabel("FILES")
        file_label.setContentsMargins(0, 0, 0, 0)

        header_layout.addWidget(file_label)
        header_widget.setLayout(header_layout)

        ### PDF list widget

        self.pdf_widget = QListWidget()
        self.pdf_widget.setObjectName("pdf-widget")
        if len(self.filenames) == 0:
            note = QListWidgetItem("There are currently no files.")
            note.setTextAlignment(Qt.AlignCenter)
            self.pdf_widget.addItem(note)
        # TODO: will remove this after testing
        else:
            note = QListWidgetItem("There are currently files.")
            note.setTextAlignment(Qt.AlignCenter)
            self.pdf_widget.addItem(note)
        # for i in range(5):
        #     item = QListWidgetItem(f"Item {i}")
        #     item.setTextAlignment(Qt.AlignCenter)
        #     self.pdf_widget.addItem(item)

        #### Button container
        button_container = QWidget()

        button_layout = QVBoxLayout()
        self.start_button = QPushButton("START")
        self.clear_button = QPushButton("REMOVE FILES")
        self.start_button.setObjectName("start-button")
        self.start_button.clicked.connect(self.startSummarization)
        self.clear_button.setObjectName("clear-button")
        self.clear_button.clicked.connect(self.selectFilesToRemove)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.clear_button)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_container.setLayout(button_layout)

        ### sidebar container

        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(header_widget, 1)
        sidebar_layout.addWidget(self.pdf_widget, 10)
        sidebar_layout.addWidget(button_container, 2)

        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebar-widget")
        sidebar_widget.setLayout(sidebar_layout)

        ### Putting it all together

        browse_button = QPushButton("Browse")
        browse_button.setObjectName("browse-button")
        browse_button.clicked.connect(self.getFiles)

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

    def getFiles(self):
        file_paths = QFileDialog.getOpenFileNames(self, "Select one or more files to open", "C:\\", "*.pdf")[0]
        if len(file_paths) == 0:
            return
        self.filenames += file_paths
        self.pdf_widget.takeItem(0)
        for file_path in self.filenames:
            pdf_icon = QIcon("./pdf-icon.png")
            filename = file_path.split("/")[-1]

            # trim file name
            filename_length = 36
            if len(filename) > filename_length:
                filename = filename[:filename_length] + "..."

            file_item = QListWidgetItem(filename)
            file_item.setIcon(pdf_icon)
            self.pdf_widget.addItem(file_item)

    def startSummarization(self):
        pass

    def clearFiles(self):
        pass

    def showSummarizedFiles(self):
        pass

    def removeSelectedFiles(self):
        # TODO: change bg color of start button, change text of start button
        # self.start_button.setText("START")

        # TODO: reconnect selectFilesToRemove to clear button, revert selection mode
        # self.pdf_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        # self.clear_button.clicked.connect(self.selectFilesToRemove)
        items = self.pdf_widget.selectedItems()
        for item in items:
            self.pdf_widget.takeItem(self.pdf_widget.row(item))

    def selectFilesToRemove(self):
        # Allow multiple items to be selected
        self.pdf_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        # TODO: change start button background color and text
        self.start_button.setText("REMOVE")
        self.clear_button.setText("CANCEL")

        # TODO: change text of clear button
        # TODO: change clicked slot
        self.start_button.clicked.connect(self.removeSelectedFiles)
        self.clear_button.clicked.connect(self.revertButtons)


    def revertButtons(self):
        self.start_button.setText("START")
        self.clear_button.setText("REMOVE FILES")

        self.start_button.clicked.connect(self.startSummarization)
        self.clear_button.clicked.connect(self.selectFilesToRemove)
        self.pdf_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)


if __name__ == "__main__":
    app = QApplication()

    w = Widget()
    w.show()

    with open("style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    sys.exit(app.exec())