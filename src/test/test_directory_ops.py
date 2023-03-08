# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    APSViz Archiver - Test directory operations

    Author: Phil Owen, 10/23/2022
"""
import os.path

from test_utils import input_path, output_path, run_rule


def test_copy_directory():
    """
    test the copy directory operation

    :return:
    """
    # get the paths to the test directories
    source_dir: str = os.path.join(input_path, 'test_files/')
    dest_dir: str = os.path.join(output_path, 'dir1/')

    # create a test rule dict
    test_rule: dict = {'name': 'Test - Copy directory', 'description': 'Directory copy.', 'query_criteria_type': None, 'query_data_type': None,
                       'query_data_value': None, 'predicate_type': None, 'sync_system_type': None, 'action_type': 'COPY', 'data_type': 'DIRECTORY',
                       'source': source_dir, 'destination': dest_dir}

    # run the rule
    process_stats = run_rule(test_rule)

    # interrogate the result
    assert process_stats['copied'] == 1 and process_stats['failed'] == 0
    assert os.path.isfile(os.path.join(dest_dir, 'test_file.txt'))


def test_move_directory():
    """
    test the  operation

    :return:
    """
    # gget the paths to the test directories
    source_dir: str = os.path.join(output_path, 'dir1/')
    dest_dir: str = os.path.join(output_path, 'dir2/')

    # create a test rule
    test_rule: dict = {'name': 'Test - Move file', 'description': 'Move file', 'query_criteria_type': None, 'query_data_type': None,
                       'query_data_value': None, 'predicate_type': None, 'sync_system_type': None, 'action_type': 'MOVE', 'data_type': 'DIRECTORY',
                       'source': source_dir, 'destination': dest_dir}

    # run the rule
    process_stats = run_rule(test_rule)

    # interrogate the result
    assert process_stats['moved'] == 1 and process_stats['failed'] == 0
    assert os.path.exists(dest_dir)
    assert not os.path.exists(source_dir)


def test_remove_directory():
    """
    test the  operation

    :return:
    """
    # get the paths to the test directories
    source_dir: str = os.path.join(output_path, 'dir2/')

    # create a test rule
    test_rule: dict = {'name': 'Test - Remove file', 'description': 'Remove file', 'query_criteria_type': None, 'query_data_type': None,
                       'query_data_value': None, 'predicate_type': None, 'sync_system_type': None, 'action_type': 'REMOVE', 'data_type': 'DIRECTORY',
                       'source': source_dir, 'destination': None}

    # run the rule
    process_stats = run_rule(test_rule)

    # interrogate the result
    assert process_stats['removed'] == 1 and process_stats['failed'] == 0
    assert not os.path.exists(source_dir)

# def test_remove_directory_and_geoserver_coverage_store():
#     # create a directory for testing
#     test_copy_directory()
#
#     # get the paths to the test directories
#     source_dir: str = os.path.join(output_path, 'dir2/')
#
#     # create a test rule
#     test_rule: dict = {'name': 'Test - Remove geoserver layer and directory', 'description': 'Remove a GeoServer layer and directory',
#                        'query_criteria_type': None, 'query_data_type': None, 'query_data_value': None, 'predicate_type': None,
#                       'sync_system_type': 'GEOSERVER', 'action_type': 'REMOVE', 'data_type': 'DIRECTORY', 'source': source_dir, 'destination': None}
#
#     # run the rule
#     process_stats = run_rule(test_rule)
#
#     # interrogate the result
#     assert process_stats['removed'] == 1 and process_stats['failed'] == 0
#     assert not os.path.exists(source_dir)
