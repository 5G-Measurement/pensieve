import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick


RESULTS_FOLDER = './results/'
NUM_BINS = 100
BITS_IN_BYTE = 8.0
MILLISEC_IN_SEC = 1000.0
M_IN_B = 1000000.0
VIDEO_LEN = 158
VIDEO_BIT_RATE = [20000, 40000, 60000, 80000, 110000, 160000]
COLOR_MAP = plt.cm.jet #nipy_spectral, Set1,Paired 
SIM_DP = 'sim_dp'
SCHEMES = ['BB', 'RB', 'BOLA', 'fastMPC', 'robustMPC', 'RL']


def main():
    time_all = {}
    bit_rate_all = {}
    buff_all = {}
    stall_all = {}
    bw_all = {}
    raw_reward_all = {}
    summay_all = {}
    for scheme in SCHEMES:
        time_all[scheme] = {}
        raw_reward_all[scheme] = {}
        bit_rate_all[scheme] = {}
        buff_all[scheme] = {}
        stall_all[scheme] = {}
        bw_all[scheme] = {}

    log_files = os.listdir(RESULTS_FOLDER)
    for log_file in log_files:

        time_ms = []
        bit_rate = []
        buff = []
        bw = []
        stall = []
        reward = []

        print log_file

        with open(RESULTS_FOLDER + log_file, 'rb') as f:
            if SIM_DP in log_file:
                for line in f:
                    parse = line.split()
                    if len(parse) == 1:
                        reward = float(parse[0])
                    elif len(parse) >= 6:
                        time_ms.append(float(parse[3]))
                        bit_rate.append(VIDEO_BIT_RATE[int(parse[6])])
                        buff.append(float(parse[4]))
                        bw.append(float(parse[5]))

            else:
                for line in f:
                    try:
                        parse = line.split()
                        if len(parse) <= 1:
                            break
                        time_ms.append(float(parse[0]))
                        bit_rate.append(int(parse[1]))
                        buff.append(float(parse[2]))
                        stall.append(float(parse[3]))
                        bw.append(float(parse[4]) / float(parse[5]) * BITS_IN_BYTE * MILLISEC_IN_SEC / M_IN_B)
                        reward.append(float(parse[6]))
                    except ZeroDivisionError:
                        bw.append(float(parse[4]) / (float(parse[5])+1) * BITS_IN_BYTE * MILLISEC_IN_SEC / M_IN_B)
                        reward.append(float(parse[6]))

        if SIM_DP in log_file:
            time_ms = time_ms[::-1]
            bit_rate = bit_rate[::-1]
            buff = buff[::-1]
            bw = bw[::-1]
        
        time_ms = np.array(time_ms)
        time_ms -= time_ms[0]
        
        # print log_file

        for scheme in SCHEMES:
            if scheme in log_file:
                time_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = time_ms
                bit_rate_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = bit_rate
                buff_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = buff
                stall_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = stall
                bw_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = bw
                raw_reward_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = reward
                break
    # print(stall_all)

    # calculate mean bitrate and stall rate
    for scheme in SCHEMES:
        summay_all[scheme] = {}
        # avg bitrate
        bitrate_avg_arr = []
        bitrate_total = 0
        total_chunk = 0
        summay_all[scheme]['all_br'] = []
        for log in bit_rate_all[scheme]:
            if len(bit_rate_all[scheme][log]) >= 158:
                bitrate_avg_arr.append(np.mean(bit_rate_all[scheme][log][:158])/1000)
                bitrate_total += np.sum(np.array(bit_rate_all[scheme][log][:158])/1000) #Mbis
                total_chunk += 158
            else:
                bitrate_avg_arr.append(np.mean(bit_rate_all[scheme][log])/1000)
                bitrate_total += np.sum(np.array(bit_rate_all[scheme][log])/1000) #Mbis
                total_chunk += len(bit_rate_all[scheme][log])
        print(scheme)
        print(bitrate_total)
        print(total_chunk)
        print(float(bitrate_total)/total_chunk)
        print(bitrate_avg_arr)
        summay_all[scheme]['avg_br'] = np.mean(bitrate_avg_arr)
        summay_all[scheme]['all_br'] = bitrate_avg_arr

        # avg stall rate
        stall_time_all = float(0)
        total_playback_time = 0
        avg_stall_arr = []
        summay_all[scheme]['all_stalled_rate'] = []
        for log in stall_all[scheme]:
            if len(stall_all[scheme][log]) >= 158:
                avg_stall_arr.append(np.sum(np.array(stall_all[scheme][log][:158]))/(158+np.sum(np.array(stall_all[scheme][log][:158]))))
                stall_time_all += float(np.sum(np.array(stall_all[scheme][log][:158], dtype=float))) # seconds
                total_playback_time = total_playback_time + 158 + np.sum(np.array(stall_all[scheme][log][:158]))
            else:
                avg_stall_arr.append(np.sum(np.array(stall_all[scheme][log]))/(len(stall_all[scheme][log])+np.sum(np.array(stall_all[scheme][log]))))
                stall_time_all += float(np.sum(np.array(stall_all[scheme][log], dtype=float))) # seconds
                total_playback_time = total_playback_time + len(stall_all[scheme][log]) + np.sum(np.array(stall_all[scheme][log]))
        print("total stall time %f" % stall_time_all)
        print("total playback time %f" % total_playback_time)
        # print("pure video time %f" % pure_video_time)
        summay_all[scheme]['time_stalled_rate'] = np.mean(avg_stall_arr) * 100 # percentage
        summay_all[scheme]['all_stalled_rate'] = np.array(avg_stall_arr) * 100
        # print(summay_all[scheme]['time_stalled_rate'])

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlim(10, 0)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())
    for scheme in SCHEMES:
        # ax.scatter(summay_all[scheme]['time_stalled_rate'], summay_all[scheme]['avg_br'])
        print("stderr for scheme %s are %f, %f" % (scheme, np.std(summay_all[scheme]['all_stalled_rate']), np.std(summay_all[scheme]['all_br'])))
        ax.errorbar(summay_all[scheme]['time_stalled_rate'], summay_all[scheme]['avg_br'], xerr=np.std(summay_all[scheme]['all_stalled_rate']), yerr=np.std(summay_all[scheme]['all_br']), capsize=4)
        if scheme == "BOLA":
            ax.annotate(scheme, (summay_all[scheme]['time_stalled_rate'], summay_all[scheme]['avg_br']))
        elif scheme == "RB":
            ax.annotate(scheme, (summay_all[scheme]['time_stalled_rate'], summay_all[scheme]['avg_br']))
        elif scheme == "truthMPC":
            ax.annotate(scheme, (summay_all[scheme]['time_stalled_rate'], summay_all[scheme]['avg_br']))
        else:
            ax.annotate(scheme, (summay_all[scheme]['time_stalled_rate'], summay_all[scheme]['avg_br']))
    
    # colors = [COLOR_MAP(i) for i in np.linspace(0, 1, len(ax.lines))]
    # for i,j in enumerate(ax.lines):
    #     j.set_color(colors[i])	
    plt.xlabel('Time Spent on Stall (Percentage)')
    plt.ylabel('Average Bitrate (Mbps)')
    plt.show()
    return

if __name__ == '__main__':
	main()