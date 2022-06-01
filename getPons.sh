#!/bin/bash

ip=$1
community=$2
hostname=$3
user=$4
password=$5
port=$6

python3 -u GetPonName.py $ip $community $hostname $user $password $port

python3 -u getOLTData.py $ip $user $password $port $hostname &
