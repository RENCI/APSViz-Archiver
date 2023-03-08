# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Test DB operations

    Author: Phil Owen, 3/2/2023
"""
# import pytest
from src.common.pg_utils_multi import PGUtilsMultiConnect


# @pytest.mark.skip(reason="Local test only")
def test_db_connection_creation():
    """
    Tests the creation and usage of the db utils multi-connect class

    :return:
    """
    # specify the DBs to gain connectivity to
    db_names: tuple = ('asgs', 'apsviz', 'adcirc_obs')

    # create a DB connection object
    db_info = PGUtilsMultiConnect(db_names)

    # check the object returned
    assert len(db_info.dbs) == len(db_names)

    # for each db specified
    for db_name in db_names:
        # make a db request
        ret_val = db_info.exec_sql(db_name, 'SELECT version()')

        # check the data returned
        assert ret_val.startswith('PostgreSQL')


def test_remove_adcirc_obs_stations():
    """
    test the SP that removes the obs/mod station data using the instance ID

    :return:
    """
    # specify the DB to get a connection
    # note the extra comma makes this single item a singleton tuple
    db_name: tuple = ('adcirc_obs',)

    # create a DB connection object
    db_info = PGUtilsMultiConnect(db_name)

    # check the object returned
    assert len(db_info.dbs) == len(db_name)

    # assign an instance id
    instance_id: str = 'test_instance'

    # create the sql statement to insert a test record
    sql: str = f"WITH added_record AS (INSERT INTO stations(instance_id) VALUES ('{instance_id}') RETURNING 1) SELECT to_json(count(*)) FROM " \
               f"added_record;"

    # make the db request
    ret_val = db_info.exec_sql(db_name[0], sql)

    # check to see that at least one record was added
    assert ret_val == 1

    # create the sql to remove the newly added record
    sql = f"SELECT remove_adcirc_obs_stations('{instance_id}')"

    # make a db request
    ret_val = db_info.exec_sql(db_name[0], sql)

    # check to make sure only one was removed
    assert ret_val == 1
