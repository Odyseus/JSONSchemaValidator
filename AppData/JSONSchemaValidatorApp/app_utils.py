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

from .python_utils import file_utils
from .python_utils import json_schema_utils
from .python_utils.exceptions import ExceptionWhitoutTraceBack


root_folder = os.path.realpath(os.path.abspath(os.path.join(
    os.path.normpath(os.getcwd()))))


class NonExistentFile(ExceptionWhitoutTraceBack):
    """NonExistentFile"""

    def __init__(self, msg):
        super().__init__(msg)


class InvalidFile(ExceptionWhitoutTraceBack):
    """InvalidFile"""

    def __init__(self, file_path):
        msg = "Only Python and JSON files are allowed and they should be named with the proper extension.\n"
        msg += file_path
        super().__init__(msg)


class MissingRequiredParameter(ExceptionWhitoutTraceBack):
    """MissingRequiredParameter"""

    def __init__(self, missing_parameter, file_path):
        msg = "It is mandatory to specify a property to get data from a Python file.\n"
        msg += "**Missing parameter: %s\n**" % missing_parameter
        msg += "**File were the property should exist:\n%s**" % file_path
        super().__init__(msg)


def get_value_from_object(file_path, obj, props, logger):
    if isinstance(props, str):
        props = props.split(".")
    else:
        return obj

    try:
        desired_value = obj[props.pop(0)]

        while props:
            desired_value = desired_value[props.pop(0)]
    except KeyError as err:
        msg = "**KeyError:** %s\n" % str(err)
        msg += "**File path:** %s" % file_path
        logger.error(msg)
        raise SystemExit(1)

    return desired_value


def validate_schema(data_file, schema_file,
                    data_prop=None,
                    schema_prop=None,
                    logger=None):
    storage = {
        "instance": {
            "file": os.path.realpath(os.path.abspath(os.path.join(
                os.path.normpath(file_utils.expand_path(data_file))))),
            "data": None,
            "property": data_prop,
            "extension": os.path.splitext(data_file)[1].lower()
        },
        "schema": {
            "file": os.path.realpath(os.path.abspath(os.path.join(
                os.path.normpath(file_utils.expand_path(schema_file))))),
            "data": None,
            "property": schema_prop,
            "extension": os.path.splitext(schema_file)[1].lower()
        }
    }

    for x in storage.values():
        if not file_utils.is_real_file(x["file"]):
            raise NonExistentFile("The following file doesn't exists: %s\n" %
                                  x["file"])

    try:
        for k, v in storage.items():
            if v["extension"] == ".json":
                with open(v["file"], "r") as file_data:
                    v["data"] = get_value_from_object(v["file"], json.load(
                        file_data), v["property"], logger)
            elif v["extension"] == ".py":
                if v["property"] is None:
                    raise MissingRequiredParameter("--%s-prop" % k, v["file"])

                v["data"] = get_value_from_object(
                    v["file"], run_path(v["file"]), v["property"], logger)
            else:
                raise InvalidFile(v["file"])
    except Exception as err:
        logger.error(err)
        raise SystemExit(1)

    extra_info = "\n".join([
        "**Data file:** %s" % storage["instance"]["file"],
        "**Data key:** %s" % str(storage["instance"]["property"]),
        "**Schema file:** %s" % storage["schema"]["file"],
        "**Schema key:** %s" % str(storage["schema"]["property"])
    ])

    json_schema_utils.validate(storage["instance"]["data"], storage["schema"]["data"],
                               error_message_extra_info=extra_info,
                               logger=logger)

    logger.success("**No validation errors found!!!**\n" + extra_info)


if __name__ == "__main__":
    pass
