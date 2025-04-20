#!/bin/bash
cd $(dirname $0)

mkdir -p logs
echo "hello, starting"
while true
do
    if [ "$1" == "debug" ]; then
        python3 weather.py --log-level DEBUG 
    else
        unbuffer python3 weather.py > "logs/output$(date +"%Y-%m-%d_%H:%M:%S").txt"
    fi
    echo "exception occured $(date +"%Y-%m-%d %H:%M:%S")"
    sleep 5
done
