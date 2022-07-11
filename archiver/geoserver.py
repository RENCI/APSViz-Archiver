

class GeoserverTools:
    """
    Class supports archival functionality for this data type

    """
    def __init__(self, logger):
        """
        Initializes this class

        """
        self.logger = logger

    def get_data(self) -> dict:
        """
        Gets the data records

        """
        ret_val: dict = {}

        # TODO: get the data

        # TODO: convert the NCEP identifier to an actual date/time for filtering

        self.logger('log event')

        return ret_val

    def get_rules(self) -> dict:
        """
        Gets the data archival rules

        """
        ret_val: dict = {}

        # TODO: get the rules

        self.logger('log event')

        return ret_val

    def remove_data(self, record_id: str) -> list:
        """
        Gets the data archival rules

        """
        ret_val: list = []

        # TODO: remove data

        self.logger('log event')

        return ret_val
