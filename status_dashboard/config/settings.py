# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from yaml import safe_load
import re
import os
import logging


logger = logging.getLogger(__name__)


class _Settings:
    __variables = {}

    def __init__(self, config_file):
        with open(config_file, "r") as file:
            try:
                config = safe_load(file)
            except yaml.YAMLError as ex:
                logger.error(f"config file {config_file} error: {ex}")
                return

            for variable in config.get("variables", []):
                try:
                    self.set(variable["name"], self._value(variable["value"]))
                except KeyError:
                    pass

            self.set("dashboards", config.get("dashboards", []))

            with open("/tmp/ready", "w") as file:
                file.write("ok\n")

    def set(self, name, value):
        self.__variables[name] = value

    def get(self, name, default=None):
        return self.__variables.get(name, default)

    def variables(self):
        for k, v in self.__variables.items():
            yield k, v

    def _value(self, raw_value):
        return os.environ.get(raw_value[1:]) if (
            raw_value[0] == '$') else raw_value

    def __str__(self):
        return str(self.__variables)

    def __repr__(self):
        return str(self.__variables)
