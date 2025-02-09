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

################## ROBUST MPC ###################

S_INFO = 5  # bit_rate, buffer_size, rebuffering_time, bandwidth_measurement, chunk_til_video_end
S_LEN = 8  # take how many frames in the past
MPC_FUTURE_CHUNK_COUNT = 5
# VIDEO_BIT_RATE = [300,750,1200,1850,2850,4300]  # Kbps
# BITRATE_REWARD = [1, 2, 3, 12, 15, 20]
# BITRATE_REWARD_MAP = {0: 0, 300: 1, 750: 2, 1200: 3, 1850: 12, 2850: 15, 4300: 20}
VIDEO_BIT_RATE = [20000, 40000, 60000, 80000, 110000, 160000]  # Kbps
BITRATE_REWARD = [1, 2, 3, 12, 15, 20]
BITRATE_REWARD_MAP = {0: 0, 20000: 1, 40000: 2, 60000: 3, 80000: 12, 110000: 15, 160000: 20}
M_IN_K = 1000.0
BUFFER_NORM_FACTOR = 10.0
# CHUNK_TIL_VIDEO_END_CAP = 48.0
# TOTAL_VIDEO_CHUNKS = 48
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

CHUNK_COMBO_OPTIONS = []

# past errors in bandwidth
past_errors = []
past_bandwidth_ests = []

# video chunk sizes
# size_video1 = [2354772, 2123065, 2177073, 2160877, 2233056, 1941625, 2157535, 2290172, 2055469, 2169201, 2173522, 2102452, 2209463, 2275376, 2005399, 2152483, 2289689, 2059512, 2220726, 2156729, 2039773, 2176469, 2221506, 2044075, 2186790, 2105231, 2395588, 1972048, 2134614, 2164140, 2113193, 2147852, 2191074, 2286761, 2307787, 2143948, 1919781, 2147467, 2133870, 2146120, 2108491, 2184571, 2121928, 2219102, 2124950, 2246506, 1961140, 2155012, 1433658]
# size_video2 = [1728879, 1431809, 1300868, 1520281, 1472558, 1224260, 1388403, 1638769, 1348011, 1429765, 1354548, 1519951, 1422919, 1578343, 1231445, 1471065, 1491626, 1358801, 1537156, 1336050, 1415116, 1468126, 1505760, 1323990, 1383735, 1480464, 1547572, 1141971, 1498470, 1561263, 1341201, 1497683, 1358081, 1587293, 1492672, 1439896, 1139291, 1499009, 1427478, 1402287, 1339500, 1527299, 1343002, 1587250, 1464921, 1483527, 1231456, 1364537, 889412]
# size_video3 = [1034108, 957685, 877771, 933276, 996749, 801058, 905515, 1060487, 852833, 913888, 939819, 917428, 946851, 1036454, 821631, 923170, 966699, 885714, 987708, 923755, 891604, 955231, 968026, 874175, 897976, 905935, 1076599, 758197, 972798, 975811, 873429, 954453, 885062, 1035329, 1026056, 943942, 728962, 938587, 908665, 930577, 858450, 1025005, 886255, 973972, 958994, 982064, 830730, 846370, 598850]
# size_video4 = [668286, 611087, 571051, 617681, 652874, 520315, 561791, 709534, 584846, 560821, 607410, 594078, 624282, 687371, 526950, 587876, 617242, 581493, 639204, 586839, 601738, 616206, 656471, 536667, 587236, 590335, 696376, 487160, 622896, 641447, 570392, 620283, 584349, 670129, 690253, 598727, 487812, 575591, 605884, 587506, 566904, 641452, 599477, 634861, 630203, 638661, 538612, 550906, 391450]
# size_video5 = [450283, 398865, 350812, 382355, 411561, 318564, 352642, 437162, 374758, 362795, 353220, 405134, 386351, 434409, 337059, 366214, 360831, 372963, 405596, 350713, 386472, 399894, 401853, 343800, 359903, 379700, 425781, 277716, 400396, 400508, 358218, 400322, 369834, 412837, 401088, 365161, 321064, 361565, 378327, 390680, 345516, 384505, 372093, 438281, 398987, 393804, 331053, 314107, 255954]
# size_video6 = [181801, 155580, 139857, 155432, 163442, 126289, 153295, 173849, 150710, 139105, 141840, 156148, 160746, 179801, 140051, 138313, 143509, 150616, 165384, 140881, 157671, 157812, 163927, 137654, 146754, 153938, 181901, 111155, 153605, 149029, 157421, 157488, 143881, 163444, 179328, 159914, 131610, 124011, 144254, 149991, 147968, 161857, 145210, 172312, 167025, 160064, 137507, 118421, 112270]
# 8k
# size_video1 = [15253753,34556096,19644535,10066599,32683868,30130938,21957223,16288319,9191375,22895873,21998130,25828233,15039004,62128224,13083969,11588086,9557061,10108832,10180766,11190449,33361467,24151255,20899456,14936176,8745453,6570733,1769183,8675719,11509440,10062929,11138265,12171499,11432319,20961512,22564240,19139082,14777942,16631652,37620029,22309940,11404773,12423529,12880959,11213112,14132175,17139707,16034969,18080837,11820034,11882604,10940529,38143287,9424897,8463278,31065185,18461833,15566131,17520693,22043849,18878529,22248430,13980128,24491279,20224959,19282364,22049239,13209398,14520305,17085880,19048461,14340141,13187047,18415308,14407916,6758451,6939715,4912416,1228596,530527,241671]
# size_video2 = [14873297,24595261,11966223,6808732,20422885,21973953,16204240,11606087,5816943,16836685,16519831,19377829,11005862,46175278,9176078,8141427,6752215,7258770,7373714,7889903,24292090,17756817,15128546,10146258,6041545,4638173,1218761,6079827,8040823,6660632,7466316,8233649,7627057,14646188,15789630,13354725,10273240,11852521,27890869,16277165,7979760,8826934,9136841,7863065,10003526,12395673,11061679,12566435,8328347,8389320,7718776,27997303,6612882,5687524,22976142,13649163,11038883,12170129,15426457,12993218,15701444,9782287,17069495,14195830,13668172,16127039,9181228,10093907,12260677,14178820,10209056,9161234,13003818,9978479,4619345,4744291,2915344,706424,203289,145941]
# size_video3 = [60760650,59174725,50237417,66051093,54872073,88592377,70604433,52644356,55468059,54230376,53861982,54577901,57126197,46104151,69587410,104068986,80938366,68337492,48959061,48819589,47559729,50043292,92760063,75615247,44382285,39412071,34944133,30405596,36042825,53737364,57501288,64686726,73899866,71303449,70813311,65844309,50490272,61933227,50489415,58394937,62185197,74322179,85684691,128245537,40226732,40011331,78843767,61928912,112457449,69151289,41184932,29478341,11824]
# size_video4 = [29700316,29587424,26315062,31774421,27006801,45216498,36040295,25840669,28398177,28484202,27066243,25578427,27551849,24920008,36654104,52768718,40205941,33718648,21571126,23164113,23996786,27849536,48279510,38166908,20867513,18042633,16549204,14284053,16963654,26146149,28228610,31918738,36612829,34429493,35726757,34380794,24580925,30183972,25391558,30177277,31719424,38541526,44893558,67647209,19969127,19415494,39453592,33102169,58282626,34908443,18975181,12769791,11820]
# size_video5 = [14708410,14903498,13102024,15417444,13636505,23148946,18553574,12737019,14147690,14161095,13406118,12533244,13560438,13644835,19686762,27179161,20255202,16904711,9457396,10969437,12925031,16377722,24555017,18827437,9854124,8095209,7526639,6380584,8166671,11191736,12458185,14723634,18001632,16926336,18205469,17617001,12440186,15690806,13343533,15277189,14351462,19155149,23485317,36239992,10485035,9424453,19944248,19719601,31330173,18105042,8803166,5349180,11813]
# size_video6 = [2348302,882136,281149,176963,747670,903121,681308,575613,119137,888845,982305,789306,721413,1567178,394992,435803,452066,405479,318382,325493,306434,264143,454316,338100,313756,323330,161126,450433,474912,247942,220331,272656,257991,492601,508186,470999,368518,460840,980113,1148925,331317,350042,350701,362142,385070,411463,400955,437316,350891,557485,421754,259774,354496,411061,392904,490770,451458,501280,716110,584539,818149,382050,519483,445610,473037,1085785,293705,349408,447965,437708,330841,426276,462274,336805,183487,172082,144336,42836,36811,8517]
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
            self.bw_file = input_dict['log_bw']
            #self.saver = input_dict['saver']
            self.s_batch = input_dict['s_batch']
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
                    curr_error = 0 # defualt assumes that this is the first request so error is 0 since we have never predicted bandwidth
                    if ( len(past_bandwidth_ests) > 0 ):
                        curr_error  = abs(past_bandwidth_ests[-1]-state[3,-1])/float(state[3,-1])
                    past_errors.append(curr_error)
                except ZeroDivisionError:
                    # this should occur VERY rarely (1 out of 3000), should be a dash issue
                    # in this case we ignore the observation and roll back to an eariler one
                    past_errors.append(0)
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
                harmonic_bandwidth = 1.0/(bandwidth_sum/len(past_bandwidths))

                # future bandwidth prediction
                # divide by 1 + max of last 5 (or up to 5) errors
                max_error = 0
                error_pos = -5
                if ( len(past_errors) < 5 ):
                    error_pos = -len(past_errors)
                max_error = float(max(past_errors[error_pos:]))
                future_bandwidth = harmonic_bandwidth/(1+max_error)
                past_bandwidth_ests.append(harmonic_bandwidth)
                self.bw_file.write(str(time.time()) + '\t' + str(future_bandwidth) + '\n')
                self.bw_file.flush()

                # future chunks length (try 4 if that many remaining)
                last_index = int(post_data['lastRequest'])
                future_chunk_length = MPC_FUTURE_CHUNK_COUNT
                if ( TOTAL_VIDEO_CHUNKS - last_index < 5 ):
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
                        download_time = (get_chunk_size(chunk_quality, index)/1000000.)/future_bandwidth # this is MB/MB/s --> seconds
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
    if len(sys.argv) == 2:
        trace_file = sys.argv[1]
        run(log_file_path=LOG_FILE + '_robustMPC_' + trace_file, bw_file_path=LOG_BW + '_robustMPC_' + trace_file)
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
