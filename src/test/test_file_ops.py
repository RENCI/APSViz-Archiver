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
import os.path
from test_utils import input_path, output_path, cleanup, run_rule


def test_copy_file():
    """
    test the simple copy of a file to another directory

    :return:
    """
    # get the paths to the test directories/files
    source: str = os.path.join(input_path, 'test_files/test_file.txt')
    dest: str = os.path.join(output_path, 'file_dir1/')

    # create a test rule dict
    test_rule: dict = {'name': 'Test - Copy Test file', 'description': '', 'query_criteria_type': None, 'query_data_type': None,
                       'query_data_value': 1, 'predicate_type': None, 'sync_system_type': None, 'action_type': 'COPY', 'data_type': 'FILE',
                       'source': source, 'destination': dest}

    # run the rule
    process_stats = run_rule(test_rule)

    # interrogate the result
    assert process_stats['copied'] == 1 and process_stats['failed'] == 0
    assert os.path.isfile(os.path.join(output_path, 'file_dir1/test_file.txt'))

    ###########
    # test the copy of a file to another directory with a different name
    ###########

    # get the paths to the test directories/files
    source: str = os.path.join(input_path, 'test_files/test_file.txt')
    dest: str = os.path.join(output_path, 'file_dir1/new_test_file.txt')

    # create a test rule dict
    test_rule: dict = {'name': 'Test - Copying Test file with different name', 'description': '', 'query_criteria_type': None,
                       'query_data_type': None, 'query_data_value': 1, 'predicate_type': None, 'sync_system_type': None, 'action_type': 'COPY',
                       'data_type': 'FILE', 'source': source, 'destination': dest}

    # run the rule
    process_stats = run_rule(test_rule)

    # interrogate the result
    assert process_stats['copied'] == 1 and process_stats['failed'] == 0
    assert os.path.isfile(os.path.join(output_path, 'file_dir1/new_test_file.txt'))


def test_move_file():
    """
    test the move operation

    :return:
    """
    # get the paths to the test directories/files
    source: str = os.path.join(output_path, 'file_dir1/test_file.txt')
    dest: str = os.path.join(output_path, 'file_dir2/')

    # create a test rule
    test_rule: dict = {'name': 'Test - Move file', 'description': 'Move file', 'query_criteria_type': None, 'query_data_type': None,
                       'query_data_value': None, 'predicate_type': None, 'sync_system_type': None, 'action_type': 'MOVE', 'data_type': 'FILE',
                       'source': source, 'destination': dest}

    # run the rule
    process_stats = run_rule(test_rule)

    # interrogate the result
    assert process_stats['moved'] == 1 and process_stats['failed'] == 0
    assert os.path.isfile(os.path.join(output_path, 'file_dir2/test_file.txt'))


def test_remove_file():
    """
    test the remove operation

    :return:
    """
    # get the test directory
    source: str = os.path.join(output_path, 'file_dir2/test_file.txt')

    # create a test rule
    test_rule: dict = {'name': 'Test - Remove file', 'description': 'Remove file', 'query_criteria_type': None, 'query_data_type': None,
                       'query_data_value': None, 'predicate_type': None, 'sync_system_type': None, 'action_type': 'REMOVE', 'data_type': 'FILE',
                       'source': source, 'destination': None}

    # run the rule
    process_stats = run_rule(test_rule)

    # interrogate the result
    assert process_stats['removed'] == 1 and process_stats['failed'] == 0
    assert not os.path.exists(os.path.join(output_path, 'file_dir2/test_file.txt'))


def test_cleanup():
    """
    Cleans up the leftover directories

    :return:
    """
    cleanup(['file_dir1/', 'file_dir2/'])
