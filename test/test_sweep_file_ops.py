# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    APSViz Archiver - Test directory sweep operations

    Author: Phil Owen, 10/23/2022
"""
import os.path

from common_funcs import output_path, sweeps_init, cleanup, run_rule


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
    source_dir: str = os.path.join(output_path, 'sweep_dir1', 'sweep_sub/')
    dest_dir: str = os.path.join(output_path, 'sweep_dir2/')

    # create a test rule
    test_rule: dict = {"name": "Test - Copy file Sweep BY_AGE", "description": "File copy BY_AGE.", "query_criteria_type": "BY_AGE",
                       "query_data_type": "INTEGER", "query_data_value": 1, "predicate_type": "LESS_THAN", "action_type": "SWEEP_COPY",
                       "data_type": "FILE", "source": source_dir, "destination": dest_dir}

    # run the rule
    process_stats = run_rule(test_rule)

    # interrogate the result
    assert process_stats['swept'] == 1 and process_stats["failed"] == 0
    assert os.path.exists(os.path.join(output_path, 'sweep_dir1', 'sweep_sub/'))

    # get a list of the contents of the source directory
    entities = os.listdir(source_dir)

    # make sure all the files were transferred
    for entity in entities:
        assert os.path.isfile(os.path.join(dest_dir, entity))


def test_move_file_sweep():
    """
    test the sweep file move operation by age

    :return:
    """
    # get the paths to the test directories
    source_dir: str = os.path.join(output_path, 'sweep_dir2/')
    dest_dir: str = os.path.join(output_path, 'sweep_dir3/')

    # create a test rule
    test_rule: dict = {"name": "Test - Move file Sweep BY_AGE", "description": "File move BY_AGE.", "query_criteria_type": "BY_AGE",
                       "query_data_type": "INTEGER", "query_data_value": 1, "predicate_type": "LESS_THAN", "action_type": "SWEEP_MOVE",
                       "data_type": "FILE", "source": source_dir, "destination": dest_dir}

    # get a list of the contents of the source directory
    entities = os.listdir(source_dir)

    # run the rule
    process_stats = run_rule(test_rule)

    # interrogate the result
    assert process_stats['swept'] == 1 and process_stats["failed"] == 0
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
    test_rule: dict = {"name": "Test - Remove files sweep BY_AGE", "description": "Remove files BY_AGE.", "query_criteria_type": "BY_AGE",
                       "query_data_type": "INTEGER", "query_data_value": 1, "predicate_type": "LESS_THAN",
                       "action_type": "SWEEP_REMOVE", "data_type": "FILE", "source": source_dir, "destination": None}

    # get a list of the contents of the source directory
    entities = os.listdir(source_dir)

    # run the rule
    process_stats = run_rule(test_rule)

    # interrogate the result
    assert process_stats['swept'] == 1 and process_stats["failed"] == 0
    assert os.path.exists(source_dir)

    # make sure all the files were removed
    for entity in entities:
        assert not os.path.isfile(os.path.join(source_dir, entity))


def test_cleanup():
    """
    Cleans up the leftover directories

    :return:
    """
    # remove all directories that were used in this test
    cleanup(['sweep_dir1/', 'sweep_dir2/', 'sweep_dir3/'])
