import mysql.connector
import time
import json
import re

#map all designated date columns (in datesvars.txt) to numerical mmddyyyy columns
##where those column names have _mm _dd or _yyyy appended to them

d=open("dbcheckconf.json","r")
t=d.read()
d.close()
conf=json.loads(t)

cnx = mysql.connector.connect(**conf)
cursor = cnx.cursor()

d=open("datesvars.txt","r")
t=d.read()
d.close()
lines=t.split("\n")
print(lines)
datevars=[l.split("__") for l in lines]

for dv in datevars:
	table,column=dv
	print(table,column)
	q="select id,%s from %s;" %(column,table)
	cursor.execute(q)
	result=cursor.fetchall()
	for r in result:
		rowid,val=r
		if val!='':
			if "," in val:
				delimiter=","
			elif "/" in val:
				delimiter="/"
			else:
				delimiter=None
			try:
				mm,dd,yyyy=[int(i) if i!='' else None for i in val.split(delimiter)]
				d={"mm":mm,"dd":dd,"yyyy":yyyy}
				for k in d:
					v=d[k]
					if v is not None:
						qstr="update " + table + " set " + column + "_" + k + "=%s where id=%s"
						cursor.execute(qstr, (v,rowid))
				cnx.commit()
			except:
				print(table,column,rowid,r)

cnx.close()