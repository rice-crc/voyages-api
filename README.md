# Voyages REST API 2021

This is an attempt to rebuild the Voyages API with as few dependencies as possible in the latest versions of django and python

THIS REQUIRES AN EXTERNAL SQL DUMP. CONTACT JCM FOR THIS.

## Local Deployment

Create an external Docker network.

```bash
host:~/Projects/voyagesapi$ docker network create voyagesapi
```

Build and run the containers.

```bash
host:~/Projects/voyagesapi$ docker-compose up -d --build
```

Create the database.

```bash
host:~/Projects/voyagesapi$ docker exec -i voyagesapi-mysql mysql -uroot -pvoyages -e "create database voyagesapi"
```

Import the database dump to MySQL.

```bash
host:~/Projects/voyagesapi$ docker exec -i voyagesapi-mysql mysql -uroot -pvoyages voyagesapi < data/voyagesapi.sql
```

View container logs.

```bash
host:~/Projects/voyagesapi$ docker logs voyagesapi-django
host:~/Projects/voyagesapi$ docker logs voyagesapi-mysql
```

*The Adminer app is provided as an additional way to work with the database.*

Note the following project resources:

* Voyages API: http://127.0.0.1:8000/
* Adminer: http://127.0.0.1:8080

## Cleanup

```bash
host:~/Projects/voyagesapi$ docker-compose down

host:~/Projects/voyagesapi$ docker container prune
host:~/Projects/voyagesapi$ docker image prune
host:~/Projects/voyagesapi$ docker volume prune
host:~/Projects/voyagesapi$ docker network prune
```

## Using the API

### 0. AUTHENTICATION

#### Required as of March 16.

documentation: https://www.django-rest-framework.org/api-guide/authentication/

It's pretty straightforward. You simply need to declare a header with the key "Authorization" and the value "Token abcdef....".

So any request, like ```GET http://127.0.0.1:8000/past``` simply becomes ```GET http://127.0.0.1:8000/past -H 'Authorization: Token abcdef....'```

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
	r=requests.get(url,headers=headers)


### 1. POST Requests

March 31: Enabled POST requests

Why?

* This will allow for the construction of more complex queries
* For instance, it allows us to use the autocomplete endpoint to turn inexact text searches into precise selectors

How does it differ from GET requests documented below?

* As little as possible :)
* Values should simply be passed wrapped as arrays
* With the one exception that inexact text matching has been deprecated in favor of exact matching of arrayed values

So a request to PAST asking of people transported on voyages with Voyage ID's between 2314 and 2500 would look like
	
	POST http://127.0.0.1:8000/past/
	
	Body:
	{
		'hierarchical': ['false'],
		'results_page': ['3'],
		'results_per_page': ['20'],
		'voyage__voyage_id': ['2314,2500']
	}
	
And would return results 60-79 of 21,867 total records.


Or, to use the exact text with autocomplete as hinted at above, you might send the following request

	POST http://127.0.0.1:8000/voyage/autocomplete

	Body:
	{'voyage_itinerary__imp_principal_region_slave_dis__region': 'jam'}

And get back

	{
		"voyage_itinerary__imp_principal_region_slave_dis__region": [
			"Jamaica"
		]
	}

Then feed that precise value into that variable:

	POST http://127.0.0.1:8000/voyage/
	
	Body:
	{	'voyage_itinerary__imp_principal_region_slave_dis__region':
		['Barbados','Jamaica']
	}

And get back 5,816 results.


### 2. Request People, Voyages, Places, Estimates, or an Autocompletion

1. People: GET http://127.0.0.1:8000/past
1. Voyages: GET http://127.0.0.1:8000/voyage
1. Places: GET http://127.0.0.1:8000/voyage/geo
1. Estimates:  GET http://127.0.0.1:8000/assessment

	'imp_broad_region_voyage_begin':
	{
	'broad_region': 'Brazil',
	'id': 6,
	'latitude': '-18.8645820',
	'longitude': '-39.7548900',
	'show_on_map': True,
	'value': 50000
	},	

#### 2a. Autocomplete

1. accepts a request
	1. for one field
	1. which must be text
1. returns
	1. the first 10 unique entries in flat list form
	1. and a results count

example: GET http://127.0.0.1:8000/voyage/autocomplete?voyage_captainconnection__captain__name=jos

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

### 3. Get a list of the variables available to you, and their labels and data types

1. People: ```OPTIONS http://127.0.0.1:8000/past?hierarchical=False```
1. Voyages: ```OPTIONS http://127.0.0.1:8000/voyage?hierarchical=False```
1. Places: ```OPTIONS http://127.0.0.1:8000/voyage/geo?hierarchical=False```
1. Estimates ```OPTIONS http://127.0.0.1:8000/assessment/?hierarchical=False```

This looks like:


	'transactions__transaction__voyage__voyage_itinerary__imp_port_voyage_begin__region__latitude':
		{
		'label': 'Latitude of point',
		'type': '<class "rest_framework.fields.DecimalField>"
		}


Why "hierarchical=False"?

1. The default is hierarchical=True, which gives you a tree
1. These variables' hierarchical relations correspond to links between db tables
1. The django syntax for those links is a double underscore: "__"
1. Coders are telling me it's easier to use the fully-qualified name of the variable rather than piecing it together

### 3a. Filter and sort on any of these variables

1. GET http://127.0.0.1:8000/voyage?voyage_dates__imp_arrival_at_port_of_dis_yyyy=1800,1810
1. GET http://127.0.0.1:8000/voyage/?voyage_itinerary__imp_principal_region_slave_dis__region=Barbados&voyage_dates__imp_arrival_at_port_of_dis_yyyy=1800,1850&selected_fields=voyage_dates__imp_arrival_at_port_of_dis_yyyy,voyage_slaves_numbers__imp_total_num_slaves_embarked,voyage_itinerary__imp_port_voyage_begin__place,voyage_ship_owner__name,voyage_itinerary__imp_principal_region_slave_dis__region&results_page=2&order_by=voyage_dates__imp_arrival_at_port_of_dis_yyyy,voyage_itinerary__imp_port_voyage_begin__name,voyage_itinerary__imp_port_voyage_begin__longitude
1. GET http://127.0.0.1:8000/voyage/geo?longitude=-20,-6&latitude=-20,38

### 3b. Aggregate on any variable

You can also aggregate on numerical voyage variables by requesting any number of comma-separated numeric fields with the parameter ```aggregate_fields=...```

It will only return aggregations on valid numeric fields.

But it returns *all* aggregation functions on selected numeric fields (sum, min, max, avg, stddev), so some data may be nonsensical (e.g., the sum of a percentage field).

You can still run filters and sorts on variables, e.g. ```voyage_dates__imp_arrival_at_port_of_dis_yyyy=1800,1810```

Fields to aggregate 

e.g., ```GET http://127.0.0.1:8000/voyage/aggregations?aggregate_fields=voyage_slaves_numbers__imp_total_num_slaves_embarked,voyage_slaves_numbers__imp_total_num_slaves_disembarked```

Looks like:

	{
	"voyage_slaves_numbers__imp_total_num_slaves_embarked":
		{
		"sum": 11264030,
		"avg": 181.3269,
		"min": 0,
		"max": 2024,
		"stddev": 186.44502407088743
		},
	"voyage_slaves_numbers__imp_total_num_slaves_disembarked":
		{
		"sum": 9776588,
		"avg": 158.1281,
		"min": 0,
		"max": 1700,
		"stddev": 163.52181290079272
		}
	}


### 4. Paginate

e.g., GET http://127.0.0.1:8000/voyage?results_page=4&results_per_page=20

Check the headers to see previous_uri, next_uri, and total_results_count

### 5. Dataframes / Field Selection

There is functionality to select only specific variables. It is best used with the voyages dataframes endpoint, which returns columns of variables (to the extent possible with multi-valued fields). It could be improved upon in terms of performance and functionality.

e.g., GET http://127.0.0.1:8000/voyage/dataframes?&voyage_dates__imp_arrival_at_port_of_dis_yyyy=1800,1810&selected_fields=voyage_itinerary__imp_broad_region_voyage_begin__broad_region,voyage_itinerary__first_landing_region__region,voyage_itinerary__first_landing_place__place,voyage_slaves_numbers__imp_total_num_slaves_embarked

Looks like:

	{   'voyage_itinerary__first_landing_place__place':
		[
			'Barbados, port unspecified',
			'Freetown',
			'Freetown',
			...
		],
		'voyage_itinerary__first_landing_region__region':
		[
			'Barbados',
			'Sierra Leone',
			'Sierra Leone',
			...
		],
		'voyage_itinerary__imp_broad_region_voyage_begin__broad_region':
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

