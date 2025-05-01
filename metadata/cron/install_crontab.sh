#!/bin/bash

#check parameter
if [ -z "$1" ]; then
    echo "No crontab specified"
    exit 1
fi

#install crontab
chmod 0644 $1
crontab $1