@echo off

call .venv\Scripts\activate 

python -m pip install wheel

cd pyinstaller

python setup.py sdist bdist_wheel

