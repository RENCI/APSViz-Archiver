# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Class APSVizArchiver - Archives data using rules.

    Author: Phil Owen, 10/19/2022
"""

import datetime
import logging

from src.common.logger import LoggingUtil
from src.archiver.rule_handler import RuleHandler
from src.common.rule_utils import RuleUtils
from src.common.general_utils import GeneralUtils
from src.common.geoserver_utils import GeoServerUtils


class APSVizArchiver:
    """
    Class that defines methods to execute archive rules.

    """

    def __init__(self, test_file=None):
        """
        Initializes this class

        """
        # get the current date/time for this run
        self.now = datetime.datetime.now()

        # get the log level and directory from the environment.
        log_level, log_path = LoggingUtil.prep_for_logging()

        # create a logger
        self.logger = LoggingUtil.init_logging("APSVIZ.Archiver", level=log_level, line_format='medium', log_file_path=log_path)

        # set debug mode based on the log level. a debug log level will turn off slack msgs
        if log_level != logging.DEBUG:
            self.debug = False
        else:
            self.debug = True

        # grab a reference to the general utils class
        self.utils = GeneralUtils(self.logger)

        # grab a reference to the GeoServer utils class
        self.geo_utils = GeoServerUtils(self.logger)

        # grab a reference to the data handlers
        self.data_handlers = [{'data_name': 'GeoServer', 'data_handler': GeoServerUtils(self.logger)},
                              # {'data_name': 'TDS', 'data_handler': ThreddsTools(self.logger)}
                              ]

        # grab a reference to the thredds tools
        self.rule_handler = RuleHandler(self.logger)

        # get a reference to the rule util tools
        self.rule_utils = RuleUtils(self.logger)

        # get a reference to the general util tools
        self.general_utils = GeneralUtils(self.logger)

        # save the file path entered
        self.test_files = test_file.split(',')

    def run(self) -> bool:
        """
        starts the archiver process

        :return:
        """
        # init the return value
        ret_val: bool = False

        # init rule definition details
        rule_def_name: dict = {}
        rule_def_version: dict = {}

        try:
            # for each rule definition file
            for infile in self.test_files:
                # get the rule configurations
                rule_defs: dict = self.general_utils.load_rule_definition_file(infile)

                # get the name/version of the rule definition
                rule_def_name = rule_defs['rule_definition_name']
                rule_def_version = rule_defs['rule_definition_version']

                self.logger.info('<---------- New Run: %s ---------->', infile)

                # create a start message
                start_msg = f'APSViz Archiver start. Name: {rule_def_name}, Version: {rule_def_version}'

                # send/log the start message
                self.utils.send_slack_msg(start_msg, 'slack_status_channel', self.debug)

                # process the rule set
                for rule_set in rule_defs['rule_sets']:
                    # execute the rule set
                    run_stats = self.rule_handler.process_rule_set(rule_set)

                    # no failures get a short message
                    if run_stats['failed'] == 0:
                        # create a success message
                        final_msg = f"Rule set {rule_set['rule_set_name']} Status: {len(rule_set['rules'])} rule(s) succeeded."

                        # set the success flag
                        ret_val = True
                    else:
                        # show all results on failure
                        final_msg = f"Rule set {rule_set['rule_set_name']} Status: Failures detected - {len(rule_set['rules'])} rule(s) in set, " \
                                    f"{run_stats['failed']} failed rule(s)."

                        # show all results on failure
                        status_msg = f"Status: Failures detected - {len(rule_set['rules'])} rule(s) in set, {run_stats['moved']} Move rule(s), " \
                                     f"{run_stats['copied']} copy rule(s), {run_stats['removed']} remove rule(s), " \
                                     f"{run_stats['swept']} sweep rule(s), {run_stats['failed']} failed rule(s)."

                        self.logger.info("APSVix-Archiver Rule set %s complete. Run %s", rule_set['rule_set_name'], status_msg)

                    # send out a slack of the details
                    self.utils.send_slack_msg(final_msg, 'slack_status_channel', self.debug)

                self.logger.info('<---------- Run complete: %s ---------->\n', infile)
        except Exception:
            self.logger.exception('Exception detected in APSViz Archiver.')

        # return to the caller
        return ret_val
