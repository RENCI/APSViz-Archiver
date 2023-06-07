# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Test Utils - Utilities used for testing

    Author: Phil Owen, 10/23/2022
"""
import os.path
from time import sleep

from src.archiver.rule_handler import RuleHandler
from src.common.rule_utils import RuleUtils
from src.common.rule_enums import DataType

# define the directory for the tests and data
input_path = os.path.dirname(__file__)
output_path = os.getenv('TESTDATA_PATH', os.path.dirname(__file__))


def geoserver_init():
    """
    creates test data for this series of sweep tests

    :return:
    """
    # source location of all test files
    source: str = os.path.join(input_path, 'geoserver_files')

    # location of destination directory
    dest_dir: str = os.path.join(output_path, 'geoserver_out/')

    print(f'source directory: {source}, destination directory: {dest_dir}')

    # pause so that the data ages long enough so age tests work
    sleep(3)


def sweeps_init():
    """
    creates test data for this series of sweep tests

    :return:
    """
    # source location of all test files
    source: str = os.path.join(input_path, 'test_files')

    # source location of a single test file
    source_file: str = os.path.join(source, 'test_file.txt')

    # location of destination directory
    dest_dir: str = os.path.join(output_path, 'sweep_dir1/')

    # location of a subdirectory
    dest_sub: str = os.path.join(dest_dir, 'sweep_sub/')

    # prep for directory sweep tests
    test_rules: list = [
        {'name': 'Test - Copy Test file', 'description': '', 'query_criteria_type': None, 'query_data_type': None, 'query_data_value': 1,
         'predicate_type': None, 'action_type': 'COPY', 'data_type': 'FILE', 'source': source_file,
         'destination': dest_dir, 'debug': False},
        {'name': 'Test - Copy directory', 'description': 'Directory creation.', 'query_criteria_type': None, 'query_data_type': None,
         'query_data_value': None, 'predicate_type': None, 'action_type': 'COPY', 'data_type': 'DIRECTORY',
         'source': source, 'destination': dest_sub, 'debug': False}]

    # create the run handler
    rule_handler = RuleHandler()

    # create a rule utility
    rule_utils = RuleUtils()

    # for each test
    for test_rule in test_rules:
        # validate and convert the dict into a rule
        rule: RuleUtils.Rule = rule_utils.validate_and_convert_to_rule(test_rule)

        # check the rule
        assert rule

        # apply the rules to the data, get back some stats
        process_stats: dict = rule_handler.process_rule(rule)

        # interrogate the result
        assert process_stats['copied'] == 1 and process_stats['failed'] == 0

        assert os.path.isfile(os.path.join(dest_dir, source_file))
        assert os.path.exists(os.path.join(dest_dir, rule.destination))

        # if this is a directory operation make sure they all made it
        if rule.data_type == DataType.DIRECTORY:
            # get a list of the contents of the source directory
            files = os.listdir(source)

            # make sure all the files were transferred
            for file in files:
                assert os.path.isfile(os.path.join(rule.destination, file))

    # pause so that the data ages long enough so age tests work
    sleep(3)


def cleanup(dirs: list):
    """
    Cleans up the leftover directories

    :return:
    """
    for target_dir in dirs:
        # get the paths to the test directories
        source_dir: str = os.path.join(output_path, target_dir)

        # create a test rule
        test_rule: dict = {'name': 'Test - Remove file', 'description': 'Remove file', 'query_criteria_type': None, 'query_data_type': None,
                           'query_data_value': None, 'predicate_type': None, 'action_type': 'REMOVE',
                           'data_type': 'DIRECTORY', 'source': source_dir, 'destination': None, 'debug': False}

        # create the run handler
        rule_handler = RuleHandler()

        # create a rule utility
        rule_utils = RuleUtils()

        # convert the dict into a rule
        rule: RuleUtils.Rule = rule_utils.validate_and_convert_to_rule(test_rule)

        # check the rule
        assert rule

        # apply the rules to the data, get back some stats
        process_stats: dict = rule_handler.process_rule(rule)

        # interrogate the result
        assert process_stats['removed'] == 1 and process_stats['failed'] == 0

        # interrogate the result
        assert not os.path.exists(source_dir)


def run_rule(test_rule: dict):
    """
    Validates and runs a rule

    :param test_rule:
    :return:
    """
    # init the return
    process_stats: dict = {'moved': 0, 'copied': 0, 'removed': 0, 'swept': 0, 'failed': 0}

    # create a rule utility
    rule_utils = RuleUtils()

    # validate and convert the dict into a rule
    rule: RuleUtils.Rule = rule_utils.validate_and_convert_to_rule(test_rule)

    # make sure this is a valid rule
    if rule:
        # create the run handler
        rule_handler = RuleHandler()

        # apply the rules to the data, get back some stats
        process_stats = rule_handler.process_rule(rule)
    else:
        process_stats['failed'] += 1

    # return to the caller
    return process_stats
