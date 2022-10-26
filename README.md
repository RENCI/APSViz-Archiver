<!--
SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.

SPDX-License-Identifier: GPL-3.0-or-later
SPDX-License-Identifier: LicenseRef-RENCI
SPDX-License-Identifier: MIT
-->
![image not found](renci-logo.png "RENCI")

# APSViz-Archiver
Archives file created by the various APSViz applications and processes.

#### Licenses...
[![MIT License](https://img.shields.io/badge/License-MIT-red.svg)](https://github.com/RENCI/APSVIZ-Supervisor/blob/master/LICENSE)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![RENCI License](https://img.shields.io/badge/License-RENCI-blue.svg)](https://renci.org/)
#### Components and versions...
[![Python](https://img.shields.io/badge/Python-3.10.8-orange)](https://github.com/PyCQA/pylint)
[![Linting Pylint](https://img.shields.io/badge/Pylint-%202.15.5-yellowgreen)](https://github.com/PyCQA/pylint)
[![Pytest](https://img.shields.io/badge/Pytest-%207.2.0-yellowgreen)](https://github.com/pytest-dev/pytest)
#### Status...
[![Pylint and Pytest](https://github.com/RENCI/APSVIZ-Archiver/actions/workflows/pylint-test.yml/badge.svg)](https://github.com/RENCI/APSVIZ-Archiver/actions/workflows/pylint-test.yml)
[![Build and push the Docker image](https://github.com/RENCI/APSVIZ-Archiver/actions/workflows/image-push.yml/badge.svg)](https://github.com/RENCI/APSVIZ-Archiver/actions/workflows/image-push.yml)

## Description
This product is designed to perform copy/move/remove operations on file or directory entities within a Kubernetes CronJob. Additional functionality 
is implemented to sweep through all file/directory entities located within a directory.

This product is rule based./ Each Rule is defined in file in json format. A Rule can contain 1 or more Rule sets which can in turn specify 
1 or more atomic Rule operations. 
 
Atomic rules can optionally specify query criteria (age, etc.) that is paired with a predicate (equals, greater than, etc.). These query criteria are used to 
interrogate an entity prior to performing an operation.

A simple Rule example shown below has specified:
 - A Rule definition with details including a name, version and a description.
 - 1 Rule set that contains atomic Rules.
 - 2 atomic Rules for copy and move operations
 - With each atomic Rule specifying optional query criteria that will act on files older than (or equal to) 30 days.

```
{
  "rule_definition_name": "APSViz data archival rule set.",
  "rule_definition_version": "0.0.0",
  "description": "Tests a complete rule.",
  "rule_sets":
  [
    {
      "rule_set_name": "Test complete rule set 1",
      "description": "tests a complete rule by making a move request",
      "rules": [
        {
          "name": "Test - Copy Test file",
          "description": "This test Copies a file from source to destination.",
          "query_criteria_type": "BY_AGE",
          "query_data_type": "INTEGER",
          "query_data_value": 30,
          "predicate_type": "GREATER_THAN_OR_EQUAL_TO",
          "action_type": "COPY",
          "data_type": "FILE",
          "source": "/source/some-data-file.ext",
          "destination": "/dest/some-new-data-location"
        },
        {
          "name": "Test - Move Test file",
          "description": "This test moves a file from source to destination.",
          "query_criteria_type": "BY_AGE",
          "query_data_type": "INTEGER",
          "query_data_value": 30,
          "predicate_type": "GREATER_THAN_OR_EQUAL_TO",
          "action_type": "MOVE",
          "data_type": "FILE",
          "source": "/dest/some-new-data-location/some-data-file.ext",
          "destination": "/dest/some-newer-data-location"
        }
      ]
    }
  ]
}
```

There are GitHub actions to manage the code in this repo:
 - Pylint (minimum score of 9.5 to pass),
 - Pytest (with code coverage),
 - Build/publish a Docker image.

Helm/k8s charts for this product are available at: [APSViz-Helm](https://github.com/RENCI/apsviz-helm/tree/main/apsviz-archiver).
