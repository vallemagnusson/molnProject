import pickledb
import sys
import os
import swiftclient.client

def to_db(key, value):
	dataBaseName = "pictureDatabase"
	db = pickledb.load(dataBaseName, False)
	dbKeys = db.getall()
	if key not in dbKeys:
		print 1, key
		db.set(key, value)
		db.dump()

def in_db(fileName):
	dataBaseName = "pictureDatabase"
	db = pickledb.load(dataBaseName, False)
	dbKeys = db.getall()
	if fileName in dbKeys:
		return True
	else:
		return False