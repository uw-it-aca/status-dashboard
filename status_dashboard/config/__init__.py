# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from status_dashboard.config.settings import _Settings
import os


config_file = os.environ.get('DASHBOARD_CONFIG_FILE', 'settings.yml')
settings = _Settings(config_file)
