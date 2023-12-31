import sys
import os
import random
from PySide6 import QtCore, QtWidgets, QtGui
from time import sleep
import markdown
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QApplication, QLabel, QPushButton, QVBoxLayout, \
    QHBoxLayout, QFileDialog, QAbstractItemView, QListView, QStackedWidget, QTextBrowser
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
        self.summarized_files = []
        self.save_location = os.path.join(os.path.expanduser("~"), "Desktop")

        ### Stack pages setup
        self.stacked_widget = QStackedWidget()
        self.page_layout = QHBoxLayout()
        self.page_layout.setContentsMargins(0, 0, 0, 0)

        ### Pages to be displayed
        self.first_page_widget = self.create_first_page()
        # self.summarized_page = self.create_second_page("EWWWWWWWWWWWWWW. WHAT THE FUCK")

        ### Add pages to stacked widgets
        self.stacked_widget.addWidget(self.first_page_widget)
        # self.stacked_widget.addWidget(self.summarized_page)

        self.page_layout.addWidget(self.stacked_widget)

        self.setLayout(self.page_layout)

        # self.navigate_to_page(1)

        # self.setLayout(layout)
        # print(self.summarized_widget.frameSize())

    def create_first_page(self):
        print(self.save_location)

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

        ### Summarized Files Widget
        self.summarized_widget = QListWidget()
        self.summarized_widget.itemDoubleClicked.connect(self.create_second_page)
        self.summarized_widget.setFlow(QListView.Flow.LeftToRight)
        self.summarized_widget.setContentsMargins(0, 0, 0, 0)
        self.summarized_widget.setFixedHeight(100)
        self.summarized_widget.setObjectName("summ-widget")

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

        ### Save location container
        save_location_container = QWidget()

        save_to_button = QPushButton("Save to...")
        save_to_button.setObjectName("save-to-button")
        save_to_button.clicked.connect(self.change_save_location)

        self.location_label = QLabel(self.save_location)
        self.location_label.setMargin(0)
        self.location_label.setAlignment(Qt.AlignLeft)
        self.location_label.setObjectName("location-label")

        save_location_layout = QHBoxLayout()
        save_location_layout.addWidget(self.location_label, 3)
        save_location_layout.addWidget(save_to_button, 1)
        save_location_layout.setContentsMargins(0, 0, 0, 0)

        save_location_container.setLayout(save_location_layout)
        save_location_container.setFixedHeight(50)

        #### Button container
        button_container = QWidget()

        button_layout = QVBoxLayout()
        self.start_button = QPushButton("START")
        self.clear_button = QPushButton("REMOVE FILES")
        self.start_button.setObjectName("start-button")
        self.start_button.clicked.connect(self.start_summarization_proc)
        self.clear_button.setObjectName("clear-button")
        self.clear_button.clicked.connect(self.select_files_to_remove)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.clear_button)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_container.setLayout(button_layout)

        ### sidebar container

        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(header_widget, 1)
        sidebar_layout.addWidget(self.pdf_widget, 10)
        sidebar_layout.addWidget(save_location_container, 1)
        sidebar_layout.addWidget(button_container, 2)

        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebar-widget")
        sidebar_widget.setLayout(sidebar_layout)

        ### Putting it all together

        browse_button = QPushButton("Browse")
        browse_button.setObjectName("browse-button")
        browse_button.clicked.connect(self.get_files)

        content_layout = QVBoxLayout()
        content_layout.addStretch(1)
        content_layout.addWidget(browse_button)
        content_layout.addStretch(1)
        content_layout.addWidget(self.summarized_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)

        left_widget = QWidget()
        left_widget.setLayout(content_layout)

        layout = QHBoxLayout()
        layout.addWidget(left_widget, 3)
        layout.addWidget(sidebar_widget, 1)
        layout.setContentsMargins(0, 0, 0, 0)

        main_widget = QWidget()
        main_widget.setLayout(layout)

        return main_widget

    def create_second_page(self, item):
        # Create and return the second page widget
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Create a horizontal layout for the back button
        button_layout = QHBoxLayout()
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.remove_widget_and_back_to_home)
        button_layout.addWidget(back_button)  # Add the button to the horizontal layout
        button_layout.addStretch(1)  # Push the button to the left

        # Add the horizontal layout to the vertical layout
        layout.addLayout(button_layout)

        # Add components for the second page
        filename_page_two = ""
        file_dir_access = ""
        current_text = item.text()
        if "..." in current_text:
            current_text = current_text[:-3]

        ### find file location
        for file_dir in self.summarized_files:
            if current_text in file_dir:
                file_dir_access = file_dir
                filename_page_two = os.path.basename(file_dir)
                break
        print(filename_page_two)
        with open(file_dir_access, "r") as fi:
            # print(fi.read())
            layout.addWidget(MarkdownViewer(fi.read()))
        # layout.addWidget(QLabel(f"This is the second page. {filename_page_two}"))
        # layout.addWidget(QLabel(f"This is the nyao page. {file_dir}"))

        self.stacked_widget.addWidget(widget)
        self.navigate_to_page(1)
        # return widget

    def open_summarized_content(self):
        pass

    def test_shit(self, item):
        filename_page_two = ""
        current_text = item.text()
        if "..." in current_text:
            current_text = current_text[:-3]

        ### find file location
        for file_dir in self.summarized_files:
            if current_text in file_dir:
                with open(file_dir, "r") as fi:
                    print(fi.read())
                filename_page_two = os.path.basename(file_dir)
                break
        print(filename_page_two)

    def remove_widget_and_back_to_home(self, index):
        # navigate to the first page first
        self.navigate_to_page(0)

        # Get the widget at the given index
        widget_to_remove = self.stacked_widget.widget(1)

        # Remove and delete the widget
        if widget_to_remove is not None:
            self.stacked_widget.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()

    def get_files(self):
        file_paths = QFileDialog.getOpenFileNames(self, "Select one or more files to open", os.path.join(os.path.expanduser("~"), "Downloads"), "*.pdf")[0]
        if len(file_paths) == 0:
            return
        self.filenames += file_paths
        self.pdf_widget.takeItem(0)
        for file_path in self.filenames:
            pdf_icon = QIcon("./pdf-icon.png")
            filename = os.path.basename(file_path)

            # trim file name
            filename_length = 36
            if len(filename) > filename_length:
                filename = filename[:filename_length] + "..."

            file_item = QListWidgetItem(filename)
            file_item.setIcon(pdf_icon)
            self.pdf_widget.addItem(file_item)
        print(self.filenames)

    def change_save_location(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory == "":
            return

        self.save_location = directory
        if len(directory) > 30:
            directory = directory[:27] + "..."
        self.location_label.setText(directory)

    def start_summarization_proc(self):
        markdown_icon = QIcon("./markdown-icon.png")
        raw_filenames = [os.path.splitext(os.path.basename(file_dir))[0] for file_dir in self.filenames]
        for file in raw_filenames:
            trim_filename_length = 20
            filename_display = file + ".md"
            self.summarized_files.append(os.path.join(self.save_location, file+".md"))
            if len(filename_display) > trim_filename_length:
                filename_display = file[:trim_filename_length] + "..."

            ### Write to save_location
            with open(os.path.join(self.save_location, file+".md"), "w") as f_summary:
                some_text = """## Introduction:

The study aimed to develop a system for translating Baybáyin script to Tagalog using a LeNet **Convolutional Neural Network** (CNN) with real-time recognition on OpenCV. The resurgence of interest in Baybáyin, due to social media and cultural reconnection, and the Philippine Congress's approval of House Bill 1022, which declares Baybáyin as the national writing system, motivated this research.

## Process:

The researchers used a LeNet CNN architecture due to its simplicity and effectiveness for beginners in CNN. The system was designed to detect Baybáyin scripts using a webcam, classify the script into Tagalog translation, and automate the conversion of hand-drawn Baybáyin characters. The dataset consisted of **36,000** images of Baybáyin characters, which were trained, validated, and tested using the model. The system was developed using Python and various libraries such as **OpenCV, NumPy, Sklearn, Keras, Matplotlib, and TensorFlow**.

## Results:

The system achieved a total accuracy of **93.91%**, with a test score of **5.17%** and a test accuracy of **98.50%** over 20 epochs used in the testing phase.

## Conclusion:

The study concluded that using CNN to automate the conversion of hand-drawn Baybáyin characters is **feasible and successful**. The objectives of developing an intelligent system for script identification and classification, utilizing LeNet CNN for recognition, and capturing scripts via webcam were achieved. However, the system's performance was *limited* by the hardware specifications of the laptop and webcam used. Future recommendations include implementing the system on a mobile platform for better accessibility and comprehensiveness.
                """
                f_summary.write(some_text)

            summary_file_item = QListWidgetItem(filename_display)
            summary_file_item.setIcon(markdown_icon)
            self.summarized_widget.addItem(summary_file_item)

    def clear_files(self):
        pass

    def summarize(self):
        pass

    def show_summarized_files(self):
        pass

    def remove_selected_files(self):
        # TODO: change bg color of start button, change text of start button

        items = self.pdf_widget.selectedItems()
        for item in items:
            print(item)
            self.pdf_widget.takeItem(self.pdf_widget.row(item))

    def select_files_to_remove(self):
        # Allow multiple items to be selected
        self.pdf_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        # TODO: change start button background color and text
        self.start_button.setText("REMOVE")
        self.clear_button.setText("CANCEL")

        # TODO: change text of clear button
        # TODO: change clicked slot
        self.start_button.clicked.connect(self.remove_selected_files)
        self.start_button.clicked.disconnect(self.start_summarization_proc)
        self.clear_button.clicked.disconnect(self.select_files_to_remove)
        self.clear_button.clicked.connect(self.revert_buttons)

    def revert_buttons(self):
        self.start_button.setText("START")
        self.clear_button.setText("REMOVE FILES")

        self.start_button.clicked.connect(self.start_summarization_proc)
        self.clear_button.clicked.connect(self.select_files_to_remove)
        self.pdf_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def navigate_to_page(self, page_index):
        # Method to switch views
        # sleep(4)
        self.stacked_widget.setCurrentIndex(page_index)


class MarkdownViewer(QTextBrowser):
    def __init__(self, text):
        super().__init__()
        # self.setStyleSheet("color: white; font-size: 2em;")
        self.setMarkdown(f"{text}")

    def setMarkdown(self, markdown_text):
        html_content = markdown.markdown(markdown_text)
        # Create a style block that sets the text color and font size
        style_block = "<style>* { color: white !important; font-size: 2em !important; }</style>"
        # Combine the style block with the HTML content
        styled_html = style_block + html_content
        # Set the combined HTML as the content of the QTextBrowser
        self.setHtml(styled_html)


if __name__ == "__main__":
    app = QApplication()

    w = Widget()
    w.show()

    with open("style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    sys.exit(app.exec())
