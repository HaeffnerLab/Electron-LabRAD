#!/bin/bash

~/LabRAD/scalabrad-0.8.3/bin/labrad --tls-required=false &
~/LabRAD/scalabrad-web-server-2.0.5/bin/labrad-web &

# ~/LabRAD/scalabrad-0.8.3/bin/labrad &
# ~/LabRAD/scalabrad-web-server-2.0.5/bin/labrad-web &
 

source virtualenvwrapper.sh #already done in ~/.bashrc
workon 'labrad'

# export LABRADPASSWORD='lab'

#start node serveron
python -m labrad.node --tls=off &
# python -m labrad.node
