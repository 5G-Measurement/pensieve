#!/bin/bash
# sudo sysctl -w net.ipv4.ip_forward=1
# Use tc instead of mahimahi as the network emulator
if [ $# -eq 0 ]
then
    echo "usage ./run_tc_test.sh <single> <Algorithm to test> <trace file> to test one trace for one algorithm or ./simple_run_test.sh all to test all algorithms with all traces"
    exit
fi

MODE=$1
num_args=1
if [ $# -eq 2 ]
then
    algorithm=$2
    num_args=2
fi

if [ $# -eq 3 ]
then
    algorithm=$2
    trace=$3
    num_args=3
fi

if [ ${MODE} = "single" ]
then
    if (( ${num_args} == 2))
    then
        bash setup.sh
        echo "run for a single algorithm for all traces.."
        for trace_file in ../cooked_traces/*
        do
            echo "replaying with trace file ${trace_file}" # in format of ../cooked_traces/5g....
            bash trace_run.sh ${trace_file} > out &
            BACK_PID=$!
            filename=$(basename ${trace_file})
            /usr/bin/python run_video.py 192.168.122.235 ${algorithm} 230 0 ${filename} 6
            kill ${BACK_PID}
            kill $(ps aux | grep _server | awk '{print $2}') > /dev/null
        done
    else  
        filename=$(basename ${trace})
        echo "run for algorithm ${algorithm} for one trace ${filename}"
        bash setup.sh
        bash trace_run.sh ${trace} > out &
        BACK_PID=$!
        /usr/bin/python run_video.py 192.168.122.235 ${algorithm} 230 0 ${filename} 6
        kill ${BACK_PID}
        kill $(ps aux | grep _server | awk '{print $2}') > /dev/null
    fi
else
    bash setup.sh
    # run for all traces and algos
    for trace_file in ../cooked_traces/*
    do
        echo "replaying with trace file ${trace_file}" # in format of ../cooked_traces/5g....
        filename=$(basename ${trace_file})
        echo "replaying with trace file ${filename}" # in format of 5g_driving...
        # echo "running for mm-link 60mbps ../cooked_traces/${trace_file} /usr/bin/python run_video.py 192.168.122.235 robustMPC 230 0 ${trace_file} 6"
        bash trace_run.sh ${trace_file} > out &
        BACK_PID=$!
        /usr/bin/python run_video.py 192.168.122.235 robustMPC 230 0 ${filename} 6
        kill ${BACK_PID}
        kill $(ps aux | grep _server | awk '{print $2}') > /dev/null
        bash trace_run.sh ${trace_file} > out &
        BACK_PID=$!
        /usr/bin/python run_video.py 192.168.122.235 fastMPC 230 6 ${filename} 5
        kill ${BACK_PID}
        kill $(ps aux | grep _server | awk '{print $2}') > /dev/null
        bash trace_run.sh ${trace_file} > out &
        BACK_PID=$!
        /usr/bin/python run_video.py 192.168.122.235 BB 230 2 ${filename} 1
        kill ${BACK_PID}
        kill $(ps aux | grep _server | awk '{print $2}') > /dev/null
        bash trace_run.sh ${trace_file} > out &
        BACK_PID=$!
        /usr/bin/python run_video.py 192.168.122.235 RB 230 3 ${filename} 4
        kill ${BACK_PID}
        kill $(ps aux | grep _server | awk '{print $2}') > /dev/null
        bash trace_run.sh ${trace_file} > out &
        BACK_PID=$!
        /usr/bin/python run_video.py 192.168.122.235 BOLA 230 4 ${filename} 3
        kill ${BACK_PID}
        kill $(ps aux | grep _server | awk '{print $2}') > /dev/null
        bash trace_run.sh ${trace_file} > out &
        BACK_PID=$!
        /usr/bin/python run_video.py 192.168.122.235 FESTIVE 230 5 ${filename} 2
        kill ${BACK_PID}
        kill $(ps aux | grep _server | awk '{print $2}') > /dev/null
        bash trace_run.sh ${trace_file} > out &
        BACK_PID=$!
        /usr/bin/python run_video.py 192.168.122.235 RL 230 9 ${filename} 7
        kill ${BACK_PID}
        kill $(ps aux | grep _server | awk '{print $2}') > /dev/null
        # bash trace_run.sh ${trace_file} > out &
        # BACK_PID=$!
        # /usr/bin/python run_video.py 192.168.122.235 truthMPC 230 9 ${filename} 7
        # kill ${BACK_PID}
        # kill $(ps aux | grep _server | awk '{print $2}') > /dev/null
        # in format of time_stamp bit_rate buffer_size rebuffer_time video_chunk_size download_time reward
    done
fi
# changes need to be made for customize video chunks 
# 1. rl_server/$(server).py change the hardcoded video chunk sizes, bitrate level, etc
# 2. chunck length (take care of this!)