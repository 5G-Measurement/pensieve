import os


TOTAL_VIDEO_CHUNCK = 158
BITRATES = [20000, 40000, 60000, 80000, 110000, 160000]
BITRATE_LEVELS = 6
VIDEO_PATH = '../video_server/'
VIDEO_FOLDER = '4k'

# assume videos are in ../video_servers/video[1, 2, 3, 4, 5]
# the quality at video5 is the lowest and video1 is the highest


for bitrate in xrange(BITRATE_LEVELS):
	with open('video_size_' + str(bitrate), 'wb') as f:
		for chunk_num in range(1, TOTAL_VIDEO_CHUNCK+1):
			video_chunk_path = VIDEO_PATH + \
							   VIDEO_FOLDER + \
							   str(bitrate+1) + \
							   '/' + \
							   '4k_'+str(BITRATES[BITRATE_LEVELS - bitrate - 1])+'_dash'+str(chunk_num) + \
							   '.m4s'
			chunk_size = os.path.getsize(video_chunk_path)
			f.write(str(chunk_size) + '\n')
