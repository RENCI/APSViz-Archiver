# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Main entry point for the APSViz data archiver.

    Author: Phil Owen, 10/19/2022
"""
import sys
import argparse
from src.archiver.archiver import APSVizArchiver


def run_rule_file(rule_file: str) -> bool:
    """
    Runs rule files. Input argument can be a singleton or a comma seperated list of file names

    :param rule_file
    :return:
    """

    # create the archiver
    archiver = APSVizArchiver(rule_file)

    # initiate the archiver. return value of True indicates success
    retval: bool = archiver.run()

    # return to the caller. invert the return for a proper sys exit code
    return not retval


if __name__ == '__main__':
    # main entry point for the rule run.
    # input argument can be a singleton or a comma seperated list

    # create a command line parser
    parser = argparse.ArgumentParser(description='help', formatter_class=argparse.RawDescriptionHelpFormatter)

    # assign the expected input arg
    parser.add_argument('-f', '--filename', help='Input can be a singleton or a comma seperated list of file names ')

    # parse the command line
    args = parser.parse_args()

    # example input
    # 'test/test_files/test_rules.json,test/test_files/test_all_rules.json'

    # execute the rule file(s)
    ret_val: bool = run_rule_file(args.filename)
    # ret_val: bool = run_rule_file('test/test_files/test_criteria.rules2.json')

    # exit with pass/fail
    sys.exit(ret_val)
