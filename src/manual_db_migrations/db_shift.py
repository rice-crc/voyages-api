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

d=open("tables.txt",'r')
t=d.read()
d.close()

tables=t.split("\n")

def get_fk_constraints(tables,dbname,cursor):
	FK_CONSTRAINTS=[]
	UNIQUE_CONSTRAINTS={}
	for table in tables:
		q="show create table %s.%s" %(dbname,table)
		cursor.execute(q)
		res=cursor.fetchall()
		fk_pattern=re.compile("CONSTRAINT `([a-z|A-Z|0-9|_]+)` FOREIGN KEY \(`([a-z|A-Z|0-9|_]+)`\) REFERENCES `([a-z|A-Z|0-9|_]+)` \(`([a-z|A-Z|0-9|_]+)`\)")
		unique_pattern=re.compile("(?<=UNIQUE KEY ).*")
		for r in res:
			source_table,create_table=r
			#print(create_table)
			table_fk_constraints=fk_pattern.findall(create_table)
			for table_fk_constraint in table_fk_constraints:
				entry=[source_table]+list(table_fk_constraint)
				#print(entry)
				FK_CONSTRAINTS.append(entry)
			table_unique_constraints=unique_pattern.findall(create_table)
			UNIQUE_CONSTRAINTS[table]=table_unique_constraints
	return FK_CONSTRAINTS,UNIQUE_CONSTRAINTS


def drop_fk_constraints(fk_constraints,db_name):
	for fkc in fk_constraints:
		source_table,constraint_id,source_column,target_table,target_column=fkc
		q='alter table %s.%s drop foreign key `%s`;' %(db_name,source_table,constraint_id)
		print(q)
		cursor.execute(q)
		cnx.commit()

def drop_unique_constraints(unique_constraints,db_name):
	for table in unique_constraints:
		table_constraints=new_unique_constraints[table]
		for tc in table_constraints:
			constraint_key,columntuple=tc.split(" ")
			q='alter table %s.%s drop constraint %s;' %(new_db,table,constraint_key)
			print(q)
			cursor.execute(q)
			cnx.commit()

new_db="voyages_api"
old_db="voyages"


old_foreign_key_constraints,old_unique_constraints=get_fk_constraints(tables,old_db,cursor)

print(old_foreign_key_constraints)

new_foreign_key_constraints,new_unique_constraints=get_fk_constraints(tables,new_db,cursor)

print(new_foreign_key_constraints)

drop_fk_constraints(old_foreign_key_constraints,old_db)
drop_fk_constraints(new_foreign_key_constraints,new_db)
drop_unique_constraints(new_unique_constraints,new_db)	


for table in tables:
	cursor.execute('show columns from %s.%s;' %(old_db,table))
	results=cursor.fetchall()
	oldtablecolumns=[r[0] for r in results]
	cursor.execute('show columns from %s.%s;' %(new_db,table))
	results=cursor.fetchall()
	newtablecolumns=[r[0] for r in results]
	mutualcolumns=[i for i in newtablecolumns if i in oldtablecolumns]
	colnamestr="`"+"`,`".join(mutualcolumns)+"`"
	shiftquery = "insert into %s.%s (%s) select %s from %s.%s;" %(new_db,table,colnamestr,colnamestr,old_db,table)
	print(shiftquery)
	cursor.execute(shiftquery)
	cnx.commit()


for fkc in new_foreign_key_constraints:
	source_table,constraint_id,source_column,target_table,target_column=fkc
	q='alter table %s.%s add constraint %s foreign key (%s) references %s (%s);' %(new_db,source_table,constraint_id,source_column,target_table,target_column)
	try:
		print(q)
		cursor.execute(q)
		cnx.commit()
	except:
		print("FAILURE TO REASSERT KEY W FOLLOWING QUERY -->",q)

for table in new_unique_constraints:
	table_constraints=new_unique_constraints[table]
	for tc in table_constraints:
		constraint_key,columntuple=tc.split(" ")
		#odd trailing comma issue?
		if columntuple.endswith(","):
			columntuple=columntuple[:-1]
		q='alter table %s.%s add constraint %s UNIQUE %s;' %(new_db,table,constraint_key,columntuple)
		
		try:
			cursor.execute(q)
			cnx.commit()
			print(q)
		except:
			print("FAILURE TO REASSERT KEY W FOLLOWING QUERY -->",q)
		

cnx.close()
