# -*- coding:utf-8 -*-
import os
import sys
import string
import logging
import toml
import jmespath
import pyexpander.lib as expander
from .utils import open


class VarTemplate(string.Template):
    delimiter = '%'
    idpattern = '[_a-z][_a-z0-9]*'


class Template:
    """
    模板解析器
    """

    def __init__(self, s, cmd_vars=None, include=None):
        self._s = None
        if isinstance(s, str):
            try:
                logging.debug(s)
                if os.path.exists(s):
                    (result, self._vars) = expander.processToList(self._parseFile(s, False),
                                                                  None, cmd_vars, False, False,
                                                                  False,
                                                                  include)
                else:
                    (result, self._vars) = expander.processToList(expander.parseString(s), None,
                                                                  cmd_vars, False, False,
                                                                  False,
                                                                  include)
            except Exception as e:
                logging.error("Template expander error:".format(e))
                return

            try:
                logging.debug("".join(result))
                self._s = toml.loads("".join(result))
                return
            except TypeError:
                logging.error("Template type error.")
            except toml.TomlDecodeError:
                logging.error("Template decode error.")
            except Exception as e:
                logging.error("Template unexpected error:".format(e))


    def _parseFile(self, filename, no_stdin_warning):
        """parse a file."""
        if filename is None:
            if not no_stdin_warning:
                sys.stderr.write("(reading from stdin)\n")
            try:
                st = sys.stdin.read()
            except KeyboardInterrupt:
                sys.exit(" interrupted\n")
        else:
            with open(filename, "rt") as f:
                st = f.read()
        return expander.parseString(st)

    @property
    def vars(self):
        return self._vars

    @property
    def value(self):
        return self._s

    def get(self, q):
        """
        """
        try:
            if self._s:
                return jmespath.search(q, self._s)
        except Exception as e:
            logging.error("Template get error:", e)
        return None

    def get_hosts(self):
        """
        """
        try:
            if self._s:
                return jmespath.search('hosts', self._s)
        except Exception as e:
            logging.error("Template get hosts error:", e)
        return None

    def get_host_by_name(self, name):
        """
        """
        try:
            if self._s:
                return jmespath.search(f"hosts.{name}", self._s)
        except Exception as e:
            logging.error("Template get host by name error:", e)
        return None

    def get_apps(self):
        """
        """
        try:
            if self._s:
                return jmespath.search('apps', self._s)
        except Exception as e:
            logging.error("Template get apps error:", e)
        return None

    def get_app_by_name(self, name):
        """
        """
        try:
            if self._s:
                return jmespath.search(f"apps.{name}", self._s)
        except Exception as e:
            logging.error("Template get app by name error:", e)
        return None

    def get_tasks(self):
        """
        """
        try:
            if self._s:
                return jmespath.search('tasks', self._s)
        except Exception as e:
            logging.error("Template get tasks error:", e)
        return None

    def get_task_by_name(self, name):
        """
        """
        try:
            if self._s:
                return jmespath.search(f"tasks[?name=='{name}'] | [0]", self._s)
        except Exception as e:
            logging.error("Template get task by name error:", e)
        return None


if __name__ == "__main__":
    pass
