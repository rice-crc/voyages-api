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

#set up location types table
for t in ["Region","Broad Region","Port"]:
	cursor.execute(("insert ignore into geo_locationtype (`name`) values (%s)"),(t,))
	cnx.commit()

cursor.execute("select name,id from geo_locationtype")
r=cursor.fetchall()
locationtypedict={i[0]:i[1] for i in r}

print(locationtypedict)

#get all broad regions and insert into db, keeping a running list of keys
cursor.execute("select id,broad_region,`value`,longitude,latitude,show_on_map from voyage_broadregion;")
resp=cursor.fetchall()

#keys are pks, values are the spss geo code ("value") field
broadregion_table_codemap={}

#keys are spss geo codes, values are the new pks in the geo_location table
new_geo_codemap={}

location_type_id=locationtypedict["Broad Region"]
for broad_region in resp:
	id,name,value,longitude,latitude,show_on_map =broad_region
	cursor.execute("insert into geo_location (`name`,longitude,latitude,`value`,show_on_map,location_type_id) values (%s,%s,%s,%s,%s,%s);",(name,longitude,latitude,value,show_on_map,location_type_id))
	cnx.commit()
	cursor.execute("select max(id) from geo_location")
	r=cursor.fetchone()
	new_geo_id=r[0]
	broadregion_table_codemap[id]=value
	new_geo_codemap[value]=new_geo_id
	
cursor.execute("select id,region,`value`,longitude,latitude,show_on_map,show_on_main_map,broad_region_id from voyage_region;")
resp=cursor.fetchall()

#keys are pks, values are the spss geo code ("value") field
region_table_codemap={}

location_type_id=locationtypedict["Region"]
for region in resp:
	id,name,value,longitude,latitude,show_on_map,show_on_main_map,broad_region_id=region
	child_of_id=new_geo_codemap[broadregion_table_codemap[broad_region_id]]
	cursor.execute("insert into geo_location (`name`,longitude,latitude,`value`,show_on_map,show_on_main_map,child_of_id,location_type_id) values (%s,%s,%s,%s,%s,%s,%s,%s)",(name,longitude,latitude,value,show_on_map,show_on_main_map,child_of_id,location_type_id))
	cnx.commit()
	cursor.execute("select max(id) from geo_location")
	r=cursor.fetchone()
	new_geo_id=r[0]
	region_table_codemap[id]=value
	new_geo_codemap[value]=new_geo_id

cursor.execute("select id,place,`value`,longitude,latitude,show_on_main_map,show_on_voyage_map,region_id from voyage_place;")
resp=cursor.fetchall()

location_type_id=locationtypedict["Port"]
for port in resp:
	id,name,value,longitude,latitude,show_on_main_map,show_on_voyage_map,region_id=port
	child_of_id=new_geo_codemap[region_table_codemap[region_id]]
	try:
		cursor.execute("insert into geo_location (`name`,longitude,latitude,`value`,show_on_main_map,show_on_voyage_map,child_of_id,location_type_id) values (%s,%s,%s,%s,%s,%s,%s,%s)",(name,longitude,latitude,value,show_on_map,show_on_main_map,child_of_id,location_type_id))
		cnx.commit()
	except:
		print('error with the following (probably the north america duplicate spss code])',port)
