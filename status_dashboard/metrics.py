# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Functions supporting Prometheus metrics
"""
from prometheus_client import Counter, REGISTRY
from prometheus_client.exposition import choose_encoder
from tornado.web import RequestHandler


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


class MetricsHandler(RequestHandler):
    """
    Torando request handler for prometheus metrics
    """
    def get(self):
        encoder, content_type = choose_encoder(
            self.request.headers.get('accept'))
        self.set_header("Content-Type", content_type)
        self.write(encoder(REGISTRY))
