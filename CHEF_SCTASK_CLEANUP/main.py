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
# Dependency:
# Python (Duh.)
#
# Description:
# Automates the Chef Decommission queue in ServiceNow (SNOW)
# --------------------------------------------------------------

# Import all the things
import os
import sys
import socket
import logging
import subprocess
from pathlib import Path
from libs.knife_util import knife_command
from libs.snow_utils import snow_queue
from libs.snow_utils import snow_update
from datetime import datetime

# Define a lockfile, so we can increase
# the run scheduled without running over ourselves
pidfile = "/tmp/servicenow_automation.lock"

# This is a more robust way to check if the process is currently running
def is_process_running(pidfile):
    try:
        subprocess.run(['pgrep', '--pidfile', pidfile], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

# If the PID File exists, check to see if the contained PID is actually running
# If its not, delete the file.
if os.path.exists(pidfile):
    if not is_process_running(pidfile):
        try:
            subprocess.run(['rm', '-f', pidfile], check=True)
        except subprocess.CalledProcessError:
            pass
    else:
        sys.exit(1) # Reaching this step means the PID exists and it is currently running. Exit.

# Create the lock file
with open(pidfile, "w") as f:
    f.write(str(os.getpid()))

# Generate the current date string in the format 'YYYY-MM-DD'
TODAY = datetime.now().strftime('%Y-%m-%d')
TIME = datetime.now().strftime('%H:%M:%S')

# Create a filename using the date string
# On 'server1234' the 'app.chefadmin' (chef) group has rwx on /var/log/chef
log_filename = f"/var/log/chef/servicenow_automation_{TODAY}.log"

# Configure logging
logging.basicConfig(filename=log_filename,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                    level=logging.INFO)

# This script will only function on a system setup ahead of time with Chef/KNIFE
DESIRED_HOSTNAME = 'server1234'

# Check if the hostname matches the desired hostname
current_hostname = socket.gethostname()
if current_hostname != DESIRED_HOSTNAME:
    raise Exception(f"This script can only be run on '{DESIRED_HOSTNAME}'. Current hostname is '{current_hostname}'.")

# Define the absolute path to the organizations directory
org_dir = Path("/home/example-user/.chef/organizations")

# Find all the 'config.rb' files
config_files = [str(f) for f in org_dir.rglob('config.rb')]

# Proof of life logging statement
logging.info(f"Checking for tickets at {TIME} ...")

# Declare Knife command subcommands
node_list = ['node', 'list']
node_show = ['node', 'show']
node_delete = ['node', 'delete']
client_delete = ['client', 'delete']

# Check for an empty return
if not snow_queue()['result']:
    logging.info("There are no tickets to process!")
else:
    # Constructing a for-loop to iterate over the requests from the imported 'snow_queue()' function
    # See libs/snow_utils.py for more information on 'snow_queue()' and what its doing
    for REQUEST in snow_queue()['result']:
        SCTASK = REQUEST['number'] # The ServiceNow task number
        SYS_ID = REQUEST['sys_id'] # The ServiceNow sys_id (not really sure what that is, but its required)
        CMDB_CI = REQUEST['cmdb_ci'] # The Configuration Item (server name)

        # We only want to move forward if the CMDB_CI field isn't blank
        if CMDB_CI != '':

            # Initializing this variable as 'False' for later use
            cmdb_found = False

            # Constructing a for-loop on the discovered config.rb file found on line 70
            for config in config_files:

                # Pull out the org name from the filename
                org = os.path.basename(os.path.dirname(config))

                # Set the nodename to None so our knife_command function does't require a hostname
                # See libs/knife_util.py (line 54/55) for more information on whats happening here
                nodename = None

                # Constructing a list that we will iterate over in the next steps, splitting the results by line
                hosts = (knife_command(node_list, nodename, config)).splitlines()

                # Constructing a for-loop on the results of our hosts list.
                # We are using the enumerate() function to assign/get an index on each item
                for index, nodename in enumerate(hosts):

                    # Checking to see if our 'Configuration Item' is in the constructed host list
                    # Forcing everything to lowercase to match it properly
                    if CMDB_CI.lower() in nodename.lower():

                        # If we found a match, set the previously initialized variable to True for later use
                        cmdb_found = True

                        # The knife command concactenates list commands and cannot concactenate lists and strings,
                        # so we need to convert the nodename to a list
                        # see libs/knife_util.py, line 57 for more information on whats happening here
                        chef_node = [nodename]

                        # Deleting the node from Chef
                        knife_command(node_delete, chef_node, config)

                        # Deleting the client PEM certificate from Chef
                        knife_command(client_delete, chef_node, config)

                        # For logging purposes, making it clearer as to what exactly 'org' means
                        if org == 'ec':
                            org = 'Export Control'
                        elif org == 'non-ec':
                            org = 'Non-Export Control'
                        elif org == 'azure':
                            org = 'Azure'
                        elif org == 'm-a':
                            org = 'Mergers And Acquisions'

                        # We've taken action on the matched chef host, and now we're updating the ticket
                        # State: 3, Closed Complete
                        snow_update(f"{SYS_ID}",3,f"Deleted {CMDB_CI} from the {org} Chef organization.")

                        # Write a log file with this information
                        logging.info(f"ServiceNow Task ({SCTASK}) has requested that we delete {CMDB_CI} from the {org} org. This has been completed successfully. The ticket has been updated accordingly.")

                        # Break out of the loop
                        break

            # If we did not match our 'CMDB_CI' with a value from our Chef Server
            # hosts list, then the previously initialized variable 'cmdb_found' should
            # still be 'False'
            if not cmdb_found:

                # Write a log file with this information
                logging.info(f"ServiceNow Task ({SCTASK}) has requested that we delete {CMDB_CI}, but this host was not found in the Chef Server. The ticket has been updated to reflect this failed request.")

                # Update the ticket with this outcome
                # State: 5, Closed Skipped
                snow_update(f"{SYS_ID}",5,f"{CMDB_CI} was not found in Chef.")
        else:
            # At this point, the JSON Request returned an SCTAK item where the 'CMDB_CI' field was blank
            # there is nothing for the autoamtion to do.

            # Write a log file with this information
            logging.info(f"ServiceNow Task ({SCTASK}) has requested that we delete a Chef node, but the 'CMDB_CI' field was blank. The ticket has been updated to a PENDING_CUSTOMER state, for further action.")

            # Update the ticket with this outcome
            # State: 9, Pending Customer
            # At time of writing, its unclear if the customer would be notified of this change/update in status
            snow_update(f"{SYS_ID}",9,"CMDB Configuration Item was empty! Please update the ticket with the proper fields for automatic processing.")

# Remove the lock file when the script finishes
os.remove(pidfile)
