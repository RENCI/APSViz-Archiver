# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2024 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    TDS Utils - Various utilities for TDS interactions.

    Author: Phil Owen, 2/8/2024
"""
import os
import shutil
import sys

from src.common.logger import LoggingUtil
from src.common.pg_impl import PGImplementation
from src.common.rule_utils import RuleUtils
from src.common.general_utils import GeneralUtils


class TDSUtils:
    """
    Class that encapsulates TDS operations.

    Given the supervisor run id look up the location of the data directory and perform operations on it.

    """
    def __init__(self, _logger=None):
        """
        Initializes this class

        """
        # if a reference to a logger passed in then use it
        if _logger is not None:
            # get a handle to a logger
            self.logger = _logger
        else:
            # get the log level and directory from the environment.
            log_level, log_path = LoggingUtil.prep_for_logging()

            # create a logger
            self.logger = LoggingUtil.init_logging("APSVIZ.Archiver.TDSUtils", level=log_level, line_format='medium', log_file_path=log_path)

        # specify the DBs to gain connectivity to
        db_names: tuple = ('apsviz',)

        # create a DB connection object
        self.db_info = PGImplementation(db_names, self.logger)

        # load environment variables
        self.tds_url = os.environ.get('TDS_URL')  # 'https://apsviz-thredds-dev.apps.renci.org/thredds/fileServer/'
        self.tds_base_directory = os.environ.get('TDS_BASE_PATH')  # thredds_data

        # get a handle to the rule utils
        self.rule_utils = RuleUtils(self.logger)

        # create the general utilities class
        self.general_utils = GeneralUtils(self.logger)

        # init some storage for the run names
        self.run_names: set = set()

        # Windows platforms use a different dir separator
        if sys.platform == 'win32':
            self.dir_sep = '\\'
        # otherwise, default to the linux seperator
        else:
            self.dir_sep = '/'

    def remove_dirs(self, instance_id: str) -> bool:
        """
        recursively removes empty directories

        :param instance_id:
        :return:
        """
        # init the return value
        ret_val: bool = True

        # split the instance id into parts
        instance_id_parts: list = instance_id.split('-')

        # ensure we got 3 parts. anything else is unexpected
        if len(instance_id_parts) == 3:
            # get the TDS directory
            data_path: str = self.get_tds_data_path(instance_id, instance_id_parts)

            try:
                # if there is no path, this must be on a TDS server outside this namespace
                if len(data_path) > 0:
                    # remove the directory specified that has the data
                    shutil.rmtree(data_path)

                    # get the number of directories that must be checked when looking for empties.
                    # we use the advisory value (YYYYMMDD) in the instance id for the directory to start checking from.
                    # this should avoid a huge number of recursive directory checks.
                    dir_count = (len(data_path.split(self.dir_sep)) - len(data_path.split(instance_id_parts[1])[0].split(self.dir_sep))) * -1

                    # get the starting directory to start traversing up to
                    interrogate_path = self.dir_sep.join(data_path.split(self.dir_sep)[0: dir_count])

                    # walk the directory path from the bottom up
                    for current_dir, _, _ in os.walk(interrogate_path, topdown=False):
                        self.logger.debug('Interrogating the %s directory.', current_dir)

                        # is anything in the subdirectory?
                        if len(os.listdir(current_dir)) == 0:
                            try:
                                # try to remove the directory
                                os.rmdir(current_dir)

                                self.logger.debug('Empty subdirectory %s has been removed.', current_dir)
                            # if this occurs, show it as a warning as the directory is not configured properly
                            except PermissionError:
                                self.logger.warning('There was a permissions error removing directory %s.', current_dir)

                                # set the failure flag
                                ret_val = False

                                # no need to continue
                                break
                            # all other issues will be ignored
                            except OSError:
                                self.logger.debug('Exception removing directory %s, ignoring.', current_dir)
                        else:
                            self.logger.debug('Directory %s was not empty, interrogation complete.', current_dir)

                            # there is no need to continue looking for empty directories
                            break
                else:
                    self.logger.warning('Warning: no TDS path found for instance id %s.', instance_id)
            except FileNotFoundError:
                self.logger.warning('Warning directory %s does not exist for %s.', data_path, instance_id)
        else:
            self.logger.warning('Error: Instance id %s is in an unexpected format.', instance_id)
            ret_val = False

        # return the result
        return ret_val

    def get_tds_data_path(self, instance_id: str, instance_id_parts: list) -> (str, int):
        """
        Given the run id get the file system path to the directory on the TDS server

        :param instance_id:
        :param instance_id_parts:

        :return:
        """
        # init the return values
        ret_val: str = ''

        # get the run properties from the DB
        run_properties = self.db_info.get_run_props(instance_id_parts[0], '-'.join(instance_id_parts[1:]))

        # did we get something?
        if run_properties == -1:
            self.logger.info('Error: Did not get the TDS run property for: %s', instance_id)
        else:
            # init the download url key name
            property_index: str = ''

            # make sure we handle the case of legacy ASGS data
            if 'output.downloadurl' in run_properties:
                property_index = 'output.downloadurl'
            elif 'downloadurl' in run_properties:
                property_index = 'downloadurl'

            # is this a path on the current namespace?
            if len(property_index) > 0 and run_properties[property_index].find(self.tds_url) != -1:
                # remove the url from the path
                ret_val = run_properties[property_index].replace(self.tds_url, '')

                # force all the directory separators to the current platform
                ret_val = ret_val.replace('/', self.dir_sep)

                # join the values to get a good file directory path
                ret_val = os.path.join(self.tds_base_directory, ret_val)

        # return the value to the caller
        return ret_val
