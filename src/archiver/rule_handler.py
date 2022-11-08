# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Class RuleHandler - Utilities for running/interpreting data manipulation rules.

    Author: Phil Owen, 10/19/2022
"""

import os
import shutil

from stat import S_ISDIR
from collections import namedtuple
from src.common.rule_enums import ActionType, DataType
from src.common.general_utils import GeneralUtils
from src.common.rule_utils import RuleUtils
from src.common.logger import LoggingUtil


class RuleHandler:
    """
    Class that uses rules to manipulate data
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
            self.logger = LoggingUtil.init_logging("APSVIZ.Archiver.RuleHandler", level=log_level, line_format='medium', log_file_path=log_path)

        # create the rule utilities class
        self.rule_utils = RuleUtils(_logger)

        # create the general utilities class
        self.general_utils = GeneralUtils(_logger)

    def process_rule_set(self, rule_set: dict) -> dict:
        """
        works through all the rules defined in the rule set.

        :return:
        """

        # get the name of the rule set
        rule_set_name = rule_set['rule_set_name']

        self.logger.info("Rule set start. Name: %s", rule_set_name)

        # init the stat counts
        ret_val: dict = {'moved': 0, 'copied': 0, 'removed': 0, 'swept': 0, 'failed': 0}

        # for each rule in the rule set
        for rule in rule_set['rules']:
            # convert elements to their equivalent types
            the_rule: namedtuple = self.rule_utils.convert_to_enum_types(rule)

            # apply the rules to the data, get back some stats
            process_stats: dict = self.process_rule(the_rule)

            # update the rule set stats
            ret_val['moved'] += process_stats['moved']
            ret_val['copied'] += process_stats['copied']
            ret_val['removed'] += process_stats['removed']
            ret_val['swept'] += process_stats['swept']
            ret_val['failed'] += process_stats['failed']

        # return to the caller
        return ret_val

    def process_rule(self, rule: RuleUtils.Rule) -> dict:
        """
        Performs an action on the data specified in the rule

        :param rule:
        :return:
        """
        # init the status counts
        stats: dict = {'moved': 0, 'copied': 0, 'removed': 0, 'swept': 0, 'failed': 0, }

        self.logger.info("Rule start. Name: %s, action type: %s.", rule.name, rule.action_type)

        # confirm the expected input and output data are populated
        if self.rule_utils.validate_rule_data(rule):
            self.logger.debug('Rule data source: %s, dest: %s, data_type: %s.', rule.source, rule.destination, rule.data_type)

            # select the operation by based on the trigger type
            if rule.action_type == ActionType.MOVE:
                # run the action handler, get the result
                if self.move_data_action(rule):
                    stats['moved'] += 1
                else:
                    stats['failed'] += 1

            elif rule.action_type == ActionType.COPY:
                # run the action handler, get the result
                if self.copy_data_action(rule):
                    stats['copied'] += 1
                else:
                    stats['failed'] += 1

            elif rule.action_type == ActionType.REMOVE:
                # run the action handler, get the result
                if self.remove_data_action(rule):
                    stats['removed'] += 1
                else:
                    stats['failed'] += 1

            elif rule.action_type in (ActionType.SWEEP_COPY, ActionType.SWEEP_MOVE, ActionType.SWEEP_REMOVE):
                # run the action handler, get the result
                if self.sweep_action(rule):
                    stats['swept'] += 1
                else:
                    stats['failed'] += 1
            # unknown rule action type
            else:
                stats['failed'] += 1
                self.logger.error('Error: The rule "%s" with action type %s is invalid.', rule.name, rule.action_type.value)
        else:
            stats['failed'] += 1
            self.logger.error('Error: The rule "%s" data source was not the expected type or does not exist.', rule.name)

        # return the stats to the caller
        return stats

    def move_data_action(self, rule: RuleUtils.Rule) -> bool:
        """
        moves data from the source to destination

        Note the approach:
            when moving a directory if the dest exists, the source directory will be moved into the
            dest directory. else the source directory will be renamed to the dest directory.

        :param rule
        :return:
        """
        # init the return value
        ret_val = False

        # operate on a data directory
        if rule.data_type == DataType.DIRECTORY:
            # perform the directory move
            ret_val = self.rule_utils.move_directory(rule)

            # set the return value
            ret_val = True
        # operate on a data file
        elif rule.data_type == DataType.FILE:
            # perform the file move
            ret_val = self.rule_utils.move_file(rule)

            # set the return value
            ret_val = True
        else:
            self.logger.error('Error: Unrecognized move data type: %s during a move.', rule.data_type)

        # return to the caller
        return ret_val

    def copy_data_action(self, rule: RuleUtils.Rule) -> bool:
        """
        copies data from the source to destination

        :param rule:
        :return:
        """
        # init the return value
        ret_val: bool = False

        try:
            # operate on a data directory
            if rule.data_type == DataType.DIRECTORY:
                ret_val = self.rule_utils.copy_directory(rule)
            # operate on a data file
            elif rule.data_type == DataType.FILE:
                ret_val = self.rule_utils.copy_file(rule)

            # set the return value
            ret_val = True

        # report the exception
        except shutil.SameFileError:
            self.logger.exception('Source and destination represents the same file.')
        except PermissionError:
            self.logger.exception('Permission denied.')
        except Exception:
            self.logger.exception('General exception detected during copy.')

        # return to the caller
        return ret_val

    def remove_data_action(self, rule: RuleUtils.Rule) -> bool:
        """
        removes data from the source

        :param rule:
        :return:
        """
        # init the return value
        ret_val: bool = True

        try:
            # operate on a data directory
            if rule.data_type == DataType.DIRECTORY:
                self.rule_utils.remove_directory(rule)
            # operate on a data file
            elif rule.data_type == DataType.FILE:
                self.rule_utils.remove_file(rule)

        except Exception:
            # report the exception
            self.logger.exception('Exception detected during move.')

            # set the return value
            ret_val = False

        # return to the caller
        return ret_val

    def sweep_action(self, rule: RuleUtils.Rule) -> bool:
        """
        performs a sweep of a source directory. sweep operations include processing a directory

        :param rule:
        :return:
        """
        # init the return value
        ret_val: bool = True
        failed_met_criteria: int = 0

        # init the entity count
        entity_count = 0

        # check to see if execution params are populated
        validated = self.rule_utils.validate_criteria_definition(rule)

        # run the rule if it meets criteria
        if validated:
            # get a list of the contents of the source directory
            entities = os.listdir(rule.source)

            # for each item found
            for entity in entities:
                # save the path to the entity
                full_path = os.path.join(rule.source, entity)

                # make sure the entity still exists
                if not os.path.exists(full_path):
                    continue

                # get the details of the entity
                entity_details = os.stat(full_path)

                # if this is a directory operation perform the action type
                if rule.data_type == DataType.DIRECTORY and S_ISDIR(entity_details.st_mode):
                    # increment the count
                    entity_count += 1

                    # does the entity meet criteria
                    if self.rule_utils.meets_criteria(rule, entity_details):
                        if rule.action_type == ActionType.SWEEP_MOVE:
                            # move the directory
                            ret_val = self.rule_utils.move_directory(rule, entity)
                        elif rule.action_type == ActionType.SWEEP_COPY:
                            # move the directory
                            ret_val = self.rule_utils.copy_directory(rule, entity)
                        elif rule.action_type == ActionType.SWEEP_REMOVE:
                            # remove the directory
                            ret_val = self.rule_utils.remove_directory(rule, entity)
                    else:
                        self.logger.debug('%s data action %s: Entity %s failed to meet criteria in %s.', rule.data_type.name, rule.action_type.name,
                                          entity, rule.source)

                        # increment the failed criteria counter
                        failed_met_criteria += 1

                # if this is a file operation perform the action type
                elif rule.data_type == DataType.FILE and not S_ISDIR(entity_details.st_mode):
                    # increment the count
                    entity_count += 1

                    # does the entity meet criteria
                    if self.rule_utils.meets_criteria(rule, entity_details):
                        if rule.action_type == ActionType.SWEEP_MOVE:
                            # move the file
                            ret_val = self.rule_utils.move_file(rule, entity)
                        elif rule.action_type == ActionType.SWEEP_COPY:
                            # move the file
                            ret_val = self.rule_utils.copy_file(rule, entity)
                        elif rule.action_type == ActionType.SWEEP_REMOVE:
                            # remove the directory
                            ret_val = self.rule_utils.remove_file(rule, entity)
                    else:
                        self.logger.debug('%s data action %s: Entity %s failed to meet criteria in %s.', rule.data_type.name, rule.action_type.name,
                                          entity, rule.source)

                        # increment the failed criteria counter
                        failed_met_criteria += 1

        # if there were any that failed report the details
        if failed_met_criteria > 0:
            self.logger.debug("%s data action %s result: %s of %s entity(ies) failed to meet criteria.", rule.data_type.name, rule.action_type.name,
                              failed_met_criteria, entity_count)

        # return to the caller
        return ret_val
