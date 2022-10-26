# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    APSViz Archiver - Test all rule operations

    Author: Phil Owen, 10/23/2022
"""
import os.path
import json

from common_funcs import input_path, output_path
from src.archiver.archiver import APSVizArchiver


def test_complete_rule():
    """
    test a complete rule

    :return:
    """

    # load the test json file
    # open the file
    with open(os.path.join(os.path.dirname(__file__), 'test_files/test_complete_rule.json'), encoding='UTF-8') as rules_fh:
        # load the json
        rule_set = json.loads(rules_fh.read())

    # specify the new directories
    source = os.path.join(input_path, 'test_files', 'test_file.txt')
    destination = os.path.join(output_path, 'dir1/')

    # modify the directories to use the test input/output directories
    rule_set['rule_sets'][0]['rules'][0]['source'] = source
    rule_set['rule_sets'][0]['rules'][0]['destination'] = destination

    # get the new file name
    new_file_name = os.path.join(os.path.dirname(__file__), 'test_files/new_complete_rule.json')

    # output the new json file
    with open(new_file_name, "w", encoding='UTF-8') as new_fh:
        json.dump(rule_set, new_fh)

    # create a new archiver
    archiver = APSVizArchiver(new_file_name)

    # launch it, check the result
    assert archiver.run()
