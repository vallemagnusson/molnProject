import os

with open('userdatafiles/server_userdata_for_worker.yml', 'r') as file:
    data = file.readlines()

i = 0

for line in data:
	if "export BROKER_USER=" in line:
		data[i] = '    - export BROKER_USER='+ os.environ['BROKER_USER'] + '\n'
	elif "export BROKER_PASS=" in line:
		data[i] = '    - export BROKER_PASS='+ os.environ['BROKER_PASS'] + '\n'
	elif "export FLOATING_IP=" in line:
		data[i] = '    - export FLOATING_IP='+ os.environ['FLOATING_IP'] + '\n'
	elif "export OS_AUTH_URL=" in line:
		data[i] = '    - export OS_AUTH_URL='+ os.environ['OS_AUTH_URL'] + '\n'
	elif "export OS_TENANT_ID=" in line:
		data[i] = '    - export OS_TENANT_ID='+ os.environ['OS_TENANT_ID'] + '\n'
	elif "export OS_TENANT_NAME=" in line:
		data[i] = '    - export OS_TENANT_NAME='+ os.environ['OS_TENANT_NAME'] + '\n'
	elif "export OS_PROJECT_NAME=" in line:
		data[i] = '    - export OS_PROJECT_NAME='+ os.environ['OS_PROJECT_NAME'] + '\n'
	elif "export OS_USERNAME=" in line:
		data[i] = '    - export OS_USERNAME='+ os.environ['OS_USERNAME'] + '\n'
	elif "export OS_PASSWORD=" in line:
		data[i] = '    - export OS_PASSWORD='+ os.environ['OS_PASSWORD'] + '\n'
	elif "export OS_REGION_NAME=" in line:
		data[i] = '    - export OS_REGION_NAME='+ os.environ['OS_REGION_NAME'] + '\n'
	i +=1
#data[i] = '    - export FLOATING_IP='+ ip +'\n'
#print data
#print data[i]

with open('userdatafiles/server_userdata_for_worker.yml', 'w') as file:
    file.writelines( data )