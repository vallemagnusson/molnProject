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

from multiprocessing import Process
from workerSetup import createWorker, terminateWorker

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

	######################################################
	# Test
	######################################################
	run_args = {}
	run_args['angle_start']=str(request.form['angle_start'])
	run_args['angle_stop']=str(request.form['angle_stop'])
	run_args['n_angles']=str(request.form['n_angles'])
	run_args['n_nodes']=str(request.form['n_nodes'])
	run_args['n_levels']=str(request.form['n_levels'])
	print run_args
	airfoil_args = {}
	airfoil_args['num_samples'] = str(request.form['num_samples'])
	airfoil_args['visc'] = str(request.form['visc'])
	airfoil_args['speed'] = str(request.form['speed'])
	airfoil_args['T'] = str(request.form['T'])
	print airfoil_args
	######################################################

	######################################################
	# Start worker
	######################################################
	jobs = []
	jobsReturn = []
	for i in range(2):
		p = Process(target=createWorker, args=(str(i)))
		jobs.append(p)
		p.start()
		jobsReturn.append("MavaServerProj-worker"+str(i))

	print 1, "- - - - - - - - Run start - - - - - - - -"
	###########################
	##### Check if exists #####
	###########################
	anglediff = (int(angle_stop) - int(angle_start)) / int(n_angles)
	
	angles = []
	list_of_pictures = []
	missing_pictures = []
	dispaly_list = []

	(response, container_list) = conn.get_container(bucket_name)
	for container in container_list:
		list_of_pictures.append( container['name'] )

	############# Maste goras om.... #########################
	for i in range(0, int(n_angles)):

		angle = 0
		angle = (int(angle_start) + anglediff * i)
		#print 1, angle
		for level in range(int(n_levels)+1):
			pictureName = "r" + str(level) + "a" + str(angle) + "n" + n_nodes + "Num" + num_samples + "Visc" + visc + "Speed" + speed + "T" + T +".png"
			if pictureName not in list_of_pictures:
				angles.append((angle,level))
				missing_pictures.append(pictureName)
			else:
				new_picture = open(pictureName, "w")
				(head, picture) = conn.get_object(bucket_name, pictureName)
				new_picture.write(picture)
				dispaly_list.append(pictureName)
				new_picture.close()
	print dispaly_list

	print "Number of tasks: " + str(len(missing_pictures))
	if len(angles) != 0:
		print "Nu skickas allt ivag :)"
		time_to_calculate = time.time()
		response = group(convertFile.s(str(angle), n_nodes, str(level), num_samples, visc, speed, T) for (angle, level) in angles)
		print "Time for response: " + str(time.time() - time_to_calculate)

		time_to_calculate_2 = time.time()
		result = response.apply_async()
		print "Time for result var: " + str(time.time() - time_to_calculate_2)
		while len(missing_pictures) != 0:
			try:
				for pictureName in missing_pictures:
					(head, picture) = conn.get_object(bucket_name, pictureName)
					new_picture = open(pictureName, "w")
					new_picture.write(picture)
					dispaly_list.append(pictureName)
					new_picture.close()
					missing_pictures.remove(pictureName)
					print "Got picture: " + str(pictureName)
			except:
				pass
		print "Starting result.get()"
		result.get()
		print "Time to calculate all: " + str(time.time() - time_to_calculate)

		print dispaly_list

		for pictureName in result.get():
			new_picture = open(pictureName + ".png", "w")
			(head, picture) = conn.get_object(bucket_name, pictureName + ".png")
			new_picture.write(picture)
			dispaly_list.append(pictureName + ".png")
			new_picture.close()

		print dispaly_list
	for workerName in jobsReturn:
		terminateWorker(workerName)
		#os.system("sudo rm -rf " + dataBaseName)
	return render_template('site/runsh.html', 
							angle_start=angle_start, 
							angle_stop=angle_stop, 
							n_angles=n_angles, 
							n_nodes=n_nodes, 
							n_levels=n_levels)

if __name__ == "__main__":
	app.run(host="0.0.0.0", debug=True )