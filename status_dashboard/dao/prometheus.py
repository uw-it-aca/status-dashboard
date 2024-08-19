# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from status_dashboard.config import settings
from prometheus_api_client import PrometheusConnect
import logging
import os


logger = logging.getLogger(__name__)


class Prometheus:
    """
    Prometheus API client
    """
    _prometheus = None

    def __init__(self):
        self._prometheus = PrometheusConnect(settings.get(
            "prometheus_api_server", "http://localhost:9090"))

    def promql_query(self, query):
        for var, value in settings.variables():
            if isinstance(value, (int, float, str, bool)):
                query = query.replace(f"${var}", value)

        logger.debug(f"query: {query}")

        # lamest mock data evar
        if os.environ.get('ENV', 'localdev') == 'localdev':
            from random import choice
            return choice([
                [{'metric': {}, 'value': [1724025393.875, '0']}],
                [{'metric': {}, 'value': [1724025393.875, '1']}],
                [{'metric': {}, 'value': [1724025393.875, '1']}],
                [{'metric': {}, 'value': [1724025393.875, '1']}]
            ])

        return self._prometheus.custom_query(query)

    def promql_boolean_query(self, query):
        response = self.promql_query(query)

        logger.debug(f"query: '{query}' response: {response}")

        # response should look like:
        #      [{'metric': {}, 'value': [1724025393.875, '0']}]
        if len(response) == 1:
            return response[0]['value'][1] == '1'

        raise ValueError(f"unexpected response: {response}")
