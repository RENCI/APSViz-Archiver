# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2024 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Test geoserver operations

    Author: Phil Owen, 2/16/2023
"""
import os
import pytest

from collections import namedtuple
from src.test.test_utils import run_rule
from src.common.geoserver_utils import GeoServerUtils
from src.common.rule_utils import RuleUtils

# init the full coverage store name (aka instance id e.g. 4303-2023020206-namforecast_maxele63)
instance_id: str = 'test_store'

# set the global test mode
test_mode: bool = True

# declare global variables
geoserver_workspace: str = ''
geoserver_proj_path: str = ''
obs_proj_dir: str = ''
source_dir : str = ''
dest_dir: str = ''


def setup_dirs_and_envs():
    """
    prepares the environment for testing

    :return:
    """
    # for all tests to use
    global obs_proj_dir, source_dir, dest_dir, geoserver_workspace, geoserver_proj_path

    # get the geoserver workspace name
    geoserver_workspace = os.environ.get('GEOSERVER_WORKSPACE', 'ADCIRC_2024')

    # get the working directory name
    input_path = os.path.dirname(__file__)

    assert input_path

    # make the dir if it doesn't exist
    if input_path and not os.path.exists(input_path):
        os.makedirs(input_path)

    # get a test directory for the geoserver files
    geoserver_proj_path = os.environ.get('GEOSERVER_PROJ_PATH', 'pytest_geoserver_data')

    assert geoserver_proj_path

    # get the base path of the test data
    base_path = os.path.join(input_path, geoserver_proj_path)

    # save the new base path
    os.environ['GEOSERVER_PROJ_PATH'] = base_path

    # get a test directory for obs data files
    obs_proj_path = os.environ.get('FILESERVER_OBS_PATH', 'obsmod_data')

    # get the location of the obs mod data
    obs_proj_dir = os.path.join(base_path, obs_proj_path)

    # save the new obs data path
    os.environ['FILESERVER_OBS_PATH'] = obs_proj_dir

    # save the TDS data path
    os.environ['TDS_BASE_PATH'] = base_path

    # set the TDS server url. this must be in sync with the namespace the geoserver is in
    # it must match the location of the TDS test data. anything else will not pe processed
    os.environ['TDS_URL'] = os.environ.get('TDS_URL', 'https://tds.renci.org/thredds/fileServer/')

    # source location of all test files
    source_dir = os.path.join(base_path, geoserver_workspace)

    # location of destination directory
    dest_dir = os.path.join(base_path, 'geoserver_out')

    # check if the geoserver directory exists
    if not os.path.exists(source_dir):
        # create the geoserver directory
        os.makedirs(source_dir)

    # check if the obsmod directory exists
    if not os.path.exists(dest_dir):
        # create the obs/mod directory
        os.makedirs(dest_dir)

    # check if the obsmod directory exists
    if not os.path.exists(obs_proj_dir):
        # create the obs/mod directory
        os.makedirs(obs_proj_dir)


# setup for testing
setup_dirs_and_envs()


def create_geoserver_store(store_type: str) -> bool:
    """
    Creates a geoserver coverage store if it doesn't exist

    :return:
    """
    # init the return
    success: bool = True

    # get a handle to the geoserver utils
    geo_svr: GeoServerUtils = GeoServerUtils()

    # get the coverage store
    stores: list = geo_svr.get_geoserver_store(store_type, instance_id)

    if len(stores) == 0:
        # create the coverage store
        success: bool = geo_svr.create_geoserver_store(store_type, instance_id)

    # return the result of the creation
    return success


def remove_geoserver_store(store_type: str) -> bool:
    """
    removes a store of the type specified.

    :param store_type:
    :return:
    """
    # create a test rule dict
    test_rule: dict = {'name': 'Test - Remove geoserver entries BY_AGE', 'description': 'Remove geoserver entries BY_AGE.',
                       'query_criteria_type': 'BY_AGE', 'query_data_type': 'INTEGER', 'query_data_value': -1, 'predicate_type': 'GREATER_THAN',
                       'action_type': 'GEOSERVER_REMOVE', 'data_type': 'NONE', 'source': 'not used', 'destination': dest_dir, 'debug': test_mode}

    # create a rule utility
    rule_utils = RuleUtils()

    # validate and convert the dict into a rule
    rule: RuleUtils.Rule = rule_utils.validate_and_convert_to_rule(test_rule)

    # get a handle to the geoserver utils
    geo_svr: GeoServerUtils = GeoServerUtils()

    # remove the coverage store
    success: bool = geo_svr.perform_geoserver_store_ops(rule, store_type, instance_id)

    # return the result
    return success


def create_test_dirs(start: int, stop: int, max_count: int):
    """
    creates a number of geoserver directories for testing

    :param start:
    :param stop:
    :param max_count:
    :return:
    """
    # get a handle to the geoserver utils
    geo_svr: GeoServerUtils = GeoServerUtils()

    # get the coverage stores list
    stores = geo_svr.get_geoserver_stores_like_instance_id('coverageStores')

    def rec_sort(entry):
        return entry['name']

    # get the items in order
    stores.sort(key=rec_sort)

    # start a counter
    count: int = 0

    # did we get data?
    if len(stores) != 0:
        # loop through the stores
        for store in stores[start:stop]:
            # check the counter
            if count < max_count:
                count += 1
            else:
                break

            # create a full path for the obsmod file
            full_geo_path = os.path.join(source_dir, store['name'])

            # if the directory doesn't exist
            if not os.path.exists(full_geo_path):
                # create a geoserver directory
                os.mkdir(full_geo_path)

            # get the instance id for the directory name
            obs_instance_id: str = store['name'].split('_')[0]

            # create a full path for the obsmod file
            full_obs_path = os.path.join(obs_proj_dir, obs_instance_id)

            # if the directory doesn't exist
            if not os.path.exists(full_obs_path):
                # create an obsmod directory
                os.mkdir(full_obs_path)


#@pytest.mark.skip(reason="Local test only")
def test_geoserver_remove_rule():
    """
    tests the retrieval of geoserver entries that meet rule criteria

    :return:
    """
    # create a test rule dict
    test_rule: dict = {'name': 'Test - Remove geoserver entries BY_AGE', 'description': 'Remove geoserver entries BY_AGE.',
                       'query_criteria_type': 'BY_AGE', 'query_data_type': 'INTEGER', 'query_data_value': 237, 'predicate_type': 'GREATER_THAN',
                       'action_type': 'GEOSERVER_REMOVE', 'data_type': 'NONE', 'source': 'NA', 'destination': 'NA', 'debug': test_mode}

    # create test data
    create_test_dirs(0, 1, 1)

    # run the rule. the first thing in this method is to convert the dict to a rule
    process_stats = run_rule(test_rule)

    # interrogate the result
    assert process_stats['failed'] == 0 and process_stats['removed'] > 0 and process_stats['swept'] > 0


@pytest.mark.skip(reason="Local test only")
def test_get_geoserver_entities():
    """
    tests the retrieval of instance ids found on the file system specified

    :return:
    """
    # create a test rule dict
    test_rule: dict = {'name': 'Test - Test get run name entities BY_AGE', 'description': 'Test get run name entities BY_AGE.',
                       'query_criteria_type': 'BY_AGE', 'query_data_type': 'INTEGER', 'query_data_value': -1, 'predicate_type': 'GREATER_THAN',
                       'action_type': 'GEOSERVER_REMOVE', 'data_type': 'NONE', 'source': 'not_used', 'destination': dest_dir, 'debug': test_mode}

    # create test data
    create_test_dirs(0, 1, 1)

    # get a handle to the geoserver utils
    geo_svr: GeoServerUtils = GeoServerUtils()

    rule_utils = RuleUtils()

    # convert elements to their equivalent types
    rule: namedtuple = rule_utils.validate_and_convert_to_rule(test_rule)

    # run the rule
    entities = geo_svr.get_geoserver_entities_from_dir(rule)

    # interrogate the result
    assert len(entities) > 0


def test_get_coverage_store():
    """
    Tests the retrieval of a geoserver coverage store

    :return:
    """
    # init the store type
    store_type = 'coverageStores'

    # create a test store, fail if we couldn't get one
    assert create_geoserver_store(store_type)

    # get a handle to the geoserver utils
    geo_svr: GeoServerUtils = GeoServerUtils()

    # get the coverage store
    ret_val: list = geo_svr.get_geoserver_store(store_type, instance_id)

    # check the result
    assert len(ret_val) == 1

    # get the layer list
    ret_val = geo_svr.get_geoserver_store(store_type, 'invalid instance id')

    # check the result
    assert len(ret_val) == 0

    # remove the test store, assert on failure
    assert remove_geoserver_store(store_type)


def test_get_coverage_stores():
    """
    Tests getting all the geoserver coverage stores

    :return:
    """
    # init the store type
    store_type = 'coverageStores'

    # create a test store, fail if we couldn't get one
    assert create_geoserver_store(store_type)

    # get a handle to the geoserver utils
    geo_svr: GeoServerUtils = GeoServerUtils()

    # get the coverage stores list
    stores = geo_svr.get_geoserver_stores_like_instance_id('coverageStores', instance_id)

    # make sure we got some back
    assert len(stores) > 0

    # get the coverage stores list
    stores = geo_svr.get_geoserver_stores_like_instance_id('coverageStores')

    # make sure we got some back
    assert len(stores) > 0

    # remove the test store, assert on failure
    assert remove_geoserver_store(store_type)


def test_remove_coverage_store():
    """
    Tests the deletion of a geoserver coverage store

    :return:
    """
    # init the store type
    store_type = 'coverageStores'

    # create a test rule dict
    test_rule: dict = {'name': 'Test - Remove geoserver entries BY_AGE', 'description': 'Remove geoserver entries BY_AGE.',
                       'query_criteria_type': 'BY_AGE', 'query_data_type': 'INTEGER', 'query_data_value': -1, 'predicate_type': 'GREATER_THAN',
                       'action_type': 'GEOSERVER_REMOVE', 'data_type': 'NONE', 'source': 'not used', 'destination': dest_dir, 'debug': test_mode}

    # create a rule utility
    rule_utils = RuleUtils()

    # validate and convert the dict into a rule
    rule: RuleUtils.Rule = rule_utils.validate_and_convert_to_rule(test_rule)

    # create a test store, fail if we couldn't get one
    assert create_geoserver_store(store_type)

    # get a handle to the geoserver utils
    geo_svr: GeoServerUtils = GeoServerUtils()

    # remove the coverage store
    ret_val: bool = geo_svr.perform_geoserver_store_ops(rule, store_type, instance_id)

    # check the result
    assert ret_val

    # get the layer list
    ret_val: list = geo_svr.get_geoserver_store(store_type, 'invalid instance id')

    # check the result
    assert len(ret_val) == 0
