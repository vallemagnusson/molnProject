#!/usr/bin/python
###############################################################################
#
# Name: plot_file
# Arguments (0):
# 	
# Output: 
# Example:
###############################################################################
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os.path
import numpy as np

###############################################################################
# Takes a .m file that is created by the airfoil binary and creates a plot 
# from the data. Must be in the same directory as the .m file
# Arguments:
#	filename: Path o the file
###############################################################################
def plot_file(filename, data):
	#f = open("drag_ligt.m", "r")
	#s = f.read().split('\n')
	time = np.array(data[0], dtype= float)
	lift = np.array(data[1], dtype= float)
	drag = np.array(data[2], dtype= float)
	#for line in s[1:]:
	#	l = line.split(' ')
	#	elemlist = []
	#	for element in l:
	#		if not element == "":
	#			elemlist.append(element)
	#	time.append(elemlist[0])
	#	drag.append(elemlist[1])
	#	lift.append(elemlist[2])
	plt.gca().set_color_cycle(['blue', 'red'])
	plt.plot(time, drag)
	plt.plot(time, lift)
	plt.grid(True)

	plt.legend(['Drag force', 'Lift force'])
	plt.xlabel('Time')
	plt.ylabel('Force')
	plt.title(filename)
	plt.yscale('log')
	plt.savefig(filename, format='png')
	plt.clf()
	#save("signal", ext="png", close=False, verbose=True)
	#image = open(os.path.splitext(filename)[0] + '.png', "w")
	#plt.savefig(image, format = "png")