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
# October 04, 2023
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
# Defines the API functions for ServiceNow
# --------------------------------------------------------------

# Filename: libs/snow_utils.py
import requests
import subprocess

RECIPIENTS = "example-user@honeywell.com"

def send_error_email(subject, recipients, body):
    # Prepare the mailx command
    cmd = ["/usr/bin/mailx", "-s", subject]
    
    if isinstance(recipients, list):
        cmd.extend(recipients)
    else:
        cmd.append(recipients)
    
    # Use subprocess to send the email
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    process.communicate(input=body.encode())

def extract_credentials(credential_file):
    """
    Extract API Info from a protected file.
    :param credential_file: The path to the file containing the API info.
    :return: The formatted authorization info.
    """
    credentials = {}
    
    with open(credential_file, 'r') as file:
        lines = file.readlines()
        
        for line in lines:
            if "ServiceNow UserID" in line:
                credentials["username"] = lines[lines.index(line) + 1].strip()
            elif "PlainText Password" in line:
                credentials["password"] = lines[lines.index(line) + 1].strip()
            elif "Client ID" in line:
                credentials["client_id"] = lines[lines.index(line) + 1].strip()
            elif "Client Secret" in line:
                credentials["client_secret"] = lines[lines.index(line) + 1].strip()
                
    return credentials


def snow_oauth():
    """
    Generate a ServiceNow OAuth Token.
    :return: The OAuth Access Token.
    """
    auth_info = extract_credentials("/home/example-user/.secure/snow.api")

    # Define the URL and headers
    url = "https://service-now.com/oauth_token.do"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Define the payload/body
    data = {
        "grant_type": "password",
        "client_id": auth_info["client_id"],
        "client_secret": auth_info["client_secret"],
        "username": auth_info["username"],
        "password": auth_info["password"]
    }

    # Make the POST request
    response = requests.post(url, headers=headers, data=data)

    # Check the response
    if response.status_code == 200:
        SNOW_TOKEN = response.json().get('access_token')
    else:
        send_error_email(f"Failed with status code: {response.status_code}", RECIPIENTS, f"{response.text}")

    return SNOW_TOKEN

def snow_queue():
    """
    Process the Chef Decommission Queue in Service Now.
    :return: The json formatted service now queue for Chef Corp CCP.
    """
    # Honeywell Production ServiceNow
    url = 'https://service-now.com/api/now/table/sc_task?sysparm_query=request_item.cat_item%5Eassignment_group%3Dad961946&sysparm_display_value=true&sysparm_fields=number%2Csys_id%2Ccmdb_ci%2Cassigned_to%2Cstate%2Cwork_notes'
    
    headers = {
        "Authorization": f"Bearer {snow_oauth()}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    queue_data = response.json()

    return queue_data

def snow_update(sys_id: str, state: str = '1', notes: str = ''):
    """
    Update a ServiceNow Task:
    :param sys_id: The ServiceNow SystemID.
    :param state: The current state of the task, available options are:
        "1: Open"
        "2: Work In Progress"
        "3: Closed Complete"
        "4: Closed Incomplete"
        "5: Closed Skipped"
        "6: Pending Vendor"
        "8: Pending Change"
        "9: Pending Customer"
    :param notes: Ticket comments
    :return: The response output.
    """
    CHEF_SERVICE_ACCOUNT = "bc8e3465hyg09bbb359a"

    # Honeywell Production ServiceNow
    url = f"https://service-now.com/api/now/table/sc_task/{sys_id}"

    # Headers
    headers = {
        "Authorization": f"Bearer {snow_oauth()}",
        "Content-Type": "application/json"
    }

    # Payload data of our request
    data = {
    	"assigned_to":f"{CHEF_SERVICE_ACCOUNT}",
    	"state":f"{state}",
    	"work_notes":f"{notes}"
    }

    # Make the PUT request
    response = requests.put(url, headers=headers, json=data)

    # Check the response
    if response.status_code != 200:
        send_error_email(f"Failed with status code: {response.status_code}", RECIPIENTS, f"{response.text}")
