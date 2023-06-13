# Development notes

I'll try to keep track, here, of all the changes that

* I had to make, and what that
	* Broke
	* Necessitated further changes in
* I wanted to make but could not / was not allowed to and
	* Why I wanted to
	* Why I wasn't able to
	* The downstream consequences of this block

## Data Structures

* New rules
	* PK's
		* Every table's PK is managed by Django as an AI ID field
		* This does not rule out Unique legacy fields, like the Geographic SPSS codes
	* Relationality
		* Names should be normalized, even if through one-to-one keys
		* No more alias tables, in other words
		* And no more free-floating data like the sound recordings
	* Caching
		* NO! NO!
		* See "Infrastructure"
	* RESERVED MODEL FIELD NAMES
		* For the sake of my "exposing the ORM" strategy, we're going to reserve "label"
			* This necessitates 9 changes to the Voyages model (see June 13 commit)
* Prelim DB Migrations
	* As of June 1, db state has 2 layers of migrations
		* A. Migrate june-1-2023-dellamonica-enslaversmerge for May 24 staging dump
			* then run the mysql-migration script
			* with one tweak -- dropped unique_together on enslavedname / lang
		* B. Migrate june-1-2023-johnconnor for MINIMAL API-ready changes
			* then run the management script
		* What are those changes?
			* all comma-spliced date fields mirrored with
				* -sparsedate suffixed fields
				* that are 1:1 on a numeric triple SparseDate object
					* the 1:1 field itself being nullable
					* and of course the individual numeric SD fields being nullable
			* place,region,broadregion
				* get an extra geo location field
				* that is 1:1'd to a generic Location object
			* voyagedatasetmanager GONE
* Down the pike
	* We want documents
		* to attach to each sourceconnection table
		* & in doing so to attach to Zotero
	* We need to reform the PAST app
		* Enslaver aliases is nonsense
		* Multifarious 
		* Nobody knows how "roles" work
		* Enslaved names are multi-fielded
	* Voyage Itinerary, Dates, and numbers tables need to be unified (into events?)
		* However this will break impute beyond repair

## Infrastructure

* Caching
	* No more in-memory db's in Django. It's unreliable.
	* Such work will be done by microservices, usually Flask:
		* Pandas
		* NetworkX