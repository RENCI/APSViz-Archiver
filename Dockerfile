# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2024 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

# This Dockerfile is used to build the APSVIZ-Archiver image

# leverage the renci python base image
FROM python:3.12.3-slim

# update the image base
RUN apt-get update && apt-get -y upgrade

# RUN apt-get install -y procps
RUN apt -y install nano

# clear the apt cache
RUN apt-get clean

# get some credit
LABEL maintainer="powen@renci.org"

# get the build argument that has the version
ARG APP_VERSION=$(APP_VERSION)

# now add the version arg value into a ENV param
ENV APP_VERSION=$APP_VERSION

# add user nru and switch to it
RUN useradd --create-home -u 1000 nru

# set up requirements
WORKDIR /home/nru/APSVIZ-Archiver

# install required python packages
ADD requirements.txt .
RUN pip install -r requirements.txt

# Copy in the rest of the code
COPY main.py main.py
COPY src/archiver src/archiver
COPY src/common src/common

# make sure everything is writable
RUN chmod -R 777 /home/nru/APSVIZ-Archiver

# switch to the non-root user
USER nru

# set the python path for source
ENV PYTHONPATH="/home/nru/APSVIZ-Archiver"
