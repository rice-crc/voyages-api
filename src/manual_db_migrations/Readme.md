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




JULY 13: batch updated a bunch of voyages whose ports of embarkation were showing as the eastern side of the atlantic -- pushed them into transatlantic -- had enough of this bad data.

update voyage_voyage set dataset=0 where voyage_id in (100033,100124,100308,100309,100384,100769,101561,101972,102058,102843,103329,103729,103788,103896,103898,103903,103955,103956,103957,103958,103959,103961,103962,103963,103964,103965,104618,104619,104692,104693,104694,104695,104698,104699,104700,104701,104702,104774,104775,104776,104777,104778,104779,104780,104781,104782,104783,104784,104785,104786,104787,104788,104789,104790,104791,104792,104793,104795,104796,104797,104798,104799,104800,104801,104802,104803,104804,104805,104806,104807,104808,104809,104810,104811,104812,104813,104814,104815,104816,104817,104818,104819,104820,104821,104822,104823,104824,104825,104826,104827,104828,104829,104830,104831,104832,104833,104834,104835,104836,104839,104843,104862,105017,105018,105076,106557,106558,106568,106569,106576,106593,106598,106599,106601,106603,106604,106608,106612,106631,106633,106634,106639,106652,106661,106663,106664,106665,106666,106672,106675,106676,106677,106683,106691,106693,106694,106699,106718,106720,106733,106759,106773,106774,106778,106779,106780,106783,106784,106786,106787,106788,106790,106791,106792,106801,106802,106806,106807,106808,106809,106810,106815,106816,106817,106818,106819,106821,106822,106823,106824,106825,106826,106827,106828,106829,106830,106831,106832,106834,106835,106836,106837,106838,106840,106841,106850,106851,106854,106855,106856,106857,106858,106859,106860,106861,106862,106863,106864,106865,106866,106867,106868,106869,106870,106872,106874,106875,106876,106879,106881,106882,106883,106884,106885,106886,106887,106888,106889,106890,106891,106892,106896,106900,106901,106902,106903,106906,106907,106908,106909,106910,106912,106913,106914,106915,106916,106917,107145,107205,107650,107713,107714,107791,107908,107958,107964,107965,107966,107967,107968,107969,107987,107999,108081,108087,108170,108177,108220,108367,108490,110308,110487,110488,110502,110714,110768,111568,112138,112139,141489,141543,141544,141553,141555,160655,160656,160661,161057,162013,162059,162081,162105,162139,162167,177704,177772,178770,178775,178971,179069,182731);


JULY 25: NULLED OUT THE GEO LOCATIONS ON A BUNCH OF BAD ENTRIES THAT HAD LAT,LONG=0,0
update geo_location set longitude=Null,latitude=Null where longitude<.1 and longitude>-.1 and latitude<.1 and latitude>-.1 and location_type_id<5;

JULY 26: ENSLAVERS AND ENSLAVED

* Staging server currently has:
	* 6099 KIN enslaver aliases
	* 21868 IAM enslaver aliases (mapped against 20119 identities)
	* 36156 other aliases ```(SELECT * FROM voyages.past_enslaveralias where manual_id not like "KIN%" and manual_id not like "IAM%";)```
* API currently has:
	* 6099 KIN enslaver aliases
	* 
	
	
	
	
	
	
	