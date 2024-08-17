# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Functions supporting Prometheus metrics
"""
from prometheus_client import start_http_server, Counter


# prepare metrics
try:
    status_dashboard_request_count = Counter(
        'dashboard_request_count',
        'Dashboard request count',
        ['service'])
except ValueError:
    pass


def request_counter(dashboard_name):
    """
    Increment dashboard name request counter
    """
    status_dashboard_request_count.labels(dashboard_name).inc()


def metrics_server(port):
    """
    Serve metrics requests
    """
    start_http_server(port)
