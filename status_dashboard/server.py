# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Dashboard initialization and tornado server launch
"""

from status_dashboard.config import settings
from status_dashboard.views.status import StatusRequest
from status_dashboard.metrics import MetricsHandler
from tornado.web import Application, StaticFileHandler
from pathlib import Path
import asyncio
import logging
import os


logger = logging.getLogger(__name__)


def dashboard_app():
    """
    Initialize the dashboard server
    """

    # register metrics and static endpoints
    file_path = Path(__file__).resolve().parent
    endpoints = [
        (r"/metrics", MetricsHandler),
        (r"/static/(.*)", StaticFileHandler, {"path": f"{file_path}/static/"})
    ]

    # register configured dashboard endpoints
    for dashboard in settings.get('dashboards'):
        endpoint = f"/{dashboard.get('app_path')}"
        endpoints.append(
            (endpoint, StatusRequest, {'dashboard': dashboard}))
        logger.info(f"Added endpoint {endpoint}")

    return Application(endpoints)


async def _dashboard_server(port):
    app = dashboard_app()
    app.listen(port)
    shutdown_event = asyncio.Event()
    await shutdown_event.wait()


def dashboard_server(port):
    asyncio.run(_dashboard_server(port))
