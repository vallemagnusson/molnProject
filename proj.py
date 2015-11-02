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
from dolfin_convert import gmsh2xml

app = Celery('proj')
app.config_from_object('celeryconfig')
config = {'user':os.environ['OS_USERNAME'], 
          'key':os.environ['OS_PASSWORD'],
          'tenant_name':os.environ['OS_TENANT_NAME'],
          'authurl':os.environ['OS_AUTH_URL']}

conn = swiftclient.client.Connection(auth_version=2, **config)

bucket_name = "MavaPictureContainer"

@app.task
def convertFile(angle, n_nodes, n_levels, num_samples, visc, speed, T):
	#############################################################
	# Creating names and output place
	#############################################################
	FNULL = open(os.devnull, 'w')
	mshFileName = "r" + n_levels + "a" + str(angle) + "n" + n_nodes + ".msh"
	fileNameWithoutExtension = os.path.splitext(mshFileName)[0]
	xmlFileName = fileNameWithoutExtension + ".xml"
	mshFileLocation = "/home/ubuntu/molnProject/" + fileNameWithoutExtension + "/msh/"
	#############################################################
	# Remove folder if exists
	#############################################################
	content = sorted(os.listdir("/home/ubuntu/molnProject/"))
	if fileNameWithoutExtension in content:
		os.system("sudo rm -rf " + fileNameWithoutExtension + "*")
	#############################################################
	# Create layout for task
	#############################################################
	print "Started to process file: " + str(mshFileName)
	print "Copying and creating files and directorys"
	subprocess.check_call(["mkdir", fileNameWithoutExtension])
	subprocess.check_call(['chmod', '-R', '777', fileNameWithoutExtension])
	subprocess.check_call(["cp", "-a", "run.sh", fileNameWithoutExtension])
	subprocess.check_call(["cp", "-a", "naca2gmsh_geo.py", fileNameWithoutExtension])
	subprocess.check_call(["cp", "-a", "airfoil", fileNameWithoutExtension])
	subprocess.check_call(["mkdir", "msh"], cwd=fileNameWithoutExtension+"/")
	subprocess.check_call(["mkdir", "geo"], cwd=fileNameWithoutExtension+"/")
	subprocess.check_call(['chmod', '-R', '777', fileNameWithoutExtension+"/msh"])
	#############################################################
	# Running run.sh
	#############################################################
	print "Running run.sh..."
	subprocess.check_call(["sudo", "./run.sh", str(angle), str(angle), "1", n_nodes, n_levels], cwd=fileNameWithoutExtension+"/")
	#############################################################
	# Running dolfin-convert
	#############################################################
	print "Running dolfin-convert..."
	#subprocess.check_call(["sudo","dolfin-convert", "msh/"+mshFileName, xmlFileName], cwd=fileNameWithoutExtension+"/", stdout=FNULL, stderr=subprocess.STDOUT)
	gmsh2xml(mshFileLocation + mshFileName, xmlFileName)
	#############################################################
	# Run airfoil on file 
	#############################################################
	print "Running airfoil..."
	num = str(num_samples)
	visc_s = str(visc)
	speed_s = str(speed)
	T_s = str(T)
	subprocess.check_call(["sudo","./airfoil", num, visc_s, speed_s, T_s, xmlFileName], cwd=fileNameWithoutExtension+"/", stdout=FNULL, stderr=subprocess.STDOUT)
	#############################################################
	# Extracting information from frag_ligt.m 
	#############################################################	
	print "Getting drag_ligt.m to lists"
	resultLists = readFile("/home/ubuntu/molnProject/" +fileNameWithoutExtension+"/results/drag_ligt.m")
	pictureName = fileNameWithoutExtension + "Num" + num + "Visc" + visc_s + "Speed" + speed_s + "T" + T_s + ".png"
	dbName = fileNameWithoutExtension + "Num" + num + "Visc" + visc_s + "Speed" + speed_s + "T" + T_s
	#############################################################
	# Ploting the values and puting them in container 
	#############################################################
	print "Plot the values"
	plot_file(pictureName, resultLists)
	pictureFile = open(pictureName, "r")
	print "Sending png to container"
	object_id = conn.put_object(bucket_name, pictureName, pictureFile)
	os.system("sudo rm -rf " + fileNameWithoutExtension + "*")
	FNULL.close()
	return (dbName)
	
@app.task
def readFile(mshFileName):
	theFile = open(mshFileName, "r").read()
	timeColumn = []
	liftColumn = []
	dragColumn = []
	lines = open(mshFileName, "r").readlines()
	for x in range(1, len(lines)):
		time = lines[x].strip().split()[0]
		timeColumn.append(float(time))
		lift = lines[x].strip().split()[1]
		liftColumn.append(float(lift))
		drag = lines[x].strip().split()[2]
		dragColumn.append(float(drag))
	resultList = []
	resultList.append(timeColumn)
	resultList.append(liftColumn)
	resultList.append(dragColumn)
	return resultList








