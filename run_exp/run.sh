bash setup.sh
bash trace_run.sh ../cooked_traces/5g_trace_104_driving > out &
BACK_PID=$!
/usr/bin/python run_video.py 192.168.122.235 BB 230 4 5g_trace_104_driving 3
wait $BACK_PID