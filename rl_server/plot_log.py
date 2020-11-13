import numpy as np
import matplotlib.pyplot as plt


LOG_PATH = './results/log'
PLOT_SAMPLES = 300
THROUGHPUT_PATH='../test/cooked_traces/5G_driving'


time_stamp = []
bit_rates = []
buffer_occupancies = []
rebuffer_times = []
rewards = []
throughput = []
trace_timestamp = []

with open(LOG_PATH, 'rb') as f:
    for line in f:
        parse = line.split()
        time_stamp.append(float(parse[0]))
        bit_rates.append(float(parse[1]))
        buffer_occupancies.append(float(parse[2]))
        rebuffer_times.append(float(parse[3]))
        rewards.append(float(parse[6]))

with open(THROUGHPUT_PATH, 'rb') as f:
    for line in f:
        parse = line.split()
        trace_timestamp.append(int(parse[0]))
        throughput.append(int(parse[1]))

time_stamp = time_stamp - np.min(time_stamp)

f, (ax1, ax2, ax4) = plt.subplots(3, sharex=True)

# ax1.plot(time_stamp[-PLOT_SAMPLES:], rewards[-PLOT_SAMPLES:])
# ax1.set_title('Average reward: ' + str(np.mean(rewards[-PLOT_SAMPLES:])))
# ax1.set_ylabel('Reward')
ax1.plot(trace_timestamp[-PLOT_SAMPLES:], throughput[-PLOT_SAMPLES:])
ax1.set_title('True Throughput (mbps)')
ax1.set_ylabel('Throughput')


ax2.plot(time_stamp[-PLOT_SAMPLES:], bit_rates[-PLOT_SAMPLES:])
ax2.set_ylabel('bit rate (Kpbs)')

# ax3.plot(time_stamp[-PLOT_SAMPLES:], buffer_occupancies[-PLOT_SAMPLES:])
# ax3.set_ylabel('buffer occupancy (sec)')

ax4.plot(time_stamp[-PLOT_SAMPLES:], rebuffer_times[-PLOT_SAMPLES:])
ax4.set_ylabel('rebuffer time (sec)')
ax4.set_xlabel('Time (s)')

f.subplots_adjust(hspace=0)

plt.show()