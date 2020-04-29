import sys
import shutil
import logging
import datetime
import re
from configparser import SafeConfigParser
from collections import OrderedDict
import toml
import json
import yaml
import yamlordereddictloader
import xmltodict
import glom
from abc import ABCMeta, abstractmethod
from .utils import open, ConfigError


class _IConfig(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, file):
        self._file = file
        self._data = None

    @property
    def file(self):
        return self._file

    @property
    def data(self):
        return self._data

    def assign(self, match, value):
        try:
            if self._data:
                glom.glom(self._data, match)
                glom.assign(self._data, match, value)
                return True
            else:
                return False
        except:
            return False

    @abstractmethod
    def save(self, old_bak=True):
        if old_bak:
            time_stamp = datetime.datetime.now()
            shutil.copy(self._file, self._file + time_stamp.strftime('-%Y%m%d-%H%M%S') + ".bak")

    @abstractmethod
    def print(self):
        pass


class JsonConfig(_IConfig):
    def __init__(self, file):
        super().__init__(file)
        with open(file, "rt") as f:
            self._data = json.load(f, object_pairs_hook=OrderedDict)

    def save(self, old_bak=True):
        if self._data:
            super().save(old_bak)
            with open(self._file, 'wt') as f:
                json.dump(self._data, f, indent=2, sort_keys=False)

    def print(self):
        if self._data:
            print(json.dumps(self._data, indent=2, sort_keys=False))


class YamlConfig(_IConfig):
    def __init__(self, file):
        super().__init__(file)
        with open(file, "rt") as f:
            self._data = yaml.load(f, Loader=yamlordereddictloader.Loader)

    def save(self, old_bak=True):
        if self._data:
            super().save(old_bak)
            with open(self._file, 'wt') as f:
                yaml.dump(self._data, f)

    def print(self):
        if self._data:
            print(yaml.dump(self._data))


class TomlConfig(_IConfig):
    def __init__(self, file):
        super().__init__(file)
        with open(file, "rt") as f:
            self._data = toml.load(f, _dict=OrderedDict)

    def save(self, old_bak=True):
        if self._data:
            super().save(old_bak)

            with open(self._file, 'wt') as f:
                toml.dump(self._data, f)

    def print(self):
        if self._data:
            print(toml.dumps(self._data))


class XmlConfig(_IConfig):
    def __init__(self, file):
        super().__init__(file)
        with open(file, "rt") as f:
            self._data = xmltodict.parse(f.read(), process_namespaces=True)

    def save(self, old_bak=True):
        if self._data:
            super().save(old_bak)

            with open(self._file, 'wt') as f:
                xml = xmltodict.unparse(self._data, pretty=True)
                f.write(xml)

    def print(self):
        if self._data:
            print(xmltodict.unparse(self._data, pretty=True))


class IniConfig(_IConfig):
    def __init__(self, file):
        super().__init__(file)
        #
        sections_dict = OrderedDict()
        with open(file, "rt") as f:
            config = SafeConfigParser()
            config.read_file(f)
            # get all defaults
            defaults = config.defaults()
            temp_dict = {}
            for k, v in defaults.items():
                temp_dict[k] = v
            sections_dict['default'] = temp_dict
            # get sections and iterate over each
            sections = config.sections()
            for section in sections:
                options = config.options(section)
                temp_dict = {}
                for option in options:
                    if option not in sections_dict['default']:
                        temp_dict[option] = config.get(section, option)

                sections_dict[section] = temp_dict

        self._data = sections_dict
        print(self._data)

    def save(self, old_bak=True):
        if self._data:
            super().save(old_bak)
            with open(self._file, 'wt') as f:
                config = SafeConfigParser()
                config.read_dict(self._data)
                config.write(f)

    def print(self):
        if self._data:
            config = SafeConfigParser()
            config.read_dict(self._data)
            config.write(sys.stdout)


class SedConfig(_IConfig):
    def __init__(self, file):
        super().__init__(file)
        with open(file, "rt") as f:
            self._data = f.readlines()

    def assign(self, match, value):
        try:
            if self._data:
                rec = re.compile(match)
                for idx, val in enumerate(self._data):
                    s, n = rec.subn(value, val, re.S)
                    if n > 0:
                        self._data[idx] = s
                return True
        except:
            pass
        return False

    def save(self, old_bak=True):
        if self._data:
            super().save(old_bak)
            with open(self._file, 'wt') as f:
                f.writelines(self._data)

    def print(self):
        if self._data:
            print(''.join(self._data))


class LineConfig(_IConfig):
    def __init__(self, file):
        super().__init__(file)
        with open(file, "rt") as f:
            self._data = f.readlines()

    def assign(self, match, value):
        try:
            if self._data:
                rec = re.compile(match)
                for idx, val in enumerate(self._data):
                    if rec.search(string=val):
                        pre = ""
                        post = ""
                        m1 = re.search('(?P<pre>\s*)(?:.+)(?P<post>\s+)', val, re.S)
                        if m1:
                            pre = m1.group('pre')
                            post = m1.group('post')
                        self._data[idx] = pre + value + post
                        return True
        except:
            pass
        return False

    def save(self, old_bak=True):
        if self._data:
            super().save(old_bak)
            with open(self._file, 'wt') as f:
                f.writelines(self._data)

    def print(self):
        if self._data:
            print(''.join(self._data))


class Config:
    def __init__(self, debug):
        self._debug = debug
        self._processor = {
            'dj': [self.__process, "JsonConfig"],
            'dy': [self.__process, "YamlConfig"],
            'dt': [self.__process, "TomlConfig"],
            'dx': [self.__process, "XmlConfig"],
            'di': [self.__process, "IniConfig"],
            'ts': [self.__process, "SedConfig"],
            'tl': [self.__process, "LineConfig"]

        }

    def config(self, of):
        m = self._processor.get(of.flag)
        if m:
            from . import config
            sm = config
            if hasattr(sm, m[1]):
                c = getattr(sm, m[1])
                m[0](c(of.file), of.clause, m[1])
                return
        raise ConfigError(f'the format {of.flag} of the config is not supported')

    def __process(self, file, clause, info):
        for mv in clause:
            if not file.assign(mv['match'], mv['value']):
                raise ConfigError(f'{info} config assign failed,match {mv["match"]}, value {mv["value"]}')
        if self._debug:
            print(f"[DEBUG MODE <start]: {file.file}")
            file.print()
            print(f"[DEBUG MODE <end  ]: {file.file}")
        else:
            file.save()


if __name__ == '__main__':
    pass
