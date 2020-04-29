import os
import copy
import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from .template import Template, VarTemplate
from .executor import Executor
from .parser import Parser, ActionModel, CommandModel
from .action import Action, Plugin
from .file import File
from .config import Config
from .utils import check_null_raise, check_none_raise
from .utils import get_abspath


class Vm:
    def __init__(self, f, cmd_var, option, task_list, plugin_list):
        self._f = f
        self._option = option
        self._task_list = task_list
        self._plugin_list = get_abspath(plugin_list)
        self._scheduler = BlockingScheduler()
        self._var = self._get_glb_var(cmd_var)
        self._template = Template(self._f, self._var, self._option.include)
        self._plugin = Plugin(self._plugin_list)
        self._vme_pool = {}
        self._parse_task_list = []
        self._parse_aps_task_list = []

    def run(self):
        try:
            if self._template.value:
                self._dispatch_task()
            else:
                logging.error("Template file syntax error.")
        except Exception as e:
            logging.error(f"Vm run error: {e}")
        except KeyboardInterrupt:
            print("process ctrl+c, exit")
        else:
            print("process execute successfully")

    def _dispatch_task(self):
        task = []
        if self._task_list:
            for name in self._task_list:
                t = self._template.get_task_by_name(name)
                if t:
                    task.append(t)
                else:
                    logging.error("task is not exist.")
        else:
            t = self._template.get_tasks()
            if t:
                task = t

        logging.info(f"The number of tasks is {len(task)}.")
        # build task
        for t in task:
            tp = Parser("task")
            ot = tp.parse(t['task'])
            for et in ot:
                self._assemble_task(et)
                if et.aps_type:
                    self._parse_aps_task_list.append(et)
                else:
                    self._parse_task_list.append(et)

        # do immediately task
        for et in self._parse_task_list:
            if "file" in et.app:
                self._do_get_file(et)
            if "config" in et.app:
                self._do_config(et)
            if "file" in et.app:
                self._do_put_file(et)
            if "action" in et.app:
                self._do_action(et)
        # do scheduler task
        for et in self._parse_aps_task_list:
            if et.aps_type == 'date':
                pass
            elif et.aps_type == 'cron':
                pass
            else:                        # interval
                pass
        if self._scheduler.get_jobs():
            self._scheduler.start()

    def _assemble_task(self, et):
        # get app
        et.app = copy.deepcopy(check_null_raise(self._template.get_app_by_name(et.app), f"get {et.app} app failed"))
        # get host
        et.host = copy.deepcopy(
            check_null_raise(self._template.get_host_by_name(et.host), f"get {et.host} host failed"))
        # build vm executor
        et.vme = check_null_raise(self._get_vme(et.host["host"], et.host["pwd"]), f"get vm failed")
        # build var
        cgv = copy.deepcopy(self._var)
        tv = self._get_task_var(et.vme, et.var)
        cgv.update(tv)
        et.var = cgv
        # task variable replace
        if "file" in et.app:
            et.app["file"] = VarTemplate(et.app["file"]).substitute(et.var)
        if "config" in et.app:
            et.app["config"] = VarTemplate(et.app["config"]).substitute(et.var)
        if "action" in et.app:
            et.app["action"] = VarTemplate(et.app["action"]).substitute(et.var)
        # build file
        if "file" in et.app:
            fp = Parser("file")
            of = check_none_raise(fp.parse(et.app["file"]), "get parsed file failed")
            et.app["file"] = of
        # build config
        if "config" in et.app:
            cp = Parser("config")
            oc = check_none_raise(cp.parse(et.app["config"]), "get parsed app failed")
            et.app["config"] = oc
        # build action
        if "action" in et.app:
            ap = Parser("action")
            oa = check_none_raise(ap.parse(et.app["action"]), "get parsed action failed")
            et.app["action"] = oa

    def _do_config(self, et):
        conf = Config(self._option.debug)
        for of in et.app["config"]:
            conf.config(of)

    def _do_put_file(self, et):
        file = File(et.vme)
        for of in et.app["file"]:
            # put file
            if of.operation == '=>':
                file.put_file(of)

    def _do_get_file(self, et):
        file = File(et.vme)
        for of in et.app["file"]:
            # get file
            if of.operation == '<=':
                file.get_file(of)

    def _do_action(self, et):
        act = Action(et.vme, self._plugin)
        for of in et.app["action"]:
            if isinstance(of, CommandModel):
                act.execute_command(of)
            elif isinstance(of, ActionModel):
                act.execute_action(of)

    def _get_glb_var(self, cmd_vars):
        # init buildin variable
        gvar = {}
        gvar["lcwd"] = os.getcwd().replace("\\", "/")
        # init command line variable
        if '__builtins__' in cmd_vars:
            del cmd_vars['__builtins__']
        gvar.update(cmd_vars)
        return gvar

    def _get_task_var(self, vme, tcv):
        # get host var
        tvar = {}
        result = vme.value.run('pwd', hide=True)
        tvar["rcwd"] = result.stdout.replace('\n', '').replace('\r', '')
        # get task var
        tvar.update(tcv)
        return tvar

    def _get_vme(self, host, pwd):
        # get vm executor
        if host in self._vme_pool.keys():
            vme = self._vme_pool[host]
        else:
            vme = Executor(host, pwd, self._option.debug)
            if vme.value:
                self._vme_pool[host] = vme
            else:
                vme = None
        return vme


if __name__ == '__main__':
    pass
