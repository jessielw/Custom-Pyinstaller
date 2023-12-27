import subprocess
import ctypes
import os
from pathlib import Path
import shutil
import tarfile

starting_dir = Path.cwd()


def install_venv():
    subprocess.run(["python", "-m", "venv", ".venv"], check=True)


def is_admin():
    """
    Determine whether the current script has admin privilege
    @return: bool. whether the script is in admin mode
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def check_chocolatey():
    try:
        subprocess.check_output(["choco", "--version"])
        print("Chocolatey is installed.")
        return True
    except FileNotFoundError:
        print("Chocolatey is not installed.")
        return False
    except subprocess.CalledProcessError:
        print("Error checking Chocolatey.")
        return False


def check_mingw():
    try:
        subprocess.check_output(["gcc", "--version"])
        print("MinGW-w64 is installed.")
        return True
    except FileNotFoundError:
        print("MinGW-w64 is not installed.")
        return False
    except subprocess.CalledProcessError:
        print("Error checking MinGW-w64.")
        return False


def check_git():
    try:
        subprocess.check_output(["git", "--version"])
        print("Git is installed.")
        return True
    except FileNotFoundError:
        print("Git is not installed.")
        return False
    except subprocess.CalledProcessError:
        print("Error checking for Git.")
        return False


def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat

    # Is the error an access error?
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def clone_pyinstaller():
    pyinstaller_path = Path.cwd() / "pyinstaller"
    if pyinstaller_path.exists():
        shutil.rmtree(str(pyinstaller_path), ignore_errors=False, onerror=onerror)

    subprocess.run(
        [
            "git",
            "clone",
            "https://github.com/pyinstaller/pyinstaller",
            str(pyinstaller_path),
        ],
        check=True,
    )
    pyinstaller_path = Path.cwd() / "pyinstaller"
    if pyinstaller_path.is_dir() and pyinstaller_path.exists():
        return True


def check_for_dependencies():
    if not check_mingw():
        choco_installed = check_chocolatey()
        if not choco_installed:
            print("You must install Chocolatey")
            return False
        else:
            check_admin = is_admin()
            if not check_admin:
                print("You must run as administrator")
                return False
            else:
                subprocess.run(["choco", "install", "mingw"], check=True)

    if check_mingw():
        if not check_git():
            print("You must install git")
            return False

        get_pyinstaller = clone_pyinstaller()
        if not get_pyinstaller:
            return False
        return True


def extract_pyinstaller():
    dist_path = starting_dir / "pyinstaller" / "dist"
    os.chdir(dist_path)

    # Find the tar.gz file
    tar_files = list(Path.cwd().glob("*.tar.gz"))

    if not tar_files:
        print("No .tar.gz files found in the directory.")
        return

    tar_file = tar_files[0]  # Assuming there is only one .tar.gz file

    # Extract the content
    with tarfile.open(tar_file, "r:gz") as tar:
        # Extract to a temporary folder
        temp_folder = Path.cwd() / "temp_extraction"
        tar.extractall(temp_folder)

    # Find the extracted folder
    extracted_folder = next(temp_folder.iterdir())

    # Rename the folder to 'pyinstaller'
    extracted_folder.rename(Path.cwd() / "pyinstaller")

    # Optionally, remove the temporary folder
    temp_folder.rmdir()


def main():
    install_venv()

    dependencies = check_for_dependencies()
    if not dependencies:
        print("Missing a dependency")
        return False

    pyinstaller_path = Path.cwd() / "pyinstaller"

    os.chdir(pyinstaller_path / "bootloader")

    subprocess.run(
        ["python", "waf", "distclean", "all", "--target-arch=64bit", "--gcc"],
        check=True,
    )

    os.chdir(starting_dir)

    subprocess.run(["cmd", "/c", "build_pyinstaller.bat"], check=True)

    extract_pyinstaller()

    os.chdir(starting_dir)

    subprocess.run(["cmd", "/c", "install_pyinstaller.bat"], check=True)

    os.chdir(starting_dir)

    get_pyinstaller_path = Path.cwd() / ".venv" / "Scripts"

    subprocess.run(["explorer", get_pyinstaller_path], shell=True)


if __name__ == "__main__":
    main()
