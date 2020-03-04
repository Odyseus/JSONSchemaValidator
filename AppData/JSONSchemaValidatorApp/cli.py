#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Main command line application.

Attributes
----------
docopt_doc : str
    Used to store/define the docstring that will be passed to docopt as the "doc" argument.
root_folder : str
    The main folder containing the application. All commands must be executed from this location
    without exceptions.
"""

import os

from . import app_utils
from .__init__ import __appdescription__
from .__init__ import __appname__
from .__init__ import __status__
from .__init__ import __version__
from .python_utils import cli_utils
from .python_utils import exceptions

root_folder = os.path.realpath(os.path.abspath(os.path.join(
    os.path.normpath(os.getcwd()))))

docopt_doc = """{appname} {version} ({status})

{appdescription}

Usage:
    app.py (-h | --help | --manual | --version)
    app.py validate (-d <path> | --data-file=<path>)
                    (-s <path> | --schema-file=<path>)
                    [--data-prop=<name>] [--schema-prop=<name>]
    app.py generate system_executable

Options:

-h, --help
    Show this screen.

--manual
    Show this application manual page.

--version
    Show application version.

-d <path>, --data-file=<path>
    Path to a Python or JSON file containing the data to validate
    against a JSON schema.

-s <path>, --schema-file=<path>
    Path to a Python or JSON file containing the JSON schema to validate
    the data against.

--data-prop=<name>
    Name of a property found inside the file specified in **--data-file**.

--schema-prop=<name>
    Name of a property found inside the file specified in **--schema-file**.

""".format(appname=__appname__,
           appdescription=__appdescription__,
           version=__version__,
           status=__status__)


class CommandLineInterface(cli_utils.CommandLineInterfaceSuper):
    """Command line interface.

    It handles the arguments parsed by the docopt module.

    Attributes
    ----------
    a : dict
        Where docopt_args is stored.
    action : method
        Set the method that will be executed when calling CommandLineTool.run().
    """
    action = None

    def __init__(self, docopt_args):
        """
        Parameters
        ----------
        docopt_args : dict
            The dictionary of arguments as returned by docopt parser.
        """
        self.a = docopt_args
        self._cli_header_blacklist = [self.a["--manual"]]

        super().__init__(__appname__)

        if self.a["--manual"]:
            self.action = self.display_manual_page
        if self.a["validate"]:
            self.action = self.validate_schema
        elif self.a["generate"]:
            if self.a["system_executable"]:
                self.logger.info("**System executable generation...**")
                self.action = self.system_executable_generation

    def run(self):
        """Execute the assigned action stored in self.action if any.
        """
        if self.action is not None:
            self.action()

    def validate_schema(self):
        """Execute the assigned action stored in self.action if any.

        Raises
        ------
        exceptions.MissingDependencyModule
            Missing ``jsonschema`` module.
        """
        if not app_utils.json_schema_utils.JSONSCHEMA_INSTALLED:
            raise exceptions.MissingDependencyModule("Missing 'jsonschema' module.")

        app_utils.validate_schema(
            self.a["--data-file"], self.a["--schema-file"],
            data_prop=self.a["--data-prop"],
            schema_prop=self.a["--schema-prop"],
            logger=self.logger
        )

    def system_executable_generation(self):
        """See :any:`cli_utils.CommandLineInterfaceSuper._system_executable_generation`.
        """
        self._system_executable_generation(
            exec_name="json-schema-validator-cli",
            app_root_folder=root_folder,
            sys_exec_template_path=os.path.join(
                root_folder, "AppData", "data", "templates", "system_executable"),
            bash_completions_template_path=os.path.join(
                root_folder, "AppData", "data", "templates", "bash_completions.bash"),
            logger=self.logger
        )

    def display_manual_page(self):
        """See :any:`cli_utils.CommandLineInterfaceSuper._display_manual_page`.
        """
        self._display_manual_page(os.path.join(root_folder, "AppData", "data", "man", "app.py.1"))


def main():
    """Initialize command line interface.
    """
    cli_utils.run_cli(flag_file=".json-schema-validator.flag",
                      docopt_doc=docopt_doc,
                      app_name=__appname__,
                      app_version=__version__,
                      app_status=__status__,
                      cli_class=CommandLineInterface)


if __name__ == "__main__":
    pass
