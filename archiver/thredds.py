# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

class ThreddsTools:
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
