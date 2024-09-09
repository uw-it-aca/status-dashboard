# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from yaml import safe_load
import re
import os
import logging


logger = logging.getLogger(__name__)


class _Settings:
    __variables = {}
    _re_variable = re.compile(r'\$([a-z_]+)')

    def __init__(self, config_file):
        with open(config_file, "r") as file:
            try:
                config = safe_load(file)
            except yaml.YAMLError as ex:
                logger.error(f"config file {config_file} error: {ex}")
                return

            for k, v in config.get("variables", {}).items():
                try:
                    self.set(k, v)
                except KeyError:
                    pass

            self.set("dashboards", config.get("dashboards", []))

            for dashboard in self.get("dashboards"):
                for panel in dashboard.get("panels", []):
                    for service in panel.get("services", []):
                        variables = [service.get("variables", {})] + [
                            dashboard.get("variables", {})] + [
                            config.get("variables", {})]

                        service['query'] = self._value(
                            service.get("query"), variables)

            with open("/tmp/ready", "w") as file:
                file.write("ok\n")

    def set(self, name, value):
        self.__variables[name] = value

    def get(self, name, default=None):
        return self.__variables.get(name, default)

    @property
    def variables(self):
        return self.__variables;

    def _value(self, value, variables=None):
        for match in self._re_variable.findall(value):
            substitute = None
            for vars in variables:
                if match in vars:
                    substitute = vars[match]
                    break

            if substitute:
                if substitute[0] == '$':
                    substitute = os.environ.get(substitute[1:])

                value = value.replace(f"${match}", substitute)

        return value

    def __str__(self):
        return str(self.__variables)

    def __repr__(self):
        return str(self.__variables)
