import subprocess
import sys
import os
import platform
import tkinter as tk
from tkinter import messagebox

def is_python_installed():
    try:
        subprocess.run(['python', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            subprocess.run(['python3', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

def create_venv():
    try:
        subprocess.run(['create_venv.bat'], check=True)
        return True
    except subprocess.CalledProcessError:
        try:
            subprocess.run(['create_venv3.bat'], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

def show_error_message(message, error_code):
    error_message = f"{message}\n\nError Code: {error_code}"
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showerror(f"Error {error_code}", error_message)
    root.destroy()

def activate_venv():
    if platform.system() == 'Windows':
        activate_script = os.path.join(script_dir, 'venv', 'Scripts', 'activate.bat')
        command = f'cmd /c "{activate_script}" & pip install -r "{os.path.join(script_dir, "requirements.txt")}" & python "{os.path.join(script_dir, "picodulce.py")}"'
    else:  # Assuming Unix-like OS
        activate_script = os.path.join(script_dir, 'venv', 'bin', 'activate')
        command = f'/bin/bash -c "source \\"{activate_script}\\" && pip install -r \\"{os.path.join(script_dir, "requirements.txt")}\\" && python \\"{os.path.join(script_dir, "picodulce.py")}\\""'

    try:
        subprocess.run(command, check=True, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

if __name__ == "__main__":
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    os.chdir(script_dir)
    
    error_codes = {
        "PythonMissing": 101,
        "RequirementsMissing": 102,
        "ScriptMissing": 103,
        "VenvCreateFailed": 104,
        "VenvActivateFailed": 105,
        "DependenciesInstallFailed": 106,
        "ScriptExecutionFailed": 107
    }

    if not is_python_installed():
        show_error_message("Please install Python.", error_codes["PythonMissing"])
    else:
        if not os.path.exists(os.path.join(script_dir, 'requirements.txt')):
            show_error_message("requirements.txt not found.", error_codes["RequirementsMissing"])
        elif not os.path.exists(os.path.join(script_dir, 'picodulce.py')):
            show_error_message("picodulce.py not found.", error_codes["ScriptMissing"])
        else:
            if os.path.exists(os.path.join(script_dir, 'venv')):
                print("Virtual environment 'venv' already exists.")
                if not activate_venv():
                    show_error_message("Failed to activate the existing virtual environment, install dependencies, or run picodulce.py.", error_codes["VenvActivateFailed"])
                else:
                    print("Existing virtual environment activated, dependencies installed, and picodulce.py executed successfully.")
            else:
                if not create_venv():
                    show_error_message("Failed to create a virtual environment using both 'create_venv.bat' and 'create_venv3.bat'.", error_codes["VenvCreateFailed"])
                else:
                    print("Virtual environment created successfully.")
                    if not activate_venv():
                        show_error_message("Failed to activate the virtual environment, install dependencies, or run picodulce.py.", error_codes["VenvActivateFailed"])
                    else:
                        print("Virtual environment activated, dependencies installed, and picodulce.py executed successfully.")
