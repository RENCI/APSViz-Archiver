from enum import Enum


class RuleSource(int, Enum):
    """
    Class that defines the rule source types
    """
    GeoServer = 1
    THREDDS = 2

class RuleClass(int, Enum):
    """
    Class that defines the rule class types
    """
    critical = 1
    routine = 2
    transient = 3

class RuleElementLocation(str, Enum):
    """
    Class that defines the rule element types
    """
    ncep_id = ''


class RuleDataType(int, Enum):
    """
    Class that defines the rule data types
    """
    string = 1
    integer = 2
    date_time = 3


class RuleTrigger(int, Enum):
    """
    Class that defines the rule trigger types
    """
    age = 1
    data_type = 2


class RuleAction(int, Enum):
    """
    Class that defines the rule action types
    """
    move_to_cold = 1
    delete = 2


class RuleHandler:
    """
    Class that uses rules to archive data
    """
    def __init__(self, logger):
        """
        Initializes this class

        """
        self.logger = logger

    @staticmethod
    def execute_rules(data_handler) -> list:
        """
        Gets data and archival rules and execute them.

        :return:
        """
        # TODO: add try/except logic

        # init the results of the application of rules on the data
        ret_val: list = []

        # get the records to process
        data: dict = data_handler.get_data()

        # get the rules
        rules: dict = data_handler.get_rules()

        # TODO: apply the rules to the data

        data_name = data_handler['data_name']

        ret_val = [f'Total {data_name} records, records removed {0}']

        return ret_val
