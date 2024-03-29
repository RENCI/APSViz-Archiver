# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2024 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Test TDS operations

    Author: Phil Owen, 2/16/2023
"""
import os

import pytest

from src.common.tds_utils import TDSUtils

# get the working directory name
input_path = os.path.dirname(__file__)

# make the dir if it doesn't exist
if input_path and not os.path.exists(input_path):
    os.makedirs(input_path)

# get the base directory for TDS. in this test case, it is the dir with test data
tds_base_path = os.environ.get('TDS_BASE_PATH', 'pytest_geoserver_data')

# get the base path of the test data
base_path = os.path.join(input_path, tds_base_path)

# save the new base dir
os.environ['TDS_BASE_PATH'] = base_path

# get the target TDS URL
tds_url = os.environ.get('TDS_URL', '')


@pytest.mark.skip(reason="Local test only")
def test_get_tds_data_path():
    """
    tests the creation of the TDS data path
    :return:
    """
    # get a TDS utils object
    tds: TDSUtils = TDSUtils()

    # declare an instance id
    instance_id = '4537-2024020600-gfsforecast'

    # get the instance id parts
    instance_id_parts = instance_id.split('-')

    # get the file path
    file_path: str = tds.get_tds_data_path(instance_id, instance_id_parts)

    assert file_path.startswith(tds.tds_base_directory)


@pytest.mark.skip(reason="Local test only")
def test_remove_dirs():
    """
    tests the recursive removal of directories

    :return:
    """
    # get a TDS utils object
    tds: TDSUtils = TDSUtils()

    # remove the directory structure in the test directory
    ret_val: bool = tds.remove_dirs('4537-2024020600-gfsforecast')

    assert ret_val

    # remove the directory structure. this should fail because it is an unexpected id format
    ret_val: bool = tds.remove_dirs('4537-2024020600')

    assert not ret_val

    # remove the TDS URL. this should return tue now as this will result in a no-op
    os.environ['TDS_URL'] = ''

    # get a new TDS utils object with a blank TDS URL
    tds: TDSUtils = TDSUtils()

    # remove the directory structure. this should pass because of the no-op
    ret_val: bool = tds.remove_dirs('4537-2024020600')

    assert ret_val
