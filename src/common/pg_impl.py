# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Class for database functionalities

    Author: Phil Owen, RENCI.org
"""
from src.common.pg_utils_multi import PGUtilsMultiConnect
from src.common.logger import LoggingUtil


class PGImplementation(PGUtilsMultiConnect):
    """
        Class that contains DB calls for the Archiver.

        Note this class inherits from the PGUtilsMultiConnect class
        which has all the connection and cursor handling.
    """

    def __init__(self, db_names: tuple, _logger=None, _auto_commit=True):
        # if a reference to a logger passed in use it
        if _logger is not None:
            # get a handle to a logger
            self.logger = _logger
        else:
            # get the log level and directory from the environment.
            log_level, log_path = LoggingUtil.prep_for_logging()

            # create a logger
            self.logger = LoggingUtil.init_logging("Archiver.PGImplementation", level=log_level, line_format='medium', log_file_path=log_path)

        # init the base class
        PGUtilsMultiConnect.__init__(self, 'APSViz.Settings', db_names, _logger=self.logger, _auto_commit=_auto_commit)

    def __del__(self):
        """
        Calls super base class to clean up DB connections and cursors.

        :return:
        """
        # clean up connections and cursors
        PGUtilsMultiConnect.__del__(self)

    def remove_adcirc_obs_stations(self, instance_id) -> bool:
        """
        Removes the adcirc_obs stations that are associated to the instance id.

        """
        # init the return value
        ret_val: bool = True

        # init storage for the SQL
        sql: str = ''

        try:
            # build up the sql
            sql = f"SELECT remove_adcirc_obs_stations('{instance_id}')"

            # execute the sql
            ret_val = self.exec_sql('adcirc_obs', sql)

            # check the result
            if ret_val < 1:
                ret_val = False

        except Exception:
            self.logger.exception("Error detected executing SQL: %s.", sql)

            # set the error code
            ret_val = False

        # return the success flag
        return ret_val
