#!/bin/bash

source virtualenvwrapper.sh 
workon 'labrad'

cd ~/LabRAD/electron/clients
python CCTGUI.py &

workon 'labrad'
cd ~/LabRAD/common/devel/RealSimpleGrapher
python rsg.py &
