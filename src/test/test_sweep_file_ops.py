# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2024 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Test directory sweep operations

    Author: Phil Owen, 10/23/2022
"""
import os.path

from test_utils import output_path, sweeps_init, cleanup, run_rule

# set the global test mode
test_mode: bool = False


def test_init():
    """
    creates test data for this series of tests

    :return:
    """
    sweeps_init()


def test_copy_file_sweep():
    """
    test the sweep file copy operation by age

    :return:
    """
    # get the paths to the test directories
    source_dir: str = os.path.join(output_path, 'sweep_dir1/')  # , 'sweep_sub/'
    dest_dir: str = os.path.join(output_path, 'sweep_dir2/')

    # create a test rule
    test_rule: dict = {'name': 'Test - Copy file Sweep BY_AGE', 'description': 'File copy BY_AGE.', 'query_criteria_type': 'BY_AGE',
                       'query_data_type': 'INTEGER', 'query_data_value': 1, 'predicate_type': 'LESS_THAN',
                       'action_type': 'SWEEP_COPY', 'data_type': 'FILE', 'source': source_dir, 'destination': dest_dir, 'debug': test_mode}

    # run the rule
    process_stats = run_rule(test_rule)

    # interrogate the result
    assert process_stats['swept'] == 1 and process_stats['failed'] == 0
    assert os.path.exists(os.path.join(output_path, 'sweep_dir1', 'sweep_sub/'))

    # get a list of the contents of the source directory
    entities = os.listdir(source_dir)

    # make sure all the files were transferred
    for entity in entities:
        # flag to capture a directory found in a file operation
        dir_found = False

        # if this is a not source directory it should have been copied
        if not os.path.isdir(os.path.join(source_dir, entity)):
            assert os.path.isfile(os.path.join(dest_dir, entity))
        # if this directory exists in the dest it is an error for file ops
        elif os.path.isdir(os.path.join(dest_dir, entity)):
            dir_found = True

        # check the result
        assert not dir_found


def test_move_file_sweep():
    """
    test the sweep file move operation by age

    :return:
    """
    # get the paths to the test directories
    source_dir: str = os.path.join(output_path, 'sweep_dir2/')
    dest_dir: str = os.path.join(output_path, 'sweep_dir3/')

    # create a test rule
    test_rule: dict = {'name': 'Test - Move file Sweep BY_AGE', 'description': 'File move BY_AGE.', 'query_criteria_type': 'BY_AGE',
                       'query_data_type': 'INTEGER', 'query_data_value': 1, 'predicate_type': 'LESS_THAN',
                       'action_type': 'SWEEP_MOVE', 'data_type': 'FILE', 'source': source_dir, 'destination': dest_dir, 'debug': test_mode}

    # get a list of the contents of the source directory that will be moved
    entities = os.listdir(source_dir)

    # run the rule
    process_stats = run_rule(test_rule)

    # interrogate the result
    assert process_stats['swept'] == 1 and process_stats['failed'] == 0
    assert os.path.exists(dest_dir)

    # make sure all the files were transferred
    for entity in entities:
        assert os.path.isfile(os.path.join(dest_dir, entity))


def test_remove_file_sweep():
    """
    test the sweep file remove operation by age

    :return:
    """
    # get the paths to the test directories
    source_dir: str = os.path.join(output_path, 'sweep_dir3/')

    # create a test rule
    test_rule: dict = {'name': 'Test - Remove files sweep BY_AGE', 'description': 'Remove files BY_AGE.', 'query_criteria_type': 'BY_AGE',
                       'query_data_type': 'INTEGER', 'query_data_value': 1, 'predicate_type': 'LESS_THAN',
                       'action_type': 'SWEEP_REMOVE', 'data_type': 'FILE', 'source': source_dir, 'destination': None, 'debug': test_mode}

    # run the rule
    process_stats = run_rule(test_rule)

    # interrogate the result
    assert process_stats['swept'] == 1 and process_stats['failed'] == 0
    assert os.path.exists(source_dir)

    # get a list of the contents of the source directory
    files = os.listdir(source_dir)

    # make sure all the files were removed
    for file in files:
        assert not os.path.isfile(os.path.join(source_dir, file))


def test_cleanup():
    """
    Cleans up the leftover directories

    :return:
    """
    # remove all directories that were used in this test
    cleanup(['sweep_dir1/', 'sweep_dir2/', 'sweep_dir3/'])
