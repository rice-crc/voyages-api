# Voyages REST API 2021

This is an attempt to rebuild the Voyages API with as few dependencies as possible in the latest versions of django and python

THIS REQUIRES AN EXTERNAL SQL DUMP. CONTACT JCM FOR THIS.

## Local Deployment

Create an external Docker network.

```bash
host:~/Projects/voyagesapi$ docker network create voyages
```

Build and run the containers.

```bash
host:~/Projects/voyagesapi$ docker-compose up -d --build
```

Create the database.

```bash
host:~/Projects/voyagesapi$ docker exec -i voyages-mysql mysql -uroot -pvoyages -e "create database voyages"
```

Import the database dump to MySQL.

```bash
host:~/Projects/voyagesapi$ docker exec -i voyages-mysql mysql -uroot -pvoyages voyages < data/voyagesapi.sql
```

Run the custom management commands (see bottom of this doc) -- and it's a good idea to run them in this order:

	docker exec -i voyages-django bash -c "python3.9 manage.py rebuild_options"
	docker exec -i voyages-django bash -c "python3.9 manage.py rebuild_indices"

View container logs.

```bash
host:~/Projects/voyagesapi$ docker logs voyages-django
host:~/Projects/voyagesapi$ docker logs voyages-mysql
host:~/Projects/voyagesapi$ docker logs voyages-flask
```

*The Adminer app is provided as an additional way to work with the database.*

Note the following project resources:

* Voyages API: http://127.0.0.1:8000/
* Adminer: http://127.0.0.1:8080

## Cleanup

	bash
	host:~/Projects/voyagesapi$ docker-compose down

	host:~/Projects/voyagesapi$ docker container prune
	host:~/Projects/voyagesapi$ docker image prune
	host:~/Projects/voyagesapi$ docker volume prune
	host:~/Projects/voyagesapi$ docker network prune

----------------------

## Using the API

There are currently 4 major endpoints, which allow you to query on People, Voyages, Places, and Estimates

1. Enslaved: POST http://127.0.0.1:8000/past/
1. Voyages: POST http://127.0.0.1:8000/voyage/
1. Places: POST http://127.0.0.1:8000/geo/
1. Estimates:  POST http://127.0.0.1:8000/assessment/

### 0. AUTHENTICATION

#### Required as of March 16.

documentation: https://www.django-rest-framework.org/api-guide/authentication/

local token: http://127.0.0.1:8000/admin/authtoken/tokenproxy/

It's pretty straightforward. You simply need to declare a header with the key "Authorization" and the value "Token abcdef....".

So any request, like ```POST http://127.0.0.1:8000/past/``` simply becomes ```POST http://127.0.0.1:8000/past/ -H 'Authorization: Token abcdef....'```

A full python example follows.

#### Authentication workflow

Create a user:

1. First, enter the django container: ```docker exec -it voyagesapi-django /bin/bash```
1. Next, create a user (in this example, a superuser): ```python3.9 manage.py createsuperuser```

Let's imagine that that username and password you've set are simply "voyages"/"voyages"

The full authentication workflow would look like:


	import requests
	import json
	url='http://127.0.0.1:8000/voyages2022_auth_endpoint/'
	r=requests.post(url,{'username':'voyages','password':'voyages'})
	token=json.loads(r.text)['token']

	headers={'Authorization':'Token %s' %token}

	print(headers)

	url='http://127.0.0.1:8000/voyage/'
	r=requests.post(url,headers=headers)


### 1. Using POST Requests

A request to PAST asking for people transported on voyages with Voyage ID's between 2314 and 2500 would look like
	
	POST http://127.0.0.1:8000/past/
	
	Body:
	{
		'hierarchical': ['false'],
		'results_page': ['3'],
		'results_per_page': ['20'],
		'voyage__voyage_id': ['2314,2500']
	}
	
And would return results 60-79 of 21,867 total records.


Or, to use the exact text with autocomplete, you might send the following request

	POST http://127.0.0.1:8000/voyage/autocomplete

	Body:
	{'voyage_itinerary__imp_principal_region_slave_dis__geo_location__name': ['jam']}

And get back

	{
		"voyage_itinerary__imp_principal_region_slave_dis__geo_location__name": [
			"Jamaica"
		]
	}

Then feed that precise value into that variable:

	POST http://127.0.0.1:8000/voyage/
	
	Body:
	{	'voyage_itinerary__imp_principal_region_slave_dis__geo_location__name':
		['Barbados','Jamaica']
	}

And get back 5,816 results.

### 2. Enumerating variables, relationships, and data types

1. People: ```OPTIONS http://127.0.0.1:8000/past/?hierarchical=False```
1. Voyages: ```OPTIONS http://127.0.0.1:8000/voyage/?hierarchical=False```
1. Places: ```OPTIONS http://127.0.0.1:8000/voyage/geo?hierarchical=False```
1. Estimates ```OPTIONS http://127.0.0.1:8000/assessment/?hierarchical=False```

Why "hierarchical=False"?

1. The default is hierarchical=True, which gives you a tree
1. These variables' hierarchical relations correspond to links between db tables
1. The django syntax for those links is a double underscore: "__"
1. Variable labels are now presented in two formats:
	1. "label" which is just the field label without context (good for nested menus)
	1. "flatlabel" which is a concatenated label -- good for menus targeting specific fields

hierarchical=False looks like:

    ...
    "voyage_itinerary__port_of_departure__geo_location__child_of__longitude": {
        "type": "<class 'rest_framework.fields.DecimalField'>",
        "label": "Longitude of Centroid",
        "flatlabel": "Itinerary : Port of departure (PORTDEP) : Location : Child of : Longitude of Centroid"
    },
    ...

hierarchical=True looks like:

	...
	"voyage_itinerary": {
			"type": "table",
			"label": "Itinerary",
			"flatlabel": "Itinerary",
			"id": {
				"type": "<class 'rest_framework.fields.IntegerField'>",
				"label": "ID",
				"flatlabel": "Itinerary : ID"
			},
			"port_of_departure": {
				"type": "table",
				"label": "Port of departure (PORTDEP)",
				"flatlabel": "Itinerary : Port of departure (PORTDEP)",
				"id": {
					"type": "<class 'rest_framework.fields.IntegerField'>",
					"label": "ID",
					"flatlabel": "Itinerary : Port of departure (PORTDEP) : ID"
				},
				"geo_location": {
					"type": "table",
					"label": "Location",
					"flatlabel": "Itinerary : Port of departure (PORTDEP) : Location",
					"id": {
						"type": "<class 'rest_framework.fields.IntegerField'>",
						"label": "ID",
						"flatlabel": "Itinerary : Port of departure (PORTDEP) : Location : ID"
					},
					"child_of": {
						"type": "table",
						"label": "Child of",
						"flatlabel": "Itinerary : Port of departure (PORTDEP) : Location : Child of",
						"id": {
							"type": "<class 'rest_framework.fields.IntegerField'>",
							"label": "ID",
							"flatlabel": "Itinerary : Port of departure (PORTDEP) : Location : Child of : ID"
						},
						"name": {
							"type": "<class 'rest_framework.fields.CharField'>",
							"label": "Location name",
							"flatlabel": "Itinerary : Port of departure (PORTDEP) : Location : Child of : Location name"
						}, ....

-------------------------

## METHODS: Filter/Search, Paginate, Autocomplete, Aggregate, and GroupBy

### Filter/Search

Filter and sort on any variable

Numeric fields: provide a range

	POST http://127.0.0.1:8000/voyage/
	data={'voyage_dates__imp_arrival_at_port_of_dis_yyyy'=[1800,1810]}
	
	POST http://127.0.0.1:8000/voyage/geo
	data={
		'longitude'=[-20,-6],
		'latitude'=[-20,38]
	}

Text fields: inclusive OR on arrayed values, exactly matched (see Autocomplete below):

	POST http://127.0.0.1:8000/voyage/
	data={'voyage_itinerary__imp_principal_region_slave_dis__geo_location__name'=['Barbados','Jamaica']}

### Paginate

Check the headers to see total_results_count, and paginate accordingly:

	POST http://127.0.0.1:8000/voyage/
		
		{
		"results_page" : [4]
		"results_per_page" : [20]
		}

### Autocomplete Text Variables (Voyages only)

1. accepts a request
	1. for one field
	1. which must be text
1. returns
	1. the first 10 unique entries in flat list form
	1. and a results count

example:

	POST http://127.0.0.1:8000/voyage/autocomplete
	
	{"voyage_captainconnection__captain__name": ["jos"]}

Looks like:

	{"voyage_captainconnection__captain__name":
		[
			"Dias, Manoel José",
			"Mata, José Maria da",
			"Ferreira, José dos Santos",
			"Amorim, José Gomes de",
			"Santos, Félix José dos",
			"Teodoro, Teotônio José",
			"Castro, Alexandre José de",
			"Teixeira, José de Souza",
			"Oliveira, José Malaquias de",
			"Gomes, Manoel José"
		],
		"results_count": 8207
	}

### Aggregate Numeric Variables (Voyages only)

You can aggregate on numerical variable. This will only return aggregations on valid numeric fields.

But it returns min & max on selected numeric fields.

You can still run filters and sorts on variables--these filters will be executed before the aggregation.

Fields to aggregate 

e.g.,

	POST http://127.0.0.1:8000/voyage/aggregations
	
	{
		"aggregate_fields" : [
			"voyage_slaves_numbers__imp_total_num_slaves_embarked"
			"voyage_slaves_numbers__imp_total_num_slaves_disembarked"
			]
	}

Looks like:

	{
	"voyage_slaves_numbers__imp_total_num_slaves_embarked":
		{
		"min": 0,
		"max": 2024
		},
	"voyage_slaves_numbers__imp_total_num_slaves_disembarked":
		{
		"min": 0,
		"max": 1700
		}
	}

### GroupBy (Voyages only)

Using Pandas-like syntax, we can also run searches and then perform groupings on categorical variables.
 
For instance:

	POST "http://127.0.0.1:8000/voyage/groupby"
	data={
		"voyage_itinerary__imp_principal_region_slave_dis__geo_location__name":[
			"Barbados",
			"Jamaica"
		],
		'groupby_fields':['voyage_itinerary__imp_broad_region_slave_dis__geo_location__name',
		                  'voyage_slaves_numbers__imp_total_num_slaves_disembarked'],
		'agg_fn':['sum'],
		'cachename':['voyage_bar_and_donut_charts']
	}


... would return the following:

	{
		"voyage_slaves_numbers__imp_total_num_slaves_disembarked": {
			"Africa": 146224.0,
			"Brazil": 3254758.0,
			"Caribbean": 4585846.0,
			"Europe": 7616.0,
			"Mainland North America": 421929.0,
			"Other": 174668.0,
			"Spanish Mainland Americas": 691717.0
		}
	}

It uses Pandas syntax and relies on the indexing functionality outlined below as well as a Flask app running alongside this Django app.

## CrossTabs

Let's say you wanted to run a search (e.g., voyages btw. 1800-1820) and then determine how many people disembarked voyages by the pairings of port A,B in those years.

You would simply hit the GroupBy endpoint with your regular search query and specify:

    which fields to group on

    which field to get the summary stat on (and the operation to run, like "sum")

For instance:

POST "http://127.0.0.1:8000/voyage/crosstabs"
data={
	"voyage_itinerary__imp_principal_region_slave_dis__geo_location__name":[
		"Barbados",
		"Jamaica"
	],
	'groupby_fields':['voyage_itinerary__principal_port_of_slave_dis__geo_location__name',
	                  'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__name'],
	'value_field_tuple':['voyage_slaves_numbers__imp_total_num_slaves_disembarked','sum'],
	'cachename':['voyage_export']
}

This will be iterated over the coming weeks to cover Pivot Tables and other functions.

It uses Pandas syntax and relies on the indexing functionality outlined below as well as a Flask app running alongside this Django app.

--------------------

## Under the hood

### Custom caching/indexing

(currently only enabled on voyages, not past, as it utilizes the dataframes functionality to rebuild efficiently, and past doesn't have that yet)

This endpoint allows full searchability as with dataframes and list endpoints above. The only difference is that you can't select all fields -- only those that exist in that particular cache.

For instance:

	data={
		'voyage_itinerary__imp_principal_region_slave_dis__geo_location__name':[
			'Barbados',
			'Jamaica'
		],
		'cachename':['voyage_export'],
		'download_csv':['True'],
		'selected_fields':['voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__name']
	}
	
	r=requests.post('http://127.0.0.1:8000/voyage/caches',headers=headers,data=data)

Returns 67 columns with 5,816 results each. Split value fields are joined with a space-buffered pipe (" | ")

	{
	'id': 
		[1860, 2555, ...],
	'voyage_captainconnection__captain__name':
		['Fabrequez, S', 'Lisboa, Antônio Pereira',...],
	'voyage_crew__crew_died_complete_voyage':
		[None, None, ...],
	...
	}

There are 2 caches/indices at the time of this writing:

1. 'voyage_export' --> this indexes 67 fields to replicate the download functionality
1. 'voyage_animation' --> this indexes 11 fields to replicate the animation functionality



### Dataframes / Field Selection

There is functionality to

1. run a search
1. select only specific variables
1. retrieve all results for them in columnar format

(But the caching/indexing is much, much faster and intended to replace this for public use)

e.g., 

	POST http://127.0.0.1:8000/voyage/dataframes
	
	{
		"voyage_dates__imp_arrival_at_port_of_dis_yyyy" : [1800,1810],
		"selected_fields" : [
			"voyage_itinerary__imp_broad_region_voyage_begin__geo_location__name"
			"voyage_itinerary__first_landing_region__geo_location__name",
			"voyage_itinerary__first_landing_place__geo_location__name",
			"voyage_slaves_numbers__imp_total_num_slaves_embarked"
			]
	}

Looks like:

	{   'voyage_itinerary__first_landing_place__geo_location__name':
		[
			'Barbados, port unspecified',
			'Freetown',
			'Freetown',
			...
		],
		'voyage_itinerary__first_landing_region__geo_location__name':
		[
			'Barbados',
			'Sierra Leone',
			'Sierra Leone',
			...
		],
		'voyage_itinerary__imp_broad_region_voyage_begin__geo_location__name':
		[
			'Mainland North America',
			None,
			None,
			...
		],
		'voyage_slaves_numbers__imp_total_num_slaves_embarked':
		[
			168,
			130,
			68,
			...
		]
	}

### Custom admin commands

2 custom admin commands have been built in to date. They are both defined in the voyage app, under src/voyage/management/commands

#### A. rebuild_options

This rebuilds the options file for all the current endpoints by:

* Running through several serializers (voyage, geo (voyage), enslaved (past), assessment)
* Articulating a full list of fields, auto-generated labels, relations, and datatypes in json format
* These are saved as flat files which the options calls then subsequently pick up

It was a necessity to do this because Django exhibits some odd behavior at times, where old data is returned for new requests.

run with ```python3.9 manage.py rebuild_options```

#### B. rebuild_indices

This rebuilds the two json flat files that enable the "Custom caching" endpoint above.

The flat files are stored in static/custom_caching/...

run with ```python3.9 manage.py rebuild_indices```

