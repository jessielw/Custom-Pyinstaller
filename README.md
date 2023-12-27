## Description

A set of scripts designed to streamline the process of downloading, creating a virtual environment, building, extracting, and installing PyInstaller to prevent false-positive virus detections.

A `venv` is automatically created to build pyinstaller in the root of the project, so your python intall is left untouched. This `venv` will automatically be removed after the job is completed.

This utility is intended for use on **Windows 8 or greater**.

## System Requirements

- Python (what ever is supported by pyinstaller at the time)
- Administrative privileges is required to run the scripts, however it will automatically elevate it for you.

## Usage

1. Clone this repository to a directory of your choice.

2. Ensure you have Python installed on your Windows operating system (Windows 8 or higher).

3. Ensure you have either MinGW or Chocolatey installed. (Chocolatey is used automatically to install MinGW64).

4. Open a terminal inside the cloned directory.

5. Run the command `python run.py`.

6. Once the process is complete, an Explorer window will open with the path to `pyinstaller.exe`. You can now use this custom PyInstaller to build binaries for your Python programs.

## Reference

- [GitHub Actions Workflow for PyInstaller Builds](https://github.com/yt-dlp/Pyinstaller-Builds/blob/master/.github/workflows/build.yml)
