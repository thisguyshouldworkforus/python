## Automate the SNOW Chef SCTASK Server Decommission Queue (Cleanup)

[![ ](https://img.shields.io/badge/DEPENDENCY-Requires%20Chef%20Infra%20Server%20Access-red)](https://docs.chef.io/server/)  
[![ ](https://img.shields.io/badge/DEPENDENCY-Requires%20Chef%20Infra%20User-red)](https://docs.chef.io/server/server_users/)  
[![ ](https://img.shields.io/badge/DEPENDENCY-Requires%20Chef%20Infra%20Knife%20Access-red)](https://docs.chef.io/server/server_users/)  

[![ ](https://img.shields.io/badge/DEPENDENCY-Requires%20ServiceNow%20API%20Access%20Token-yellow)](https://support.servicenow.com/kb?id=kb_article_view&sysparm_article=KB0725643)  

[Chef SCTASK Cleanup](main.py) is a project intended to automate the previously manual task of searching for and deleting nodes from the Chef Infra Server, and then closing those tickets with the proper disposition. This project was developed while employed with Honeywell, and this project is shared with their knowledge and explicit permission.

## Purpose
* Create an automated solution to daily cleanups of the Service Now Queue:
  * All > Request Item = Server Decommission > Active = true > Assignment Group = Chef App Support (CORP:CCP)

## Method
* Written in Python
  * API Communication with Service Now to enable automation
  * Queue is monitored for new tickets every 5 minutes
