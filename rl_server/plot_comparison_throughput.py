import numpy as np
import matplotlib.pyplot as plt
import sys

run_num = sys.argv[1]

PREDICT_PREFIX = 'log_fastMPC_5g_trace_'
SUFFIX = '_driving'
LOG_PATH = '../run_exp/bw_prediction/'
PLOT_SAMPLES = 300
THROUGHPUT_PATH='../sim/cooked_traces/'
TRACE_PREFIX = '5g_trace_'


time_stamp = []
bit_rates = []
buffer_occupancies = []
rebuffer_times = []
rewards = []
time_stamp2 = []
bit_rates2 = []
buffer_occupancies2 = []
rebuffer_times2 = []
rewards2 = []
pred_throughput = []
throughput = []
trace_timestamp = []
startup_time = 0

with open(LOG_PATH+PREDICT_PREFIX+str(run_num)+SUFFIX, 'rb') as f:
    startup_time = float(f.readline()[:-1])
    lines = f.readlines()
    for line in lines:
        parse = line.split()
        time_stamp.append(float(parse[0]))
        pred_throughput.append(float(parse[1])*8)

with open(THROUGHPUT_PATH+TRACE_PREFIX+str(run_num)+SUFFIX, 'rb') as f:
    for line in f:
        parse = line.split()
        trace_timestamp.append(float(parse[0]))
        throughput.append(int(parse[1]))

time_stamp = np.array(time_stamp) - startup_time

fig, ax = plt.subplots(1, sharex=True)
ax.plot(trace_timestamp, throughput)
ax.plot(time_stamp, pred_throughput)
ax.set_ylabel('Throughput (Mbps)')
ax.set_xlabel('Time (Sec)')
ax.legend(['bw ground-truth', 'bw predicted by fastMPC'])
plt.show()


# f, (ax1, ax2, ax3, ax4) = plt.subplots(4, sharex=True)

# truth = ax1.plot(time_stamp[-PLOT_SAMPLES:], rewards[-PLOT_SAMPLES:], label='fastMPC')
# ax1.set_title('Average reward: ' + str(np.mean(rewards[-PLOT_SAMPLES:])))
# ax1.set_ylabel('QoE')

# ax2.plot(trace_timestamp[-PLOT_SAMPLES:], throughput[-PLOT_SAMPLES:])
# ax2.plot()
# ax2.set_ylabel('Throughput (Mbps)')

# ax3.plot(time_stamp[-PLOT_SAMPLES:], bit_rates[-PLOT_SAMPLES:])
# ax3.plot(time_stamp2[-PLOT_SAMPLES:], bit_rates2[-PLOT_SAMPLES:])
# ax3.set_ylabel('Bitrate (Kpbs)')

# # ax3.plot(time_stamp[-PLOT_SAMPLES:], buffer_occupancies[-PLOT_SAMPLES:])
# # ax3.set_ylabel('buffer occupancy (sec)')

# ax4.plot(time_stamp[-PLOT_SAMPLES:], rebuffer_times[-PLOT_SAMPLES:])
# ax4.plot(time_stamp2[-PLOT_SAMPLES:], rebuffer_times2[-PLOT_SAMPLES:])
# ax4.set_ylabel('Rebuffer Time (sec)')
# ax4.set_xlabel('Time (s)')
# ax4.legend(['MPC w/ future BW', 'fastMPC'])

# f.subplots_adjust(hspace=0)
