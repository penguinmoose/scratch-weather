#!/bin/bash
cd $(dirname $0)

while true
do
    unbuffer python3 weather.py > "output$(date +"%Y%m%d-%H%M%S").txt"
    echo "exception occured"
done