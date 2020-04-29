#! /usr/bin/env python3
# -*- coding: UTF-8 -*-
"""audep.py: this is the audep application.
"""

import logging
import os.path
import sys
from optparse import OptionParser
from . import Vm, __version__


def _process_files(options, args):
    """process all the command line options."""
    # log
    logging.basicConfig(level=options.level)
    # var
    my_globals = {}
    if options.eval is not None:
        for expr in options.eval:
            exec(expr, my_globals)
    # task
    tasklist = None
    if options.task is not None:
        tasklist = options.task
    # plugins
    pluginlist = None
    if options.plugin is not None:
        pluginlist = options.plugin
    # file
    filelist = []
    if options.file is not None:
        filelist = options.file
    if len(args) > 0:  # extra arguments
        filelist.extend(args)
    if len(filelist) <= 0:
        vm = Vm(None, my_globals, options, tasklist, pluginlist)
        vm.run()

    else:
        for f in filelist:
            vm = Vm(f, my_globals, options, tasklist, pluginlist)
            vm.run()


def _script_shortname():
    """return the name of this script without a path component."""
    return os.path.basename(sys.argv[0])


def _print_summary():
    """print a short summary of the scripts function."""
    print(("%-20s: a powerful template language " + "based on python ...\n") % _script_shortname())


def main():
    """The main function.

    parse the command-line options and perform the command
    """
    # command-line options and command-line help:
    usage = "usage: %audep [options] {files}"

    parser = OptionParser(usage=usage,
                          version="%%prog %s" % __version__,
                          description="execute template in a file with audep.")

    parser.add_option("--summary",
                      action="store_true",
                      help="Print a summary of the function of the program.",
                      )

    parser.add_option("-f", "--file",
                      action="append",
                      type="string",
                      help="Specify a FILE to process. This "
                           "option may be used more than once "
                           "to process more than one file but note "
                           "than this option is not really needed. "
                           "Files can also be specified directly after "
                           "the other command line options.",
                      metavar="FILE"
                      )

    parser.add_option("-t", "--task",
                      action="append",
                      type="string",
                      help="Specify a task to execute. This"
                           "option may be used more than once "
                           "to process more than one file but note "
                           "than this option is not really needed. ",
                      metavar="TASK"
                      )

    parser.add_option("-p", "--plugin",
                      action="append",
                      type="string",
                      help="Specify a plugin path. This"
                           "option may be used more than once "
                           "to process more than one file but note "
                           "than this option is not really needed. ",
                      metavar="PLUGIN",
                      default=["plugins"]
                      )

    parser.add_option("-i", "--include",
                      action="append",
                      type="string",
                      help="Specify a template path. This"
                           "option may be used more than once "
                           "to process more than one file but note "
                           "than this option is not really needed. ",
                      metavar="TEMPLATE",
                      default=["template"]
                      )

    parser.add_option("--eval",
                      action="append",
                      type="string",
                      help="Evaluate PYTHONEXPRESSION in global context.",
                      metavar="PYTHONEXPRESSION"
                      )

    parser.add_option("-l", "--level",
                      action="store",
                      type="int",
                      help="Set debug level.",
                      metavar="LEVEL",
                      default=40
                      )

    parser.add_option("--debug",
                      action="store_true",
                      help="Set test mode, not execute, only print a debug info of the program.",
                      )

    # x= sys.argv
    (options, args) = parser.parse_args()
    # options: the options-object
    # args: list of left-over args

    if options.summary:
        _print_summary()
        sys.exit(0)
    # process
    _process_files(options, args)
    sys.exit(0)
