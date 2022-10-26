# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Various Enum classes that define constants used for rule definitions.

    Author: Phil Owen, 10/19/2022
"""

from enum import Enum


class QueryCriteriaType(int, Enum):
    """
    Enum Class that defines the rule query criteria
    """
    BY_AGE = 1
    # BY_NAME = 2
    # BY_SIZE = 3
    NONE = 99


class QueryDataType(int, Enum):
    """
    Enum Class that defines the rule query data types
    """
    INTEGER = 1
    STRING = 2
    NONE = 99


class PredicateType(int, Enum):
    """
    Enum Class that defines the rule predicate types
    """
    EQUALS = 1
    GREATER_THAN = 2
    GREATER_THAN_OR_EQUAL_TO = 3
    LESS_THAN = 4
    LESS_THAN_OR_EQUAL_TO = 5
    NONE = 99


class ActionType(int, Enum):
    """
    Enum Class that defines the rule action types
    """
    COPY = 1
    MOVE = 2
    REMOVE = 3
    WS_DB = 4
    SWEEP_MOVE = 5
    SWEEP_COPY = 6
    SWEEP_REMOVE = 7
    NONE = 99


class DataType(int, Enum):
    """
    Enum class that defines the data types
    """
    DIRECTORY = 1
    FILE = 2
    URL = 3
    NONE = 99
