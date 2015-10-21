#!flask/bin/python

from flask import Flask, jsonify, request, render_template, url_for
from celery import group
import sys
import os
import time
from proj import convertFile
import subprocess
from plot_result import plot_file
from save_to_db import to_db, in_db

app = Flask(__name__, template_folder="/home/ubuntu/naca_airfoil")

@app.route('/')
def form():
	return render_template('site/form_submit.html')

@app.route('/runsh/', methods=['POST'])
def runsh():
	angle_start=request.form['angle_start']
	angle_stop=request.form['angle_stop']
	n_angles=request.form['n_angles']
	n_nodes=request.form['n_nodes']
	n_levels=request.form['n_levels']
	num_samples=request.form['num_samples']
	visc=request.form['visc']
	speed=request.form['speed']
	T=request.form['T']
	print 1, "- - - - - - - - Run start - - - - - - - -"
	###########################
	##### Check if exists #####
	###########################
	#anglediff=$((($angle_stop-$angle_start)/$n_angles))

	anglediff = (int(angle_stop) - int(angle_start)) / int(n_angles)
	
	angles = []
	for i in range(0, int(n_angles)):
		print 1, i
		angle = 0
		angle = (int(angle_start) + anglediff * i)
		if in_db("r" + n_levels + "a" + str(angle) + "n" + n_nodes + "N" + num_samples + "v" + visc + "s" + speed + "T" + T + ".msh") == False :
			print "Ja en vinkel!"
			angles.append(angle)
	
	if len(angles) != 0:
		print "Nu skickas allt ivag :)"
		response = group(convertFile.s(angle, n_nodes, n_levels, num_samples, visc, speed, T) for angle in angles)
		result = response.apply_async()
		result.get()


		########################
		##### Create *.msh #####
		########################
		#time_1 = time.time()
		#subprocess.call(["./run.sh", angle_start, angle_stop, n_angles, n_nodes, n_levels])
		#time_2 = time.time()
		#print 2, time_2 - time_1
		#############################################
		##### Convert *.msh to *.xml + lite mer #####
		#############################################
		#appLocation = app.root_path
		#fileLocation = appLocation + "/msh/"
		#content = sorted(os.listdir(fileLocation))
		#response = group(convertFile.s(fileName, open(fileLocation+fileName, "r").read()) for fileName in content)
		#result = response.apply_async()
		#result.get()
		#time_3 = time.time()
		#print 3, time_3 - time_2


		####################################
		#for t in result.get():
		#	(fileNamePlot, data) = t
		#	plot_file(fileNamePlot, data)
		#	to_db(fileNamePlot, "")
		#os.system("rm -rf  msh/*")
		#os.system("rm -rf  geo/*")
		#os.system("mv *.png pictures/")
		#####################################

		
		##subprocess.call(["mv", "*.png", "pictures/"])

	return render_template('site/runsh.html', 
							angle_start=angle_start, 
							angle_stop=angle_stop, 
							n_angles=n_angles, 
							n_nodes=n_nodes, 
							n_levels=n_levels)

if __name__ == "__main__":
	app.run(host="0.0.0.0", debug=True )