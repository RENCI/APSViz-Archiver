# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Test geoserver operations

    Author: Phil Owen, 2/16/2023
"""
import pytest
from src.common.geoserver_utils import GeoServerUtils

# init the coverage store name used for all these tests
coverage_store_name: str = 'test_coverage_store'


#@pytest.mark.skip(reason="Local test only")
def test_create_coverage_store():
    """
    Tests the creation of a geoserver coverage store

    :return:
    """
    # get a handle to the geoserver utils
    geo_svr: GeoServerUtils = GeoServerUtils()

    # create the coverage store
    success: bool = geo_svr.create_coverage_store(coverage_store_name)

    # check the result
    assert success


#@pytest.mark.skip(reason="Local test only")
def test_get_coverage_store():
    """
    Tests the retrieval of a geoserver coverage store

    :return:
    """
    # get a handle to the geoserver utils
    geo_svr: GeoServerUtils = GeoServerUtils()

    # get the coverage store
    success, store = geo_svr.get_coverage_store(coverage_store_name)

    # check the result
    assert success and len(store) == 1

    # get the layer list
    success, store = geo_svr.get_coverage_store('this is a invalid coverage store name')

    # check the result
    assert not success and store.text.startswith('No such coverage store: ')


#@pytest.mark.skip(reason="Local test only")
def test_get_coverage_stores():
    """
    Tests getting all the geoserver coverage stores

    :return:
    """
    # get a handle to the geoserver utils
    geo_svr: GeoServerUtils = GeoServerUtils()

    # get the coverage stores list
    success, stores = geo_svr.get_coverage_stores()

    # make sure we got some back
    assert len(stores['coverageStores']['coverageStore']) > 1

    # init the new coverage store name found flag
    found = False

    # look for the one we added above
    for item in stores['coverageStores']['coverageStore']:
        # was it found
        if item['name'].startswith(coverage_store_name):
            # set the flag
            found = True

            # no need to continue
            break

    # check the results
    assert success and found


#@pytest.mark.skip(reason="Local test only")
def test_remove_coverage_store():
    """
    Tests the deletion of a geoserver coverage store

    :return:
    """
    # get a handle to the geoserver utils
    geo_svr: GeoServerUtils = GeoServerUtils()

    # remove the coverage store
    success: bool = geo_svr.remove_coverage_store(coverage_store_name)

    # check the result
    assert success

    # get the layer list
    success, store = geo_svr.get_coverage_store(coverage_store_name)

    # check the result
    assert not success and store.text.startswith('No such coverage store: ')
