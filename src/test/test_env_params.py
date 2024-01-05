# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2024 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    APSViz Archiver - Test directory operations

    Author: Phil Owen, 07/07/2023
"""
import os


def test_env_params():
    """
    tests that the needed environment params are installed.

    :return:
    """
    # get a list of the target params
    env_params: list = ['FILESERVER_OBS_PATH', 'GEOSERVER_HOST', 'GEOSERVER_PASSWORD', 'GEOSERVER_PROJ_PATH', 'GEOSERVER_URL', 'GEOSERVER_USER',
                        'GEOSERVER_WORKSPACE']

    # for each env param
    for item in env_params:
        # a value should be there
        assert os.getenv(item)
