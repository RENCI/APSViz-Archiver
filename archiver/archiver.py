# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

import os
import logging
import datetime
from common.logger import LoggingUtil
from utils import Utils
from geoserver import GeoserverTools
from thredds import ThreddsTools
from rules import RuleHandler


class APSVizArchiver:
    def __init__(self):
        """
        Initializes this class

        """
        # get the configuration
        self.config: dict = self.get_config()

        # get the current date/time for this run
        self.now = datetime.datetime.now()

        # get the log level and directory from the environment.
        # level comes from the container dockerfile, path comes from the k8s secrets
        log_level: int = int(os.getenv('LOG_LEVEL', logging.INFO))
        log_path: str = os.getenv('LOG_PATH', os.path.dirname(__file__))

        # create the dir if it does not exist
        if not os.path.exists(log_path):
            os.mkdir(log_path)

        # create a logger
        self.logger = LoggingUtil.init_logging("APSVIZ.Archiver", level=log_level, line_format='medium', log_file_path=log_path)

        # grab a reference to the utils class
        self.utils = Utils(self.logger)

        # grab a reference to the data handlers
        self.data_handlers = [{'data_name': 'GeoServer', 'data_handler': GeoserverTools(self.logger)}, {'data_name': 'THREDDS', 'data_handler': ThreddsTools(self.logger)}]

        # grab a reference to the thredds tools
        self.rule_handler = RuleHandler(self.logger)

    @staticmethod
    def get_config() -> dict:
        """
        gets the run configuration

        :return: Dict, baseline run params
        """
        # init the config data
        config_data: dict = {}

        # TODO: get the config. not sure what yet tho

        # return the config data
        return config_data

    def run(self):
        # TODO: add try/except logic
        # init the run statistic storage
        run_stats: list = []

        # execute the rules utilizing a data handler
        for data_handler in self.data_handlers:
            run_stats = self.rule_handler.execute_rules(data_handler)

            # save the run statistics
            run_stats.append(run_stats)

        self.logger.info(f'Archival complete. Run stats: {run_stats}')
