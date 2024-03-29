# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2024 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Test DB operations

    Author: Phil Owen, 3/2/2023
"""
import pytest
from src.common.pg_impl import PGImplementation


@pytest.mark.skip(reason="Local test only")
def test_db_connection_creation():
    """
    Tests the creation and usage of the db utils multi-connect class

    :return:
    """
    # specify the DBs to gain connectivity to
    db_names: tuple = ('apsviz', 'adcirc_obs')

    # create a DB connection object
    db_info = PGImplementation(db_names)

    # check the object returned
    assert len(db_info.dbs) == len(db_names)

    # for each db specified
    for db_name in db_names:
        # make a db request
        ret_val = db_info.exec_sql(db_name, 'SELECT version()')

        # check the data returned
        assert ret_val.startswith('PostgreSQL')


@pytest.mark.skip(reason="Local test only")
def test_remove_adcirc_obs_stations():
    """
    test the SP that removes the obs/mod station data using the instance ID

    :return:
    """
    # specify the DB to get a connection
    # note the extra comma makes this single item a singleton tuple
    db_name: tuple = ('adcirc_obs',)

    # create a DB connection object
    db_info = PGImplementation(db_name)

    # check the object returned
    assert len(db_info.dbs) == len(db_name)

    # assign an instance id
    instance_id: str = 'test_instance'

    # create the sql statement to insert a test record
    sql: str = f"WITH added_record AS (INSERT INTO stations(instance_id) VALUES ('{instance_id}') RETURNING 1) SELECT to_json(count(*)) FROM " \
               f"added_record;"

    # make the db request
    ret_val = db_info.exec_sql('adcirc_obs', sql)

    # check to see that at least one record was added
    assert ret_val == 1

    # create the sql to remove the newly added record
    sql = f"SELECT remove_adcirc_obs_stations('{instance_id}')"

    # make a db request
    ret_val = db_info.exec_sql('adcirc_obs', sql)

    # check to make sure only one was removed
    assert ret_val == 1


@pytest.mark.skip(reason="Local test only")
def test_is_tropical():
    """
    test the SP that determines if the run is tropical (or synoptic)

    :return:
    """
    # specify the DB to get a connection
    # note the extra comma makes this single item a singleton tuple
    db_name: tuple = ('apsviz',)

    # create a DB connection object
    db_info = PGImplementation(db_name)

    # check the object returned
    assert len(db_info.dbs) == len(db_name)

    # make a failure call
    ret_val = db_info.is_tropical_run("invalid instance id")

    assert not ret_val

    # make a good call for a synoptic run
    ret_val = db_info.is_tropical_run('4356-2023042018-nowcast')

    assert not ret_val

    # make a good call to a tropical run
    ret_val = db_info.is_tropical_run('4397-031-nowcast')

    assert ret_val
