# audep
automated deployment tool

# used as a python package.
pip install poetry

poetry install

poetry build

pip install audep-*.whl 

./audep -f redis.toml -l 10
# used as a stand-alone procedure
pip install  poetry

poetry install

poetry run pyinstaller -F audep-cli.spec 

poetry run pyinstaller -F --upx-dir=./tools/upx32 audep-cli.spec

./audep-cli -f redis.toml -l 10

# windows dependencies
poetry shell

python -m pip install --upgrade pip

pip install pywin32-ctypes

pip install pefile

# linux dependencies

no dependencies

# examples

https://github.com/coolxv/audep-example.git
