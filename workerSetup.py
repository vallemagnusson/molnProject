import os
import swiftclient.client
import sys
import time
from novaclient.client import Client
#config = {'username':os.environ['OS_USERNAME'], 
#          'api_key':os.environ['OS_PASSWORD'],
#          'project_id':os.environ['OS_TENANT_NAME'],
#          'auth_url':os.environ['OS_AUTH_URL']}

#nc = Client('2',**config)
##import paramiko
def createWorker(nc, workerNumber):
  ##############################
  ##### Remove known_hosts #####
  ##############################
  os.system("rm -rf ~/.ssh/known_hosts")
  ##############################
  ########## Flavors ###########
  ##############################
  flavor = nc.flavors.find(name="m1.medium")
  ##############################
  ########### Images ###########
  ##############################
  #image = nc.images.find(name="Ubuntu Server 14.04 LTS (Trusty Tahr)")
  image = nc.images.find(name="MavaProjWorker")
  print image
  ##############################
  ########## Keypair ###########
  ##############################
  keypair = nc.keypairs.find(name="mava_keypair")
  ##############################
  ########## Network ###########
  ##############################
  network_a = nc.networks.find(label="ACC-Course-net")
  ##############################
  ###### Worker User Data ######
  ##############################
  #worker_userdata_file = open("userdatafiles/worker_userdata.yml","r")
  worker_userdata_file = open("userdatafiles/server_userdata_for_worker.yml","r")
  ##############################
  ######## Create Worker #######
  ##############################
  worker = nc.servers.create(name="MavaServerProj-worker"+str(workerNumber), image=image, flavor=flavor, userdata=worker_userdata_file, key_name=keypair.name, network=network_a)
  status = worker.status
  ##############################
  ########### Status ###########
  ##############################
  wait = 0
  while status == 'BUILD':
      print "Not ready... " + str(wait) + " seconds"
      time.sleep(1) 
      wait += 1
      worker = nc.servers.get(worker.id)
      status = worker.status
  print "Server status: " + status
  print "Server up!"
  ##############################
  #### Finding Floating IP #####
  ##############################
  floating_ip_information_list = nc.floating_ips.list()
  floating_ip_list = []
  for floating_ip_information in floating_ip_information_list:
      if getattr(floating_ip_information, 'fixed_ip') == None:
        floating_ip_list.append(getattr(floating_ip_information, 'ip'))
  if len(floating_ip_list) == 0:
    new_ip = nc.floating_ips.create(getattr(nc.floating_ip_pools.list()[0],'name'))
    print new_ip
    floating_ip_list.append(getattr(new_ip, 'ip'))
  floating_ip = floating_ip_list[0]
  print floating_ip
  ##############################
  ###### Add Floating IP #######
  ##############################
  worker.add_floating_ip(floating_ip)