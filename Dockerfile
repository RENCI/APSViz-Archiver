# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

# This Dockerfile is used to build the APSVIZ-Supervisor image

# leverage the renci python base image
FROM python:3.11.3-slim

# update the image base
RUN apt-get update && apt-get -y upgrade
# RUN apt-get install -y procps

# clear the apt cache
RUN apt-get clean

# create/switch to a non-root user
RUN useradd --create-home -u 1000 nru
USER nru

# set up requirements
WORKDIR /repo/APSVIZ-Archiver

# install required python packages
ADD requirements.txt .
RUN pip install -r requirements.txt

# Copy in the rest of the code
COPY main.py main.py
COPY src src

# set the python path for source
ENV PYTHONPATH="/repo/APSVIZ-Archiver"
