# sudo sysctl -w net.ipv4.ip_forward=1
# mm-link 60mbps ../cooked_traces/5g_trace_1_driving /usr/bin/python run_video.py 141.212.108.160 BOLA 230 4 5g_trace_1_driving 3

# for trace_file in ../cooked_traces/*
# do
trace_file=5g_trace_23_driving
    echo "replaying with trace file ${trace_file}"
    mm-link 60mbps ../cooked_traces/5g_trace_23_driving /usr/bin/python run_video.py 141.212.108.160 robustMPC 230 0 5g_trace_23_driving 6
    mm-link 60mbps ../cooked_traces/5g_trace_23_driving /usr/bin/python run_video.py 141.212.108.160 fastMPC 230 6 5g_trace_23_driving 5
    mm-link 60mbps ../cooked_traces/5g_trace_23_driving /usr/bin/python run_video.py 141.212.108.160 BB 230 2 5g_trace_23_driving 1
    mm-link 60mbps ../cooked_traces/5g_trace_23_driving /usr/bin/python run_video.py 141.212.108.160 RB 230 3 5g_trace_23_driving 4
    mm-link 60mbps ../cooked_traces/5g_trace_23_driving /usr/bin/python run_video.py 141.212.108.160 BOLA 230 4 5g_trace_23_driving 3
    mm-link 60mbps ../cooked_traces/5g_trace_23_driving /usr/bin/python run_video.py 141.212.108.160 FESTIVE 230 5 5g_trace_23_driving 2
    sleep 300
# in format of time_stamp bit_rate buffer_size rebuffer_time video_chunk_size download_time reward
# done
# changes need to be made for customize video chunks 
# 1. rl_server/$(server).py change the hardcoded video chunk sizes, bitrate level, etc
# 2. 