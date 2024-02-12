# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2024 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    GeoServer Utils - Various utilities for GeoServer interactions.

    Author: Phil Owen, 2/16/2023
"""
import os
import glob
from pathlib import Path
from stat import S_ISDIR
import requests

from src.common.logger import LoggingUtil
from src.common.pg_impl import PGImplementation
from src.common.rule_utils import RuleUtils
from src.common.rule_enums import ActionType
from src.common.general_utils import GeneralUtils
from src.common.tds_utils import TDSUtils


class GeoServerUtils:
    """
    Class that encapsulates GeoServer operations.

    The process involves identifying candidates for archival (age) and synchronizes data removal across a number of systems (databases and the
    geoserver indexes).

    The geoserver operations start with discovering the data directories on the geoserver file system that meet rule criteria (age). The Directory
    name contains the "instance_id" which is used as a key to identify target data in other systems (database records and geoserver images).
    """

    def __init__(self, _logger=None):
        """
        Initializes this class

        """
        # if this is a reference to a logger passed in use it
        if _logger is not None:
            # get a handle to a logger
            self.logger = _logger
        else:
            # get the log level and directory from the environment.
            log_level, log_path = LoggingUtil.prep_for_logging()

            # create a logger
            self.logger = LoggingUtil.init_logging("APSVIZ.Archiver.GeoServerUtils", level=log_level, line_format='medium', log_file_path=log_path)

        # specify the DBs to gain connectivity to
        db_names: tuple = ('apsviz', 'adcirc_obs')

        # create a DB connection object
        self.db_info = PGImplementation(db_names, self.logger)

        # load environment variables
        self.username = os.getenv('GEOSERVER_USER')
        self.password = os.environ.get('GEOSERVER_PASSWORD')
        self.geoserver_url = os.environ.get('GEOSERVER_URL')
        self.geoserver_workspace = os.environ.get('GEOSERVER_WORKSPACE')
        self.geoserver_proj_path = os.environ.get('GEOSERVER_PROJ_PATH')
        self.fileserver_obs_path = os.environ.get('FILESERVER_OBS_PATH')

        # get the full path to the geoserver data directory
        self.full_geoserver_data_path = os.path.join(self.geoserver_proj_path, self.geoserver_workspace)

        # get a handle to the rule utils
        self.rule_utils = RuleUtils(self.logger)

        # create the general utilities class
        self.general_utils = GeneralUtils(self.logger)

        # create a TDS utilities class
        self.tds_utils = TDSUtils()

        # init some storage for the run names
        self.run_names: set = set()

    def process_geoserver_rule(self, stats: dict, rule: RuleUtils.Rule) -> (bool, dict):
        """
        Does the action specify (copy, move, remove) for the file system, DB and geoserver data for a run.

        Note that:
            The GEOSERVER_COPY action only copies data file directories to another location. DB and GeoServer records are not touched.
            The GEOSERVER_MOVE action moves data file directories to another location as well as updating DB and GeoServer records.
            The GEOSERVER_REMOVE action removes data file directories as well as DB and GeoServer records.

        The base data directory is defined in the EDS secrets GEOSERVER_PROJ_PATH and GEOSERVER_WORKSPACE
        and is usually located at "/opt/geoserver/data_dir/data/<catalog>>/<data directories>". The names of the directories are used to as
        instance ids which can be used to target DB and GeoServer records.

        Here is the full set of operations that can be performed on each instance id:
            1. remove the obs/mod records from the station table in the adcirc_obs DB.
            2. remove the image.* records from the run properties table in the apsviz DB.
            3. remove the catalog member records from the apsviz DB.
            4. copy, move or remove the geoserver files from the data directory (e.g. <base dir>/4362-2023030112-gfsforecast*).
            5. copy, move or remove the obs/mod files from the file server (/fileserver/obs_png/4362-2023030112-gfsforecast).
            6: remove the coverage/data stores for each product in the geoserver

        :return:
        """
        # init the success flag
        success: bool = True

        # get the stat action type for this rule
        if rule.action_type == ActionType.GEOSERVER_COPY:
            rule_action_type_name = 'copied'
        elif rule.action_type == ActionType.GEOSERVER_MOVE:
            rule_action_type_name = 'moved'
        elif rule.action_type == ActionType.GEOSERVER_REMOVE:
            rule_action_type_name = 'removed'
        else:
            # invalid action type, abort
            success = False

            # handle the run stats
            stats['failed'] += 1

            # return to the caller
            return success, stats

        # get the list of directory names found on the geoserver.
        # these are also considered to be instance ids without a product type.
        instance_ids: set = self.get_geoserver_entities_from_dir(rule)

        try:
            # create a list of functions to call to perform DB and directory operations
            operations: list = [self.perform_obs_mod_db_ops, self.perform_apsviz_db_ops, self.perform_catalog_db_ops, self.perform_dir_ops,
                                self.perform_tds_dir_ops]

            # for each entity
            for instance_id in instance_ids:
                self.logger.info('Geoserver ops operating on run %s.', instance_id)

                # for each operation to perform
                for operation in operations:
                    self.logger.debug('Running %s on %s', operation.__name__, instance_id)

                    # step 1: remove the obs/mod records from the adcirc_obs DB.
                    # step 2: remove the image.* records from the run properties DB.
                    # step 3. remove the catalog member records from the apsviz DB.
                    # step 4. copy, move or remove the files from the geoserver data directory.
                    # step 5. copy, move or remove the files from the obs/mod file directory.
                    # step 6. copy, move or remove the files from the TDS file directory.
                    if operation(rule, instance_id):
                        # handle the run stats
                        stats[rule_action_type_name] += 1
                    else:
                        self.logger.error('Error running %s on %s', operation.__name__, instance_id)

                        # handle the run stats
                        stats['failed'] += 1

                # step 6: remove the coverage/data stores for each product in the geoserver
                for store_type in ['coverageStores', 'dataStores']:
                    # get the filtered list of the stores by instance id. this id includes the product type
                    instance_id_products: list = self.get_geoserver_stores_like_instance_id(store_type, instance_id)

                    # for each instance (+ a product type) found
                    for instance_id_product in instance_id_products:
                        # remove the product from the geoserver
                        if self.perform_geoserver_store_ops(rule, store_type, instance_id_product):
                            self.logger.debug('Removed the %s for: %s', store_type, instance_id_product)

                            # handle the run stats
                            stats[rule_action_type_name] += 1
                        else:
                            self.logger.error('Error removing the %s for: %s', store_type, instance_id_product)

                            # handle the run stats
                            stats['failed'] += 1

                # if we got this far, it ran to a successful completion
                stats['swept'] += 1

        except Exception:
            self.logger.exception('Exception: Failed to process the geoserver rule.')

            # set the failure flag
            success = False

        # return to the caller
        return success, stats

    def create_geoserver_store(self, store_type: str, instance_id: str) -> bool:
        """
        Adds a GeoServer store for the store type and instance id pas
        :param store_type:
        :param instance_id:
        :return:
        """
        # init the success flag
        success: bool = True

        try:
            # # build the URL to the service
            # url = f'{self.geoserver_url}/rest/workspaces/{self.geoserver_workspace}/coveragestores'
            #
            # # create the config body
            # store_config = json.loads('{"coverageStore": {"name": "' + coverage_store_name + '", "workspace": "' + self.geoserver_workspace + '"}}')
            # store_config: dict = {
            #     'coverageStore': {'name': instance_id, 'workspace': self.geoserver_workspace,
            #                       'url': 'file:data/{geoserver_workspace}/test_coverage_store',
            #                       'type': 'imagemosaic'}}

            geoserver_workspace: str = os.environ.get('GEOSERVER_WORKSPACE', 'ADCIRC_2024')

            # build the URL to the service
            url = f'{self.geoserver_url}/rest/workspaces/{self.geoserver_workspace}/{store_type.lower()}'

            # create the config request
            store_config: dict = {
                store_type[:-1]: {'name': instance_id, 'workspace': self.geoserver_workspace, 'url': f'file:data/{geoserver_workspace}/{instance_id}',
                                  'type': 'imagemosaic'}}

            # execute the post
            ret_val = requests.post(url, auth=(self.username, self.password), json=store_config, timeout=10)

            # was the call unsuccessful? 201 is returned for success for this one
            if ret_val.status_code != 201:
                # log the error
                self.logger.error('Error %s when creating %s: "%s".', ret_val.status_code, store_type, instance_id)

                # set the failure flag
                success = False

        except Exception:
            # log the error
            self.logger.exception('Exception when creating %s for "%s"', store_type, instance_id)

            # set the failure code
            success = False

        # return pass/fail
        return success

    def get_geoserver_store(self, store_type: str, instance_id: str) -> list:
        """
        Get a geoserver store by store type and instance id

        note: url is all lowercase and plural

        :param store_type:
        :param instance_id:
        :return:
        """
        # init the return value
        ret_val: list = []

        try:
            # build the URL to the service
            url = f'{self.geoserver_url}/rest/workspaces/{self.geoserver_workspace}/{store_type.lower()}/{instance_id}'

            # execute the get
            result_val = requests.get(url, auth=(self.username, self.password), timeout=10)

            # was the call unsuccessful?
            if result_val.status_code != 200:
                # log the error
                self.logger.error('Error %s when getting coverage store "%s"', result_val.status_code, instance_id)

                # return an empty list
                ret_val = []
            # get the return in the correct format
            else:
                # save the result
                ret_val = result_val.json()

        except Exception:
            self.logger.exception('Exception getting %s store "%s"', store_type, instance_id)

        # return the json to the caller
        return ret_val

    def get_geoserver_stores_like_instance_id(self, store_type: str, instance_id: str = None) -> list:
        """
        Get all the coverage stores inside a <store type> workspace

        note:
            - valid store types are coverageStores and dataStores
            - the url store type is all lowercase
            - keys in the response data array are [store type][singular store type]

        :param store_type:
        :param instance_id:
        :return:
        """
        # init the return value
        ret_val: list = []

        try:
            # build the URL to the service
            url = f'{self.geoserver_url}/rest/workspaces/{self.geoserver_workspace}/{store_type.lower()}'

            # execute the get
            response: requests.Response = requests.get(url, auth=(self.username, self.password), timeout=10)

            # was the call unsuccessful?
            if response.status_code != 200:
                # log the error
                self.logger.error('Error %s gathering all geoserver %s stores.', response.status_code, store_type)

                # set the failure flag
                ret_val = []
            # get the return in the correct format
            else:
                # get the json from the return
                result_val: dict = response.json()

                # get the root of the stores
                store: dict = result_val.get(store_type)

                # get the array of stores
                stores: list = store.get(store_type[:-1])

                # only return the matches if there was a search criteria
                if instance_id is not None:
                    # save all the coverage store names that meet filter criteria
                    ret_val = [x['name'] for x in stores if x['name'].startswith(instance_id)]
                else:
                    ret_val = stores

        except Exception:
            self.logger.exception('Exception gathering all geoserver %s stores', store_type)

            # set the failure flag
            ret_val = []

        # return the json to the caller
        return ret_val

    def get_geoserver_entities_from_dir(self, rule: RuleUtils.Rule) -> set:
        """
        Method to collect and return the run names from the data file path that meet criteria.

        :param rule:
        :return:
        """
        # init the return
        ret_val: set = set()

        # get a listing of the contents in the geoserver data directory
        entities = glob.glob(os.path.join(self.full_geoserver_data_path, '*'))

        # loop through the director names and validate
        for entity in entities:
            # get the details of the entity
            entity_details = os.stat(entity)

            # make sure the entity still exists and is a directory
            if not os.path.exists(entity) or not S_ISDIR(entity_details.st_mode):
                continue

            # does the entity meet criteria?
            if self.rule_utils.meets_criteria(rule, entity_details):
                # get the full instance id
                full_instance_id: str = Path(entity).parts[-1]

                # get the base part of the instance id
                instance_id: str = full_instance_id.split('_')[0]

                # is this a tropical run?
                if self.db_info.is_tropical_run(instance_id):
                    self.logger.info('Warning: %s was detected to be a tropical run. No processing will occur on this item.', instance_id)
                else:
                    # add this entity to the list of instances to process
                    ret_val.add(instance_id)

        # return to the caller
        return ret_val

    def perform_tds_dir_ops(self, rule: RuleUtils.Rule, instance_id: str) -> bool:
        """
        performs the TDS directory ops

        :param rule:
        :param instance_id:
        :return:
        """
        # init the success flag
        success: bool = True

        # check the instance id
        if instance_id and len(instance_id) > 5:
            # only remove operations are supported
            if rule.action_type == ActionType.GEOSERVER_REMOVE:
                self.logger.debug('Executing perform_tds_dir_ops( %s )', instance_id)

                # if we are not in debug mode
                if not rule.debug:
                    # remove the records
                    success = self.tds_utils.remove_dirs(instance_id)
                else:
                    self.logger.debug('Debug mode on. Would have executed perform_tds_dir_ops( %s )', instance_id)
            else:
                # log the error
                self.logger.warning('Warning - perform_tds_dir_ops(): Only remove operations are supported in perform_tds_dir_ops()')

                # set the failure flag
                success = False
        else:
            # log the error
            self.logger.error('Error - perform_tds_dir_ops(): Invalid instance ID: %s', instance_id)

        # return to the caller
        return success

    def perform_dir_ops(self, rule: RuleUtils.Rule, instance_id: str) -> bool:
        """
        performs the directory ops

        :param rule:
        :param instance_id:
        :return:
        """
        # init the success flag
        success: bool = True

        # get the obs/mod directory path
        obs_mod_dir = os.path.join(self.fileserver_obs_path, instance_id)

        # get the geo server directory path
        geo_svr_dir = os.path.join(self.full_geoserver_data_path, f"{instance_id}*")

        # execute the call if not in debug mode
        if not rule.debug:
            # make sure the entity still exists
            if not os.path.exists(obs_mod_dir):
                success = False
                self.logger.error('OBS/MOD (%s) directory not found.', obs_mod_dir)
            else:
                # get a listing of the dirs associated to this instance id
                entities = glob.glob(geo_svr_dir)

                # if the directory wasn't found
                if len(entities) == 0:
                    self.logger.debug('No directory entities found in %s', geo_svr_dir)

                    # set the error flag
                    success = False
                else:
                    # do the directory operation based on the rule action type
                    if rule.action_type == ActionType.GEOSERVER_COPY:
                        # eventually, use the target dir as specified in the rule.
                        # specifically, a directory specifying the /<instance id>/<data type> will be the final target
                        new_dest: str = os.path.join(rule.destination, instance_id)

                        # process the geoserver directories
                        for entity in entities:
                            success = success and self.rule_utils.copy_directory(rule, entity, os.path.join(new_dest, 'obsmod'))

                        # process the obs/mod directory
                        success = success and self.rule_utils.copy_directory(rule, obs_mod_dir, new_dest)
                    elif rule.action_type == ActionType.GEOSERVER_MOVE:
                        # eventually use real target dir here too?
                        new_dest: str = ''

                        # process the geoserver directories
                        for entity in entities:
                            success = success and self.rule_utils.move_directory(rule, entity, new_dest)

                        # process the obs/mod directory
                        success = success and self.rule_utils.move_directory(rule, obs_mod_dir, new_dest)
                    elif rule.action_type == ActionType.GEOSERVER_REMOVE:
                        self.logger.debug('Executing perform_dir_ops( %s )', instance_id)

                        # process the geoserver directories
                        for entity in entities:
                            success = success and self.rule_utils.remove_directory(rule, entity)

                        # process the obs/mod directory
                        success = success and self.rule_utils.remove_directory(rule, obs_mod_dir)

                # check the return
                if not success:
                    self.logger.error('General error: perform_dir_ops( %s ) with %s on %s and %s', instance_id, rule.action_type, obs_mod_dir,
                                      geo_svr_dir)
        else:
            self.logger.debug('Debug mode on. Would have executed: perform_dir_ops( %s ) with %s on %s and %s', instance_id, rule.action_type,
                              obs_mod_dir, geo_svr_dir)

        # return to the caller
        return success

    def perform_apsviz_db_ops(self, rule: RuleUtils.Rule, instance_id) -> (bool, object):
        """
        removes the apsviz DB image.* run prop records associated to the run name

        :param rule:
        :param instance_id:
        :return:
        """
        # init the success flag
        success: bool = True

        # only remove operations are supported
        if rule.action_type == ActionType.GEOSERVER_REMOVE:
            self.logger.debug('Executing perform_apsviz_db_ops( %s )', instance_id)

            # execute the call if not in debug mode
            if not rule.debug:
                # remove the records
                success = self.db_info.remove_run_props_db_image_records(instance_id)
            else:
                self.logger.debug('Debug mode on. Would have executed perform_apsviz_db_ops( %s )', instance_id)
        else:
            # log the error
            self.logger.warning('Warning: Only remove operations are supported in perform_apsviz_db_ops()')

            # set the failure flag
            success = False

        # return the json to the caller
        return success

    def perform_catalog_db_ops(self, rule, instance_id) -> (bool, object):
        """
        removes the catalog member apsviz DB records associated to the run name

        :param rule:        
        :param instance_id:

        :return:
        """
        # init the success flag
        success: bool = True

        # check the instance id
        if instance_id and len(instance_id) > 5:
            # only remove operations are supported
            if rule.action_type == ActionType.GEOSERVER_REMOVE:
                self.logger.debug('Executing perform_catalog_db_ops( %s )', instance_id)

                # if we are not in debug mode
                if not rule.debug:
                    # remove the records
                    success = self.db_info.remove_catalog_db_records(instance_id + '%')
                else:
                    self.logger.debug('Debug mode on. Would have executed perform_catalog_db_ops( %s )', instance_id)
            else:
                # log the error
                self.logger.warning('Warning - perform_catalog_db_ops(): Only remove operations are supported in perform_catalog_db_ops()')

                # set the failure flag
                success = False
        else:
            # log the error
            self.logger.error('Error - perform_catalog_db_ops(): Invalid instance ID: %s', instance_id)

        # return the json to the caller
        return success

    def perform_geoserver_store_ops(self, rule, store_type: str, instance_id: str) -> bool:
        """
        Removes a GeoServer store

        note: valid store types are coverageStores and dataStores

        :param rule:

        :param store_type:
        :param instance_id:
        :return:
        """
        # init the success flag
        success: bool = True

        # only remove operations are supported
        if rule.action_type == ActionType.GEOSERVER_REMOVE:
            self.logger.debug('Executing perform_geoserver_store_ops( %s )', instance_id)

            try:
                # build the URL to the service. we want a recursive deletion of everything here
                url = f'{self.geoserver_url}/rest/workspaces/{self.geoserver_workspace}/{store_type.lower()}/{instance_id}?recurse=true'

                # execute the call if not in debug mode and is a remove operation
                if not rule.debug:
                    # execute the delete
                    ret_val = requests.delete(url, auth=(self.username, self.password), timeout=60)

                    # the coverage store wasn't found
                    if ret_val.status_code == 404:
                        # log the error
                        self.logger.warning('Warning %s for %s not found.', store_type, instance_id)
                    # else some type of fatal error
                    elif ret_val.status_code != 200:
                        # log the error
                        self.logger.error('Error %s when removing % for "%s".', ret_val.status_code, store_type, instance_id)

                        # set the failure flag
                        success = False
                else:
                    self.logger.debug('Debug mode on. Would have executed: perform_geoserver_store_ops( %s, %s )', store_type, instance_id)
            except Exception:
                # log the error
                self.logger.exception('Exception when performing on store %s for "%s"', store_type, instance_id)

                # set the failure code
                success = False
        else:
            # log the error
            self.logger.warning('Warning: Only remove operations are supported in perform_geoserver_store_ops()')

            # set the failure flag
            success = False

        # return pass/fail
        return success

    def perform_obs_mod_db_ops(self, rule: RuleUtils.Rule, instance_id: str) -> (bool, object):
        """
        removes the obs/mod adcirc_obs DB records associated to the run name

        :param rule:
        :param instance_id:
        :return:
        """
        # init the success flag
        success: bool = True

        # only remove operations are supported
        if rule.action_type == ActionType.GEOSERVER_REMOVE:
            self.logger.debug('Executing perform_obs_mod_db_ops( %s )', instance_id)

            # execute the call if not in debug mode
            if not rule.debug:
                # remove the records
                success = self.db_info.remove_obs_mod_db_records(instance_id)
            else:
                self.logger.debug('Debug mode on. Would have executed: perform_obs_mod_db_ops( %s )', instance_id)
        else:
            # log the error
            self.logger.warning('Warning: Only remove operations are supported in perform_obs_mod_db_ops()')

            # set the failure flag
            success = False

        # return the json to the caller
        return success
