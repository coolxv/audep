import logging
from pluginbase import PluginBase
from .utils import ActionError, PluginError, CommandError


class Action:
    def __init__(self, vme, plugin):
        self._vme = vme
        self._plugin = plugin

    def execute_command(self, of):
        if of.flag == 'r':
            result = self._vme.run(of.command)
            if result < self._vme.error:
                raise CommandError(f'remote command excute failed: {of.command}')
            elif result == self._vme.error:
                return
            logging.debug(f'remote command result: {result}')
            if of.result != None:
                if result != of.result:
                    raise CommandError(f'remote command result failed: {of.command}')
        elif of.flag == 's':
            result = self._vme.sudo(of.command)
            if result < self._vme.error:
                raise CommandError(f'sudo command excute failed: {of.command}')
            elif result == self._vme.error:
                return
            logging.debug(f'sudo command result: {result}')
            if of.result != None:
                if result != of.result:
                    raise CommandError(f'sudo command result failed: {of.command}')
        elif of.flag == 'l':
            result = self._vme.local(of.command)
            if result < self._vme.error:
                raise CommandError(f'local command excute failed: {of.command}')
            elif result == self._vme.error:
                return
            logging.debug(f'local command result: {result}')
            if of.result != None:
                if result != of.result:
                    raise CommandError(f'local command result failed: {of.command}')
        else:
            raise CommandError(f'not recognized command : {of.command}')

    def execute_action(self, of):
        result = self._plugin.call(self._vme, of.plugin, of.action, *of.args, **of.kwargs)
        if result < self._vme.error:
            raise ActionError(f'action plugin excute failed:{of.plugin}::{of.action}({of.args} {of.kwargs}')
        elif result == self._vme.error:
            return
        logging.debug(f'action plugin result: {result}')
        if of.result != None:
            if not result or result != of.result:
                raise ActionError(f'action plugin result failed:{of.plugin}::{of.action}({of.args} {of.kwargs})')


class Plugin(object):
    def __init__(self, path):
        # Each application has a name
        self._plugin = PluginBase(package='plugins')
        self._source = self._plugin.make_plugin_source(
            searchpath=path,
            identifier='plugins')

    def call(self, ctx, plugin, func, *args, **kwargs):
        p = self._source.load_plugin(plugin)
        if hasattr(p, func):
            f = getattr(p, func)
            return f(ctx, *args, **kwargs)
        else:
            raise PluginError(f'plugin not supported:{plugin}::{func}')


if __name__ == '__main__':
    pass
