import os
import pkg_resources
import subprocess
import sys
from optparse import OptionParser

from rbtools import get_version_string
from rbtools.commands import RB_MAIN


GLOBAL_OPTIONS = []


def main():
    """Execute a rb command."""

    parser = OptionParser(prog=RB_MAIN,
                          usage='%prog <command> [options] [<args>]',
                          option_list=GLOBAL_OPTIONS,
                          add_help_option=False,
                          version='RBTools %s' % get_version_string())
    parser.disable_interspersed_args()
    opt, args = parser.parse_args()

    if not args:
        parser.print_help()
        sys.exit(1)

    command_name = args[0]

    # Attempt to retrieve the command class from the entry points.
    ep = pkg_resources.get_entry_info("rbtools", "rbtools_commands", args[0])

    if ep:
        try:
            command = ep.load()()
        except ImportError:
            # TODO: It might be useful to actual have the strack
            # trace here, due to an import somewhere down the import
            # chain failing.
            sys.stderr.write("Could not load command entry point %s\n" %
                             ep.name)
            sys.exit(1)
        except Exception, e:
            sys.stderr.write("Unexpexted error loading command %s: %s\n" %
                             (ep.name, e))
            sys.exit(1)

        command.run_from_argv([RB_MAIN] + args)
    else:
        # A command class could not be found, so try and execute
        # the "rb-<command>" on the system.
        args[0] = "%s-%s" % (RB_MAIN, args[0])

        try:
            sys.exit(subprocess.call(args,
                                     stdin=sys.stdin,
                                     stdout=sys.stdout,
                                     stderr=sys.stderr,
                                     env=os.environ.copy()))
        except OSError:
            parser.error("'%s' is not a command" % command_name)


if __name__ == "__main__":
    main()
