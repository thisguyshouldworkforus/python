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

