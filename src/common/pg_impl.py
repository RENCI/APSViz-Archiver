# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2024 Renaissance Computing Institute. All rights reserved.
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

        Note this class is inherited from the PGUtilsMultiConnect class
        which has all the connection and cursor handling.
    """

    def __init__(self, db_names: tuple, _logger=None, _auto_commit=True):
        # if a reference to a logger is passed in, use it
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

    def remove_catalog_db_records(self, run_name: str):
        """
        Removes the adcirc_obs stations that are associated to the instance id from the DB.

        """
        # init the return value
        ret_val: bool = True

        # init storage for the SQL
        sql: str = ''

        try:
            # build up the sql
            sql = f"SELECT remove_catalog_member('{run_name}%')"

            # execute the sql
            sql_ret = self.exec_sql('apsviz', sql)

            # check the result
            if int(sql_ret) < 0:
                ret_val = False

        except Exception:
            self.logger.exception("Error detected executing SQL: %s.", sql)

            # set the error code
            ret_val = False

        # return the success flag
        return ret_val

    def is_tropical_run(self, run_name: str) -> bool:
        """
        Checks to see if this is a tropical (hurricane) run.

        Note that hurricanes aren't worked on. So a True return
        will force no activity on the run

        :param run_name:
        :return:
        """
        # init the return value
        ret_val: bool = True

        # init storage for the SQL
        sql: str = ''

        try:
            # build up the sql
            sql = f"SELECT is_tropical_run('{run_name}%')"

            # execute the sql
            sql_ret = self.exec_sql('apsviz', sql)

            # check the return
            if 'result' in sql_ret:
                # return whatever the result is
                ret_val = sql_ret['result']
            # this is an error
            else:
                ret_val = True

        except Exception:
            self.logger.exception("Error detected executing SQL: %s.", sql)

            # set the error code
            ret_val = True

        # return the success flag
        return ret_val

    def remove_run_props_db_image_records(self, run_name: str):
        """
        Removes the apsviz image run props that are associated to the instance id from the DB.

        """
        # init the return value
        ret_val: bool = True

        # init storage for the SQL
        sql: str = ''

        try:
            # build up the sql
            sql = f"SELECT remove_image_run_props('{run_name}')"

            # execute the sql
            sql_ret = self.exec_sql('apsviz', sql)

            # check the result
            if sql_ret < 0:
                ret_val = False

        except Exception:
            self.logger.exception("Error detected executing SQL: %s.", sql)

            # set the error code
            ret_val = False

        # return the success flag
        return ret_val

    def remove_obs_mod_db_records(self, run_name: str) -> bool:
        """
        Removes the adcirc_obs stations that are associated to the instance id from the DB.

        """
        # init the return value
        ret_val: bool = True

        # init storage for the SQL
        sql: str = ''

        try:
            # build up the sql
            sql = f"SELECT * FROM remove_adcirc_obs_stations('{run_name}')"

            # execute the sql
            sql_ret = self.exec_sql('adcirc_obs', sql)

            # check the result
            if sql_ret < 0:
                ret_val = False

        except Exception:
            self.logger.exception("Error detected executing SQL: %s.", sql)

            # set the error code
            ret_val = False

        # return the success flag
        return ret_val

    def get_run_props(self, instance_id: int, uid: str):
        """
        gets the run properties for a run

        :return:
        """
        # create the sql
        sql: str = f"SELECT * FROM public.get_run_prop_items_json({instance_id}, '{uid}')"

        # get the data
        ret_val = self.exec_sql('apsviz', sql)

        # check the result
        if ret_val != 0:
            # replace with the data sorted by keys
            ret_val = {x: ret_val[0]['run_data'][x] for x in sorted(ret_val[0]['run_data'])}
        else:
            ret_val = -1

        # return the data
        return ret_val
