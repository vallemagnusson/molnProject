#!flask/bin/python

from flask import Flask, jsonify, request, render_template, url_for
from celery import group
import sys
import os
import time
from proj import convertFile
import subprocess
import swiftclient.client
#from plot_result import plot_file
from save_to_db import to_db, in_db

app = Flask(__name__, template_folder="/home/ubuntu/molnProject")

config = {'user':os.environ['OS_USERNAME'], 
          'key':os.environ['OS_PASSWORD'],
          'tenant_name':os.environ['OS_TENANT_NAME'],
          'authurl':os.environ['OS_AUTH_URL']}

conn = swiftclient.client.Connection(auth_version=2, **config)

bucket_name = "MavaPictureContainer"
dataBaseName = "pictureDatabase"

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
	anglediff = (int(angle_stop) - int(angle_start)) / int(n_angles)
	
	angles = []
	(header, fileContent) = conn.get_object(bucket_name, dataBaseName)
	dbFile = open(dataBaseName, "w")
	dbFile.write(fileContent)
	dbFile.close()

	############# Maste goras om.... #########################
	for i in range(0, int(n_angles)):

		angle = 0
		angle = (int(angle_start) + anglediff * i)
		print 1, angle
		for level in range(int(n_levels)+1):
			if in_db("r" + level + "a" + str(angle) + "n" + n_nodes + "Num" + num_samples + "Visc" + visc + "Speed" + speed + "T" + T) == False :
				print "Ja en vinkel!"
				angles.append((angle,level))
	print angles
	if len(angles) != 0:
		print "Nu skickas allt ivag :)"
		response = group(convertFile.s(angle, n_nodes, str(level), num_samples, visc, speed, T) for (angle, level) in angles)
		result = response.apply_async()
		result.get()

		####################################
		for t in result.get():
			fileNamePlot = t
			#plot_file(fileNamePlot, data)
			to_db(fileNamePlot, "")
		db = open(dataBaseName, "r")
		conn.put_object(bucket_name, dataBaseName, db)
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