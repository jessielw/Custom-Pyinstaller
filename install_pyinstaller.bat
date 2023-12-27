@echo off

call .venv\Scripts\activate 

cd pyinstaller\dist\pyinstaller

python -m pip install .

