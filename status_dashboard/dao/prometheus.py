# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from status_dashboard.config import settings
from prometheus_api_client import PrometheusConnect
from random import choice
import logging
import os


logger = logging.getLogger(__name__)


class Prometheus:
    """
    Prometheus API client
    """
    _prometheus = None

    def __init__(self):
        self._prometheus_api = PrometheusConnect(settings.get(
            "prometheus_api_server", "http://localhost:9090"))
        self.query = self.mock_query if (
            os.environ.get("ENV", "") == "localdev") else self.live_query

    def live_query(self, query):
        response = self._prometheus_api.custom_query(query)

        logger.debug(f"query: '{query}' response: {response}")

        # query should sum metrics, so responses should look like:
        #      [{'metric': {}, 'value': [1724025393.875, '0']}]
        if len(response) < 2:
            try:
                return response[0]['value'][1]
            except IndexError:
                return "0"
            except KeyError:
                pass

        raise ValueError(f"unexpected response: {response}")

    def mock_query(self, query):
        return choice(['0.5', '0.9999', '0.9999', '0.9999'])
