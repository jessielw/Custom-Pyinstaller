from pathlib import Path
import ctypes

starting_dir = str(Path.cwd())

commands = f"/k pushd {starting_dir} && python main_process.py"
ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", commands, None, 1)
