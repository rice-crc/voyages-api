import mysql.connector
import time
import json
import re



'''
THIS SCRIPT PUSHES ALL OF OUR PLACE, REGION, BROADREGION DATA INTO THE GEO APP'S UNIFIED STRUCTURE
NEXT STEP WILL BE TO PRESENT A GEO ENDPOINT AND SERIALIZE THE OUTPUT
AND THEN TO POINT THE ITINERARY AND OTHER GEO VARS OVER AT THE GEO APP
'''

d=open("dbconf.json","r")
t=d.read()
d.close()
conf=json.loads(t)

cnx = mysql.connector.connect(**conf)
cursor = cnx.cursor()

conf['database']='voyages_api'

cnx2 = mysql.connector.connect(**conf)
cursor2 = cnx.cursor()

#first, we need the id's of all enslaver identities that we do not currently have in the api db

cursor.execute("SELECT identity_id FROM voyages.past_enslaveralias where manual_id not like \"KIN%\";")
resp=cursor.fetchall()

identity_ids=[i[0] for i in resp]

#then iterate over those records and create new ones in the api db, while mapping the new pk's

identity_id_map={}

for id in identity_ids:
	
	cols=[
		'id',
		'principal_alias',
		'birth_year',
		'birth_month',
		'birth_day',
		'birth_place_id',
		'death_year',
		'death_month',
		'death_day',
		'death_place_id',
		'father_name',
		'father_occupation',
		'mother_name',
		'probate_date',
		'will_value_pounds',
		'will_value_dollars',
		'principal_location_id'
	]
	
	cursor.execute("SELECT %s from voyages.past_enslaveridentity where id=%s;" %(','.join(cols),str(id)))
	resp=cursor.fetchone()
	obj={k:resp[cols.index(k)] for k in cols}
	
	
	
	
	
	
	print(obj)
	
	
	









