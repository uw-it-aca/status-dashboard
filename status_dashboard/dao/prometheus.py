# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from status_dashboard.config import settings
from prometheus_api_client import PrometheusConnect
import logging
import os


logger = logging.getLogger(__name__)


def promql_query(query):
    """
    Execute query against Prometheus
    """
    for var, value in settings.variables():
        if isinstance(value, (int, float, str, bool)):
            query = query.replace(f"${var}", value)

    logger.debug(f"query: {query}")

    if os.environ.get('ENV', 'localdev') == 'localdev':
        from random import choice
        return choice(["0", "1", "1", "1"])

    prom = PrometheusConnect(
        url=os.environ.get('PROMETHEUS_SERVER', "http://localhost:9090"))

    return query


def promql_query_boolean(query, variables={}):
    return promql_query(query) == "1"
