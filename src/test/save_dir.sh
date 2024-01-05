# SPDX-FileCopyrightText: 2024 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

#/bin/bash
now=$(date +"%m-%d-%Y")               
ls -halt /data/logs >> log_dir_list_$now.txt
