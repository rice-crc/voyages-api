import time


def timer(label,times,done=False):
	
	times.append([time.time(),label])
	if done:
		print('--timings--')
		for i in range(1,len(times)):
			print(times[i-1][1],times[i][0]-times[i-1][0])
	else:
		return times

