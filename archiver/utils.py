# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class Utils:
    def __init__(self, logger):
        """
        Initializes this class

        """
        # save the logger handle
        self.logger = logger

        # instantiate slack connectivity
        self.slack_status_channel = os.getenv('SLACK_STATUS_CHANNEL')
        self.slack_issues_channel = os.getenv('SLACK_ISSUES_CHANNEL')

        # get the environment this instance is running on
        self.system = os.getenv('SYSTEM', 'System name not set')

    def send_slack_msg(self, run_id, msg, channel, debug_mode=False):
        """
        sends a msg to the Slack status channel

        :param run_id:
        :param msg:
        :param channel:
        :param debug_mode:
        :return:
        """
        # if the channel is empty default to the status channel
        if channel == self.slack_status_channel:
            client = WebClient(token=os.getenv('SLACK_STATUS_TOKEN'))
        else:
            client = WebClient(token=os.getenv('SLACK_ISSUES_TOKEN'))

        # init the final msg
        final_msg = f"APSViz Archiver ({self.system}) - "

        # add the run id and msg
        final_msg += f"{msg}"

        # log the message
        self.logger.info(final_msg)

        try:
            # send the message to slack if not in debug mode
            if not debug_mode and self.system in ['Dev', 'Prod']:
                result = self.slack_status_client.chat_postMessage(channel=channel, text=final_msg)
        except SlackApiError as e:
            self.logger.exception(f'Slack {channel} messaging failed. msg: {final_msg}')
