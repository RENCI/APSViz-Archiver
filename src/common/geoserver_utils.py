# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    GeoServer Utils - Various utilities for GeoServer interactions.

    Author: Phil Owen, 2/16/2023
"""
import os
import requests

from src.common.logger import LoggingUtil


class GeoServerUtils:
    """
    Class that encapsulates GeoServer operations.

    """

    def __init__(self, _logger=None):
        """
        Initializes this class

        """
        # if a reference to a logger passed in use it
        if _logger is not None:
            # get a handle to a logger
            self.logger = _logger
        else:
            # get the log level and directory from the environment.
            log_level, log_path = LoggingUtil.prep_for_logging()

            # create a logger
            self.logger = LoggingUtil.init_logging("APSVIZ.Archiver.GeoServerUtils", level=log_level, line_format='medium', log_file_path=log_path)

        # load environment variables
        self.username = os.getenv('GEOSERVER_USER')
        self.password = os.environ.get('GEOSERVER_PASSWORD')
        self.geoserver_url = os.environ.get('GEOSERVER_URL')
        self.geoserver_workspace = os.environ.get('GEOSERVER_WORKSPACE')

        # init the Slack channels
        self.slack_channels: dict = {'slack_status_channel': os.getenv('SLACK_STATUS_CHANNEL'),
                                     'slack_issues_channel': os.getenv('SLACK_ISSUES_CHANNEL')}

        # get the environment this instance is running on
        self.system = os.getenv('SYSTEM', 'System name not set')

    def get_coverage_store(self, coverage_store_name: str) -> (bool, object):
        """
        Get a geoserver coverage store by name

        :param coverage_store_name:
        :return:
        """
        # init the return values
        success: bool = True
        ret_val = None

        try:
            # build the URL to the service
            url = f'{self.geoserver_url}/rest/workspaces/{self.geoserver_workspace}/coveragestores/{coverage_store_name}'

            # execute the get
            ret_val = requests.get(url, auth=(self.username, self.password), timeout=10)

            # was the call unsuccessful
            if ret_val.status_code != 200:
                # log the error
                self.logger.error('Error %s when getting coverage store "%s"', ret_val.status_code, coverage_store_name)

                # set the failure flag
                success = False
            # get the return in the correct format
            else:
                ret_val = ret_val.json()

        except Exception:
            self.logger.exception('Exception getting coverage store "%s"', coverage_store_name)
            success = False

        # return the json to the caller
        return success, ret_val

    def get_coverage_stores(self):
        """
        Get all the coverage stores inside specific workspace

        :return:
        """
        # init the return values
        success: bool = True
        ret_val = None

        try:
            # build the URL to the service
            url = f'{self.geoserver_url}/rest/workspaces/{self.geoserver_workspace}/coveragestores'

            # execute the get
            ret_val = requests.get(url, auth=(self.username, self.password), timeout=10)

            # was the call unsuccessful
            if ret_val.status_code != 200:
                # log the error
                self.logger.error('Error %s gathering all geoserver coverage stores.', ret_val.status_code)

                # set the failure flag
                success = False
            # get the return in the correct format
            else:
                ret_val = ret_val.json()

        except Exception:
            self.logger.exception('Exception gathering all geoserver coverage stores')
            success = False

        # return the json to the caller
        return success, ret_val

    def remove_coverage_store(self, coverage_store_name: str) -> bool:
        """
        Removes a GeoServer coverage store

        :param coverage_store_name:
        :return:
        """
        success: bool = True

        try:
            # build the URL to the service
            url = f'{self.geoserver_url}/rest/workspaces/{self.geoserver_workspace}/coveragestores/{coverage_store_name}?recurse=true'

            # execute the delete
            ret_val = requests.delete(url, auth=(self.username, self.password), timeout=60)

            # was the call unsuccessful
            if ret_val.status_code != 200:
                # log the error
                self.logger.error('Error %s when removing coverage store "%s".', ret_val.status_code, coverage_store_name)

                # set the failure flag
                success = False

        except Exception:
            # log the error
            self.logger.exception('Exception when removing coverage store "%s"', coverage_store_name)

            # set the failure code
            success = False

        # return pass/fail
        return success

    def create_coverage_store(self, coverage_store_name: str) -> bool:
        """
        Adds a GeoServer coverage store

        :param coverage_store_name:
        :return:
        """
        # init the return
        success: bool = True

        try:
            # build the URL to the service
            url = f'{self.geoserver_url}/rest/workspaces/{self.geoserver_workspace}/coveragestores'

            # create the config body
            # store_config = json.loads('{"coverageStore": {"name": "' + coverage_store_name + '", "workspace": "' + self.geoserver_workspace + '"}}')
            store_config: dict = {'coverageStore': {'name': coverage_store_name, 'workspace': self.geoserver_workspace,
                                                    'url': 'file:data/ADCIRC_2023/test_coverage_store', 'type': 'imagemosaic'}}

            # execute the post
            ret_val = requests.post(url, auth=(self.username, self.password), json=store_config, timeout=10)

            # was the call unsuccessful. 201 is returned on success for ths one
            if ret_val.status_code != 201:
                # log the error
                self.logger.error('Error %s when creating coverage store "%s".', ret_val.status_code, coverage_store_name)

                # set the failure flag
                success = False

        except Exception:
            # log the error
            self.logger.exception('Exception when creating coverage store "%s"', coverage_store_name)

            # set the failure code
            success = False

        # return pass/fail
        return success
