import sys
import os
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QTextEdit, QCheckBox, QLineEdit, QHBoxLayout, QSizePolicy
import win32com.client
from PyQt5.QtCore import Qt

class Installer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Picodulce Launcher')
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        self.title_label = QLabel('<h2>Picodulce Launcher Installer</h2>')
        self.layout.addWidget(self.title_label)

        self.description_label = QLabel('Welcome to the Picodulce Launcher Installer. This installer will help you set up the Picodulce Launcher on your system.')
        self.layout.addWidget(self.description_label)

        self.next_button = QPushButton('Next')
        self.next_button.clicked.connect(self.show_license)
        self.layout.addWidget(self.next_button)

        self.setLayout(self.layout)

        self.source_directory = None
        self.destination_directory = None
        self.license_content = None

        # Set default installation path to user's home directory with a subfolder "picodulce"
        self.default_install_path = os.path.join(os.path.expanduser("~"), 'picodulce')
        if not os.path.exists(self.default_install_path):
            os.makedirs(self.default_install_path)

    def show_license(self):
        self.next_button.deleteLater()
        
        self.title_label.setText('<h2>License Agreement</h2>')
        self.description_label.setText('Please read the following license carefully:')
        
        self.license_text = QTextEdit()
        self.license_text.setReadOnly(True)
        
        license_file_path = os.path.join(os.path.dirname(__file__), 'LICENSE.md')
        if os.path.exists(license_file_path):
            with open(license_file_path, 'r') as f:
                self.license_content = f.read()
                self.license_text.setPlainText(self.license_content)
        else:
            self.license_text.setPlainText('LICENSE.md file not found.')
        
        self.layout.addWidget(self.license_text)

        self.accept_checkbox = QCheckBox('I accept the Terms and Conditions')
        self.accept_checkbox.stateChanged.connect(self.toggle_next_button)
        self.layout.addWidget(self.accept_checkbox)

        self.next_button = QPushButton('Next')
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self.show_directory_selection)
        
        # Align the button to the right side and make it smaller
        self.next_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.next_button.setFixedWidth(100)
        self.layout.addWidget(self.next_button, alignment=Qt.AlignRight)

    def toggle_next_button(self):
        self.next_button.setEnabled(self.accept_checkbox.isChecked())

    def show_directory_selection(self):
        self.title_label.setText('<h2>Choose Installation Directory</h2>')
        self.description_label.setText('Choose a directory for the install:')
        
        self.license_text.hide()
        self.accept_checkbox.hide()
        self.next_button.hide()
        
        self.directory_layout = QHBoxLayout()

        self.directory_input = QLineEdit(self)
        self.directory_input.setText(self.default_install_path)
        self.directory_layout.addWidget(self.directory_input)

        self.explore_button = QPushButton('Explore', self)
        self.explore_button.clicked.connect(self.select_directory)
        self.directory_layout.addWidget(self.explore_button)

        self.layout.addLayout(self.directory_layout)

        self.next_button = QPushButton('Next')
        self.next_button.clicked.connect(self.show_shortcut_options)
        
        # Align the button to the right side and make it smaller
        self.next_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.next_button.setFixedWidth(100)
        self.layout.addWidget(self.next_button, alignment=Qt.AlignRight)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Directory')
        if directory:
            self.directory_input.setText(directory)

    def show_shortcut_options(self):
        self.title_label.setText('<h2>Additional Options</h2>')
        self.description_label.setText('Select additional options:')
        
        self.directory_input.hide()
        self.explore_button.hide()
        self.next_button.hide()
        
        self.shortcut_checkbox = QCheckBox('Create a shortcut on the desktop')
        self.shortcut_checkbox.setChecked(True)
        self.layout.addWidget(self.shortcut_checkbox)
        
        self.startmenu_checkbox = QCheckBox('Add it to Start Menu')
        self.startmenu_checkbox.setChecked(True)
        self.layout.addWidget(self.startmenu_checkbox)

        self.install_button = QPushButton('Install')
        self.install_button.clicked.connect(self.show_install_screen)
        
        # Align the button to the right side and make it smaller
        self.install_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.install_button.setFixedWidth(100)
        self.layout.addWidget(self.install_button, alignment=Qt.AlignRight)

    def show_install_screen(self):
        self.title_label.setText('<h2>Installing</h2>')
        self.description_label.setText('Installation in progress. Please wait...')
        
        self.shortcut_checkbox.hide()
        self.startmenu_checkbox.hide()
        self.install_button.hide()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.layout.addWidget(self.log_text)

        self.install()

    def log(self, message):
        self.log_text.append(message)
        QApplication.processEvents()  # Update the GUI

    def install(self):
        self.destination_directory = self.directory_input.text()
        if not self.destination_directory:
            self.log('Error: Please select a directory for installation.')
            return

        try:
            self.log('Creating installation directory...')
            os.makedirs(self.destination_directory, exist_ok=True)
            
            picodulce_folder = os.path.join(os.path.dirname(__file__), 'picodulce')
            if not os.path.isdir(picodulce_folder):
                self.log('Error: "picodulce" folder not found.')
                return

            self.log(f'Copying files to {self.destination_directory}...')
            for item_name in os.listdir(picodulce_folder):
                source_item = os.path.join(picodulce_folder, item_name)
                destination_item = os.path.join(self.destination_directory, item_name)
                if os.path.isdir(source_item):
                    self.log(f'Copying directory {item_name}...')
                    shutil.copytree(source_item, destination_item, dirs_exist_ok=True)
                else:
                    self.log(f'Copying file {item_name}...')
                    shutil.copy2(source_item, destination_item)
            
            if self.shortcut_checkbox.isChecked():
                self.log('Creating desktop shortcut...')
                self.create_shortcut()
            if self.startmenu_checkbox.isChecked():
                self.log('Adding to Start Menu...')
                self.add_to_startmenu()

            self.log('Installation completed successfully.')
        except Exception as e:
            self.log(f'Error: Failed to install: {str(e)}')

    def create_shortcut(self):
        exe_path = os.path.join(self.destination_directory, 'pds.exe')
        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop', 'PicoDulce Launcher.lnk')

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(desktop_path)
        shortcut.Targetpath = exe_path
        shortcut.WorkingDirectory = os.path.dirname(exe_path)
        shortcut.save()

    def add_to_startmenu(self):
        exe_path = os.path.join(self.destination_directory, 'pds.exe')
        startmenu_path = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'PicoDulce Launcher.lnk')

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(startmenu_path)
        shortcut.Targetpath = exe_path
        shortcut.WorkingDirectory = os.path.dirname(exe_path)
        shortcut.save()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    installer = Installer()
    installer.show()
    sys.exit(app.exec_())
