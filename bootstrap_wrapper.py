#!/usr/bin/env python3

# --------------------------------------------------------------
# Copyright (C) 2020: Snyder Business And Technology Consulting, LLC. - All Rights Reserved
#
# Licensing:
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# Date:
# September 03, 2020
#
# Author:
# Alexander Snyder
#
# Email:
# alexander@sba.tc
#
# Repository:
# https://github.com/thisguyshouldworkforus/python.git
#
# Dependency:
# Python3
#
# Description:
# Determines RedHat Satellite SERVER and ACTIVATION KEY
# by system hostname. Tests connectivity with the Satellite capsule.
# --------------------------------------------------------------

# Import Modules
import socket, os, urllib, logging, platform, shutil
from socket import timeout
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# Set prompt text color
NORMAL_TEXT="\033[0;37;40m"
RED_TEXT="\033[1;31;40m"

# Ensure only ROOT or another SuperUser runs this script
gid = str(os.getegid())
if gid != '0':
    print(RED_TEXT + '\n\nPlease become root and re-run this script!\n\n' + NORMAL_TEXT)
    exit(1)

# Set Variables
hostname = socket.getfqdn()
shortname = str(hostname.split('.')[0])
environment = shortname[-4]
datacenter = shortname[-3]
servertype = shortname[-1]
os_info = platform.uname().release
release = platform.platform().split('-')
ver = str(release[6])
dist = 'el' + str(ver.split('.')[0])

# Determine the SERVER and ACTIVATION KEY to use
if dist == 'el7':
    if datacenter == 'a':
        if environment == 'k':
            if servertype == 'v':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL7_CHEF-KITCHEN_AK,7_DEV-AK"
        elif environment == 'd':
            if servertype == 'v':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL7_DEV_AK,7_DEV-AK"
            elif servertype == 'p':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL7_DEV_PHYSICAL_AK,7_DEV-AK"
        elif environment == 'q':
            if servertype == 'v':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL7_QA_AK,7_QA-AK"
            elif servertype == 'p':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL7_QA_PHYSICAL_AK,7_QA-AK"
        elif environment == 'c':
            if servertype == 'v':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL7_CORP_AK,7_CORP-AK"
            elif servertype == 'p':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL7_CORP_PHYSICAL_AK,7_CORP-AK"
        elif environment == 'p':
            if servertype == 'v':
                SERVER='west-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL7_PROD_AK,7_PROD-AK"
            elif servertype == 'p':
                SERVER='west-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL7_PROD_PHYSICAL_AK,7_PROD-AK"
        elif environment == 's':
            if servertype == 'v':
                SERVER='west-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL7_DR_AK,7_DR-AK"
            elif servertype == 'p':
                SERVER='west-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL7_DR_PHYSICAL_AK,7_DR-AK"
        elif environment == 't':
            if servertype == 'v':
                SERVER='west-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL7_CAT-UAT_AK,7_CAT-UAT-AK"
            elif servertype == 'p':
                SERVER='west-prod-capsule-satellite'
                ACTIVATIONKEY="RHEL7_CAT-UAT_PHYSICAL_AK,7_CAT-UAT-AK"

    if datacenter == 'p':
        if environment == 'd':
            if servertype == 'v':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL7_DEV_AK,7_DEV-AK"
            elif servertype == 'p':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL7_DEV_PHYSICAL_AK,7_DEV-AK"
        elif environment == 'q':
            if servertype == 'v':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL7_QA_AK,7_QA-AK"
            elif servertype == 'p':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL7_QA_PHYSICAL_AK,7_QA-AK"
        elif environment == 'c':
            if servertype == 'v':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL7_CORP_AK,7_CORP-AK"
            elif servertype == 'p':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL7_CORP_PHYSICAL_AK,7_CORP-AK"
        elif environment == 'p':
            if servertype == 'v':
                SERVER='north-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL7_PROD_AK,7_PROD-AK"
            elif servertype == 'p':
                SERVER='north-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL7_PROD_PHYSICAL_AK,7_PROD-AK"
        elif environment == 's':
            if servertype == 'v':
                SERVER='north-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL7_DR_AK,7_DR-AK"
            elif servertype == 'p':
                SERVER='north-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL7_DR_PHYSICAL_AK,7_DR-AK"
        elif environment == 't':
            if servertype == 'v':
                SERVER='north-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL7_CAT-UAT_AK,7_CAT-UAT-AK"
            elif servertype == 'p':
                SERVER='north-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL7_CAT-UAT_PHYSICAL_AK,7_CAT-UAT-AK"
elif dist == 'el8':
    if datacenter == 'a':
        if environment == 'd':
            if servertype == 'v':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL8_DEV_AK,8_DEV-AK"
            elif servertype == 'p':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL8_DEV_PHYSICAL_AK,8_DEV-AK"
        elif environment == 'q':
            if servertype == 'v':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL8_QA_AK,8_QA-AK"
            elif servertype == 'p':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL8_QA_PHYSICAL_AK,8_QA-AK"
        elif environment == 'c':
            if servertype == 'v':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL8_CORP_AK,8_CORP-AK"
            elif servertype == 'p':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL8_CORP_PHYSICAL_AK,8_CORP-AK"
        elif environment == 'p':
            if servertype == 'v':
                SERVER='west-prod-capsule-satellite'
                ACTIVATIONKEY="RHEL8_PROD_AK,8_PROD-AK"
            elif servertype == 'p':
                SERVER='west-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL8_PROD_PHYSICAL_AK,8_PROD-AK"
        elif environment == 's':
            if servertype == 'v':
                SERVER='west-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL8_DR_AK,8_DR-AK"
            elif servertype == 'p':
                SERVER='west-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL8_DR_PHYSICAL_AK,8_DR-AK"
        elif environment == 't':
            if servertype == 'v':
                SERVER='west-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL8_CAT-UAT_AK,8_CAT-UAT-AK"
            elif servertype == 'p':
                SERVER='west-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL8_CAT-UAT_PHYSICAL_AK,8_CAT-UAT-AK"

    if datacenter == 'p':
        if environment == 'd':
            if servertype == 'v':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL8_DEV_AK,8_DEV-AK"
            elif servertype == 'p':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL8_DEV_PHYSICAL_AK,8_DEV-AK"
        elif environment == 'q':
            if servertype == 'v':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL8_QA_AK,8_QA-AK"
            elif servertype == 'p':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL8_QA_PHYSICAL_AK,8_QA-AK"
        elif environment == 'c':
            if servertype == 'v':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL8_CORP_AK,8_CORP-AK"
            elif servertype == 'p':
                SERVER='north-corp-satellite-capsule'
                ACTIVATIONKEY="RHEL8_CORP_PHYSICAL_AK,8_CORP-AK"
        elif environment == 'p':
            if servertype == 'v':
                SERVER='north-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL8_PROD_AK,8_PROD-AK"
            elif servertype == 'p':
                SERVER='north-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL8_PROD_PHYSICAL_AK,8_PROD-AK"
        elif environment == 's':
            if servertype == 'v':
                SERVER='north-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL8_DR_AK,8_DR-AK"
            elif servertype == 'p':
                SERVER='north-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL8_DR_PHYSICAL_AK,8_DR-AK"
        elif environment == 't':
            if servertype == 'v':
                SERVER='north-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL8_CAT-UAT_AK,8_CAT-UAT-AK"
            elif servertype == 'p':
                SERVER='north-prod-satellite-capsule'
                ACTIVATIONKEY="RHEL8_CAT-UAT_PHYSICAL_AK,8_CAT-UAT-AK"

# Print our variables out, to ensure we captured them correctly
print("\n\nHostname: %s\nShortname: %s\nDatacenter: %s\nEnvironment: %s\nServer Type: %s\nOS Release: %s\nDistribution: %s\n\n" % (hostname, shortname, datacenter, environment, servertype, os_info, dist))

# Test our connection to the SERVER
connection = 'https://' + SERVER + ':8443/rhsm'
file_name = 'bootstrap.py'
download = 'https://' + SERVER + ':443/pub/' + file_name
try:
    response = urllib.request.urlopen(connection, timeout=10)
    if str(response.getcode()) == '200':
        print(RED_TEXT + connection + ' is reachable!' + NORMAL_TEXT + '\n\n')
        urllib.request.urlretrieve(download, '/root/' + file_name)
        os.system("bash -c 'chown root:root /root/bootstrap.py'")
        os.system("bash -c 'chmod 0755 /root/bootstrap.py'")
        os.system('/usr/bin/python2 /root/bootstrap.py --login=bootstrap --server=' + SERVER + ' --download-method=https --organization=SBATC_LLC --location=int.snyderfamily.co --activationkey=' + ACTIVATIONKEY + ' --skip foreman --force')
    else:
        print(RED_TEXT + 'There was an error trying to reach\n\t' + connection + 'Please review this error before continuing' + NORMAL_TEXT + '\n\n')
        exit(1)
except (HTTPError, URLError) as error:
    print(error)
    exit(1)
except timeout:
    logging.error('socket timed out - URL %s', connection)
    exit(1)