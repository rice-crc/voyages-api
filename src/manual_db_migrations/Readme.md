This shifts selected tables from one identical database into another

by dropping foreign key constraints

shifting values

then reasserting the fk constraints

This handles mutual fk constraints btw. tables (e.g. voyages-->itineraries-->voyages)