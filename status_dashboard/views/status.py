# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from status_dashboard.config import settings
from status_dashboard.metrics import request_counter
from status_dashboard.dao.prometheus import promql_query_boolean
from jinja2 import Environment, PackageLoader, select_autoescape
from tornado.web import RequestHandler
from datetime import datetime, timedelta
import asyncio
import pytz
import os
import logging


logger = logging.getLogger(__name__)
jinja2_env = Environment(
    loader=PackageLoader("status_dashboard"),
    autoescape=select_autoescape()
)


class StatusRequest(RequestHandler):
    def initialize(self, dashboard):
        self.dashboard = dashboard

    def get(self):
        app_path = self.dashboard.get('app_path')
        app_name = self.dashboard.get('app_name')
        now = datetime.now()

        request_counter(f"{app_path}")

        # serve cached dashboard if available
        cache_file = f"/tmp/{app_path}.html"
        timeout = 0 if self.request.arguments.get(
            'refresh', False) else self.dashboard.get("cache_duration", 5)
        if timeout:
            try:
                stat = os.stat(cache_file)
                datetime_mtime = datetime.fromtimestamp(stat.st_mtime)
                datetime_expires = datetime_mtime + timedelta(
                    seconds=(timeout * 60))
                if datetime_expires > now:
                    with open(cache_file, "r") as f:
                        self.write(f.read())
                        return
            except FileNotFoundError:
                pass

        # no cached file, get to queryin'
        pacific = pytz.timezone(settings.get('timezone', 'US/Pacific'))
        application = []
        for component in self.dashboard.get('application', []):
            application.append({
                "name": component.get('name'),
                "description": component.get('description'),
                "link": component.get('link'),
                "nominal": promql_query_boolean(component.get('test'))
            })

        dependencies = []
        for dependency in self.dashboard.get('dependencies', []):
            dependencies.append({
                "name": dependency.get('name'),
                "description": dependency.get('description'),
                "link": dependency.get('link'),
                "nominal": promql_query_boolean(dependency.get('test'))
            })

        context = {
            "name": app_name,
            "application_section": application,
            "dependencies_section": dependencies,
            "last_update": now.astimezone(pytz.timezone(
                'US/Pacific')).strftime("%-I:%M:%S %p %Y-%m-%d %Z")
        }

        template = jinja2_env.get_template("dashboard.html")
        html = template.render(context)

        with open(cache_file, "w") as f:
            f.write(html)

        self.write(template.render(context))
