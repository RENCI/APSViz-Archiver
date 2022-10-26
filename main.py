# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Main entry point for the APSViz data archiver.

    Author: Phil Owen, 10/19/2022
"""

from src.archiver.archiver import APSVizArchiver

# create the archiver
# '../../test/test_files/test_rules.json', '../../test/test_files/test_all_rules.json',
archiver = APSVizArchiver('../../test/test_files/test_rules.json,../../test/test_files/test_all_rules.json')

# initiate the archiver
retval: str = archiver.run()
