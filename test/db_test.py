# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Test file operations

    Author: Phil Owen, 10/23/2022
"""
from src.common.pg_utils_multi import PGUtilsMultiConnect


def test_db_connection_creation():
    """
    Tests the creation and usage of the db utils multi-connect class

    :return:
    """
    # specify the DBs to gain connectivity to
    db_names: tuple = ('asgs', 'apsviz')

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
