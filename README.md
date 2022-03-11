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

### 1. Request People, Voyages, Places, or Estimates

1. People: GET http://127.0.0.1:8000/past
1. Voyages: GET http://127.0.0.1:8000/voyage
1. Places: GET http://127.0.0.1:8000/voyage/geo
1. Estimates:  GET http://127.0.0.1:8000/assessment

This looks like:


```
	'imp_broad_region_voyage_begin':
		{
		'broad_region': 'Brazil',
		'id': 6,
		'latitude': '-18.8645820',
		'longitude': '-39.7548900',
		'show_on_map': True,
		'value': 50000
		},
	
```


### 2. Get a list of the variables available to you, and their labels and data types

1. People: ```OPTIONS http://127.0.0.1:8000/past?hierarchical=False```
1. Voyages: ```OPTIONS http://127.0.0.1:8000/voyage?hierarchical=False```
1. Places: ```OPTIONS http://127.0.0.1:8000/voyage/geo?hierarchical=False```
1. Estimates ```OPTIONS http://127.0.0.1:8000/assessment/?hierarchical=False```

This looks like:

```
	'transactions__transaction__voyage__voyage_itinerary__imp_port_voyage_begin__region__latitude':
		{
		'label': 'Latitude of point',
		'type': '<class "rest_framework.fields.DecimalField>"
		}
```

Why "hierarchical=False"?

1. The default is hierarchical=True, which gives you a tree
1. These variables' hierarchical relations correspond to links between db tables
1. The django syntax for those links is a double underscore: "__"
1. Coders are telling me it's easier to use the fully-qualified name of the variable rather than piecing it together

### 3a. Filter, Sort, Order_by on any of these variables

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

```
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
```

### 4. Paginate

e.g., GET http://127.0.0.1:8000/voyage?results_page=4&results_per_page=20

Check the headers to see previous_uri, next_uri, and total_results_count

### 5. Dataframes / Field Selection

There is functionality to select only specific variables. It is best used with the voyages dataframes endpoint, which returns columns of variables (to the extent possible with multi-valued fields). It could be improved upon in terms of performance and functionality.

e.g., GET http://127.0.0.1:8000/voyage/dataframes?&voyage_dates__imp_arrival_at_port_of_dis_yyyy=1800,1810&selected_fields=voyage_itinerary__imp_broad_region_voyage_begin__broad_region,voyage_itinerary__first_landing_region__region,voyage_itinerary__first_landing_place__place,voyage_slaves_numbers__imp_total_num_slaves_embarked

Looks like:

```
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
```
