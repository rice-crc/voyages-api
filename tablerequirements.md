Requirements for a flexible table:

TOP-LINE

* We're working to replicate the functionality in the "Results" tab here: https://www.slavevoyages.org/voyage/database
* This should be designed so that it works for both of the following endpoints:
	* Voyages: https://voyages3-api.crc.rice.edu/voyage/
	* People https://voyages3-api.crc.rice.edu/past/
* Design features in the API that should make this possible
	* Each column corresponds to a single variable in the db
	* Variable labels and data types are accessible through an OPTIONS call
* Admin view
	* Necessary: elect which variables are available to the user in the table view
	* Reach goal: organize how these vars are grouped in the search menu
* Results tabular view
	* User can select which columns to display in the table
	* With a default list already being in place
	* And user can search/filter on and sort by any variable that the admin view has enabled
	* Clicking on a row opens a modal card view that shows all vars
* Card view
	* Easy toggle from table to card view
	* No filter menus on card view
	* Click to expand a card to show all vars on an item
* Lazy loading/virtual scrolling on both tabular & card views (reach goal)

OPEN QUESTIONS

* How do we organize the table, the filters, and the available variables?
	* I'm thinking something like this: https://react-table.tanstack.com/docs/examples/filtering
		* Folds the search/filter option components into the header row
		* Vars are grouped
		* We could, hopefully
			* Allow the group header to be the place where a user elects to show or hide columns
	* Very much open to alternatives -- but right now we're not maximizing our real estate.
* Where do we display the active searches/filters, and make it easy to modify or remove those filters?
* When a user modifies a filter, do we automatically execute the search? Or do they have to hit a submit button? I'd personally like to try the automatic execution.
* How do we display highly nested data?
	* Perhaps a nested table for cases like voyages embedded in PAST (see https://voyages3-api.crc.rice.edu/past/)
	* But probably something like a text formatter for cases like voyage_sourceconnection (see https://voyages3-api.crc.rice.edu/voyage/)

DETAILED BREAKDOWN

* The labels for the columns must come from an options call
	* (this allows the Voyages team to change the labels on the API side)
* The user must be able to select which columns are shown in the table
	* But the react app will need an administrative interface that determines which columns are available for user selection
		* (We have nearly 1000 fields, so we're going to need to pare it down)
	* The means of governing this would be, ideally, a json file that looks like this: https://github.com/JohnMulligan/voyages-api/blob/main/src/voyage/voyage_options.json
		* But which has one extra attribute for each field, something like "visible" w boolean values
		* I would suggest a simple tree structure w checkboxes
			* Looks like OPTIONS https://voyages3-api.crc.rice.edu/voyage/?hierarchical=False
			* Xinna Pan has a working example of this tree structure: https://github.com/XinnaPan/Slave_Voyage
		* Indeed, by managing this with a flat json file that has the same structure as our OPTIONS response
			* You'd be able to quickly identify whether a variable had become unavailable, or its datatype or label had changed
			* In fact, this admin tool would eventually replace my manual management of these OPTIONS json files
	* We will want a similar (if not combined?) interface for organizing the grouping of vars in table and card displays
		* This could probably be reduced to a json flat file
		* That hierarchically nests just the names of the visible variables
* Sorting is easy: https://voyages3-api.crc.rice.edu/voyage/?order_by=VARNAME1,-VARNAME2....
* Searching/filtering is relatively straightforward for now
	* Quick breakdown of field types:
		* As of right now, there are only 4 types of field we're concerned with allowing users to filter on:
			* <class 'rest_framework.fields.DecimalField'>
			* <class 'rest_framework.fields.FloatField'>
			* <class 'rest_framework.fields.IntegerField'>
			* <class 'rest_framework.fields.CharField'>
		* "table" type field is a special case:
			* essentially a placeholder that allows for hierarchical nesting of fields
			* can't be searched on
		* the below types can be ignored for now
			* <class 'rest_framework.fields.BooleanField'> (though this has been implemented)
			* <class 'rest_framework.fields.DateTimeField'>
			* <class 'rest_framework.relations.PrimaryKeyRelatedField'>
	* Numeric fields accept ranges and give back inclusive matches on that range: varname=min,max
		* e.g., https://voyages3-api.crc.rice.edu/voyage/?voyage_dates__imp_arrival_at_port_of_dis_yyyy=1800,1850
		* The filter component should therefore be a range slider -- and I think they'll all work well with a step of 1
		* The min/max for the range slider, when a user calls it up, can be obtained by hitting the stats endpoint: https://voyages3-api.crc.rice.edu/voyage/aggregations?aggregate_fields=VARNAME
	* Text fields accept strings and give back inexact matches: varname=str
		* e.g., https://voyages3-api.crc.rice.edu/voyage/?voyage_itinerary__imp_principal_region_slave_dis__region=Barbados
		* but we're going to tweak this a bit -- see below
* Improving text field searching/filtering
	* You'll probably want to start with a simple text input just to get it working
	* But very quickly iterate that into an autocomplete selector
		* https://react-select.com/advanced (multi-select)
		* https://www.npmjs.com/package/react-autocomplete (async)
	* Autocomplete selection workflow
		* A user selects a text field they want to filter on
		* A text input is presented which, as they type,
			* hits the autocomplete endpoint: https://voyages3-api.crc.rice.edu/voyage/autocomplete?VARNAME=PARTIALSTRING
			* provides a drop-down menu of the results and lets them select up to 10
* Menu special cases
	* Geo var selection/filtering
		* Almost certainly has to be displayed in a nested format, just as it currently is
		* And ideally, we'd be able to do the same sort of tree autocomplete filtering that's currently enabled
		* Fortunately, we have an endpoint for that! https://voyages3-api.crc.rice.edu/voyage/geo
* Pagination
	* req params:
		* results_per_page=INT (default = 10, make the max = 100 for now)
		* results_page=INT
	* resp headers that will help w pagination:
		* next_uri=URI or None
		* prev_uri=URI or None
		* total_results_count=INT
* Exclude the following functionality from this first build
	* Download results
	* Saved searches
	