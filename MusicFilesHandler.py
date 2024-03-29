import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenuBar, QAction, QToolBar, QVBoxLayout, QWidget, QLabel,
                             QScrollArea, QLineEdit, QHBoxLayout, QCheckBox, QStatusBar, QMessageBox, QFileDialog, QDialog, QGroupBox, QGridLayout, QShortcut)
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence, QFont
from PyQt5.QtMultimedia import QSound
import os
import tinytag
import re
import random
import json


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MusicHandler")
        self.setGeometry(100, 100, 1500, 900)

        # Creating status bar object
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        # Setting text in status bar
        self.status_bar.showMessage("סטטוס: מוכן")

        self.center_label = None
        self.input_fields_layout = None
        self.layout = None
        self.drag_area = None
        self.year, self.track_number, self.contributing_artists, self.album_artist, self.title, self.file_name = None, None, None, None, None, None

        self.audio_files_paths = []   # Contains all the paths of the audio files displayed in the software
        self.new_file_paths = []
        self.new1_file_paths = []
        self.input_fields = []
        self.previous_names = {}

        self.initui()

    def initui(self):
        # Creating a widget for GUI components
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_widget.setAcceptDrops(True)  # אפשר גרירה על האובייקט הראשי
        central_widget.dragEnterEvent = self.dragEnterEvent
        central_widget.dragLeaveEvent = self.dragLeaveEvent
        central_widget.dropEvent = self.dropEvent
        # Creating the main frame/tunnel
        self.layout = QVBoxLayout(central_widget)

        self.create_bars()
        self.create_check_boxes()
        self.creating_a_frame_with_a_scroll_bar()
        self.Add_a_label_to_the_frame()

        self.show()

    def create_bars(self):
        # create a menu bar
        menu_bar = QMenuBar(self)
        file_menu = menu_bar.addMenu("קובץ")

        open_folder_action = QAction("בחר מתיקייה", self)
        open_folder_action.triggered.connect(self.open_file)
        file_menu.addAction(open_folder_action)

        exit_action = QAction("יציאה", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        tools_menu = menu_bar.addMenu("כלים")
        Manage_json_files_action = QAction("נהל קבצי json", self)
        Manage_json_files_action.triggered.connect(self.manage_json_files)
        tools_menu.addAction(Manage_json_files_action)

        self.setMenuBar(menu_bar)

        # create toolbar
        tool_bar = QToolBar("סרגל כלים", self)
        self.addToolBar(tool_bar)
        # create the save button
        save_action = QAction(QIcon(r'dependence\images\save.png'), 'שמור (Ctrl+S)', self)
        # Create a shortcut for Ctrl+S and Ctrl+ד
        save_shortcut = QShortcut(QKeySequence('Ctrl+S'), self)
        save_shortcut.activated.connect(self.save_action_triggered)
        save_shortcut_heb = QShortcut(QKeySequence('Ctrl+ד'), self)
        save_shortcut_heb.activated.connect(self.save_action_triggered)

        save_action.triggered.connect(self.save_action_triggered)
        tool_bar.addAction(save_action)
        # create the clean all button
        clear_action = QAction(QIcon(r'dependence\images\clear.png'), "נקה הכל", self)
        clear_action.triggered.connect(self.clear_action_triggered)
        tool_bar.addAction(clear_action)
        # create the back button
        back_action = QAction(QIcon(r'dependence\images\back.png'), "חזור", self)
        # Create a shortcut for Ctrl+S and Ctrl+ד
        back_shortcut = QShortcut(QKeySequence('Ctrl+Z'), self)
        back_shortcut.activated.connect(self.restore_names_triggered)
        back_shortcut_heb = QShortcut(QKeySequence('Ctrl+ז'), self)
        back_shortcut_heb.activated.connect(self.restore_names_triggered)

        back_action.triggered.connect(self.restore_names_triggered)
        tool_bar.addAction(back_action)

    def create_check_boxes(self):
        self.check_boxes_layout = QHBoxLayout()
        self.layout.addLayout(self.check_boxes_layout)
        check_box_names = ["שנה", "כותרת", "אמן האלבום", "אמנים משתתפים", "רצועה", "שם הקובץ"]
        self.check_boxes = []
        for name in check_box_names:
            if name == "שם הקובץ":
                label = QLabel(name, self)
                self.check_boxes_layout.addWidget(label)
            else:
                check_box = QCheckBox(name, self)
                self.check_boxes_layout.addWidget(check_box)
                self.check_boxes.append(check_box)
                check_box.setLayoutDirection(Qt.RightToLeft)  # קביעת כיוון הטקסט לימין לשמאל

    def creating_a_frame_with_a_scroll_bar(self):
        # Creating a frame for the song details with a scroll bar
        scroll_area = QScrollArea(self)
        self.layout.addWidget(scroll_area)
        scroll_content = QWidget(scroll_area)
        scroll_area.setWidget(scroll_content)
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidgetResizable(True)

        self.input_fields_layout = QVBoxLayout()
        scroll_layout.addLayout(self.input_fields_layout)

    def Add_a_label_to_the_frame(self):
        # יצירת והוספת ה- QLabel ל- input_fields_layout
        self.center_label = QLabel("גרור שירים לכאן\n\n\n\n\n", self)
        self.center_label.setAlignment(QtCore.Qt.AlignCenter)  # מיון הטקסט למרכז
        # הגדרת גופן גדול יותר לטקסט
        font = QFont()
        font.setPointSize(20)  # גודל הגופן בנקודות
        self.center_label.setFont(font)
        self.input_fields_layout.addWidget(self.center_label)

# So far the initial interface has been designed
# From here on, mainly the functions of the software operations

    def manage_json_files(self):
        json_manager_window = JSONFileManager()
        json_manager_window.exec_()

    def open_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly  # לא לאפשר עריכת הקובץ
        file_paths, _ = QFileDialog.getOpenFileNames(self, "פתח קובץ", "",
                                                     "קבצי מוזיקה (*.mp3 *.wav *.flac *.ogg *.m4a *.aac *.wma *.aiff "
                                                     "*.opus);;כל הקבצים (*.*)",
                                                     options=options)
        for file_path in file_paths:
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext.lower() not in ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac', '.wma', '.aiff', '.opus']:
                self.status_bar.showMessage("הבאת סוג קובץ שאינו נתמך")
                continue
            if file_path in self.audio_files_paths:  # בדיקה שהקובץ אינו כבר ברשימה
                self.status_bar.showMessage("הבאת שיר שכבר נמצא ברשימה")
                continue
            self.audio_files_paths.append(file_path)
            self.apply_text_corrections(file_path)
            self.add_song_info_fields()

    def dragLeaveEvent(self, event):
        # self.drag_area.setStyleSheet("background-color: white; border: 2px dashed gray;")
        pass

    def dragEnterEvent(self, event):
        # Checks if the dragged content is files or web addresses and not words or coordinates etc.
        if event.mimeData().hasUrls():
            # self.drag_area.setStyleSheet("background-color: yellow; border: 2px dashed gray;")
            event.acceptProposedAction()

    def dropEvent(self, event):
        # self.drag_area.setStyleSheet("background-color: white; border: 2px dashed gray;")
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext.lower() not in ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac', '.wma', '.aiff', '.opus']:
                self.status_bar.showMessage("גררת סוג קובץ שאינו נתמך")
                continue
            if file_path in self.audio_files_paths:  # Checking that the path is not already in the list
                self.status_bar.showMessage("גררת שיר שהינו כבר ברשימה")
                continue
            self.audio_files_paths.append(file_path)
            self.apply_text_corrections(file_path)
            self.center_label.clear()
            self.add_song_info_fields()

    def apply_text_corrections(self, file_path):
        # Reads the song information
        audiofile = tinytag.TinyTag.get(file_path)
        # Converts gibberish characters to Hebrew letters and removes spaces from the beginning and end of the content
        # כותרת
        self.title = self.replace_non_ascii_chars(audiofile.title.strip()) if audiofile.title else ""
        # אמן אלבום
        self.album_artist = self.replace_non_ascii_chars(audiofile.albumartist.strip()) if audiofile.albumartist else ""
        # אמנים משתתפים
        self.contributing_artists = self.replace_non_ascii_chars(audiofile.artist.strip()) if audiofile.artist else ""
        # מספר רצועה
        self.track_number = self.replace_non_ascii_chars(audiofile.track.strip()) if audiofile.track else ""
        if len(self.track_number) == 1 and self.track_number.isdigit():  # Checking if the number is a single digit
            self.track_number = "0" + self.track_number  # Adding 0 before the number
        # שנה
        self.year = self.replace_non_ascii_chars(audiofile.year.strip()) if audiofile.year else ""
        # שם קובץ
        self.file_name = self.replace_non_ascii_chars(os.path.basename(file_path).strip()) if os.path.basename(file_path) else ""

        # Clean invalid characters in Windows from the content
        invalid_chars = r'[\\/:"*?<>|]'  # The incorrect characters in the file names in Windows
        self.title = re.sub(invalid_chars, "", self.title)
        self.album_artist = re.sub(invalid_chars, "", self.album_artist)
        self.contributing_artists = re.sub(invalid_chars, "", self.contributing_artists)
        self.track_number = re.sub(invalid_chars, "", self.track_number)
        self.year = re.sub(invalid_chars, "", self.year)
        self.file_name = re.sub(invalid_chars, "", self.file_name)

        # Separating the artists' names with commas and "&"
        self.album_artist = self.last_artist_patch(self.album_artist)
        self.contributing_artists = self.last_artist_patch(self.contributing_artists)

        # Function to convert the words of the content according to the user .json files
        self.convert_by_instructions_from_json_files()

    @staticmethod
    def replace_non_ascii_chars(text):
        char_mapping = {
            'à': 'א', 'á': 'ב', 'â': 'ג', 'ã': 'ד', 'ä': 'ה', 'å': 'ו', 'æ': 'ז', 'ç': 'ח', 'è': 'ט',
            'é': 'י', 'ë': 'כ', 'ê': 'ך', 'ì': 'ל', 'î': 'מ', 'í': 'ם', 'ð': 'נ', 'ï': 'ן', 'ñ': 'ס',
            'ò': 'ע', 'ô': 'פ', 'ó': 'ף', 'ö': 'צ', 'õ': 'ץ', '÷': 'ק', 'ø': 'ר', 'ù': 'ש', 'ú': 'ת'
        }
        for char, replacement in char_mapping.items():
            text = text.replace(char, replacement)
        return text

    @staticmethod
    def load_replacements_from_json(json_path):
        with open(json_path, 'r', encoding='utf-8') as file:
            replacements = json.load(file)
        return replacements

    @staticmethod
    def last_artist_patch(artists_string):
        # convert "and" or "&" to ","
        to_replace = [" and ", " & "]
        for replace_string in to_replace:
            if replace_string in artists_string:
                artists_string = artists_string.replace(replace_string, ", ")

        # Split the artists string using the separator ", "
        artists_list = artists_string.split(", ")
        # Check if there are at least two artists
        if len(artists_list) >= 2:
            # Process the last separator based on the language of the last artist
            last_artist = artists_list[-1]
            if any(ord(c) > 127 for c in last_artist):  # Check if there are non-ASCII characters (assuming Hebrew)
                artists_list[-1] = " ו" + artists_list[-1]
            else:
                artists_list[-1] = " & " + artists_list[-1]

        # Join the artists list with the separator ", " for all except the last artist
        processed_artists_string = ", ".join(artists_list[:-1]) + "" + artists_list[-1]

        return processed_artists_string

    @staticmethod
    def apply_replacements(text, replacements):
        for original, replacement in replacements.items():
            text = text.replace(original, replacement)
        return text

    def convert_by_instructions_from_json_files(self):
        # Reads text conversion instructions from json files
        title_replacements = self.load_replacements_from_json(r'dependence\DicFiles\Title.json')
        album_artist_replacements = self.load_replacements_from_json(r'dependence\DicFiles\AlbumArtist.json')
        contributing_artists_replacements = self.load_replacements_from_json(
            r'dependence\DicFiles\ContributingArtists.json')
        track_number_replacements = self.load_replacements_from_json(r'dependence\DicFiles\TrackNumber.json')
        year_replacements = self.load_replacements_from_json(r'dependence\DicFiles\Year.json')
        # Apply the text converting according to the .json files instructions
        self.title = self.apply_replacements(self.title, title_replacements)
        self.album_artist = self.apply_replacements(self.album_artist, album_artist_replacements)
        self.contributing_artists = self.apply_replacements(self.contributing_artists, contributing_artists_replacements)
        self.track_number = self.apply_replacements(self.track_number, track_number_replacements)
        self.year = self.apply_replacements(self.year, year_replacements)

# So far the text corrections in the content before putting it in the window
# From here on, placing the songs inside the window and adding functionality to the software in order to make it easier for the user

    def add_song_info_fields(self):
        # Creates a content line of the song details within the frame
        input_row_layout = QHBoxLayout()
        self.input_fields_layout.insertLayout(0, input_row_layout)
        # Adding the content to the frame by order
        self.add_input_field(input_row_layout, f"{self.year}", is_year=True)
        self.add_input_field(input_row_layout, f"{self.title}", is_title=True)
        self.add_input_field(input_row_layout, f"{self.album_artist}", is_artists=True)
        self.add_input_field(input_row_layout, f"{self.contributing_artists}", is_artists=True)
        self.add_input_field(input_row_layout, f"{self.track_number}", is_track_number=True)
        self.add_input_field(input_row_layout, f"{self.file_name}", is_file_name=True)

    def add_input_field(self, layout, text, is_year=False, is_title=False, is_artists=False, is_track_number=False, is_file_name=False):
        title_edit = QLineEdit(self)

        title_edit.is_year = is_year  # Set the "is_year" attribute
        title_edit.is_title = is_title  # Set the "is_title" attribute
        title_edit.is_artists = is_artists  # Set the "is_artists" attribute
        title_edit.is_track_number = is_track_number  # Set the "is_track_number" attribute
        title_edit.is_file_name = is_file_name  # Set the "is_track_number" attribute

        if not is_file_name:
            title_edit.setStyleSheet("background-color: #99ccff;")

        # When the user changes the content in the field
        title_edit.textChanged.connect(self.text_content_changed)  # Connect the signal to the slot

        title_edit.setText(text)
        layout.addWidget(title_edit)
        self.input_fields.append(title_edit)

    def text_content_changed(self):
        title_edit = self.sender()  # Get the sender of the signal
        text = title_edit.text()

        if title_edit.is_year:  # Check if this is the "year" field
            invalid_characters = r"-*+=_()*&^%$#@!~`'\|{}[],\":;?<>./"

            title_edit.setStyleSheet("")  # Clear the background color
            if not text.isdigit() or len(text) > 4 or len(text) < 4 or any(char in invalid_characters for char in
                                                                           text):  # Checks if it's not all digits or if there are more than 4 digits or invalid characters
                title_edit.setStyleSheet("background-color: #ffffb4;")

        elif title_edit.is_title:  # Check if this is the "title" field
            invalid_characters = r"-*=_()*&^%$#@!~`'\|{}[],\":;?<>./"

            title_edit.setStyleSheet("background-color: #ffffb4;")
            if not any(char.isdigit() or char in invalid_characters for char in text): # Checks if there are any characters or numbers that shouldn't be there
                title_edit.setStyleSheet("")  # Clear the background color

        elif title_edit.is_artists:  # Check if this is the "artists" field
            invalid_characters = r"-*+=_()*&^%$#@!~`'\|{}[]\":;?<>/"

            title_edit.setStyleSheet("background-color: #ffffb4;")
            if not any(char.isdigit() or char in invalid_characters for char in text): # Checks for characters that shouldn't be there
                title_edit.setStyleSheet("")  # Clear the background color

        elif title_edit.is_track_number:  # Check if this is the "year" field
            invalid_characters = r"-*+=_()*&^%$#@!~`'\|{}[],\":;?<>./"

            title_edit.setStyleSheet("")  # Clear the background color
            if not text.isdigit() or len(text) > 2 or len(text) < 2 or any(char in invalid_characters for char in
                                                          text):  # Checks if it's not all digits or if there are more than 4 digits or invalid characters
                title_edit.setStyleSheet("background-color: #ffffb4;")

        if text == "":
            title_edit.setStyleSheet("background-color: #99ccff;")

        if title_edit.is_file_name:  # Check if this is the "is_file_name" field
            title_edit.setStyleSheet("")


# So far the songs are placed in the window and the software alerts you to anything that is needed
# From here on, the buttons actions

    def save_action_triggered(self):
        QSound.play("C:/Windows/Media/chimes.wav")
        self.previous_names.clear()
        duplicate_files = {}  # מילון לאחסון קבצים כפולים (שם קובץ: רשימת נתיבים)
        for i, path in enumerate(self.audio_files_paths):
            if not os.path.exists(path):  # בדיקה שהקובץ קיים
                print(f"הקובץ {path} אינו קיים")
                return

            new_name = "="  # שם השיר החדש יתחיל עם סימן השיוויון
            if self.check_boxes[4].isChecked():
                track_number_edit = self.input_fields[i * 6 + 4]
                if track_number_edit.text():
                    new_name += f"{track_number_edit.text()} "  # נוסיף את המספר רצועה

            if self.check_boxes[3].isChecked():
                artists_edit = self.input_fields[i * 6 + 3]
                if artists_edit.text():
                    new_name += f"{artists_edit.text()} - "  # נוסיף את אמנים משתתפים

            if self.check_boxes[2].isChecked():
                album_artist_edit = self.input_fields[i * 6 + 2]
                if album_artist_edit.text():
                    new_name += f"{album_artist_edit.text()} - "  # נוסיף את אמן האלבום

            if self.check_boxes[1].isChecked():
                title_edit = self.input_fields[i * 6 + 1]
                if title_edit.text():
                    new_name += f"{title_edit.text()} - "  # נוסיף את הכותרת

            if self.check_boxes[0].isChecked():
                year_edit = self.input_fields[i * 6]
                if year_edit.text():
                    new_name += f"{year_edit.text()} "  # נוסיף את השנה

            if new_name != "=":  # נבדוק שישנו תוכן להוספה לשם השיר
                # בדיקה והסרת הסימן "=" אם קיים בשם השיר החדש
                new_name = new_name.replace("=", "")
                if new_name.endswith(" - "):
                    new_name = new_name[:-2]  # Remove the " - " from the end of the string
                file_ext = os.path.splitext(os.path.basename(path))[1]
                new_name += file_ext    # add the file extension to the file name
                file_dir = os.path.dirname(path)    # extract the old path to ver

                new_path = file_dir + "/" + new_name

                try:    # Check if the new path does not already exist
                    os.rename(path, new_path)   # change the old path with the new path (rename)
                except FileExistsError:
                    base_name, file_ext = os.path.splitext(new_name)
                    file_exist_counter = 2
                    while os.path.exists(new_path):
                        new_name = f"{base_name}_{file_exist_counter} {file_ext}"
                        new_path = file_dir + "/" + new_name
                        file_exist_counter += 1

                    os.rename(path, new_path)

                    # כאן אתה מוסיף נתיב לרשימת הכפילויות במילון
                    if base_name not in duplicate_files:
                        duplicate_files[base_name] = []
                    duplicate_files[base_name].append(new_path)

                self.new_file_paths.append(new_path)

                new_key = str(random.randint(1, 10000))  # יצירת מפתח מספרי אקראי בין 1 ל-100
                self.previous_names[new_key] = [path]  # הוספת הזוג מפתח-ערך למילון

                self.previous_names[new_key].append(new_path)  # הוספת הזוג מפתח-ערך למילון

        self.audio_files_paths.clear()
        self.audio_files_paths = self.new_file_paths.copy()
        self.new_file_paths.clear()

        if duplicate_files:
            error_message = "נמצאו קבצים כפולים:\n\n"
            for file_name, paths in duplicate_files.items():
                error_message += f"הקובץ '{file_name}' שוכפל:\n"
                for path in paths:
                    error_message += f"- {path}\n"

            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Duplicate Files Detected")
            msg_box.setText(error_message)
            msg_box.exec_()

    def clear_action_triggered(self):
        QSound.play("C:/Windows/Media/Windows Recycle.wav")
        # ניקוי רשימות הנתיבים
        self.audio_files_paths.clear()
        self.new_file_paths.clear()

        # הסרת שדות הקלט מהתצוגה
        for input_field in self.input_fields:
            input_field.deleteLater()

        self.input_fields.clear()

        # הסרת השדות הגרפיים מהתצוגה
        while self.input_fields_layout.count() > 0:
            item = self.input_fields_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.Add_a_label_to_the_frame()

    def restore_names_triggered(self):
        QSound.play("C:/Windows/Media/chord.wav")
        if self.previous_names:
            for key, values in self.previous_names.items():
                original_name = values[0]  # קריאה לאיבר הראשון שברשימת הערכים
                second_value = values[1]
                os.rename(second_value, original_name)
                self.new1_file_paths.append(original_name)

            self.previous_names.clear()
            self.audio_files_paths.clear()
            self.audio_files_paths = self.new1_file_paths.copy()
            self.new1_file_paths.clear()
        else:
            print("Sdasdadadasdasdasdasdasdasdasd")


class JSONFileManager(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ניהול קבצי JSON")
        self.setGeometry(150, 150, 1400, 800)

        # Create a scroll area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget(scroll_area)
        scroll_area.setWidget(self.scroll_content)

        # Create a QHBoxLayout for adding the QGroupBoxes side by side
        layout = QHBoxLayout(self.scroll_content)

        # JSON files
        json_files = ["Title.json", "AlbumArtist.json", "ContributingArtists.json", "TrackNumber.json", "Year.json"]

        # Create QGroupBoxes for each JSON file
        self.group_boxes = {}  # Store references to the group boxes
        for json_file_name in json_files:
            group_box = QGroupBox(json_file_name)
            self.group_layout = QVBoxLayout()  # QVBoxLayout for each group box

            # Load JSON data and create QLineEdit widgets
            json_data = self.load_json_data(json_file_name)
            has_empty_row = False  # Flag to track if an empty row already exists

            for key, value in json_data.items():
                row_layout = QHBoxLayout()  # QHBoxLayout for each row

                # Create QLineEdit for the key
                key_edit = QLineEdit(key)
                key_edit.textChanged.connect(self.update_empty_row_status)
                row_layout.addWidget(key_edit)

                # Create QLineEdit for the value
                value_edit = QLineEdit(value)
                value_edit.textChanged.connect(self.update_empty_row_status)
                row_layout.addWidget(value_edit)

                # Add the row to the group box layout
                self.group_layout.addLayout(row_layout)

                # Check if this row is empty (both key and value are empty strings)
                if key == "" and value == "":
                    has_empty_row = True

            # Add an empty row with two empty QLineEdit widgets if one doesn't exist
            if not has_empty_row:
                empty_row_layout = QHBoxLayout()
                empty_key_edit = QLineEdit()
                empty_key_edit.textChanged.connect(self.update_empty_row_status)
                empty_value_edit = QLineEdit()
                empty_value_edit.textChanged.connect(self.update_empty_row_status)
                empty_row_layout.addWidget(empty_key_edit)
                empty_row_layout.addWidget(empty_value_edit)
                self.group_layout.addLayout(empty_row_layout)


            # Set the layout of the group box
            group_box.setLayout(self.group_layout)

            # Add the group box to the main layout
            layout.addWidget(group_box)

            # Store a reference to the group box
            self.group_boxes[json_file_name] = group_box

        # Set the layout of scroll_content to the QHBoxLayout
        self.scroll_content.setLayout(layout)

        # Set up the scroll area in the main layout
        main_layout = QVBoxLayout(self)

        # Create a toolbar and add a "Save" action
        toolbar = QToolBar("סרגל כלים", self)
        main_layout.addWidget(toolbar)

        save_action = QAction(QIcon(r'dependence\images\save.png'), 'שמור (Ctrl+S)', self)
        # Create a shortcut for Ctrl+S and Ctrl+ד
        save_shortcut = QShortcut(QKeySequence('Ctrl+S'), self)
        save_shortcut.activated.connect(self.save_data_to_json)
        save_shortcut_heb = QShortcut(QKeySequence('Ctrl+ד'), self)
        save_shortcut_heb.activated.connect(self.save_data_to_json)

        save_action.triggered.connect(self.save_data_to_json)
        toolbar.addAction(save_action)

        # Add the scroll area containing the QGroupBoxes
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)

    def load_json_data(self, json_file_name):
        json_path = os.path.join('dependence', 'DicFiles', json_file_name)
        try:
            with open(json_path, 'r', encoding='utf-8') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            return {}  # Return an empty dictionary if the file is not found

    def save_data_to_json(self):
        QSound.play("C:/Windows/Media/chimes.wav")
        # Iterate through the stored group boxes and save the data to JSON files
        for json_file_name, group_box in self.group_boxes.items():
            json_data = {}
            for index in range(group_box.layout().count()):
                row_layout = group_box.layout().itemAt(index)
                key_edit = row_layout.itemAt(0).widget()
                value_edit = row_layout.itemAt(1).widget()
                key = key_edit.text()
                value = value_edit.text()
                json_data[key] = value

            json_path = os.path.join('dependence', 'DicFiles', json_file_name)
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, ensure_ascii=False, indent=4)

    def add_empty_row(self, json_file_name):
        # Get the current group box
        group_box = self.group_boxes[json_file_name]

        # Check if there are any empty rows in the group box
        empty_row_found = False
        for index in range(group_box.layout().count()):
            row_layout = group_box.layout().itemAt(index)
            key_edit = row_layout.itemAt(0).widget()
            value_edit = row_layout.itemAt(1).widget()
            if key_edit.text() == "" and value_edit.text() == "":
                empty_row_found = True
                break

        # If no empty row was found, add a new empty row with two QLineEdit widgets
        if not empty_row_found:
            empty_row_layout = QHBoxLayout()
            empty_key_edit = QLineEdit()
            empty_key_edit.textChanged.connect(self.update_empty_row_status)
            empty_value_edit = QLineEdit()
            empty_value_edit.textChanged.connect(self.update_empty_row_status)
            empty_row_layout.addWidget(empty_key_edit)
            empty_row_layout.addWidget(empty_value_edit)

            # Add the empty row layout to the group box layout
            group_box.layout().addLayout(empty_row_layout)

    def update_empty_row(self, json_file_name, remove=True):
        # Get the current group box
        group_box = self.group_boxes[json_file_name]

        # Create a list to store the indices of empty rows
        empty_row_indices = []

        # Find and store the indices of empty rows
        for index in range(group_box.layout().count()):
            row_layout = group_box.layout().itemAt(index)
            key_edit = row_layout.itemAt(0).widget()
            value_edit = row_layout.itemAt(1).widget()
            if key_edit.text() == "" and value_edit.text() == "":
                empty_row_indices.append(index)

        # Check if there are at least two empty rows
        if len(empty_row_indices) >= 2:
            # Remove the first empty row found
            index_to_remove = empty_row_indices[1]
            row_layout = group_box.layout().itemAt(index_to_remove)
            for i in range(row_layout.count()):
                item = row_layout.itemAt(i)
                widget = item.widget()
                if widget:
                    widget.deleteLater()  # Remove the widget from the layout
            row_layout.deleteLater()  # Remove the layout itself


    def update_empty_row_status(self):
        # Check if there are any empty rows in each group box and update the status label
        for json_file_name, group_box in self.group_boxes.items():
            empty_row_found = False
            for index in range(group_box.layout().count()):
                row_layout = group_box.layout().itemAt(index)
                key_edit = row_layout.itemAt(0).widget()
                value_edit = row_layout.itemAt(1).widget()
                if key_edit.text() == "" and value_edit.text() == "":
                    empty_row_found = True
                    break

            # Update the status label for the current group box
            if empty_row_found:
                self.update_empty_row(json_file_name)
            else:
                self.add_empty_row(json_file_name)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    json_manager = JSONFileManager()  # יצירת החלון לניהול קבצי JSON
    sys.exit(app.exec_())
