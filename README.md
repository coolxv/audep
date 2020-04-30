# audep
automated deployment tool

# use
pip install --user poetry

poetry install

poetry build

pip install audep-*.whl 

poetry run pyinstaller -F audep-cli.spec 

poetry run pyinstaller -F --upx-dir=./tools/upx32 audep-cli.spec

./audep-cli -f redis.toml -l 10

# windows dependencies
poetry shell

python -m pip install --upgrade pip

pip install pywin32-ctypes

pip install pefile

pip install win32com

# linux dependencies

no dependencies

# examples

https://github.com/coolxv/audep-example.git
