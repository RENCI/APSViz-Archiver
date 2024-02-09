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

from src.common.rule_utils import RuleUtils
from src.common.tds_utils import TDSUtils

# get the working directory name
input_path = os.path.dirname(__file__)

# make the dir if it doesn't exist
if input_path and not os.path.exists(input_path):
    os.makedirs(input_path)

# get the base directory for TDS
tds_base_path = os.environ.get('TDS_BASE_DIR', 'pytest_geoserver_data')

# get the base path of the test data
base_path = os.path.join(input_path, tds_base_path)

# save the new base dir
os.environ['TDS_BASE_DIR'] = base_path

# set the test mode
test_mode = True


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


def test_remove_dirs():
    """
    tests the recursive removal of directories

    :return:
    """
    # create a test rule dict
    test_rule: dict = {'name': 'Test - Remove geoserver entries BY_AGE', 'description': 'Remove geoserver entries BY_AGE.',
                       'query_criteria_type': 'BY_AGE', 'query_data_type': 'INTEGER', 'query_data_value': 237, 'predicate_type': 'GREATER_THAN',
                       'action_type': 'GEOSERVER_REMOVE', 'data_type': 'NONE', 'source': 'NA', 'destination': 'NA', 'debug': test_mode}

    # create a rule utility
    rule_utils = RuleUtils()

    # validate and convert the dict into a rule
    rule: RuleUtils.Rule = rule_utils.validate_and_convert_to_rule(test_rule)

    # get a TDS utils object
    tds: TDSUtils = TDSUtils()

    # remove the directory structure. this should fail
    ret_val: bool = tds.remove_dirs(rule, '4537-2024020600')

    assert not ret_val

    # remove the directory structure
    ret_val: bool = tds.remove_dirs(rule, '4537-2024020600-gfsforecast')

    assert ret_val