# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Rule Utils - Various rule utilities common to this project's components.

    Author: Phil Owen, 10/20/2022
"""

import os
import shutil
import time

from collections import namedtuple
from src.common.rule_enums import DataType, QueryCriteriaType, PredicateType, ActionType, QueryDataType
from src.common.logger import LoggingUtil


class RuleUtils:
    """
    Utility methods used for rule based components in this project.
    """
    # define a named tuple where a rule can be housed
    Rule: namedtuple = namedtuple('Rule', ['name', 'description', 'query_criteria_type', 'query_data_type', 'query_data_value', 'predicate_type',
                                           'action_type', 'data_type', 'source', 'destination', 'debug'])

    """
    Rule utility methods used for components in this project.
    """

    def __init__(self, _logger=None):
        """
        Initializes this class

        """
        # if a reference to a logger passed in use it
        if _logger is not None:
            # get a handle to a logger
            self.logger = _logger
        else:
            # get the log level and directory from the environment.
            log_level, log_path = LoggingUtil.prep_for_logging()

            # create a logger
            self.logger = LoggingUtil.init_logging("APSVIZ.Archiver.RuleUtils", level=log_level, line_format='medium', log_file_path=log_path)

    def move_file(self, rule: Rule, opt_name: str = None) -> bool:
        """
        Moves the file from source to destination

        :param rule:
        :param opt_name:
        :return:
        """
        # init the return value
        ret_val: bool = False

        # init the final directory
        new_source = rule.source

        try:
            # create the destination directory if it doesn't exist
            if os.path.dirname(rule.destination) is not None and not os.path.exists(rule.destination) and not os.path.basename(rule.destination):
                # create the destination directory
                os.mkdir(rule.destination)

            # append the optional file name if exists
            if opt_name:
                new_source = os.path.join(rule.source, opt_name)

            # log the targets
            self.logger.debug('Source: %s, destination: %s', new_source, rule.destination)

            # preform the move
            shutil.move(new_source, rule.destination)

            # set the return value
            ret_val = True

        # report the exception
        except IsADirectoryError:
            self.logger.exception('Error: Source is a file but destination is a directory detected during a move.')
        except NotADirectoryError:
            self.logger.exception('Error: Source is a directory but destination is a file detected during a move.')
        except PermissionError:
            self.logger.exception('Error: Operation not permitted detected during a file move.')
        except FileNotFoundError:
            self.logger.exception('Error: Exception File not found detected during file a move.')
        except Exception:
            self.logger.exception('Error: General exception detected during a file move.')

        # return to the caller
        return ret_val

    def move_directory(self, rule_source: str, rule_destination: str, opt_name: str = None) -> bool:
        """
        Moves the directory from source to destination

        :param rule_source:
        :param rule_destination:
        :param opt_name:
        :return:
        """
        # init the return value
        ret_val: bool = False

        # init the final directories
        new_source = rule_source
        new_destination = rule_destination

        try:
            # is there more to this source sweep operation
            if opt_name:
                # append the sweep dir
                new_source = os.path.join(rule_source, opt_name)
                new_destination = os.path.join(rule_destination, opt_name)

            # log the targets
            self.logger.debug('Source: %s, destination: %s', new_source, new_destination)

            # if the path exists the source directory is moved to the dest
            # if os.path.exists(destination):
            shutil.move(new_source, new_destination)
            # else the source directory is renamed to the destination directory
            # else:
            #     os.rename(source, destination)

            # do we
            # set the return value
            ret_val = True

        # report the exception
        except IsADirectoryError:
            self.logger.exception('Error: Source is a file but destination is a directory detected during a move.')
        except NotADirectoryError:
            self.logger.exception('Error: Source is a directory but destination is a file detected during a move.')
        except PermissionError:
            self.logger.exception('Error: Operation not permitted detected during a move.')
        except FileNotFoundError:
            self.logger.exception('Error: Exception File not found detected during a move.')
        except Exception:
            self.logger.exception('Error: General exception detected during a move.')

        # return to the caller
        return ret_val

    def copy_file(self, rule: Rule, opt_name: str = None) -> bool:
        """
        copies a file from source to destination

        :param rule:
        :param opt_name:
        :return:
        """
        # init the return value
        ret_val: bool = False

        # init the final directory
        new_source = rule.source

        try:
            # create the destination directory if it doesn't exist
            if os.path.dirname(rule.destination) is not None and not os.path.exists(rule.destination) and not os.path.basename(rule.destination):
                # create the destination directory
                os.mkdir(rule.destination)

            # append the optional file name if exists
            if opt_name:
                new_source = os.path.join(rule.source, opt_name)

            # log the targets
            self.logger.debug('Source: %s, destination: %s', new_source, rule.destination)

            # perform the file copy operation
            shutil.copy(new_source, rule.destination)

            # set the return value
            ret_val = True

        except FileExistsError:
            self.logger.exception('Error: File %s already exists.', rule.destination)
        except Exception:
            self.logger.exception('Error: General exception detected during a file copy.')

        # return to the caller
        return ret_val

    def copy_directory(self, rule_source: str, rule_destination: str, opt_name: str = None) -> bool:
        """
        copies a directory from source to destination

        :param rule_source:
        :param rule_destination:
        :param opt_name:
        :return:
        """
        # init the return value
        ret_val: bool = False

        # init the final directories
        new_source = rule_source
        new_destination = rule_destination

        try:
            # is there more to this source sweep operation
            if opt_name:
                # append the sweep dir
                new_source = os.path.join(rule_source, opt_name)
                new_destination = os.path.join(rule_destination, opt_name)

            # log the targets
            self.logger.debug('Source: %s, destination: %s', new_source, new_destination)

            # copy the directory
            shutil.copytree(new_source, new_destination, dirs_exist_ok=True)

            # set the return value
            ret_val = True

        except FileNotFoundError:
            self.logger.exception('Error: Directory %s not found.', new_source)
        except FileExistsError:
            self.logger.exception('Error: Directory %s already exists.', new_destination)
        except Exception:
            self.logger.exception('Error: General exception detected during a directory copy.')

        # return to the caller
        return ret_val

    def remove_file(self, rule: Rule, opt_name: str = None) -> bool:
        """
        remove a file

        :param rule:
        :param opt_name:
        :return:
        """
        # init the return value
        ret_val: bool = False

        # init the final directory
        new_source = rule.source

        try:
            # append the optional file name if exists
            if opt_name:
                new_source = os.path.join(rule.source, opt_name)

            # log the targets
            self.logger.debug('Source: %s', new_source)

            # perform the file operation
            os.remove(new_source)

            # set the return value
            ret_val = True

        except Exception:
            self.logger.exception('Error: General exception detected during a directory remove.')

        # return to the caller
        return ret_val

    def remove_directory(self, rule_source: str, opt_name: str = None) -> bool:
        """
        remove a directory

        :param rule_source:
        :param opt_name:
        :return:
        """
        # init the return value
        ret_val: bool = False

        # init the final directory
        new_source = rule_source

        try:
            # append the optional file name if exists
            if opt_name:
                new_source = os.path.join(rule_source, opt_name)

            # log the targets
            self.logger.debug('Source: %s', new_source)

            # perform the directory removal operation
            shutil.rmtree(new_source)

            # set the return value
            ret_val = True

        except Exception:
            self.logger.exception('Error: General exception detected during a file directory remove.')

        # return to the caller
        return ret_val

    def validate_criteria_definition(self, rule: Rule) -> bool:
        """
        Checks to see if the rule has the appropriate criteria elements

        :param rule:
        :return:
        """
        # init the return value
        ret_val: bool = False

        # no criteria pass through
        if rule.query_criteria_type == QueryCriteriaType.NONE:
            ret_val = True
        # by age needs the data type and predicate type verified
        elif rule.query_criteria_type == QueryCriteriaType.BY_AGE:
            # make sure all the data exists
            if rule.query_data_type and rule.predicate_type:
                ret_val = True
        else:
            self.logger.error('Error: Invalid query criteria.')

        # if this is a sweep operation ensure that the source directory exists
        if rule.action_type in [ActionType.SWEEP_COPY, ActionType.SWEEP_REMOVE, ActionType.SWEEP_MOVE]:
            # warn if the source doesn't exist
            if not os.path.exists(rule.source):
                self.logger.warning('Warning: Source directory doesnt exist for sweep operation.')
                ret_val = False

        # return to the caller
        return ret_val

    def check_by_age(self, rule: Rule, entity_details: namedtuple):
        """
        Checks to see if the rule data meets the data age criteria

        :param rule:
        :param entity_details:
        :return:
        """
        # init the return value
        ret_val: bool = False

        # get the age of the entity and convert to days
        current_age = int((time.time() - entity_details.st_ctime) / 86400)

        # the data value for age is in days
        target_age = rule.query_data_value

        # log the targets
        self.logger.debug('Source: %s, destination: %s, current age: %s, target age: %s, predicate: %s', rule.source, rule.destination, current_age,
                          target_age, rule.predicate_type)

        # make the EQUALS comparison
        if rule.predicate_type == PredicateType.EQUALS:
            # compare the age vs. the age to trigger the rule
            if current_age == target_age:
                ret_val = True
        # make the GREATER_THAN comparison
        elif rule.predicate_type == PredicateType.GREATER_THAN:
            # compare the age vs. the age to trigger the rule
            if current_age > target_age:
                ret_val = True
        # make the GREATER_THAN_OR_EQUAL_TO comparison
        elif rule.predicate_type == PredicateType.GREATER_THAN_OR_EQUAL_TO:
            # compare the age vs. the age to trigger the rule
            if current_age >= target_age:
                ret_val = True
        # make the LESS_THAN comparison
        elif rule.predicate_type == PredicateType.LESS_THAN:
            # compare the age vs. the age to trigger the rule
            if current_age < target_age:
                ret_val = True
        # make the LESS_THAN_OR_EQUAL_TO comparison
        elif rule.predicate_type == PredicateType.LESS_THAN_OR_EQUAL_TO:
            # compare the age vs. the age to trigger the rule
            if current_age <= target_age:
                ret_val = True
        else:
            self.logger.error("Error: Unspecified predicate type.")

        self.logger.info("%s - Source: %s, destination: %s, current age: %s, target age: %s, predicate: %s", 'Success' if ret_val else 'Failed.',
                         rule.source, rule.destination, current_age, target_age, rule.predicate_type)

        # return to the caller
        return ret_val

    def meets_criteria(self, rule: Rule, entity_details: namedtuple) -> bool:
        """
        determines if the details of the entity meets criteria so the rule can execute

        :param rule:
        :param entity_details:
        :return:
        """
        # init the return value
        ret_val: bool = False

        # if this is a by age criteria
        if rule.query_criteria_type == QueryCriteriaType.BY_AGE:
            # check the data by age
            ret_val = self.check_by_age(rule, entity_details)

        # return to the caller
        return ret_val

    def validate_and_convert_to_rule(self, rule: dict) -> namedtuple:
        """
        Validates and converts json rule elements to a Rule named tuple.

        :return:
        """
        # init the return value
        the_rule: namedtuple = None

        # flag to indicate success
        success = True

        try:
            # ensure that all elements are in the data
            for item in self.Rule._fields:
                # if the element was not found
                if item not in rule:
                    self.logger.error('Error: Rule element %s not found in rule definition.', item)

                    # set the failure flag
                    success = False

                    # no need to continue
                    break

            # if things are ok so far
            if success:
                # convert values that are enum types
                rule['query_criteria_type'] = QueryCriteriaType[rule['query_criteria_type']] \
                    if rule['query_criteria_type'] is not None else QueryCriteriaType.NONE
                rule['query_data_type'] = QueryDataType[rule['query_data_type']] if rule['query_data_type'] is not None else QueryDataType.NONE
                rule['predicate_type'] = PredicateType[rule['predicate_type']] if rule['predicate_type'] is not None else PredicateType.NONE
                rule['action_type'] = ActionType[rule['action_type']] if rule['action_type'] is not None else ActionType.NONE
                rule['data_type'] = DataType[rule['data_type']] if rule['data_type'] is not None else DataType.NONE

                # convert rule to a named tuple
                the_rule = RuleUtils.Rule(**rule)

                # continue to check for more rule conformance
                if success:
                    # reset the success flag for the next validation
                    success = False

                    # validate the data exists and matches the expected type
                    if the_rule.data_type == DataType.FILE and os.path.isfile(the_rule.source):
                        # everything os ok so far
                        success = True
                    elif the_rule.data_type == DataType.DIRECTORY and not os.path.isfile(the_rule.source):
                        # everything is ok so far
                        success = True
                    elif the_rule.action_type in [ActionType.SWEEP_COPY, ActionType.SWEEP_MOVE, ActionType.SWEEP_REMOVE] and not os.path.isfile(
                            the_rule.source):
                        success = True
                    elif the_rule.action_type in [ActionType.GEOSERVER_COPY, ActionType.GEOSERVER_MOVE, ActionType.GEOSERVER_REMOVE]:
                        success = True

                    else:
                        self.logger.error('Error: Rule data missing or does not match the expected type.')

        except Exception:
            self.logger.exception('Exception validating or converting rule input')

            # set the failure flag
            success = False

        # return to the caller
        return the_rule if success else None
