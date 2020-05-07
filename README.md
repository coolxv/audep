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


```
#const
$py(ip1='192.168.10.10')
#host
[hosts.centos1]
host = 'root@$(ip1):22'
pwd = '123456'

#app
[apps.redis]
file = '''
       d"$(lcwd)/../redis/">>d"/opt/redis/"
       (
            "redis-"=>775,
            "xxx-"=>775
       )
       '''
config = '''
         tl"$(lcwd)/../redis/conf/redis.conf"
         (
            "^bind"=>"bind 127.0.0.1",
            "^port"=>"port %{port}",
            "^daemonize"=>"daemonize yes"
         )
         '''
action = '''
         r"ls"->0
         redis::start("/opt/redis/")
         '''

#task
[[tasks]]
name = 'redis'
task = '''
       redis@centos1(port=6379)
       '''
```

# documentation 

[中文](doc/audep_zh.png)|[English](doc/audep_en.png)
