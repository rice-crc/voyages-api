# API refactor

## I. simplifications/built-ins

* pagination with paginator
* dataframes with valuelist
* can the field selection on nested objects be arbitrary/flexible through some built-in?
* another way of putting it:
	* can we get rid of the serializer now that it's not "dynamic" w.r.t. fields?
		* doing that would require finding a new way of building my indices/dataframes
		* ... which is doable. 
	* or do we in fact need to go through the serializer middleware, in which case,
		* we're going to need multiple serializers for different kinds of requests
		* as we saw in the past graph-like requests, where the serializers interweave

## II. logical improvements

* naming conventions
	* the variable names are unwieldy on nested objects
	* however, i am using those to line up my queries with my serializers
	* allowing me to do things like arbitrary prefetches
	* so it's an open question if that can actually be improved on much
	* this relates to the serializer question in the prior question as well
* break out items in the request
	* search object
	* view arguments e.g. 
		* list/table/card: pageNumber & resultsPerPage
		* pivot table: aggregation functions
	* try to make a hash of the whole thing for redis caching