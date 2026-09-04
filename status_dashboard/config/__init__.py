# Copyright 2026 UWIT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import os

from status_dashboard.config.settings import _Settings

config_file = os.environ.get('DASHBOARD_CONFIG_FILE', 'settings.yml')
settings = _Settings(config_file)
