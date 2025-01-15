#!/bin/bash

source virtualenvwrapper.sh
workon 'labrad'

#start all servers
cd ~/LabRAD/electron/clients
python NodeClient-electron.py
