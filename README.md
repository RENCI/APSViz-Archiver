<!--
SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
SPDX-FileCopyrightText: 2024 Renaissance Computing Institute. All rights reserved.

SPDX-License-Identifier: GPL-3.0-or-later
SPDX-License-Identifier: LicenseRef-RENCI
SPDX-License-Identifier: MIT
-->

![image not found](renci-logo.png "RENCI")

# APSViz-Archiver
Archives file created by the various APSViz applications and processes.

#### Licenses...
[![MIT License](https://img.shields.io/badge/License-MIT-orange.svg)](https://github.com/RENCI/APSVIZ-Archiver/tree/master/LICENSE)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![RENCI License](https://img.shields.io/badge/License-RENCI-blue.svg)](https://www.renci.org/)
#### Components and versions...
[![Python](https://img.shields.io/badge/Python-3.12.2-orange)](https://github.com/python/cpython)
[![Linting Pylint](https://img.shields.io/badge/Pylint-%203.0.3-yellow)](https://github.com/PyCQA/pylint)
[![Pytest](https://img.shields.io/badge/Pytest-%208.0.0-blue)](https://github.com/pytest-dev/pytest)
#### Build status...
[![Pylint and Pytest](https://github.com/RENCI/APSVIZ-Archiver/actions/workflows/pylint-pytest.yml/badge.svg)](https://github.com/RENCI/APSVIZ-Archiver/actions/workflows/pylint-pytest.yml)
[![Build and push the Docker image](https://github.com/RENCI/APSVIZ-Archiver/actions/workflows/image-push.yml/badge.svg)](https://github.com/RENCI/APSVIZ-Archiver/actions/workflows/image-push.yml)

## Description
This product is designed to perform copy/move/remove operations on file or directory entities. Additional functionality 
is implemented to sweep through all file/directory entities located within a directory. This product is intended to be run within a Kubernetes 
CronJob.

This product is rule based. Each Rule is defined in json format. A Rule can contain 1 or more Rule sets which can in turn specify 
1 or more atomic Rule operations. 
 
Atomic rules can optionally specify query criteria (age, etc.) that is paired with a predicate (equals, greater than, etc.). These query criteria
are used to interrogate an entity prior to performing an operation.

A simple Rule example shown below has specified:
 - A rule definition with details including a name, version and a description.
 - A rule Set that contains rule operations.
 - 3 rule operations for copy, move and a directory sweep.
   - With each rule specifying a query criteria that will trigger the rule operation.

```
{
  "rule_definition_name": "APSViz data archival rule set.",
  "rule_definition_version": "0.0.0",
  "description": "Tests a complete rule.",
  "rule_sets":
  [
    {
      "rule_set_name": "Test rule set",
      "description": "Tests a rule set by making a copy then a  move request.",
      "rules": [
        {
          "name": "Test - Copy test file",
          "description": "This test copies a file from source to destination.",
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
          "name": "Test - Move test file",
          "description": "This test moves a file from source to destination.",
          "query_criteria_type": "BY_AGE",
          "query_data_type": "INTEGER",
          "query_data_value": 30,
          "predicate_type": "GREATER_THAN_OR_EQUAL_TO",

          "action_type": "MOVE",
          "data_type": "FILE",
          "source": "/dest/some-new-data-location/some-data-file.ext",
          "destination": "/dest/some-newer-data-location"
        },
        {         
          "name": "Test - Sweep copy test",
          "description": "This test copies the directory contents of source to destination.",
          "query_criteria_type": "BY_AGE",
          "query_data_type": "INTEGER",
          "query_data_value": 2,
          "predicate_type": "GREATER_THAN_OR_EQUAL_TO",

          "action_type": "SWEEP_COPY",
          "data_type": "DIRECTORY",
          "source": "/source/root_directory",
          "destination": "/dest/new_directory"
        }
      ]
    }
  ]
}
```

There are GitHub actions to maintain code quality in this repo:
 - Pylint (minimum score of 10/10 to pass),
 - Pytest (with code coverage),
 - Build/publish a Docker image.

Helm/k8s charts for this product are available at: [APSViz-Helm](https://github.com/RENCI/apsviz-helm/tree/main/apsviz-archiver).
