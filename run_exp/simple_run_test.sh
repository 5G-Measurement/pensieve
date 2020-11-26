# sudo sysctl -w net.ipv4.ip_forward=1
# mm-link 60mbps ../cooked_traces/5g_trace_1_driving /usr/bin/python run_video.py 141.212.108.160 fastMPC 230 4 5g_trace_1_driving 3
if [ $# -eq 0 ]
then
    echo "usage ./simple_run_test.sh <single> <Algorithm to test> <trace file> to test one trace for one algorithm or ./simple_run_test.sh all to test all algorithms with all traces"
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
        echo "run for a single algorithm for all traces.."
        for trace_file in ../cooked_traces/*
        do
            echo "replaying with trace file ${trace_file}" # in format of ../cooked_traces/5g....
            filename=$(basename ${trace_file})
            mm-delay 10 mm-link 60mbps ${trace_file} /usr/bin/python run_video.py 141.212.108.160 ${algorithm} 230 0 ${filename} 6
        done
    else
        filename=$(basename ${trace})
        echo "run for algorithm ${algorithm} for one trace ${filename}"
        mm-link --meter-downlink 60mbps ${trace} /usr/bin/python run_video.py 141.212.108.160 ${algorithm} 230 0 ${filename} 6
    fi
else
    # run for all traces and algos
    for trace_file in ../cooked_traces/*
    do
    # trace_file=5g_trace_23_driving
        echo "replaying with trace file ${trace_file}" # in format of ../cooked_traces/5g....
        filename=$(basename ${trace_file})
        echo "replaying with trace file ${filename}" # in format of 5g_driving...
        # echo "running for mm-link 60mbps ../cooked_traces/${trace_file} /usr/bin/python run_video.py 141.212.108.160 robustMPC 230 0 ${trace_file} 6"
        mm-delay 27 mm-link 60mbps ${trace_file} /usr/bin/python run_video.py 141.212.108.160 robustMPC 230 0 ${filename} 6
        # mm-delay 27 mm-link 60mbps ${trace_file} /usr/bin/python run_video.py 141.212.108.160 fastMPC 230 6 ${filename} 5
        # mm-delay 27 mm-link 60mbps ${trace_file} /usr/bin/python run_video.py 141.212.108.160 BB 230 2 ${filename} 1
        # mm-delay 27 mm-link 60mbps ${trace_file} /usr/bin/python run_video.py 141.212.108.160 RB 230 3 ${filename} 4
        # mm-delay 27 mm-link 60mbps ${trace_file} /usr/bin/python run_video.py 141.212.108.160 BOLA 230 4 ${filename} 3
        # mm-delay 27 mm-link 60mbps ${trace_file} /usr/bin/python run_video.py 141.212.108.160 FESTIVE 230 5 ${filename} 2
        mm-delay 27 mm-link 60mbps ${trace_file} /usr/bin/python run_video.py 141.212.108.160 RL 230 9 ${filename} 7
        # in format of time_stamp bit_rate buffer_size rebuffer_time video_chunk_size download_time reward
    done
fi
# changes need to be made for customize video chunks 
# 1. rl_server/$(server).py change the hardcoded video chunk sizes, bitrate level, etc
# 2. 