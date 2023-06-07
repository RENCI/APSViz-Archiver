# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
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


def test_init():
    """
    creates test data for this series of tests

    :return:
    """
    sweeps_init()


def test_move_directory_sweep():
    """
    test the sweep directory move operation by age

    :return:
    """
    # get the paths to the test directories
    source_dir: str = os.path.join(output_path, 'sweep_dir1')
    dest_dir: str = os.path.join(output_path, 'sweep_dir2')

    # create a test rule dict
    test_rule: dict = {'name': 'Test - Move directory Sweep BY_AGE', 'description': 'Directory move BY_AGE.', 'query_criteria_type': 'BY_AGE',
                       'query_data_type': 'INTEGER', 'query_data_value': 1, 'predicate_type': 'LESS_THAN',
                       'action_type': 'SWEEP_MOVE', 'data_type': 'DIRECTORY', 'source': source_dir, 'destination': dest_dir, 'debug': False}

    # get a list of the contents of the source directory
    entities = os.listdir(os.path.join(source_dir, 'sweep_sub'))

    # run the rule
    process_stats = run_rule(test_rule)

    # interrogate the result
    assert process_stats['swept'] == 1 and process_stats['failed'] == 0

    # note this is a directory operation. no files in the source directory should be touched
    assert not os.path.isfile(os.path.join(dest_dir, 'test_file.txt'))

    # make sure all the files were transferred to the destination
    for entity in entities:
        assert os.path.isfile(os.path.join(dest_dir, 'sweep_sub', entity))


def test_copy_directory_sweep():
    """
    test the sweep directory copy operation by age

    :return:
    """
    # get the paths to the test directories
    source_dir: str = os.path.join(output_path, 'sweep_dir2')
    dest_dir: str = os.path.join(output_path, 'sweep_dir1')

    # create a test rule
    test_rule: dict = {'name': 'Test - Copy directory Sweep BY_AGE', 'description': 'Directory copy BY_AGE.', 'query_criteria_type': 'BY_AGE',
                       'query_data_type': 'INTEGER', 'query_data_value': 1, 'predicate_type': 'LESS_THAN',
                       'action_type': 'SWEEP_COPY', 'data_type': 'DIRECTORY', 'source': source_dir, 'destination': dest_dir, 'debug': False}

    # run the rule
    process_stats = run_rule(test_rule)

    # interrogate the result
    assert process_stats['swept'] == 1 and process_stats['failed'] == 0
    assert os.path.exists(dest_dir)

    # get a list of the contents of the source directory
    entities = os.listdir(os.path.join(source_dir, 'sweep_sub'))

    # make sure all the files were transferred
    for entity in entities:
        assert os.path.isfile(os.path.join(dest_dir, 'sweep_sub', entity))


def test_remove_directory_sweep():
    """
    test the sweep directory remove operation by age

    :return:
    """
    # get the paths to the test directories
    source_dir: str = os.path.join(output_path, 'sweep_dir1')

    # create a test rule
    test_rule: dict = {'name': 'Test - Copy directory Sweep BY_AGE', 'description': 'Directory copy BY_AGE.', 'query_criteria_type': 'BY_AGE',
                       'query_data_type': 'INTEGER', 'query_data_value': 1, 'predicate_type': 'LESS_THAN',
                       'action_type': 'SWEEP_REMOVE', 'data_type': 'DIRECTORY', 'source': source_dir, 'destination': None, 'debug': False}

    # run the rule
    process_stats = run_rule(test_rule)

    # interrogate the result
    assert process_stats['swept'] == 1 and process_stats['failed'] == 0
    assert os.path.isfile(os.path.join(source_dir, 'test_file.txt'))
    assert not os.path.exists(os.path.join(source_dir, 'sweep_sub/'))


def test_cleanup():
    """
    Cleans up the leftover directories

    :return:
    """
    cleanup(['sweep_dir1/', 'sweep_dir2/'])
