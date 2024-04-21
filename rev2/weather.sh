#!/bin/bash
cd $(dirname $0)

mkdir -p logs

while true
do
    unbuffer python3 weather.py > "logs/output$(date +"%Y%m%d-%H%M%S").txt"
    echo "exception occured"
    sleep 5
done