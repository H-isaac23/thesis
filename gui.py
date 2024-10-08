import sys
import os
import tempfile
import sqlite3
import markdown
from PySide6.QtCore import Qt, QThreadPool, QRunnable, Signal, QObject, QMetaObject, Slot, QSize
from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QApplication, QLabel, QPushButton, QVBoxLayout, \
    QHBoxLayout, QFileDialog, QAbstractItemView, QListView, QStackedWidget, QTextBrowser, QDialog
from PySide6.QtGui import QIcon
from PySide6.QtGui import QTextDocument, QTextOption, QFont
import dotenv
import time
from pathlib import Path
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
import re

dotenv.load_dotenv()

class Widget(QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        self.temp_dir = tempfile.gettempdir()
        self.db_path = os.path.join(self.temp_dir, 'app_data.db')
        self.check_privacy_policy()

        self.width = 1280
        self.height = 720

        self.setFixedHeight(self.height)
        self.setFixedWidth(self.width)
        self.setContentsMargins(0, 0, 0, 0)

        self.threads = QThreadPool()

        self.filenames = []
        self.summarized_files = []
        self.save_location = os.path.join(os.path.expanduser("~"), "Desktop")

        ### Stack pages setup
        self.stacked_widget = QStackedWidget()
        self.page_layout = QHBoxLayout()
        self.page_layout.setContentsMargins(0, 0, 0, 0)

        ### Pages to be displayed
        self.first_page_widget = self.create_first_page()

        ### Add pages to stacked widgets
        self.stacked_widget.addWidget(self.first_page_widget)

        self.page_layout.addWidget(self.stacked_widget)

        self.setLayout(self.page_layout)
    def create_first_page(self):

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
        self.pdf_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        # if len(self.filenames) == 0:
        #     note = QListWidgetItem("There are currently no files.")
        #     note.setTextAlignment(Qt.AlignCenter)
        #     self.pdf_widget.addItem(note)
        # TODO: will remove this after testing
        # else:
        #     note = QListWidgetItem("There are currently files.")
        #     note.setTextAlignment(Qt.AlignCenter)
        #     self.pdf_widget.addItem(note)
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
        self.start_button.setDisabled(True)
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
        # self.filenames += file_paths
        # self.pdf_widget.takeItem(0)
        for file_path in file_paths:
            if file_path not in self.filenames:
                self.filenames.append(file_path)
                pdf_icon = QIcon("./pdf-icon.png")
                filename = os.path.basename(file_path)

                # trim file name
                filename_length = 36
                if len(filename) > filename_length:
                    filename = filename[:filename_length] + "..."

                file_item = QListWidgetItem(filename)
                file_item.setIcon(pdf_icon)
                self.pdf_widget.addItem(file_item)
        if len(self.filenames) > 0:
            self.start_button.setDisabled(False)
        # print(self.filenames)

    def change_save_location(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory == "":
            return

        self.save_location = directory
        if len(directory) > 30:
            directory = directory[:27] + "..."
        self.location_label.setText(directory)

    def start_summarization_proc(self):
        print(self.filenames)
        # raw_filenames = [os.path.splitext(os.path.basename(file_dir))[0] for file_dir in self.filenames]

        selected_files = self.pdf_widget.selectedItems()
        for file in selected_files:
            trim_filename_length = 20
            f_displayed = file.text()
            if "..." in f_displayed:
                f_displayed = f_displayed[:-3]

            filename = os.path.splitext(os.path.basename([s for s in self.filenames if f_displayed in s][0]))[0]
            filename_display = filename + ".md"
            print(f"filename_display {filename_display}")
            print(f"filename {filename}")

            file_path = os.path.join(self.save_location, filename+".md")
            if file_path in self.summarized_files:
                continue

            self.summarized_files.append(file_path)

            if len(filename_display) > trim_filename_length:
                filename_display = filename_display[:trim_filename_length] + "..."
                print(filename_display)

            ### Summarize file
            f_find = ""
            if "..." in filename:
                f_find = filename[:-3]
                print(f"f_find {f_find}")
            elif ".." in filename:
                f_find = filename[:-2]
            else:
                f_find = filename
                print(f"f_find {f_find}")
            file_to_summarize = [s for s in self.filenames if f_find in s][0]
            print("hi")
            worker = SummaryWorker(1, file_to_summarize)
            print("after init")
            worker.signals.finished.connect(self.on_summarize_finished)
            # worker.finished.connect(worker.deleteLater)
            self.threads.start(worker)
            print("after connect")
            # thread.start()

            print("after start")

#             with open(os.path.join(self.save_location, filename + ".md"), "w") as f_summary:
#                 some_text = """## Introduction:
#
# The study aimed to develop a system for translating Baybáyin script to Tagalog using a LeNet **Convolutional Neural Network** (CNN) with real-time recognition on OpenCV. The resurgence of interest in Baybáyin, due to social media and cultural reconnection, and the Philippine Congress's approval of House Bill 1022, which declares Baybáyin as the national writing system, motivated this research.
#
# ## Process:
#
# The researchers used a LeNet CNN architecture due to its simplicity and effectiveness for beginners in CNN. The system was designed to detect Baybáyin scripts using a webcam, classify the script into Tagalog translation, and automate the conversion of hand-drawn Baybáyin characters. The dataset consisted of **36,000** images of Baybáyin characters, which were trained, validated, and tested using the model. The system was developed using Python and various libraries such as **OpenCV, NumPy, Sklearn, Keras, Matplotlib, and TensorFlow**.
#
# ## Results:
#
# The system achieved a total accuracy of **93.91%**, with a test score of **5.17%** and a test accuracy of **98.50%** over 20 epochs used in the testing phase.
#
# ## Conclusion:
#
# The study concluded that using CNN to automate the conversion of hand-drawn Baybáyin characters is **feasible and successful**. The objectives of developing an intelligent system for script identification and classification, utilizing LeNet CNN for recognition, and capturing scripts via webcam were achieved. However, the system's performance was *limited* by the hardware specifications of the laptop and webcam used. Future recommendations include implementing the system on a mobile platform for better accessibility and comprehensiveness.
#                 """
#                 f_summary.write(some_text)

    def on_summarize_finished(self, summary, file_to_summarize):
        filename_display = os.path.splitext(os.path.basename(file_to_summarize))[0] + ".md"
        file_save_path = os.path.join(self.save_location, filename_display)
        with open(file_save_path, "w") as f_summary:
            f_summary.write(summary)
        markdown_icon = QIcon("./markdown-icon.png")
        if len(filename_display) > 20:
            filename_display = filename_display[:20] + "..."

        summary_file_item = QListWidgetItem(filename_display)
        summary_file_item.setIcon(markdown_icon)
        self.summarized_widget.addItem(summary_file_item)

    def remove_selected_files(self):
        # TODO: change bg color of start button, change text of start button

        items = self.pdf_widget.selectedItems()
        for item in items:
            print(item)
            self.filenames = [s for s in self.filenames if item.text() not in s]
            self.pdf_widget.takeItem(self.pdf_widget.row(item))
        if len(self.filenames) < 1:
            self.start_button.setDisabled(True)

    def select_files_to_remove(self):
        # Allow multiple items to be selected

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
        self.start_button.clicked.disconnect(self.remove_selected_files)
        self.clear_button.clicked.connect(self.select_files_to_remove)
        self.clear_button.clicked.disconnect(self.revert_buttons)
        # self.pdf_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def navigate_to_page(self, page_index):
        # Method to switch views
        # sleep(4)
        self.stacked_widget.setCurrentIndex(page_index)

    def check_privacy_policy(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences
            (id INTEGER PRIMARY KEY, privacy_accepted BOOLEAN)
        ''')

        cursor.execute("SELECT privacy_accepted FROM user_preferences")
        result = cursor.fetchone()
        print(result)

        if result is None or not result[0]:
            self.show_privacy_policy(conn)
        else:
            # User has already accepted the privacy policy
            pass

        conn.close()

    def show_privacy_policy(self, conn):
        privacy_policy_text = """
        <style>
            body {
                font-family: Arial, sans-serif;
                font-size: 14px;
                line-height: 1.5;
                color: #333;
            }

            h1 {
                font-size: 34px;
                font-weight: bold;
                margin-bottom: 20px;
            }

            h2 {
                font-size: 24px;
                font-weight: bold;
                margin-top: 30px;
                margin-bottom: 10px;
            }

            p {
                margin-bottom: 22px;
            }
        </style>

        <h1>Privacy Policy</h1>

        <p>At PSU, we understand the importance of protecting your privacy and the confidentiality of your personal information. This Privacy Policy outlines how we collect, use, and safeguard the data you provide when using our PDF summarization application.</p>

        <h2>Data Collection and Usage</h2>
        <p>Our app is designed to summarize PDF documents on your local device. We do not collect, store, or transmit any personal information. However, the contents of your PDF files are temporarily transmitted to a third-party service for the summarization process. This data is not stored or retained by the third-party service after the summarization is complete.</p>

        <h2>Third-Party Services</h2>
        <p>Our app utilizes a third-party service provided by LangChain to perform the summarization of your PDF documents. This service is subject to its own privacy policy and data practices, which you can review at https://www.langchain.com/privacy-policy.</p>

        <h2>Data Security</h2>
        <p>While your PDF contents are transmitted to the third-party service for summarization, we employ industry-standard encryption and security measures to protect the data in transit. Once the summarization is complete, no data is stored or retained by the third-party service or our application.</p>
        
        <h2>Changes to this Privacy Policy</h2>
        <p>We may update this Privacy Policy from time to time to reflect changes in our practices, third-party services, or legal requirements. We encourage you to review the Privacy Policy periodically for any updates.</p>
        
        <h2>Contact Us</h2>
        <p>If you have any questions or concerns about this Privacy Policy or our data practices, please contact us at contact@test.com.</p>
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Privacy Policy")

        text_browser = QTextBrowser()
        text_browser.setHtml(privacy_policy_text)
        text_browser.setReadOnly(True)
        text_browser.setOpenExternalLinks(True)
        text_browser.document().setDefaultTextOption(QTextOption(Qt.AlignJustify))
        text_browser.setMinimumSize(QSize(1280, 720))

        accept_button = QPushButton("Accept")
        accept_button.clicked.connect(dialog.accept)

        reject_button = QPushButton("Reject")
        reject_button.clicked.connect(dialog.reject)

        layout = QVBoxLayout()
        layout.addWidget(text_browser)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(accept_button)
        button_layout.addWidget(reject_button)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        if dialog.exec() == QDialog.Accepted:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM user_preferences WHERE id = 1")
            result = cursor.fetchone()

            if result[0] == 0:
                cursor.execute("INSERT INTO user_preferences (id, privacy_accepted) VALUES (1, ?)", (True,))
            else:
                cursor.execute("UPDATE user_preferences SET privacy_accepted = ? WHERE id = 1", (True,))

            conn.commit()
        else:
            QMetaObject.invokeMethod(self, "quit_app", Qt.QueuedConnection)

    @Slot()
    def quit_app(self):
        QApplication.quit()

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    '''
    finished = Signal(str, str)  # QtCore.Signal
    error = Signal(tuple)
    result = Signal(object)

class SummaryWorker(QRunnable):
    finished = Signal(str, str)  # Signal to indicate the API call is done

    def __init__(self, data, file_to_summarize, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = data
        self.file_to_summarize = file_to_summarize
        self.signals = WorkerSignals()
        print("inside init")

    def run(self):
        print("inside run")
        summary = self.long_running_api_call(self.file_to_summarize)
        self.signals.finished.emit(summary, self.file_to_summarize)

    def long_running_api_call(self, file_to_summarize):
        # # Simulate a long-running task
        # time.sleep(1)  # Replace with your actual API call
        # return f"API response for {file_to_summarize} {self.data}"
        # Define prompt
        prompt_template = """Write a concise summary for the introduction, process, results, and conclusion of the
        following (skip images), append the authors at the end (if they exist), give back the results in a markdown
        format: "{text}" CONCISE SUMMARY: """
        # prompt_template = """Write a summary for each chapter of the following PDF. The summary for each chapter should include
        # a detailed and at least a 150-word summary of the chapter. Focus especially on chapter 3-5, and discuss the results of the PDF.
        # "{text}"
        # CONCISE SUMMARY:"""
        prompt = PromptTemplate.from_template(prompt_template)

        loader = PyPDFLoader(file_to_summarize)
        docs = loader.load()

        llm = ChatOpenAI(temperature=0, model_name="gpt-4-turbo-2024-04-09")
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        stuff_chain = StuffDocumentsChain(llm_chain=llm_chain, document_variable_name="text")

        return stuff_chain.run(docs)


class MarkdownViewer(QTextBrowser):
    def __init__(self, text):
        super().__init__()
        # self.setStyleSheet("color: white; font-size: 2em;")
        self.setMarkdown(f"{text}")

    def setMarkdown(self, markdown_text):
        html_content = markdown.markdown(markdown_text)
        # Create a style block that sets the text color and font size
        style_block = """
            <style>
                * { color: white !important; font-size: 20px !important; } 
                pre { color: white !important; font-size: 20px !important; }
                h1 { color: white !important; font-size: 30px !important; }
                h2 { color: white !important; font-size: 26px !important; }
                h3 { color: white !important; font-size: 22px !important; } 
                h4 { color: white !important; font-size: 22px !important; } 
                h5 { color: white !important; font-size: 22px !important; } 
                h6 { color: white !important; font-size: 22px !important; } 
            </style>
        """
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
