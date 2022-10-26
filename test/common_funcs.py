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
from time import sleep

from src.archiver.rule_handler import RuleHandler
from src.common.rule_utils import RuleUtils

# define the directory for the tests and data
input_path = os.path.dirname(__file__)
output_path = os.getenv('TESTDATA_PATH', os.path.dirname(__file__))


def sweeps_init():
    """
    creates test data for this series of tests

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
         'predicate_type': None, 'action_type': 'COPY', 'data_type': 'FILE', 'source': source_file, 'destination': dest_dir},
        {"name": "Test - Copy directory", "description": "Directory creation.", "query_criteria_type": None, "query_data_type": None,
         "query_data_value": None, "predicate_type": None, "action_type": "COPY", "data_type": "DIRECTORY", "source": source,
         "destination": dest_sub}]

    # create the run handler
    rule_handler = RuleHandler()

    # for each test
    for test_rule in test_rules:
        # convert the dict into a rule
        rule: RuleUtils.Rule = RuleUtils.convert_to_enum_types(test_rule)

        # apply the rules to the data, get back some stats
        process_stats: dict = rule_handler.process_rule(rule)

        # interrogate the result
        assert process_stats['copied'] == 1 and process_stats["failed"] == 0

    assert os.path.isfile(os.path.join(dest_dir, 'test_file.txt'))
    assert os.path.exists(os.path.join(dest_dir, 'sweep_sub'))

    # get a list of the contents of the source directory
    entities = os.listdir(source)

    # make sure all the files were transferred
    for entity in entities:
        assert os.path.isfile(os.path.join(dest_sub, entity))

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
        test_rule: dict = {"name": "Test - Remove file", "description": "Remove file", "query_criteria_type": None, "query_data_type": None,
                           "query_data_value": None, "predicate_type": None, "action_type": "REMOVE", "data_type": "DIRECTORY", "source": source_dir,
                           "destination": None}

        # create the run handler
        rule_handler = RuleHandler()

        # convert the dict into a rule
        rule: RuleUtils.Rule = RuleUtils.convert_to_enum_types(test_rule)

        # apply the rules to the data, get back some stats
        process_stats: dict = rule_handler.process_rule(rule)

        # interrogate the result
        assert process_stats['removed'] == 1 and process_stats["failed"] == 0

        # interrogate the result
        assert not os.path.exists(source_dir)


def run_rule(test_rule):
    """

    :param test_rule:
    :return:
    """
    # convert the dict into a rule
    rule: RuleUtils.Rule = RuleUtils.convert_to_enum_types(test_rule)

    # create the run handler
    rule_handler = RuleHandler()

    # apply the rules to the data, get back some stats
    process_stats: dict = rule_handler.process_rule(rule)

    # return to the caller
    return process_stats
