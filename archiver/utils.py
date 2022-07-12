# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

import os
import slack


class Utils:
    def __init__(self, logger):
        """
        Initializes this class

        """
        # save the logger handle
        self.logger = logger

        # instantiate slack connectivity
        self.slack_client = slack.WebClient(token=os.getenv('SLACK_ACCESS_TOKEN'))
        self.slack_channel = os.getenv('SLACK_CHANNEL')

        # get the environment this instance is running on
        self.system = os.getenv('SYSTEM', 'System name not set')

    def send_slack_msg(self, run_id, msg, debug_mode=False, instance_name=None):
        """
        sends a msg to the Slack channel

        :param run_id:
        :param msg:
        :param debug_mode:
        :param instance_name:
        :return:
        """
        # init the final msg
        final_msg = f"APSViz Archiver ({self.system}) - "

        # if there was an instance name use it
        if instance_name is not None:
            final_msg += f'Instance name: ' + instance_name + ', '

        # add the run id and msg
        final_msg += f"Run ID: {run_id} {msg}"

        # log the message if in debug mode
        if debug_mode:
            self.logger.info(final_msg)
        # else send the message to slack
        else:
            self.slack_client.chat_postMessage(channel=self.slack_channel, text=final_msg)
