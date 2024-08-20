# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from status_dashboard.config import settings
from status_dashboard.metrics import request_counter
from status_dashboard.dao.prometheus import Prometheus
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
prometheus = Prometheus()


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
            "application_section": self._load_group_context('application'),
            "dependencies_section": self._load_group_context('dependencies'),
            "last_update": now.astimezone(
                app_timezone).strftime("%-I:%M:%S %p %Y-%m-%d %Z")
        }

        context["overall_nominal"] = (
            all([s['nominal'] for s in context['application_section']]) and
                all([s['nominal'] for s in context['dependencies_section']]))

        template = jinja2_env.get_template("dashboard.html")
        html = template.render(context)

        with open(cache_file, "w") as f:
            f.write(html)

        self.write(html)

    def _load_group_context(self, group_name):
        context = []

        for member in self.dashboard.get(group_name, []):
            try:
                try:
                    query = member["_query"]
                except KeyError:
                    query = self._expand_query(member.get('query'))
                    member["_query"] = query

                health = self._health(prometheus.query(query), member)
            except Exception as ex:
                logger.error(f"query '{query}' error: {ex}")
                health = False

            context.append({
                "name": member.get('name', ""),
                "description": member.get('description', ""),
                "link": member.get('link', ""),
                "nominal": health
            })

        return context

    def _expand_query(self, query):
        for var, value in settings.variables():
            if isinstance(value, (int, float, str, bool)):
                query = query.replace(f"${var}", value)

        return query

    def _health(self, raw_result, member):
        on_null = float(member.get('on_null', "0.0"))
        result = float(raw_result) if (
            raw_result and raw_result != 'NaN') else on_null
        threshold = float(member.get('threshold', "0.0"))

        return result > threshold
