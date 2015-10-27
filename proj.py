#!flask/bin/python

import os
import json
import time
import sys
import time
import shutil
import celery
from celery import Celery
from collections import Counter
import urllib2
import subprocess
from plot_result import plot_file
import swiftclient.client

#celery.config_from_object('celeryconfig')
app = Celery('proj')
app.config_from_object('celeryconfig')
config = {'user':os.environ['OS_USERNAME'], 
          'key':os.environ['OS_PASSWORD'],
          'tenant_name':os.environ['OS_TENANT_NAME'],
          'authurl':os.environ['OS_AUTH_URL']}

conn = swiftclient.client.Connection(auth_version=2, **config)

bucket_name = "MavaPictureConatiner"


#app = Celery()#'proj', backend='amqp', broker='amqp://mava:orkarinte@130.238.29.120:5672/app2')

@app.task
def convertFile(angle, n_nodes, n_levels, num_samples, visc, speed, T):
	fileName = "r" + n_levels + "a" + str(angle) + "n" + n_nodes + ".msh"
	fileNameWithoutExtension = os.path.splitext(fileName)[0]
	xmlFileName = fileNameWithoutExtension + ".xml"
	subprocess.call(["mkdir", fileNameWithoutExtension])
	subprocess.call(['chmod', '-R', '777', fileNameWithoutExtension])
	print 1, "Started to process file: " + str(fileName)
	subprocess.call(["cp", "-a", "run.sh", fileNameWithoutExtension])
	subprocess.call(["cp", "-a", "naca2gmsh_geo.py", fileNameWithoutExtension])
	subprocess.call(["cp", "-a", "airfoil", fileNameWithoutExtension])
	subprocess.call(["mkdir", "msh"], cwd=fileNameWithoutExtension+"/")
	subprocess.call(["mkdir", "geo"], cwd=fileNameWithoutExtension+"/")
	subprocess.call(['chmod', '-R', '777', fileNameWithoutExtension+"/msh"])
	subprocess.Popen(["sudo", "./run.sh", str(angle), str(angle), "1", n_nodes, n_levels], cwd=fileNameWithoutExtension+"/")
	
	fileLocation = "/home/ubuntu/molnProject/" + fileNameWithoutExtension + "/msh/"
	content = sorted(os.listdir(fileLocation))
	print 2, "Files in msh-directory: " + str(content)
	while fileName not in content:
		print "Making msh not ready"
		time.sleep(0.5)
		content = sorted(os.listdir(fileLocation))

	subprocess.call(["dolfin-convert", "msh/"+fileName, xmlFileName], cwd=fileNameWithoutExtension+"/")

	##########################################
	########## Run airfoil on file ###########
	##########################################
	num = str(num_samples)
	visc_s = str(visc)
	speed_s = str(speed)
	T_s = str(T)
	subprocess.call(["./airfoil", num, visc_s, speed_s, T_s, xmlFileName], cwd=fileNameWithoutExtension+"/")
	##########################################
	######### Get drag_ligt.m values #########
	##########################################
	#while "results" not in content:
	#	print "result form airfoil not ready"
	#	content = sorted(os.listdir(fileLocation))
	resultLists = readFile("/home/ubuntu/molnProject/" +fileNameWithoutExtension+"/results/drag_ligt.m")
	#!!!!!!!!!!!!!os.system("rm -rf " + fileNameWithoutExtension + "*")
	#!!!!!!!!!!!!!os.system("rm -rf  msh/*")
	#!!!!!!!!!!!!!os.system("rm -rf  geo/*")
	#!!!!!!!!!!!!!return (fileNameWithoutExtension+"N"+num+"v"+visc_s+"s"+speed_s+"T"+T_s+".msh", resultLists)
	plot_file(fileName, data)
	object_id = conn.put_object(bucket_name, fileNameWithoutExtension+".png")
	return ("hej",[[],[],[]])
	
@app.task
def readFile(fileName):
	theFile = open(fileName, "r").read()
	timeColumn = []
	liftColumn = []
	dragColumn = []
	lines = open(fileName, "r").readlines()
	for x in range(1, len(lines)):
		time = lines[x].strip().split()[0]
		timeColumn.append(time)
		lift = lines[x].strip().split()[1]
		liftColumn.append(lift)
		drag = lines[x].strip().split()[2]
		dragColumn.append(drag)
	resultList = []
	resultList.append(timeColumn)
	resultList.append(liftColumn)
	resultList.append(dragColumn)
	return resultList








