#!/usr/bin/env python
import logging
from lark import Lark, Transformer, v_args
from .utils import ParserError


class ActionModel:
    """
    """

    def __init__(self, tree):
        self._plugin = None
        self._action = None
        self._args = []
        self._kwargs = {}
        self._result = None
        self._processor = {
            'plugin': self.__plugin,
            'action': self.__action,
            'params': self.__params,
            'result': self.__result
        }

        for t in tree:
            method = self._processor.get(t.data)
            if method:
                method(t.children)

    @property
    def plugin(self):
        return self._plugin

    @property
    def action(self):
        return self._action

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs

    @property
    def result(self):
        return self._result

    def __str__(self):
        return f"the plugin is {self._plugin}, action is {self._action}," \
               f" args is {self._args}, kwargs is {self._kwargs}," \
               f" result is {self._result}"

    __repr__ = __str__

    def __plugin(self, children):
        logging.debug(children[0])
        self._plugin = children[0]

    def __action(self, children):
        logging.debug(children[0].value)
        self._action = children[0].value

    def __params(self, children):
        logging.debug(children)
        for t in children:
            if t.children[0].data == 'kwargs':
                if t.children[0].children[0].children[0].value not in self._kwargs:
                    self._kwargs[t.children[0].children[0].children[0].value] = t.children[0].children[1].children[0]
                else:
                    raise SyntaxError('parameter duplicate definition')
            else:
                self._args.append(t.children[0].children[0].children[0])

    def __result(self, children):
        logging.debug(children[0].children[0])
        self._result = children[0].children[0]


class CommandModel:
    def __init__(self, tree):
        self._flag = 'r'
        self._command = None
        self._result = None
        self._processor = {
            'command': self.__command,
            'result': self.__result,
            'flag': self.__flag
        }

        for t in tree:
            method = self._processor.get(t.data)
            if method:
                method(t.children)

    @property
    def flag(self):
        return self._flag

    @property
    def command(self):
        return self._command

    @property
    def result(self):
        return self._result

    def __str__(self):
        return f"the command is {self._command}, flag is {self._flag}, result is {self._result} "

    __repr__ = __str__

    def __command(self, children):
        logging.debug(children[0])
        self._command = children[0]

    def __result(self, children):
        logging.debug(children[0].children[0])
        self._result = children[0].children[0]

    def __flag(self, children):
        if children:
            logging.debug(children[0])
            self._flag = children[0].value
        else:
            pass


class ConfigModel:
    def __init__(self, tree):
        self._file = None
        self._clause = []
        self._flag = None
        self._processor = {
            'clause': self.__clause,
            'file': self.__file,
            'flag': self.__flag
        }
        for t in tree:
            method = self._processor.get(t.data)
            if method:
                method(t.children)

    @property
    def file(self):
        return self._file

    @property
    def clause(self):
        return self._clause

    @property
    def flag(self):
        return self._flag

    def __str__(self):
        return f"the file is {self._file}, clause is {self._clause}, flag is {self._flag}"

    __repr__ = __str__

    def __clause(self, children):
        logging.debug(children)
        for t in children:
            self._clause.append({"match": t.children[0].children[0], "value": t.children[1].children[0]})

    def __file(self, children):
        logging.debug(children)
        self._file = children[0]

    def __flag(self, children):
        logging.debug(children[0])
        self._flag = children[0].value


class FileModel:
    def __init__(self, tree):
        self._local = None
        self._remote = None
        self._operation = None
        self._lflag = None
        self._rflag = None
        self._mode = []
        self._processor = {
            'local': self.__local,
            'remote': self.__remote,
            'operation': self.__operation,
            'mode': self.__mode,
            'lflag': self.__lflag,
            'rflag': self.__rflag
        }
        for t in tree:
            method = self._processor.get(t.data)
            if method:
                method(t.children)

    @property
    def local(self):
        return self._local.strip()

    @property
    def remote(self):
        return self._remote.strip()

    @property
    def operation(self):
        return self._operation

    @property
    def lflag(self):
        return self._lflag

    @property
    def rflag(self):
        return self._rflag

    @property
    def mode(self):
        return self._mode

    def __str__(self):
        return f"the local is {self._local}, lflag is {self._lflag}," \
               f" remote is {self._remote}, rflag is {self._rflag}," \
               f" mode is {self._mode}"

    __repr__ = __str__

    def __local(self, children):
        logging.debug(children)
        self._local = children[0]

    def __remote(self, children):
        logging.debug(children)
        self._remote = children[0]

    def __operation(self, children):
        logging.debug(children[0])
        self._operation = children[0].value

    def __lflag(self, children):
        logging.debug(children[0])
        self._lflag = children[0].children[0].value

    def __rflag(self, children):
        logging.debug(children[0])
        self._rflag = children[0].children[0].value
        if self._operation == "=>" and self._lflag == 'd' and self._rflag == "f":
            raise SyntaxError('file model flag error')
        elif self._operation == "<=" and self._lflag == 'f' and self._rflag == "d":
            raise SyntaxError('file model flag error')

    def __mode(self, children):
        logging.debug(children[0])
        for t in children:
            permit = t.children[1].children[0] * 100 + t.children[1].children[1] * 10 + t.children[1].children[2]
            self._mode.append({"filter": t.children[0].children[0], "permit": permit})


class TaskModel:
    def __init__(self, tree):
        self._app = None
        self._host = None
        self._var = {}
        self._vme = None
        self._aps_type = None
        self._aps_value = None
        self._processor = {
            'app': self.__app,
            'host': self.__host,
            'params': self.__params,
            'scheduler': self.__scheduler,
        }

        for t in tree:
            method = self._processor.get(t.data)
            if method:
                method(t.children)

    @property
    def aps_type(self):
        return self._aps_type

    @property
    def aps_value(self):
        return self._aps_value

    @property
    def app(self):
        return self._app

    @app.setter
    def app(self, v):
        self._app = v

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, v):
        self._host = v

    @property
    def var(self):
        return self._var

    @var.setter
    def var(self, v):
        self._var = v

    @property
    def vme(self):
        return self._vme

    @vme.setter
    def vme(self, v):
        self._vme = v

    def __str__(self):
        return f"the app is {self._app}, host is {self._host}, var is {self._var}"

    __repr__ = __str__

    def __app(self, children):
        logging.debug(children[0])
        self._app = children[0]

    def __host(self, children):
        logging.debug(children[0])
        self._host = children[0]

    def __params(self, children):
        logging.debug(children)
        for t in children:
            if t.children[0].children[0].value not in self._var:
                self._var[t.children[0].children[0].value] = t.children[1].children[0]
            else:
                raise SyntaxError('parameter duplicate definition')

    def __scheduler(self, children):
        logging.debug(children)
        self._aps_type = children[0].data
        self._aps_value = children[0].children[1]


_action_grammar = """
    start: (call | exec)*                                            -> start
    call: [plugin "::"] action  "(" params ")" ["->" result]         -> call
    plugin: CNAME
    action: CNAME
    params: [var ("," var)*]
    var: (args | kwargs)
    args: value
    kwargs: name "=" value
    exec: flag command ["->" result]                                 -> exec
    !flag: ("l" | "r" | "s")?
    command: string
    result: value
    name: CNAME 
    value: number | string
    number: SIGNED_NUMBER                                 -> number
    string: ESCAPED_STRING                                -> string
    %import common.CNAME
    %import common.SIGNED_NUMBER
    %import common.ESCAPED_STRING 
    %import common.WS
    %ignore WS
"""

_config_grammar = """
    start: config*                                        -> start
    config: flag file "(" clause ")"                      -> config
    clause: pattern ("," pattern)* 
    pattern:  match "=>" value
    file: string
    !flag: ("dj" | "dy" | "dt" | "dx" | "di"  | "dc" | "ts" | "tt" | "tl")
    match: string
    value: number | string
    number: SIGNED_NUMBER                                 -> number
    string: ESCAPED_STRING                                -> string
    %import common.CNAME
    %import common.SIGNED_NUMBER
    %import common.ESCAPED_STRING 
    %import common.WS
    %ignore WS
"""

_file_grammar = """
    start: file*                                                 -> start
    file: lflag local operation rflag remote "(" [mode] ")"      -> file
    local: string
    remote: string
    !operation: (">>" | "<<")
    lflag: flag
    rflag: flag
    !flag: ("f" | "d")
    mode: [pattern] ("," pattern)* 
    pattern:  filter "=>" permit
    filter: string
    permit:  number~3
    !number: ("1"|"2"|"4"|"5"|"6"|"7")                    -> number
    string: ESCAPED_STRING                                -> string
    %import common.ESCAPED_STRING 
    %import common.WS
    %ignore WS
"""

_task_grammar = """
    start: task+                                           -> start
    task: [scheduler] app "@" host "(" params ")"          -> task
    scheduler: (date | interval | cron | event)
    !date: "d[" string "]"
    !interval: "i[" string "]"
    !cron: "c[" string "]"
    !event: "e[" string "]"
    app: CNAME
    host: CNAME
    params: [var ("," var)*]
    var: name "=" value
    name: CNAME 
    value: number | string
    number: SIGNED_NUMBER                                 -> number
    string: ESCAPED_STRING                                -> string
    %import common.CNAME
    %import common.SIGNED_NUMBER
    %import common.ESCAPED_STRING 
    %import common.WS
    %ignore WS
"""


@v_args(inline=False)
class _ActionTree(Transformer):

    def __init__(self):
        self.vars = []

    def start(self, c):
        return self.vars

    def call(self, c):
        logging.debug(c)
        act = ActionModel(c)
        self.vars.append(act)
        return c

    def exec(self, c):
        logging.debug(c)
        cmd = CommandModel(c)
        self.vars.append(cmd)
        return c

    def number(self, c):
        logging.debug(c)
        return int(c[0].value)

    def string(self, c):
        logging.debug(c)
        return c[0].value[1:-1]


@v_args(inline=False)
class _ConfigTree(Transformer):

    def __init__(self):
        self.vars = []

    def start(self, c):
        return self.vars

    def config(self, c):
        logging.debug(c)
        conf = ConfigModel(c)
        self.vars.append(conf)
        return c

    def number(self, c):
        logging.debug(c)
        return int(c[0].value)

    def string(self, c):
        logging.debug(c)
        return c[0].value[1:-1]


@v_args(inline=False)
class _TaskTree(Transformer):

    def __init__(self):
        self.vars = []

    def start(self, c):
        return self.vars

    def task(self, c):
        logging.debug(c)
        tsk = TaskModel(c)
        self.vars.append(tsk)
        return c

    def number(self, c):
        logging.debug(c)
        return int(c[0].value)

    def string(self, c):
        logging.debug(c)
        return c[0].value[1:-1]


@v_args(inline=False)
class _FileTree(Transformer):

    def __init__(self):
        self.vars = []

    def start(self, c):
        return self.vars

    def file(self, c):
        logging.debug(c)
        conf = FileModel(c)
        self.vars.append(conf)
        return c

    def number(self, c):
        logging.debug(c)
        return int(c[0].value)

    def string(self, c):
        logging.debug(c)
        return c[0].value[1:-1]


class Parser:
    """
    动作解析器
    """

    def __init__(self, t):
        self._type = t
        try:
            if t == 'action':
                iparser = Lark(_action_grammar, parser='lalr', transformer=_ActionTree())
            elif t == 'config':
                iparser = Lark(_config_grammar, parser='lalr', transformer=_ConfigTree())
            elif t == 'task':
                iparser = Lark(_task_grammar, parser='lalr', transformer=_TaskTree())
            elif t == 'file':
                iparser = Lark(_file_grammar, parser='lalr', transformer=_FileTree())
            else:
                raise ParserError('parameter not supported: {}'.format(t))
            self._parser = iparser.parse
            return
        except Exception as e:
            logging.error('Parser init error: {}'.format(e))
        self._parser = None

    def parse(self, text):
        """
        parse interface
        """
        try:
            if self._parser:
                return self._parser(text)
        except Exception as e:
            if self._type == 'action':
                logging.error('Parser parse action error: {}'.format(e))
            elif self._type == 'config':
                logging.error('Parser parse config error: {}'.format(e))
            elif self._type == 'task':
                logging.error('Parser parse task error: {}'.format(e))
            elif self._type == 'file':
                logging.error('Parser parse file error: {}'.format(e))
            else:
                logging.error('Parser parse error: {}'.format(e))
        return None


if __name__ == '__main__':
    pass
