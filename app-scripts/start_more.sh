#!/bin/bash

/opt/nifi/scripts/start.sh &
tail -f $NIFI_HOME/logs/nifi-app.log &

$NIFI_HOME/app-scripts/post-nifi-startup.sh
PID=$(cat $NIFI_HOME/run/nifi.pid)
wait $PID
