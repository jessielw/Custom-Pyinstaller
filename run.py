import subprocess
import ctypes
import os
import shutil
import tarfile
from pathlib import Path


def onerror(func, path, exc_info):
    """
    Error handler for shutil.rmtree.
    If the error is due to an access error (read-only file),
    it attempts to add write permission and then retries.
    If the error is for another reason, it re-raises the error.
    Usage: shutil.rmtree(path, onerror=onerror)
    """
    import stat

    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def re_launch_elevated():
    commands = f"/k pushd {starting_dir} && python run.py"
    ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", commands, None, 1)


def install_venv():
    venv_path = Path(".venv")
    if venv_path.exists():
        shutil.rmtree(".venv", ignore_errors=False, onerror=onerror)
    subprocess.run(["python", "-m", "venv", ".venv"], check=True)


def is_admin():
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


def check_mingw(echo_output: bool):
    try:
        subprocess.check_output(["gcc", "--version"])
        if echo_output:
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
    if not check_mingw(True):
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

    if check_mingw(False):
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

    # Assuming there is only one .tar.gz file
    tar_file = tar_files[0]

    # Extract the content
    with tarfile.open(tar_file, "r:gz") as tar:
        # Extract to a temporary folder
        temp_folder = Path.cwd() / "temp_extraction"
        tar.extractall(temp_folder)

    # Find the extracted folder
    extracted_folder = next(temp_folder.iterdir())

    # Rename the folder to 'custom_pyinstaller'
    pyinstaller_path = extracted_folder.rename(starting_dir / "custom_pyinstaller")

    # Optionally, remove the temporary folder
    temp_folder.rmdir()

    return pyinstaller_path


def clean_dir(staring_dir):
    shutil.rmtree(str(staring_dir / ".venv"), ignore_errors=False, onerror=onerror)
    shutil.rmtree(
        str(staring_dir / "pyinstaller"), ignore_errors=False, onerror=onerror
    )


def main():
    check_admin = is_admin()
    if not check_admin:
        re_launch_elevated()
        return

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

    custom_pyinstaller = extract_pyinstaller()

    if custom_pyinstaller.exists():
        subprocess.run(["explorer", str(custom_pyinstaller.parent)])

        os.chdir(starting_dir)

        clean_dir(starting_dir)


if __name__ == "__main__":
    starting_dir = Path.cwd()
    main()
