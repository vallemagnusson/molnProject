import os

#a = os.listdir("./")
def addIP(ip):
	#print a
	with open('userdatafiles/worker_userdata.yml', 'r') as file:
	    # read a list of lines into data
	    data = file.readlines()

	i = 0

	for line in data:
		if "export FLOATING_IP=" in line:
			break
		i +=1
	data[i] = '    - export FLOATING_IP='+ ip +'\n'
	#print data
	#print data[i]

	with open('userdatafiles/worker_userdata.yml', 'w') as file:
	    file.writelines( data )