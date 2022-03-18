import mysql.connector
import time
import json
import re				


d=open("dbconf.json","r")
t=d.read()
d.close()
conf=json.loads(t)

cnx = mysql.connector.connect(**conf)
cursor = cnx.cursor()

#"ALTER TABLE voyagesapi_mar16.voyage_voyage add column voyage_outcome_id int;"

q="SELECT id,voyage_id FROM voyagesapi_mar16.voyage_voyageoutcome;"

cursor.execute(q)
res=cursor.fetchall()

for outcome in res:
	outcome_id,voyage_id=outcome
	q="update voyagesapi_mar16.voyage_voyage set voyage_outcome_id=%d where voyage_id=%d;" %(outcome_id,voyage_id)
	cursor.execute(q)
	cnx.commit()
cnx.close()