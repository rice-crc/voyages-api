# VOYAGES API

## System Requirements

For reference, this document was written while testing on a 2022 MacBook Pro 
running MacOS Ventura and Docker Desktop 4.21.1.

Install the macOS Xcode Command Line Tools.

```bash
local:~$ sudo xcodebuild -license
local:~$ xcode-select install
```

Install Homebrew.

```bash
local:~$ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Install and configure the GitHub CLI.

```bash
local:~$ brew install gh
local:~$ gh auth login
```

Install Docker Desktop.

Optionally, download and install manually instead of using Homebrew.

```bash
local:~$ brew install --cask docker
```

## Getting Started

Change to your local project directory (in this case, `~/Projects`).

```bash
local:~$ cd Projects
```

Fork the `rice-crc/voyages-api` repository and clone to your local environment.

```bash
local:~/Projects$ gh repo fork rice-crc/voyages-api --remote --default-branch-only --clone
```

## Local App Deployment

Change to the cloned repository directory.

```bash
local:~/Projects$ cd voyages-api
```

Copy the default config files for each app component.

```bash
local:~/Projects/voyages-api$ cp api/voyages3/localsettings.py{-default,}
local:~/Projects/voyages-api$ cp networks/localsettings.py{-default,}
local:~/Projects/voyages-api$ cp stats/localsettings.py{-default,}
```

Download the latest database dump from the Google Drive project share and 
expand into the `data/` directory. Rename the expanded file to `data/voyages_prod.sql`.

Build the API containers. The component containers must be built separately.

Remove the `-d` option to run the process in the foreground.

Allow a short bit of time for the mysql container to initialize.

```bash
local:~/Projects/voyages-api$ docker compose up --build -d voyages-mysql voyages-api voyages-adminer
```

Verify the data import.

```bash
local:~/Projects/voyages-api$ docker exec -i voyages-mysql mysql -uvoyages -pvoyages -e "show databases"
local:~/Projects/voyages-api$ docker exec -i voyages-mysql mysql -uvoyages -pvoyages -e "show tables from voyages_api"
local:~/Projects/voyages-api$ docker exec -i voyages-mysql mysql -uvoyages -pvoyages -e "select * from voyages_api.voyage_voyage limit 1"
```

Run the app setup and configuration tasks.

```bash
local:~/Projects/voyages-api$ docker exec -i voyages-api bash -c 'python3 manage.py collectstatic --noinput'
local:~/Projects/voyages-api$ docker exec -i voyages-api bash -c 'python3 manage.py migrate'
local:~/Projects/voyages-api$ docker exec -i voyages-api bash -c 'python3 manage.py sync_geo_data'
local:~/Projects/voyages-api$ docker exec -i voyages-api bash -c 'python3 manage.py sync_voyage_dates_data'
```

Build the API component containers.

```bash
local:~/Projects/voyages-api$ docker compose up --build -d voyages-networks voyages-stats
```

## Generating an API Key for the Flask Components

The Flask components of the app require an API key.

Create a new Django superuser account through the CLI.

```bash
local:~/Projects/voyages-api$ docker exec -it voyages-api bash -c 'python3 manage.py createsuperuser'
```

Use those credentials to log in to the Django admin interface at 
[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) and create an API 
token for the account.

Update the `stats/localsettings.py` and `networks/localsettings.py` files with 
the new token.

Restart the Flask component containers.

```bash
local:~/Projects/voyages-api$ docker restart voyages-networks voyages-stats
```

## Cleanup

If you want to tear it down:

```bash
local:~/Projects/voyagesapi$ docker compose down
local:~/Projects/voyagesapi$ docker container prune -f
local:~/Projects/voyagesapi$ docker image prune -f
local:~/Projects/voyagesapi$ docker volume prune -f
local:~/Projects/voyagesapi$ docker network prune -f
```
## Resources

Note the following project resources:

* Voyages API: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* API Stats Component: [http://127.0.0.1:5000](http://127.0.0.1:5000/)
* API Networks Component: [http://127.0.0.1:5005](http://127.0.0.1:5005/)
* Solr: [http://127.0.0.1:8983](http://127.0.0.1:8983)
* Adminer: [http://127.0.0.1:8080](http://127.0.0.1:8080)

## Adminer

The Adminer container is provided as an optional way of working with the database.

Visit http://127.0.0.1:8080 and log in with the following values.

* Server: voyages-mysql
* User: voyages
* Password: voyages
* Database: voyages-api

## Development Workflow

This project follows a fork-and-pull workflow.

* The `rice-crc:voyages-api` repository is referred to as `upstream` and your fork as `origin`
* The upstream/develop branch serves as the default change integration point between developers
* A developer makes Pull Requests from their origin/working-branch to upstream/develop

Keep the following in mind when contributing code.

* Keep your fork up-to-date with the upstream repository
* Always start new work with a new working branch
* Periodically fetch and rebase the latest upstream/develop changes onto your local working-branch
* Do not make Pull Requests containing untested or unfinished code unless intended for temporary review and discussion
* Clean up the work in your local environment once a Pull Request has been accepted and merged

Use the following git process to contribute work.

```bash
git fetch upstream            # Pull the latest changes from upstream/develop
git checkout -b <short-desc>  # and create a new working branch

git fetch upstream            # Do work; before any commits, pull the latest
git rebase upstream/develop   # changes from upstream/develop and rebase onto
                              # your working branch

git add . && git commit       # Commit your changes to the working branch
										# Repeat pulling changes and adding commits until
										# your work is done

git push origin HEAD          # Push the working branch to your fork and make
gh pr create --fill           # a Pull Request to upstream/develop

git checkout develop          # Once the PR is accepted and merged, delete
git branch -D <short-desc>    # your working branch

git pull                      # Pull the latest changes from upstream/develop
git push                      # and update your fork by pushing to origin/develop
```

----------------------

## Using the API --> NEEDS AN UPDATE

There are currently 5 major endpoints, which allow you to query on People, Voyages, Places, and Estimates

1. Enslaved: POST http://127.0.0.1:8000/past/enslaved/
1. Enslavers: POST http://127.0.0.1:8000/past/enslavers/
1. Voyages: POST http://127.0.0.1:8000/voyage/
1. Places: POST http://127.0.0.1:8000/geo/
1. Estimates:  POST http://127.0.0.1:8000/assessment/
1. Documents:  GET http://127.0.0.1:8000/docs/

### 0. AUTHENTICATION

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
	resp=requests.post(url,headers=headers)
	print(resp.status_code)
	j=json.loads(resp.text)
	print(json.dumps(j,indent=2))

### 1. Using POST Requests


#### 1A. Numerics

RANGES: A request to PAST asking for people transported on voyages with Voyage ID's between 2314 and 2500 would look like
	
	POST http://127.0.0.1:8000/past/enslaved/
	
	Body:
	{
		'results_page': ['3'],
		'results_per_page': ['20'],
		'voyage__voyage_id': ['2314,2500']
	}
	
ONE-SIDED INTERVALS: Use double-asterisks in a list of length 2 for a greater-than or less-than request.

	POST http://127.0.0.1:8000/past/enslaved/
	
	Body:
	{
		'results_page': ['3'],
		'results_per_page': ['20'],
		'voyage__voyage_id': ['2314,**']
	}

DISCRETE INTEGER VALUES: You can filter on specific values *on an integer field only* by including an single asterisk in your list.

	POST http://127.0.0.1:8000/past/enslaved/
	
	Body:
	{
		'voyage__voyage_id': ['*,2314,2500']
	}

#### 1B. Text fields

Text fields accept exact matches only: 

	POST http://127.0.0.1:8000/voyage/
	
	Body:
	{	'voyage_itinerary__imp_principal_region_slave_dis__geo_location__name':
		['Barbados','Jamaica']
	}

How do you find the exact matches? By using autocomplete to see the valid values on that field.

This request

	POST http://127.0.0.1:8000/voyage/autocomplete

	Body:
	{'voyage_itinerary__imp_principal_region_slave_dis__geo_location__name': ['jam']}

Would return

	{
		"results": [
			{
				"id": 2419,
				"label": "Jamaica"
			}
		],
		"total_results_count": 3715
	}


### 2. Enumerating variables, relationships, and data types

1. People: ```OPTIONS http://127.0.0.1:8000/past/?hierarchical=False```
1. Voyages: ```OPTIONS http://127.0.0.1:8000/voyage/?hierarchical=False```
1. Places: ```OPTIONS http://127.0.0.1:8000/voyage/geo?hierarchical=False```
1. Estimates ```OPTIONS http://127.0.0.1:8000/assessment/?hierarchical=False```

Why "hierarchical=False"?

1. The default is hierarchical
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

### Routes (voyage/aggroutes)

Get routes for aggregations of voyages, while performing searches. Routes come back in the format of bezier curves. May reintroduce a geojson option down the line so we can build an "export to storymaps" option.

*brief update, august 22*

It was observed to me that there appear to be fewer routes than expected on the map with certain searches. I've added an option for more verbose server logging of failed routes by passing the parameter verbose_mode = True. Running this myself, I find that the list of failed A/B routes for voyages comes entirely from pairs where the source or destination of a voyage has null lat/long coords.

Specifically, in my current version of the API db, I have 390 total locations with null lat/longs:

* 1 broad region
* 23 regions
* 366 ports

Whereas on prod, I see the following breakdown:

* 0 broad regions
* 1 region
* 57 ports

This is great -- it means that some major cleanup has been done on production. A quick sync will make a world of difference. Having done that (see sync_locations.py), and then sifting through for intra-american voyages that actually belong in the trans-atlantic database, the only bad routes we have are the ones that the researchers entered without proper lat/long data for that port or region.

IAM voyages that should be TASTDB (visually, at least): 
102468,102744,107315,107352,107368,107400
104692,104693,104694,104695,104698,104699,104700,104701,104702

Madeira needs a different region in the system as well (at least, visually)

*end brief update*

Required fields:

1. GROUPBY FIELDS. 2 VALID OPTIONS RIGHT NOW

A. PORTS source/target geo id var pair:
	"groupby_fields": [
		"voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__id",
		"voyage_itinerary__imp_principal_region_slave_dis__geo_location__id"
	]
		
B. REGIONS source/target geo id var par:

	'groupby_fields': [
		'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__id',
		'voyage_itinerary__imp_principal_port_slave_dis__geo_location__id'
	]

2. DATASET. 2 VALID OPTIONS RIGHT NOW:

(this lets the system to know which route network it will use to generate the map)

A. [0,0] --> TRANSATLANTIC

B. [1,1] --> INTRA-AMERICAN

3. VALUE FIELD TUPLE:

(the numerical )


--post req params--
{   'cachename': ['voyage_maps'],
    'dataset': ['0', '0'],
    'groupby_fields': [   'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__id',
                          'voyage_itinerary__imp_principal_port_slave_dis__geo_location__id'],
    'output_format': ['geosankey'],
    'value_field_tuple': [   'voyage_slaves_numbers__imp_total_num_slaves_embarked',
                             'sum']}

#### ROUTES EXAMPLE REQUEST

Showing the REGIONAL routes of the numbers of people who disembarked from Trans-Atlantic voyages that are believed [imputed] to have landed in Barbados between 1790 and 1800):

	POST http://127.0.0.1:8000/voyage/aggroutes

	{
		"voyage_itinerary__imp_principal_region_slave_dis__geo_location__name": [
			"Barbados"
		],
		"voyage_dates__imp_arrival_at_port_of_dis_yyyy": [
			1790,
			1800
		],
		"groupby_fields": [
			"voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__id",
			"voyage_itinerary__imp_principal_region_slave_dis__geo_location__id"
		],
		"value_field_tuple": [
			"voyage_slaves_numbers__imp_total_num_slaves_disembarked",
			"sum"
		],
		"cachename": [
			"voyage_maps"
		],
		"dataset": [
			0,
			0
		]
	}

#### ROUTES EXAMPLE RESPONSE 

The above will result in a two-part response:

* "points": First a geojson feature collection of points (here, regional lat/long/name/id quads)
* and after those points, a collection of connected splined line segments with various weights and the edge_id corresponding to the database's internal id for the connection between two points on the map (which I'm not currently hooking into but could be used later)

	{"points": {
			"type": "FeatureCollection",
			"features": [
				{
					"type": "Feature",
					"id": 2391,
					"geometry": {
						"type": "Point",
						"coordinates": [
							"-66.2374610",
							"14.5017080"
						]
					},
					"properties": {
						"name": "Caribbean"
					}
				},
			...
			]
		},
		"routes": [
			[
				[
					[
						17.881263,
						-76.522778
					],
					[
						17.6858952,
						-76.8273926
					]
				],
				[
					[
						17.774928285,
						-76.84761837500001
					],
					[
						17.774928285,
						-76.84761837500001
					]
				],
				931574
			],
		]
	}
	
#### EXAMPLE JS RENDERING OF RESPONSE CURVES ON LEAFLET

AS OF AUG. 4, THE REACT APP IS HANDLING THOSE SPLINED CURVES WITH CODE LIKE THE BELOW
(FROM https://github.com/ZhihaoWan/Integ_CRC/blob/main/src/Component/VoyagePage/mapping/Spatial.js#L335-L344)

	routes.map((route) => {
		var commands = [];

		commands.push("M", route[0][0]);
		commands.push("C", route[1][0], route[1][1], route[0][1]);

		L.curve(commands, { color: "blue", weight: valueScale(route[2]) })
		  .bindPopup("Sum of slaves: " + route[2])
		  .addTo(map);
	  });

#### how does it work?

And what are the specific requirements of a post request like the above?

Piggybacks on the crosstabs endpoint, which means that you have to specify:

* source/target field pair, which must be geo_location__id fields
	* the first is the source (start) for the route, like the broad region of embarkation
	* the second is the target (end) for the route, like the region of disembarkation
* magnitude field and value function, such as number of people embarked and sum
* the name of the cache where your fields live (should be in voyage_maps)

Currently (July 1), we're accepting requests for the below a/b itinerary variable pairings -- that is, the "groupby_fields" parameter -- covering region-level and port-level embarkations/disembarkations:

	[
		"voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__id",
		"voyage_itinerary__imp_principal_region_slave_dis__geo_location__id"
	]
	
	[
		'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__id',
		'voyage_itinerary__imp_principal_port_slave_dis__geo_location__id']
	]

So a peek under the hood is necessary here, for now.

The custom django management command rebuild_geo_networks has already used NetworkX to find all the "best" a/b routes on the above variable pairings via the adjacencies and waypoints in the geo endpoint, and stored them as "Route" objects. That takes about 5 minutes to run.

The results of the above, highly-specific crosstabs request will be a dictionary in the format of ```{geolocation_source_id: {geolocation_target_id: magnitude...}...}```. With a couple extra parameters, then, the routes can simply be looked up and formatted as either geojson or geosankey outputs:

* dataset (trans-atlantic or intra-american)
* some kind of filter, for now, if you're going to be getting a dense network
* an output format. options are "geojson" or "geosankey"

format=geojson

* points (id is the id field for the location)
	* names are applied to all non-oceanic waypoint locations
* linestring segments with weights, summed up where the trips overlap
	* id is the id field in the adjacencies table

format=geosankey (in the hopes of using this: https://github.com/geodesign/spatialsankey )

* points and waypoints are returned as geojson
* links between them are returned as a source,target,weight triple

An interesting use-case: this would lend itself nicely to visual representations of pivot tables, with barely any alteration to the POST request.

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

Using Pandas-like syntax, we can also run searches and then find the aggregated values of numerical variables, grouped by a categorical variable.

For instance:

	POST "http://127.0.0.1:8000/voyage/groupby"
	data={
		"voyage_itinerary__imp_principal_region_slave_dis__geo_location__name":[
			"Barbados",
			"Jamaica"
		],
		'groupby_fields':['voyage_itinerary__imp_broad_region_slave_dis__geo_location__name',
		                  'voyage_dates__imp_length_home_to_disembark',
		                  voyage_slaves_numbers__imp_jamaican_cash_price],
		'agg_fn':['mean'],
		'cachename':['voyage_bar_and_donut_charts']
	}
	
... would return the following:

	{
		"voyage_dates__imp_length_home_to_disembark": {
			"Africa": 204.75903614457832,
			"Brazil": 261.37118868758284,
			"Caribbean": 292.67427568042143,
			"Europe": 346.45454545454544,
			"Mainland North America": 272.14159292035396,
			"Other": 340.63157894736844,
			"Spanish Mainland Americas": 501.7817258883249
		},
		"voyage_slaves_numbers__imp_jamaican_cash_price": {
			"Africa": 0.0,
			"Brazil": 0.0,
			"Caribbean": 38.931458094144666,
			"Europe": 0.0,
			"Mainland North America": 39.5338596491228,
			"Other": 0.0,
			"Spanish Mainland Americas": 37.36666666666667
		}
	}

Acceptable values for "agg_fn":

* "mean"
* "sum"

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

#### C. rebuild_geo_network

This rebuilds the voyage route networks (a little aggressively):

First, it deletes all entries

* in the adjacencies table
* in the locations table when those locations are coded as "oceanic waypoints"

Then, it

* takes the legacy routeNodes.js files from intra-american and trans-atlantic
* creates the oceanic network
	* nodes (in the locations table) for each of the oceanic waypoints in those networks, and codes them as dataset=0 (for translatlantic) or dataset=1 (for intraamerican)
	* edges (in the adjacencies table) for each of the links between these oceanic waypoints as defined in the js file
* creates more edges
	* walks through every entity in the geo network that has a lat/long pair
	* finds the closest oceanic waypoint node (inaccurate -- using euclidean distance)
	* makes a connection to it
	
If you don't like the connections it's making ... draw a better map !!!!

Run it with ```python3.9 manage.py rebuild_geo_network```

#### C. rebuild_geo_routes (NEW!)

This must be run for the voyage/aggroutes endpoint to work

Uses NetworkX to find all the "best" a/b routes on the above variable pairings via the adjacencies and waypoints in the geo endpoint, and stored them as "Route" objects. That takes about 5 minutes to run when finding approximately 17,000 valid routes between the following a/b and b/c pairs which I've for the time being hard-coded into the management command:

	a--> imp_begin=[
		"voyage_itinerary__imp_port_voyage_begin__geo_location__id",
		"voyage_itinerary__imp_region_voyage_begin__geo_location__id",
		"voyage_itinerary__imp_broad_region_voyage_begin__geo_location__id"
	]

	b--> imp_purchase=[
		"voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__id",
		"voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__id",
		"voyage_itinerary__imp_broad_region_of_slave_purchase__geo_location__id"
	]

	c--> imp_dis=[
		"voyage_itinerary__imp_principal_port_slave_dis__geo_location__id",
		"voyage_itinerary__imp_principal_region_slave_dis__geo_location__id",
		"voyage_itinerary__imp_broad_region_slave_dis__geo_location__id"
	]

-----------------

