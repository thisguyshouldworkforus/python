[![logo](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/480px-Python-logo-notext.svg.png)](https://www.python.org/)  

A simple repo to hold scripts that I have written over the years for a variety of purposes

## License

[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)


## Bootstrap Wrapper

[![ ](https://img.shields.io/badge/DEPENDENCY-RedHat%20Satellite-green)](https://www.redhat.com/en/technologies/management/satellite)  
[![ ](https://img.shields.io/badge/DEPENDENCY-Requires%20Root%20Access-red)](https://tldp.org/LDP/lame/LAME/linux-admin-made-easy/root-account.html)  
[![ ](https://img.shields.io/badge/ALERT-Deprecated%20in%20Satellite%20v6.9-blue)](https://access.redhat.com/documentation/en-us/red_hat_satellite/6.9/html-single/release_notes/index#deprecated_functionality)  

[system_bootstrap.py](system_bootstrap.py) is a script that will gather information about the system it is being run on and use that information to bootstrap the system for RedHat Satellite.

- In this script, it will:
  - Import Modules
    - `socket`, `os`, `urllib`, `logging`, `platform`, `shutil`
    - from `socket` import `timeout`
    - from `urllib.request` import `Request`, `urlopen`
    - from `urllib.error` import `URLError`, `HTTPError`
  - Set PS1 Prompt color
  - Ensure only ROOT or another SuperUser runs this script
  - Set Variables
    - hostname = `socket.getfqdn()`
    - shortname = `str(hostname.split('.')[0])`
    - environment = `shortname[-4]`
    - datacenter = `shortname[-3]`
    - servertype = `shortname[-1]`
    - os_info = `platform.uname().release`
    - release = `platform.platform().split('-')`
    - ver = `str(release[6])`
    - dist = 'el' + `str(ver.split('.')[0])`
  - Determine the SERVER and ACTIVATION KEY to use
  - Print our variables out, to ensure we captured them correctly
  - Build our strings for the SERVER connection
    - connection = `https://` + `SERVER` + `:8443/rhsm`
    - file_name = `bootstrap.py`
    - download = `https://` + `SERVER` + `:443/pub/` + `file_name`
  - Test our connection to the SERVER
    - try block
      - response = `urllib.request.urlopen(connection, timeout=10)`
      - test if response code is `200`
        - if success:
          - download RedHat Satellite `bootstrap.py`
          - run `bootstrap.py`
        - if fail:
          - print error
      - catch exception (HTTPError, URLError, timeout)

## Automate the SNOW Chef SCTASK Server Decommission Queue (Cleanup)

[![ ](https://img.shields.io/badge/DEPENDENCY-Requires%20Chef%20Infra%20Server%20Access-red)](https://docs.chef.io/server/)  
[![ ](https://img.shields.io/badge/DEPENDENCY-Requires%20Chef%20Infra%20User-red)](https://docs.chef.io/server/server_users/)  
[![ ](https://img.shields.io/badge/DEPENDENCY-Requires%20Chef%20Infra%20Knife%20Access-red)](https://docs.chef.io/server/server_users/)  

[![ ](https://img.shields.io/badge/DEPENDENCY-Requires%20ServiceNow%20API%20Access%20Token-yellow)](https://support.servicenow.com/kb?id=kb_article_view&sysparm_article=KB0725643)  

[Chef SCTASK Cleanup](CHEF_SCTASK_CLEANUP/main.py) is a project intended to automate the previously manual task of searching for and deleting nodes from the Chef Infra Server, and then closing those tickets with the proper disposition. This project was developed while employed with Honeywell, and this project is shared with their knowledge and explicit permission.

## Purpose
* Create an automated solution to daily cleanups of the Service Now Queue:
  * All > Request Item = Server Decommission > Active = true > Assignment Group = Chef App Support (CORP:CCP)

## Method
* Written in Python
  * API Communication with Service Now to enable automation
  * Queue is monitored for new tickets every 5 minutes
