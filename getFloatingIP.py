import os
import urllib2

myip = urllib2.urlopen("http://myip.dnsdynamic.org/").read()

print myip
with open("/etc/environment", "a") as outfile:
        outfile.write("export FLOATING_IP="+myip)





