# Migration scripts

It's going to be a real pain to migrate the old db to this new structure. Lots of my changes have been ad-hoc, admittedly. However, I'm trying to record them here to reduce that pain :)

## First round (the heavy lift)

The following scripts:

* db_shift.py
* reset.sh
* tables.txt

... shift selected tables from one identical database into another by:

* dropping foreign key constraints
* shifting values
* then reasserting the fk constraints
* This handles mutual fk constraints btw. tables (e.g. voyages-->itineraries-->voyages)

## Second round (geo)

* migrate_geo_data.py (~may 27) pushes all of our place, region, broadregion data from voyages over into the geo app's unified PLACE model
	* runs externally hitting a mysql server
	* so requires you to dump the db, patch it, then inject it again
	* unless you connect directly to the docker mysql server
* map_geo_codes.txt (~june 1) -- after some futzing with the models & serializers in the new geo app, this one will now do a quick linking up of the voyages geo data to the new geo app
	* going to see if I can't run this as django commands

then we'll test and finally tear away the scaffolding (i.e. the place region and broad region models in voyages)

and then we'll fill in the route data

