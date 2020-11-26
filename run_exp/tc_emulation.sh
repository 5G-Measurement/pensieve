#!/bin/bash
# bandwidth profile name
profile="$1"
echo $profile
# interval value in seconds. this is used for sleep.
interval=0.1
# read each line in the profile: [timestamp in millisecond] [WiFi bandwidth in kbps] [LTE bandwidth in kbps]
while read a b;
do
    echo $a $b
    # if [ "$t" -lt 5000 ]; then
    #     # if [ "$t" -ne 5000 ]; then
    #     # echo "$t"
    #     continue
    # fi
    # # echo $t
    startt=$(date +%s.%4N)
    # # change the bandwidth throttling value
    # sudo tc qdisc change dev ifb1 handle 1: root tbf rate $a"kbit" burst 20k latency 50ms 
    # sudo tc qdisc change dev ifb2 handle 1: root tbf rate $b"kbit" burst 20k latency 50ms
​
    sudo tc class change dev lo parent 1:1 classid 1:10 htb rate $a"mbit"
    # sudo tc class change dev em4 parent 1:1 classid 1:11 htb rate $b"mbit"
​
    delay=$(awk "BEGIN {print $startt+$interval-$(date +%s.%4N)-0.002}")
    # echo $startt, $lastt, $delay
    # echo "iter"
    # sleep into next interval
    if (( $(echo "$delay > 0 "|bc -l) )); then sleep $delay; fi
done < $profile
echo "finish dynamic."
