#!/usr/bin/python3.11

# --------------------------------------------------------------
# Copyright (C) 2023: Honeywell Aerospace, Inc. - All Rights Reserved
#
# Disclaimer:
# This utility was developed using Honeywell Aerospace time and resources.
# explicit permission to share this project as open source was requested
# and received ahead of time. Please reach out to Manish.Chopra@Honeywell.com
# for questions, comments, or concerns regarding this. Any sensitive or otherwise
# proprietary information has been either redacted or changed.
#
# Date:
# October 02, 2023
#
# Author:
# Alexander Snyder
#
# Email:
# alexander.snyder@honeywell.com
#
#
# Dependency:
# Python (Duh.)
#
# Description:
# Defines knife for use later on
# --------------------------------------------------------------

# Filename: libs/knife_util.py
import socket
import subprocess

# Desired hostname
DESIRED_HOSTNAME = 'server1234'

def knife_command(subcommands: list[str], nodename: str, config: str):
    """
    Execute a knife command and return the output.
    :param subcommands: The knife subcommand to run.
    :return: The output from the knife command.
    """
    if subcommands is None:
        raise Exception(f"Incomplete knife command!.")
    if config is None:
        raise Exception(f"This script requires a configuration file!")

    # Check if the hostname matches the desired hostname.
    current_hostname = socket.gethostname()
    if current_hostname != DESIRED_HOSTNAME:
        raise Exception(f"This script can only be run on '{DESIRED_HOSTNAME}'. Current hostname is '{current_hostname}'.")

    # If hostname matches, proceed to execute the knife command.
    if nodename is None:
        cmd = ['/opt/chef-workstation/bin/knife'] + subcommands + ['-c', config]
    else:
        cmd = ['/opt/chef-workstation/bin/knife'] + subcommands + nodename + ['-c', config] + ['--yes']

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        return result.stdout
    else:
        raise Exception(f'Error executing knife command: {result.stderr}')

