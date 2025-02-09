#!/usr/bin/env python
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import base64
import urllib
import sys
import os
import json
import time
os.environ['CUDA_VISIBLE_DEVICES']=''

import numpy as np
import time
import itertools

######################## FAST MPC #######################

S_INFO = 5  # bit_rate, buffer_size, rebuffering_time, bandwidth_measurement, chunk_til_video_end
S_LEN = 8  # take how many frames in the past
MPC_FUTURE_CHUNK_COUNT = 5
VIDEO_BIT_RATE = [20000, 40000, 60000, 80000, 110000, 160000]  # Kbps
BITRATE_REWARD = [1, 2, 3, 12, 15, 20]
BITRATE_REWARD_MAP = {0: 0, 20000: 1, 40000: 2, 60000: 3, 80000: 12, 110000: 15, 160000: 20}
M_IN_K = 1000.0
BUFFER_NORM_FACTOR = 10.0
CHUNK_TIL_VIDEO_END_CAP = 157.0
TOTAL_VIDEO_CHUNKS = 157
DEFAULT_QUALITY = 0  # default video quality without agent
REBUF_PENALTY = 160  # 1 sec rebuffering -> this number of Mbps
SMOOTH_PENALTY = 1
TRAIN_SEQ_LEN = 100  # take as a train batch
MODEL_SAVE_INTERVAL = 100
RANDOM_SEED = 42
RAND_RANGE = 1000
SUMMARY_DIR = './results'
LOG_FILE = './results/log'
LOG_BW = './bw_prediction/log'
# in format of time_stamp bit_rate buffer_size rebuffer_time video_chunk_size download_time reward
NN_MODEL = None
truth_bw = []
trace_file = sys.argv[1]
with open('../rl_server/traces/'+trace_file+'oneline', 'r') as truth_trace:
    truth_bw = truth_trace.readline().split(',')[0:-1]
    truth_bw = [float(i) for i in truth_bw]
startup_time = time.time()

CHUNK_COMBO_OPTIONS = []

# video chunk sizes
size_video1 = [337339,14912671,24265636,22711544,19639705,20946809,11895609,7597636,56067905,45444680,54798068,69464107,50637608,19559369,22224402,22578365,8346702,15775481,9163235,41307095,28763893,21266416,23702229,27580394,20329780,16109183,58830800,66935122,15251076,16574034,13009028,12791674,11137898,11485310,12428518,9963766,12189364,10142396,10185488,14061455,20074099,46115254,40906522,7891151,21012466,23519424,18715420,17000816,14448126,6958676,9088791,7211881,3063586,2782179,9958410,12158708,12300216,15815684,13526256,11995130,13394791,14135828,15366126,14248439,13843717,14665119,21079187,25480074,23021754,27527834,26155848,17849379,16546531,17718949,17337137,20008245,58430914,16292703,25587422,23982306,13347845,14337991,14584990,13962401,14393788,14649457,13409715,13909605,13301968,19025846,19295426,18261873,19847604,18767181,22420858,19324333,20392234,7671072,17781906,12839336,10779770,14606687,41866951,37238410,14347759,11399187,10358641,14315696,23283631,37521367,22241104,15813346,17116450,18867054,17393609,24759401,25782433,25885372,26242011,23865378,25470681,27258768,17853711,14829893,27779697,27714923,25946474,19596259,23774167,19373656,23977420,24493733,14528511,16841176,16743604,17975224,22329548,16001583,18238584,21308824,17749058,14127787,17525699,14240042,20324139,21993033,18863108,15964734,8284939,9004706,6955279,10701639,9459459,3212828,2509989,2004927,591360,2394426]
size_video2 = [337339,14912671,24132566,21016487,17473873,17432386,9099663,7044111,48103258,28884539,26873304,33588177,25684661,10838546,12783186,13101938,5268213,9838179,6126794,26576979,19285617,14817542,17002609,19316039,13919609,11073078,44076779,49215857,10019282,10921784,8768798,8740660,7610374,7822163,8433079,6951419,8625024,6833121,6808950,9608563,13956444,33926116,29928879,5545322,15180886,16044226,12394633,11196580,9698716,4738333,6072231,4799875,1790651,1529278,6558222,7961846,8148750,10662977,8793419,7475950,8601429,9576793,10221665,8760683,8711578,9417807,14377779,17340552,15365006,19021488,17918889,11843178,10916331,12021075,11809774,13817529,44222240,11574285,17560011,16439864,8847416,9530442,9945160,9471489,9833576,10023423,8908280,9004051,8764764,13175394,14191823,12316520,13245175,12490444,15265366,13365138,13994870,5391903,12114555,8739355,7401667,9761239,30352856,26354219,9662265,7008597,6126549,9409059,16742448,27817780,16060560,11168326,12064050,12122131,10969714,16960361,17875878,17343962,17781436,16547208,17390834,18638649,12036523,9918331,19006737,19028716,18031107,13308895,16649620,13175624,16608135,17077492,9645423,11281629,11179031,12016215,15214650,11200919,12984407,15340646,12480173,9581283,11843441,9470053,13845974,15054391,12467336,10680491,5208724,5906076,4674535,6705784,6312703,2410559,1922862,1128453,517365,1201371]
size_video3 = [337243,14912671,22644885,17135714,13114792,11497228,6232523,5425476,29583867,15816325,15275967,20600381,17710542,7412644,9055732,9337721,3201928,6731501,4543558,20277060,14877694,11453319,13274781,14862949,10513690,8329186,34554431,37801487,7180834,7801969,6381056,6393963,5578363,5739662,6190601,5198830,6516530,4960781,4876023,7013013,10250816,26113743,22860019,4146191,11601071,11589115,8720528,7852064,6922163,3458958,4351089,3468038,1235756,1010776,4682485,5642819,5815666,7667415,6118130,5098216,5982646,6905077,7258180,5903236,5922485,6487715,10395993,12476436,10883852,13889966,12943936,8355811,7699623,8697196,8539884,10111273,34025057,8652970,12877164,11975956,6280571,6681274,7178853,6803527,7120614,7243569,6378767,6369153,6270064,9600822,10839240,8798342,9413866,8818409,10884020,9684889,10113016,3986512,8761637,6255843,5347529,6979884,22955881,19576633,6968696,4651140,3942750,6587403,12556616,21334076,12161730,8326048,8972855,8446369,7511410,12247427,13038195,12229430,12704190,12007698,12501375,13457876,8587729,7067075,13578682,13658286,13106871,9469564,12216668,9408461,12195097,12613176,6800911,8020179,7882490,8469705,10869298,8336931,9782551,11598573,9254020,6922363,8494032,6723557,9962942,10840351,8732970,7562882,3563377,4074589,3243768,4688403,4246384,1491121,1146202,447883,279272,803570]
size_video4 = [377897,14898753,20421673,13063186,8954217,7325507,4014386,3830488,17832465,9877442,10988410,15230785,13601559,5612759,6789212,7016601,1942216,4718233,3263003,15945082,11785554,9003718,10489883,11644166,8135330,6391364,27018238,29587565,5395812,5799553,4738322,4764193,4183888,4325721,4668463,3966453,5053481,3697571,3577346,5249724,7686878,20100626,17639418,3174755,9032460,8531701,6264914,5629782,5045231,2581365,3233321,2594645,911715,719615,3496204,4154630,4281107,5707279,4397748,3533955,4257694,5050780,5270336,4123549,4164335,4586890,7674948,9132721,7880072,10340109,9558538,6050499,5568885,6422673,6358479,7595952,26329427,6659174,9827222,9075578,4644666,4851731,5349884,5028861,5304043,5390156,4721651,4637025,4630741,7197388,8482578,6443358,6864434,6405222,7920104,7204570,7551736,3037981,6591562,4617597,3982768,5173499,17736300,14917504,5249262,3327042,2811660,4702600,9611993,16684805,9434694,6370300,6846629,6132241,5426584,9064385,9739432,8845382,9324884,8914856,9267595,10030748,6285842,5207162,9939880,10038030,9757084,6892659,9177908,6923540,9283858,9627205,4915398,5898498,5744951,6170363,7991868,6409879,7627654,9016602,6981592,5103310,6244074,4926138,7379602,8011132,6322575,5529168,2585313,3010411,2342869,3304851,2809840,891813,692632,235564,124268,427098]
size_video5 = [336477,14648397,17616813,8581118,4726840,3421740,1987360,2185110,9295618,5971357,7669174,10578989,9449433,3829326,4447520,4548277,1103419,2715414,1997555,11199212,8376884,6254528,7313446,8054223,5596063,4316804,18604040,20723782,3622285,3854472,3217701,3212580,2781171,2867806,3105896,2659767,3460653,2382623,2243677,3408862,5061692,13308063,11857920,2182595,6334422,5516229,3897146,3491407,3184630,1728577,2155907,1753721,618968,482994,2354236,2715272,2754002,3700338,2697401,2077748,2596297,2942589,3269601,2472824,2501617,2761582,4894685,5759046,4905689,6695853,6133072,3789723,3478014,4098626,4165439,5066445,18183186,4623087,6754819,6222613,3078962,3080827,3535232,3285443,3494448,3529670,3123898,3029270,3059193,4729676,5966743,4031950,4314280,4037231,4959415,4687332,4811858,2054604,4462862,3046638,2648526,3387394,12176825,10062382,3552565,2139919,1859346,3131242,6479978,11490169,6507505,4368401,4682869,3815757,3334508,5889797,6433588,5638739,6062060,5850985,6118487,6683536,4036556,3322499,6343093,6446252,6361946,4367184,6033322,4507990,6371885,6582726,3090648,3851594,3709626,3979395,5202497,4422067,5339294,6235334,4653534,3314391,4039495,3205850,4848722,5225224,4026891,3588599,1551058,1792688,1471940,2079411,1669374,352526,267244,111836,48639,121164]
size_video6 = [334476,11007815,8849724,3191121,1661718,1315024,698359,730082,4047415,2863079,4167844,5571764,4925652,2030157,2240782,2211169,382046,1113969,820127,6357933,4814284,3419258,3944328,4284196,3022025,2248581,9946363,11684632,1849732,1942795,1704756,1697111,1529441,1568649,1677618,1415096,1894067,1186604,1068386,1700843,2536859,4742872,4955535,1260540,3605246,2770338,1855168,1666915,1555467,1008919,1227619,1015853,384076,295687,1328674,1492829,1484812,1868314,1253406,887933,1153403,1249023,1423973,1060162,1080597,1156442,2222640,2587311,2178351,3121089,2857420,1702477,1531670,1863424,1987392,2505586,9620218,2561608,3633991,3324070,1560020,1429188,1754144,1626020,1739228,1722735,1538145,1473412,1498968,2247334,3156442,1895098,1939135,1842874,2235830,2202171,2242042,1081763,2409013,1615028,1413467,1632450,5664827,4578115,1783835,1093613,975642,1658005,3055257,5355572,3278424,2318501,2473561,1730311,1455812,2869222,3226650,2705936,2998622,2928342,3059979,3367422,1950694,1541020,2926720,2991202,3002106,2015412,2894863,2185316,3370605,3492243,1307592,1881404,1806471,1945842,2538877,2298557,2831497,3200905,2180586,1500505,1939246,1599193,2364826,2517454,1883143,1726706,707364,796460,596962,947625,832859,151562,90390,50278,26471,56059]

def get_chunk_size(quality, index):
    if ( index < 0 or index > TOTAL_VIDEO_CHUNKS ):
        return 0
    # note that the quality and video labels are inverted (i.e., quality 8 is highest and this pertains to video1)
    sizes = {5: size_video1[index], 4: size_video2[index], 3: size_video3[index], 2: size_video4[index], 1: size_video5[index], 0: size_video6[index]}
    return sizes[quality]

def make_request_handler(input_dict):

    class Request_Handler(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.input_dict = input_dict
            self.log_file = input_dict['log_file']
            #self.saver = input_dict['saver']
            self.s_batch = input_dict['s_batch']
            self.bw_file = input_dict['log_bw']
            # hard code the entire trace here
            self.ground_truth = truth_bw
            # self.startup_time = time.time()
            #self.a_batch = input_dict['a_batch']
            #self.r_batch = input_dict['r_batch']
            BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length))
            print post_data

            if ( 'pastThroughput' in post_data ):
                # @Hongzi: this is just the summary of throughput/quality at the end of the load
                # so we don't want to use this information to send back a new quality
                print "Summary: ", post_data
            else:
                # option 1. reward for just quality
                # reward = post_data['lastquality']
                # option 2. combine reward for quality and rebuffer time
                #           tune up the knob on rebuf to prevent it more
                # reward = post_data['lastquality'] - 0.1 * (post_data['RebufferTime'] - self.input_dict['last_total_rebuf'])
                # option 3. give a fixed penalty if video is stalled
                #           this can reduce the variance in reward signal
                # reward = post_data['lastquality'] - 10 * ((post_data['RebufferTime'] - self.input_dict['last_total_rebuf']) > 0)

                # option 4. use the metric in SIGCOMM MPC paper
                rebuffer_time = float(post_data['RebufferTime'] -self.input_dict['last_total_rebuf'])

                # --linear reward--
                reward = VIDEO_BIT_RATE[post_data['lastquality']] / M_IN_K \
                        - REBUF_PENALTY * rebuffer_time / M_IN_K \
                        - SMOOTH_PENALTY * np.abs(VIDEO_BIT_RATE[post_data['lastquality']] -
                                                  self.input_dict['last_bit_rate']) / M_IN_K

                # --log reward--
                # log_bit_rate = np.log(VIDEO_BIT_RATE[post_data['lastquality']] / float(VIDEO_BIT_RATE[0]))   
                # log_last_bit_rate = np.log(self.input_dict['last_bit_rate'] / float(VIDEO_BIT_RATE[0]))

                # reward = log_bit_rate \
                #          - 4.3 * rebuffer_time / M_IN_K \
                #          - SMOOTH_PENALTY * np.abs(log_bit_rate - log_last_bit_rate)

                # --hd reward--
                # reward = BITRATE_REWARD[post_data['lastquality']] \
                #         - 8 * rebuffer_time / M_IN_K - np.abs(BITRATE_REWARD[post_data['lastquality']] - BITRATE_REWARD_MAP[self.input_dict['last_bit_rate']])

                self.input_dict['last_bit_rate'] = VIDEO_BIT_RATE[post_data['lastquality']]
                self.input_dict['last_total_rebuf'] = post_data['RebufferTime']

                # retrieve previous state
                if len(self.s_batch) == 0:
                    state = [np.zeros((S_INFO, S_LEN))]
                else:
                    state = np.array(self.s_batch[-1], copy=True)

                # compute bandwidth measurement
                video_chunk_fetch_time = post_data['lastChunkFinishTime'] - post_data['lastChunkStartTime']
                video_chunk_size = post_data['lastChunkSize']

                # compute number of video chunks left
                video_chunk_remain = TOTAL_VIDEO_CHUNKS - self.input_dict['video_chunk_coount']
                self.input_dict['video_chunk_coount'] += 1

                # dequeue history record
                state = np.roll(state, -1, axis=1)

                # this should be S_INFO number of terms
                try:
                    state[0, -1] = VIDEO_BIT_RATE[post_data['lastquality']] / float(np.max(VIDEO_BIT_RATE))
                    state[1, -1] = post_data['buffer'] / BUFFER_NORM_FACTOR
                    state[2, -1] = rebuffer_time / M_IN_K
                    state[3, -1] = float(video_chunk_size) / float(video_chunk_fetch_time) / M_IN_K  # kilo byte / ms
                    state[4, -1] = np.minimum(video_chunk_remain, CHUNK_TIL_VIDEO_END_CAP) / float(CHUNK_TIL_VIDEO_END_CAP)
                except ZeroDivisionError:
                    # this should occur VERY rarely (1 out of 3000), should be a dash issue
                    # in this case we ignore the observation and roll back to an eariler one
                    if len(self.s_batch) == 0:
                        state = [np.zeros((S_INFO, S_LEN))]
                    else:
                        state = np.array(self.s_batch[-1], copy=True)

                # log wall_time, bit_rate, buffer_size, rebuffer_time, video_chunk_size, download_time, reward
                self.log_file.write(str(time.time()) + '\t' +
                                    str(VIDEO_BIT_RATE[post_data['lastquality']]) + '\t' +
                                    str(post_data['buffer']) + '\t' +
                                    str(rebuffer_time / M_IN_K) + '\t' +
                                    str(video_chunk_size) + '\t' +
                                    str(video_chunk_fetch_time) + '\t' +
                                    str(reward) + '\n')
                self.log_file.flush()

                # pick bitrate according to MPC           
                # first get harmonic mean of last 5 bandwidths
                past_bandwidths = state[3,-5:]
                while past_bandwidths[0] == 0.0:
                    past_bandwidths = past_bandwidths[1:]
                #if ( len(state) < 5 ):
                #    past_bandwidths = state[3,-len(state):]
                #else:
                #    past_bandwidths = state[3,-5:]
                bandwidth_sum = 0
                for past_val in past_bandwidths:
                    bandwidth_sum += (1/float(past_val))
                future_bandwidth = 1.0/(bandwidth_sum/len(past_bandwidths))
                # print("future bandwidth est = %d" % future_bandwidth)
                # print("time passed since start: %f" % (time.time()-startup_time))

                future_bandwidth_sum = 0
                for idx in range(2):
                    try:
                        future_bandwidth_sum += (1/self.ground_truth[int(time.time()-startup_time)+idx])
                    except ZeroDivisionError:
                        future_bandwidth_sum += 100000    
                future_bandwidth_truth = 1.0/(future_bandwidth_sum/2)
                self.bw_file.write(str(time.time()) + '\t' + str(future_bandwidth_truth) + '\n')
                self.bw_file.flush()
                # future_bandwidth_truth = (self.ground_truth[int(time.time()-startup_time)] )/1
                # print("future bandwidth = %d" % future_bandwidth_truth)

                # future chunks length (try 4 if that many remaining)
                last_index = int(post_data['lastRequest'])
                future_chunk_length = MPC_FUTURE_CHUNK_COUNT
                if ( TOTAL_VIDEO_CHUNKS - last_index < 4 ):
                    future_chunk_length = TOTAL_VIDEO_CHUNKS - last_index

                # all possible combinations of 5 chunk bitrates (9^5 options)
                # iterate over list and for each, compute reward and store max reward combination
                max_reward = -100000000
                best_combo = ()
                start_buffer = float(post_data['buffer'])
                #start = time.time()
                for full_combo in CHUNK_COMBO_OPTIONS:
                    combo = full_combo[0:future_chunk_length]
                    # calculate total rebuffer time for this combination (start with start_buffer and subtract
                    # each download time and add 2 seconds in that order)
                    curr_rebuffer_time = 0
                    curr_buffer = start_buffer
                    bitrate_sum = 0
                    smoothness_diffs = 0
                    last_quality = int(post_data['lastquality'])
                    for position in range(0, len(combo)):
                        chunk_quality = combo[position]
                        index = last_index + position + 1 # e.g., if last chunk is 3, then first iter is 3+0+1=4
                        download_time = (get_chunk_size(chunk_quality, index)/1000000.)/(future_bandwidth_truth+0.0001) # this is MB/MB/s --> seconds
                        if ( curr_buffer < download_time ):
                            curr_rebuffer_time += (download_time - curr_buffer)
                            curr_buffer = 0
                        else:
                            curr_buffer -= download_time
                        curr_buffer += 1
                        
                        # linear reward
                        bitrate_sum += VIDEO_BIT_RATE[chunk_quality]
                        smoothness_diffs += abs(VIDEO_BIT_RATE[chunk_quality] - VIDEO_BIT_RATE[last_quality])

                        # log reward
                        # log_bit_rate = np.log(VIDEO_BIT_RATE[chunk_quality] / float(VIDEO_BIT_RATE[0]))
                        # log_last_bit_rate = np.log(VIDEO_BIT_RATE[last_quality] / float(VIDEO_BIT_RATE[0]))
                        # bitrate_sum += log_bit_rate
                        # smoothness_diffs += abs(log_bit_rate - log_last_bit_rate)

                        # hd reward
                        # bitrate_sum += BITRATE_REWARD[chunk_quality]
                        # smoothness_diffs += abs(BITRATE_REWARD[chunk_quality] - BITRATE_REWARD[last_quality])

                        last_quality = chunk_quality
                    # compute reward for this combination (one reward per 5-chunk combo)
                    # bitrates are in Mbits/s, rebuffer in seconds, and smoothness_diffs in Mbits/s

                    # linear reward 
                    reward = (bitrate_sum/1000.) - (160*curr_rebuffer_time) - (smoothness_diffs/1000.)

                    # log reward
                    # reward = (bitrate_sum) - (4.3*curr_rebuffer_time) - (smoothness_diffs)

                    # hd reward
                    # reward = bitrate_sum - (8*curr_rebuffer_time) - (smoothness_diffs)

                    if ( reward > max_reward ):
                        max_reward = reward
                        best_combo = combo
                # send data to html side (first chunk of best combo)
                send_data = 0 # no combo had reward better than -1000000 (ERROR) so send 0
                if ( best_combo != () ): # some combo was good
                    # print("best combo is")
                    # print(best_combo)
                    send_data = str(best_combo[0])

                end = time.time()
                #print "TOOK: " + str(end-start)

                end_of_video = False
                if ( post_data['lastRequest'] == TOTAL_VIDEO_CHUNKS ):
                    send_data = "REFRESH"
                    end_of_video = True
                    self.input_dict['last_total_rebuf'] = 0
                    self.input_dict['last_bit_rate'] = DEFAULT_QUALITY
                    self.input_dict['video_chunk_coount'] = 0
                    # self.log_file.write('\n')  # so that in the log we know where video ends

                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-Length', len(send_data))
                self.send_header('Access-Control-Allow-Origin', "*")
                self.end_headers()
                self.wfile.write(send_data)

                # record [state, action, reward]
                # put it here after training, notice there is a shift in reward storage

                if end_of_video:
                    self.s_batch = [np.zeros((S_INFO, S_LEN))]
                else:
                    self.s_batch.append(state)

        def do_GET(self):
            print >> sys.stderr, 'GOT REQ'
            self.send_response(200)
            #self.send_header('Cache-Control', 'Cache-Control: no-cache, no-store, must-revalidate max-age=0')
            self.send_header('Cache-Control', 'max-age=3000')
            self.send_header('Content-Length', 20)
            self.end_headers()
            self.wfile.write("console.log('here');")

        def log_message(self, format, *args):
            return

    return Request_Handler


def run(server_class=HTTPServer, port=8333, log_file_path=LOG_FILE, bw_file_path=LOG_BW):

    np.random.seed(RANDOM_SEED)

    if not os.path.exists(SUMMARY_DIR):
        os.makedirs(SUMMARY_DIR)

    # make chunk combination options
    for combo in itertools.product([0,1,2,3,4,5], repeat=5):
        CHUNK_COMBO_OPTIONS.append(combo)

    with open(log_file_path, 'wb') as log_file:
        with open(bw_file_path, 'wb') as bw_file:
            bw_file.write(str(startup_time)+'\n')
            s_batch = [np.zeros((S_INFO, S_LEN))]

            last_bit_rate = DEFAULT_QUALITY
            last_total_rebuf = 0
            # need this storage, because observation only contains total rebuffering time
            # we compute the difference to get

            video_chunk_count = 0

            input_dict = {'log_file': log_file,
                        'log_bw': bw_file,
                        'last_bit_rate': last_bit_rate,
                        'last_total_rebuf': last_total_rebuf,
                        'video_chunk_coount': video_chunk_count,
                        's_batch': s_batch}

            # interface to abr_rl server
            handler_class = make_request_handler(input_dict=input_dict)

            server_address = ('localhost', port)
            httpd = server_class(server_address, handler_class)
            print 'Listening on port ' + str(port)
            httpd.serve_forever()


def main():
    startup_time = time.time()
    if len(sys.argv) == 2:
        trace_file = sys.argv[1]
        run(log_file_path=LOG_FILE + '_truthMPC_' + trace_file, bw_file_path=LOG_BW + '_truthMPC_' + trace_file)
    else:
        run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "Keyboard interrupted."
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
