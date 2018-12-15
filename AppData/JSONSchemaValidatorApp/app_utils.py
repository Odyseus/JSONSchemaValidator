#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Module with utility functions and classes.

Attributes
----------
root_folder : str
    The main folder containing the application. All commands must be executed
    from this location without exceptions.
"""
import json
import os

from runpy import run_path

from .python_utils import exceptions
from .python_utils import file_utils
from .python_utils import json_schema_utils


root_folder = os.path.realpath(os.path.abspath(os.path.join(
    os.path.normpath(os.getcwd()))))


class InvalidFile(exceptions.ExceptionWhitoutTraceBack):
    """InvalidFile"""

    def __init__(self, file_path):
        msg = "Only Python and JSON files are allowed and they should be named with the proper extension.\n"
        msg += file_path
        super().__init__(msg)


def get_value_from_object(obj, props):
    props = props.split(".")
    desired_value = obj[props.pop(0)]

    while props:
        desired_value = desired_value[props.pop(0)]

    return desired_value


def validate_schema(data_file, schema_file,
                    data_prop="data",
                    schema_prop="schema",
                    logger=None):
    data_file = os.path.realpath(os.path.abspath(os.path.join(
        os.path.normpath(data_file))))
    schema_file = os.path.realpath(os.path.abspath(os.path.join(
        os.path.normpath(schema_file))))

    for f_path in [data_file, schema_file]:
        if not file_utils.is_real_file(f_path):
            raise exceptions.MissingRequiredFile("The following file doesn't exists: %s\n" %
                                                 f_path)

    data_file_extension = os.path.splitext(data_file)[1].lower()
    schema_file_extension = os.path.splitext(schema_file)[1].lower()

    try:
        if data_file_extension == ".json":
            instance = json.load(data_file)
        elif data_file_extension == ".py":
            instance = get_value_from_object(run_path(data_file), data_prop)
        else:
            raise InvalidFile(data_file)

        if schema_file_extension == ".json":
            schema = json.load(schema_file)
        elif schema_file_extension == ".py":
            schema = get_value_from_object(run_path(schema_file), schema_prop)
        else:
            raise InvalidFile(schema_file)

    except Exception as err:
        logger.error(err)
        raise SystemExit(1)

    json_schema_utils.validate(instance, schema,
                               error_message_extra_info="\n".join([
                                   "Data file: %s" % data_file,
                                   "" if data_file_extension == ".py" else "Data key: %s" % data_prop,
                                   "Schema file: %s" % schema_file,
                                   "" if schema_file_extension == ".py" else "Schema key: %s" % schema_prop
                               ]),
                               logger=logger)

    logger.success("No validation errors found!!!")


if __name__ == "__main__":
    pass
