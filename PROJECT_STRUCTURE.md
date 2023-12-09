# Project Structure

The project is built around a microservices model. It intends to farm out work to dedicated, containerized processes wherever possible. This document provides an overview of those services.

## Supporting Containers

The app is supported with some infrastructural containers built by Docker. Refer to the main Readme file for instructions on these.

### MySQL

The Django app is configured to use a MySQL db backend, running on port 3306.

### Adminer

In order to directly inspect the database (when this is necessary), we have installed an Adminer container running on port 8080.

### Solr

This service is used to index entities in the database (Voyages, Enslaved People, Enslavers, and Blog Posts). Currently, it is only being used for the global search feature. However, it would make sense to use this to index documents at well (though full-text search always requires some tuning).

## Python Containers

These containers run python services in Flask or Django. The "main" API container runs a barebones Django web app, which the other processes essentially index the data from, in order to provide efficient use of these data (for instance, when aggregating to make data visualizations).

### API

This is the Python Django project that manages the database, provides an admin interface for directly editing the data, and presents the data out via API views.

A core principle of the rearchitecture was that the ORM should be exposed so that the relational data could be searched on more or less arbitrarily. For instance, you should be able to search Enslaved People by the name of the ship they were transported on, and you should be able to search Voyages for the names of the Enslaved People transported on them.

#### Core dependencies

* The API functionality is built on the Django Rest Framework (DRF) package
* The DRF serializers use drf-writable-nested
	* This allows us to create & edit the highly-relational data
	* But it also necessitates READONLY serializers because it is not performant at scale
	* and that package does not support unique-together constraints
* The more generic api endpoints are documented with Swagger at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
	* on the basis of the serializes
	* using the drf-spectacular package

If your main concern is to pull a paginated list view of items or a single item by its primary key, read the Django Swagger docs: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

#### Main routes

Each of the project's main object classes has its own route and related endpoints:

* Voyages: [voyage/](http://127.0.0.1:8000/voyage/)
* Enslaved People: [past/enslaved/](http://127.0.0.1:8000/past/enslaved/)
* Enslavers: [past/enslaver/](http://127.0.0.1:8000/past/enslaver/)
* Geographic Locations (presented as a tree): [geo/](http://127.0.0.1:8000/geo/)
* Documents: [docs/](http://127.0.0.1:8000/docs/)
* Blog Posts: [blog/](http://127.0.0.1:8000/blog/)
* Common: [common/](http://127.0.0.1:8000/common/)

The frontend application uses some customized endpoints, which we are still iterating on, in order to provide some highly useful search capabilities. To the extent possible, the methods of using these customized endpoints is kept consistent.

#### Schema Presentation

Because we are exposing as much of the ORM as is practicable, it is crucial to be able to inspect what variables are available to us for searching, and what their data types are so that we will know how to search them.

The app uses the Serializers to record in json format the schema for these main object classes, e.g., [http://127.0.0.1:8000/common/schemas/?hierarchical=False&schema_name=Voyage](http://127.0.0.1:8000/common/schemas/?hierarchical=False&schema_name=Voyage) will return a double-underscore-notation representation of the schema for Voyages:

	{
	  "id": {
		"type": "integer",
		"many": false
	  },
	  "voyage_source_connections__id": {
		"type": "integer",
		"many": true
	  },
		...
	  },
	  "voyage_source_connections__source__zotero_grouplibrary_name": {
		"type": "string",
		"many": true
	  }...
	  "voyage_itinerary__imp_principal_region_slave_dis__name": {
		"type": "string",
		"many": true
	  },
	}
  
... and [http://127.0.0.1:8000/common/schemas/?hierarchical=False&schema_name=Voyage](http://127.0.0.1:8000/common/schemas/?hierarchical=False&schema_name=Voyage) will return a nested representation of the schema for Enslaved People:

	{
	  "id": {
		"type": "integer",
		"many": false
	  },
	  "post_disembark_location": {
		"id": {
		  "type": "integer",
		  "many": false
		},
		"uuid": {
		  "type": "number",
		  "many": false
		},
		"name": {
		  "type": "string",
		  "many": false
		},
		"longitude": {
		  "type": "number",
		  "many": false
		}...
	  }...
	}

#### Queries on custom endpoints

Requests for data are made via POST calls. In any call, if a double-underscore-notation variable for that endpoint is present as a key in the request body, then its value will be used as a filter.

For instance, if 
```voyage_itinerary__imp_principal_region_slave_dis__name``` is a key in the payload of a call to [http://127.0.0.1:8000/voyage/](http://127.0.0.1:8000/voyage/), then the associated value would be used to filter voyages by the name of their imputed principal region of disembarkation.

Right now, we have 2 basic types of variable, each of which is always handled in the same way -- this will have to change eventually.

##### Numeric variables and aggregation views

Numeric variables are filtered according to a min/max range as given by a tuple. A call to voyages with the below payload: 

	{
		'voyage_dates__voyage_began_sparsedate__year':[1820,1850]
	}

Will return voyages that began in the years between 1820-1850 (inclusive).

Use these with aggregation views to make responsive rangesliders. The numeric variables on the different endpoints can all be queried in order to get their min/max.

For instance, a call to ```voyage/aggregations/``` like so:

	{
		'aggregate_fields': [  
			'voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year'
		]
	}

... will return the minimum and maximum values for the years on which voyages arrived at their port of disembarkation. This can be used to make a rangeslider customized for that variable.

##### String variables & autocomplete

String variables are filtered according to exact matches in an OR statement. For instance, a call to voyages with the below payload:
	
	{
		voyage_itinerary__imp_principal_region_slave_dis__name : [
			'Barbados',
			'Jamaica'
		]
	}

Will return all the voyages for whom the imputed principal region of disembarkation is either Barbados OR Jamaica.


Use these with autocomplete views to make responsive autocomplete multi-select filter components. This allows for an efficient searching of the text fields with inexact text matches, in order to then subsequently filter on them with an exact OR match.

For instance, a search on [http://127.0.0.1:8000/voyage/autocomplete/](http://127.0.0.1:8000/voyage/autocomplete/) like so:

	{
		voyage_itinerary__imp_principal_region_slave_dis__name : ['jam']
	}
	
...will return: 

	{
		"total_results_count": 1,
		"results": [
			{"id": 71, "label": "Jamaica"}
		]
	}

.... which lets you know that the only valid value in that field that starts with "jam" is "Jamaica" -- from which information you can construct an autocomplete component.

##### TBD:

There's work to be done here:

* allow for an inexact match on strings
* allow for a single numeric value to be selected
	* which is only doable if the exact OR filters are no longer the default
* autocomplete views should be paginated

But that will require coordination with the front-end folks, as it will involve breaking changes.

#### List views

These are more or less use generic DRF views. Pagination and ordering are handled like so:

	{
		'results_page': [2],
		'results_per_page': [12]
	}

Yes, I know, I'll get rid of the brackets.

#### Dataframe views:

You can get long, columnar presentations of data at the dataframe endpoints for voyages, enslaved, and enslavers. For these calls, use the "selected_fields" key:

	{
		'selected_fields': [
			'id',
			'voyage_ship__ship_name',
			'voyage_itinerary__imp_principal_place_of_slave_purchase__name',
			'voyage_itinerary__imp_principal_port_slave_dis__name',
			'voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year'
		]
	}

And you will receive a dictionary whose keys are those variable names and whose values are arrays of equal length containing the corresponding data.

#### Statistics views

These requests are handed off to the voyages-stats container.

#### Maps views

These requests are handed off to the voyages-geo-networks container.

#### Network graph views

These requests are handed off to the voyages-people-networks container.

----------

## Supporting containers

The statistics, mapping, and network endpoints all run in flask containers that are typically only accessed through the voyages-api django endpoint.

The typical workflow for these ancillary services is:

* On initialization, the supporting container
	* Runs several dataframe queries against voyages-api
	* Transforms that data and stores it in a networkx or pandas in-memory database
	* Waits for requests from voyages-api
* The supported endpoint (like [voyage/groupby](http://127.0.0.1:8000/voyage/groupby/)) receives
	* A normal filter object
	* One or more extra arguments particular to that endpoint
* The query is run by django, which
	* Retrieves only the pk's for the objects that meet the criteria
	* Passes those pk's and the extra arguments to the external container
* The supporting container then
	* Uses the pk's to filter down what it will be computing on
	* Uses the extra arguments to use Pandas or NetworkX functionality
	* Returns the json-serialized results to voyages-api, which completes the request
	
What follows summarizes how these containers work.

### Voyages-Stats

This container uses Pandas to build in-memory databases that can quickly produce json summary statistics that fit well into the plotly.js graphing library. Typically, these requests are about providing summary statistics using pandas functions like groupby.

### Voyages-People-Networks

This container uses NetworkX to map the numerous connections between people and voyages. Its default behavior is to receive an ID for one of its core object classes (an enslaved person, an enslaver, or a voyage), and to return the node with that ID, its neighbors out two hops, and the associated edges.

### Voyages-Geo-Networks

This container uses NetworkX to create essentially a routing system, and then runs every entity for each object class through that routing system, in order to cache, in Pandas, a large dataframe of the various edges and weights for each entity, so that these can be aggregated on, and splined appropriately based on the weights. It's complicated.