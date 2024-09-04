# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from status_dashboard.config import settings
from status_dashboard.metrics import request_counter
from status_dashboard.dao.prometheus import Prometheus
from jinja2 import Environment, PackageLoader, select_autoescape
from tornado.web import RequestHandler
from urllib import request
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
prometheus = Prometheus()


class StatusRequest(RequestHandler):
    def initialize(self, dashboard):
        self.dashboard = dashboard

    def get(self):
        app_path = self.dashboard.get('app_path')
        app_name = self.dashboard.get('app_name')
        app_notification_url = self.dashboard.get('app_notification_url')

        now = datetime.now()

        request_counter(f"{app_path}")

        # serve cached dashboard if available
        cache_file = f"/tmp/{app_path}.html"
        timeout = 0 if self.request.arguments.get(
            'refresh', False) else self.dashboard.get("cache_timeout", 5)
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
        app_timezone = pytz.timezone(settings.get('timezone', 'US/Pacific'))
        context = {
            "name": app_name,
            "notifications": self._load_app_notifications(
                app_notification_url),
            "panels": self._load_panel_context(
                self.dashboard.get('panels', [])),
            "last_update": now.astimezone(
                app_timezone).strftime("%-I:%M:%S %p %Y-%m-%d %Z")
        }

        context["overall_nominal"] = all(
            [s['nominal'] for p in context['panels'] for s in p["services"]])
        template = jinja2_env.get_template("dashboard.html")
        html = template.render(context)

        with open(cache_file, "w") as f:
            f.write(html)

        self.write(html)

    def _load_panel_context(self, panels):
        panel_context = []

        for panel in panels:
            services = self._load_service_contexts(
                panel.get('services', []))

            panel_context.append({
                'name': panel.get('name', ''),
                'description': panel.get('description', ''),
                'critical_description': panel.get('critical_description', ''),
                'services': services,
                'overall_nominal': all([s['nominal'] for s in services])
            })

        return panel_context

    def _load_service_contexts(self, services):
        service_context = []

        for service in services:
            try:
                try:
                    query = service["_query"]
                except KeyError:
                    query = self._expand_query(service.get('query'))
                    service["_query"] = query

                health, status = self._health(prometheus.query(query), service)
            except Exception as ex:
                logger.error(f"query '{query}' error: {ex}")
                health = False
                status = "Unknown"

            service_context.append({
                "name": service.get('name', ""),
                "description": service.get('description', ""),
                "link": service.get('link', ""),
                "nominal": health,
                "status": status
            })

        return service_context

    def _expand_query(self, query):
        for var, value in settings.variables():
            if isinstance(value, (int, float, str, bool)):
                query = query.replace(f"${var}", value)

        return query

    def _health(self, raw_result, member):
        result = float(raw_result)
        for threshold in member.get('threshold', []):
            limit = float(threshold.get('limit', "0.0"))
            if result < limit:
                return False, threshold.get('description', "Critical")

        return True, "Normal"

    def _load_app_notifications(self, url):
        try:
            with request.urlopen(url) as response:
                return response.read().decode("utf-8")
        except Exception as ex:
            logger.error(f"notification url '{url}' error: {ex}")

        return ""
