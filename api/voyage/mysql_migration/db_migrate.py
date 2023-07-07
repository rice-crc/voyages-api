import MySQLdb
import re
import json

target_db_name="voyages_api"
source_db_name="voyages_voyages_past_merge"

db=MySQLdb.connect("voyages-mysql","voyages","voyages",target_db_name)

c=db.cursor()
c.execute("show tables;")
tables={i[0]:{'constraints':[],'columns':[]} for i in c.fetchall()}

exclude_table_prefixes=[
# 	'account',
# 	'auth',
# 	'authtoken',
# 	'captcha',
# 	'django',
# 	'socialaccount',
# 	'thumbnail',
# 	'past_enslavedcontribut',
# 	'past_enslavercontribution'
]

def excludetable(tablename):
	exclude=False
	for e in exclude_table_prefixes:
		if tablename.startswith(e):
			exclude=True
	return exclude

for tablename in tables:
	print(tablename)
	c.execute("show create table %s;" %tablename)
	create_table_statement=c.fetchone()[1]
	c.execute("show columns from %s;" %tablename)
	columns=c.fetchall()
	column_names=[i[0] for i in columns]
	constraints=[l.strip() for l in create_table_statement.split('\n') if "CONSTRAINT" in l]
	print(constraints)
	if not excludetable(tablename):
		tables[tablename]['constraints']=constraints
		tables[tablename]['column_names']=column_names

for tablename in tables:
	print(tablename)
	if not excludetable(tablename):
		for constraint in tables[tablename]['constraints']:
			constraint_name=re.search("(?<=CONSTRAINT `)[^`]+",constraint).group(0)
			print(constraint_name)
			c.execute("alter table %s drop constraint %s;" %(tablename,constraint_name))

db.close()

d=open("constraints_tmp.json","w")
d.write(json.dumps(tables,indent=2))
d.close()

d=open("constraints_tmp.json","r")
t=d.read()
tables=json.loads(t)
d.close()

db=MySQLdb.connect("voyages-mysql","voyages","voyages")
 
c=db.cursor()

for tablename in tables:
	print(tablename)
	if not excludetable(tablename):
		
		c.execute("delete from %s.%s;" %(target_db_name,tablename))
		db.commit()
	
		colnames=",".join(["`%s`" %c for c in tables[tablename]['column_names']])
	
		executestr="insert into %s.%s (%s) select %s from %s.%s;" %(
			target_db_name,
			tablename,
			colnames,
			colnames,
			source_db_name,
			tablename
		)
		print(executestr)
	
		c.execute(executestr)
		db.commit()

db.close()

db=MySQLdb.connect("voyages-mysql","voyages","voyages",target_db_name)

c=db.cursor()
print("--->reinstating constraints")

d=open("constraints_tmp.json","r")
t=d.read()
tables=json.loads(t)
d.close()

for tablename in tables:
	print(tablename)
	if not excludetable(tablename):
		constraints=tables[tablename]['constraints']
		for constraint in constraints:
# 			print(constraint)
			constraint_formatted=re.sub("CONSTRAINT","",constraint)
			if constraint_formatted.endswith(","):
				constraint_formatted=constraint_formatted[:-1]
			constraint_formatted.strip()
			execstr="alter table %s add constraint %s;" %(tablename,constraint_formatted)
			print(execstr)
			c.execute(execstr)
db.close()