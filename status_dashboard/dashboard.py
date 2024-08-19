# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Status Dashboard

Dashboard configuration comes from a yaml file.  The file path
is defined in the DASHBOARD_CONFIG environment variable.  An
example configuration file can be found in the repository.
"""

from server import dashboard_server
from metrics import metrics_server
import sys
import os
import logging


# setup basic logging
logging.basicConfig(level=logging.DEBUG if (
    os.environ.get('ENV') == 'localdev') else logging.INFO,
                    format=('%(asctime)s %(levelname)s %(module)s.'
                            '%(funcName)s():%(lineno)d:'
                            ' %(message)s'),
                    handlers=(logging.StreamHandler(sys.stdout),))

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    try:
        # open metrics exporter endpoint
        metrics_server(int(os.environ.get('METRICS_PORT', 9100)))

        # launch dashboard server
        dashboard_server(int(os.environ.get("PORT", 8000)))
    except Exception as e:
        logger.exception(e)
        logger.critical(e)
