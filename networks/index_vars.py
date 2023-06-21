transatlantic_maps={
	'endpoint':'voyage/dataframes',
	'name':'voyage_transatlantic_maps',
	## USE THE VOYAGES SEARCH FILTERS TO ENSURE THAT WE ONLY GET THE OBJECTS WE WANT
	## FOR INSTANCE, ONLY TRANSATLANTIC VOYAGES
	'filter':{'dataset':[0,0]},
	## THIS OCEANIC FLAG IS BASICALLY TAKEN FOR GRANTED RIGHT NOW
	## BUT MAYBE LATER ON WE'LL LOAD IN PERSON-TO-PERSON DATA
	'type':'oceanic',
	## STRUCTURE:
	### THE NAME OF THE GRAPH (E.G., PLACE ROUTES)
	### THE NODES, IN ORDER (E.G., ORIGIN, EMBARK, OCEAN, DISEMBARK, POST-DISEMBARK)
	'graph_params': [
		{
			'name':'place',
			'ordered_nodes':[
				{
					## BECAUSE WE WILL ENCOUNTER SOME NODES IN DIFFERENT CONTEXTS
					### E.G., THE BIGHT OF BIAFRA AS A REGION OF EMBARK & AS DISEMBARK
					### WE WILL WANT TO MAKE SURE THAT WE 
					### SO THAT
					#### A. SUB-GRAPH CALLS WORK PROPERLY
					###### LIKE WHEN WE'RE LINKING ORIGINS TO EMBARKATIONS TO OCEANIC...
					#### B. WE DON'T DUPLICATE, OR TOO AGGRESSIVELY DE-DUPLICATE
					'tag':'embarkation',
					'values':{
						'pk':'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__id',
						'name':'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__name',
						'lat':'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__latitude',
						'lon':'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__longitude',
						'val':'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__value'
					}
				},
				## THE OCEANIC GRAPH IS A SPECIAL CASE
				## IT COMES FROM A FLAT FILE, NOT AN API CALL
				'OCEANIC',
				{
					'tag':'disembarkation',
					'values':{
						'pk':'voyage_itinerary__imp_principal_port_slave_dis__geo_location__id',
						'name':'voyage_itinerary__imp_principal_port_slave_dis__geo_location__name',
						'lat':'voyage_itinerary__imp_principal_port_slave_dis__geo_location__latitude',
						'lon':'voyage_itinerary__imp_principal_port_slave_dis__geo_location__longitude',
						'val':'voyage_itinerary__imp_principal_port_slave_dis__geo_location__value'
					}
				}
			]
		},
		{
			'name':'region',
			'ordered_nodes':[
				{
					'tag':'embarkation',
					'values':{
						'pk':'voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__id',
						'name':'voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__name',
						'lat':'voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__latitude',
						'lon':'voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__longitude',
						'val':'voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__value'		
					}
				},
				'OCEANIC',
				{
					'tag':'disembarkation',
					'values':{
						'pk':'voyage_itinerary__imp_principal_region_slave_dis__geo_location__id',
						'name':'voyage_itinerary__imp_principal_region_slave_dis__geo_location__name',
						'lat':'voyage_itinerary__imp_principal_region_slave_dis__geo_location__latitude',
						'lon':'voyage_itinerary__imp_principal_region_slave_dis__geo_location__longitude',
						'val':'voyage_itinerary__imp_principal_region_slave_dis__geo_location__value'		
					}
				}
			]
		}
	],
	'oceanic_network_file':'maps/transatlantic_routes.json'
}

intraamerican_maps={
	'endpoint':'voyage/dataframes',
	'name':'voyage_intraamerican_maps',
	'filter':{'dataset':[1,1]},
	'type':'oceanic',
	'graph_params': [
		{
			'name':'place',
			'ordered_nodes':[
				{
					'tag':'embarkation',
					'values':{
						'pk':'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__id',
						'name':'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__name',
						'lat':'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__latitude',
						'lon':'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__longitude',
						'val':'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__value'
					}
				},
				'OCEANIC',
				{
					'tag':'disembarkation',
					'values':{
						'pk':'voyage_itinerary__imp_principal_port_slave_dis__geo_location__id',
						'name':'voyage_itinerary__imp_principal_port_slave_dis__geo_location__name',
						'lat':'voyage_itinerary__imp_principal_port_slave_dis__geo_location__latitude',
						'lon':'voyage_itinerary__imp_principal_port_slave_dis__geo_location__longitude',
						'val':'voyage_itinerary__imp_principal_port_slave_dis__geo_location__value'
					}
				}
			]
		},
		{
			'name':'region',
			'ordered_nodes':[
				{
					'tag':'embarkation',
					'values':{
						'pk':'voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__id',
						'name':'voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__name',
						'lat':'voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__latitude',
						'lon':'voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__longitude',
						'val':'voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__value'		
					}
				},
				'OCEANIC',
				{
					'tag':'disembarkation',
					'values':{
						'pk':'voyage_itinerary__imp_principal_region_slave_dis__geo_location__id',
						'name':'voyage_itinerary__imp_principal_region_slave_dis__geo_location__name',
						'lat':'voyage_itinerary__imp_principal_region_slave_dis__geo_location__latitude',
						'lon':'voyage_itinerary__imp_principal_region_slave_dis__geo_location__longitude',
						'val':'voyage_itinerary__imp_principal_region_slave_dis__geo_location__value'		
					}
				}
			]
		}
	],
	'oceanic_network_file':'maps/intraamerican_routes.json'
}

ao_maps={
	'endpoint':'past/enslaved/dataframes',
	'name':'african_origins_maps',
	'filter':{
		'dataset':[0,0]
	},
	'type':'oceanic',
	'graph_params': [
		{
			'name':'place',
			'ordered_nodes':[
				{
					'tag':'origin',
					'values':{
						'pk':'language_group__id',
						'lat':'language_group__latitude',
						'lon':'language_group__longitude',
						'name':'language_group__name',
						'val':None
					}
				},
				{
					'tag':'embarkation',
					'values':{
						'pk':'voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__id',
						'name':'voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__name',
						'lat':'voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__latitude',
						'lon':'voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__longitude',
						'val':'voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__value'
					}
				},
				'OCEANIC',
				{
					'tag':'disembarkation',
					'values':{
						'pk':'voyage__voyage_itinerary__imp_principal_port_slave_dis__geo_location__id',
						'name':'voyage__voyage_itinerary__imp_principal_port_slave_dis__geo_location__name',
						'lat':'voyage__voyage_itinerary__imp_principal_port_slave_dis__geo_location__latitude',
						'lon':'voyage__voyage_itinerary__imp_principal_port_slave_dis__geo_location__longitude',
						'val':'voyage__voyage_itinerary__imp_principal_port_slave_dis__geo_location__value'
					}
				},
				{
					'tag':'post-disembarkation',
					'values':{
						'pk':'post_disembark_location__geo_location__id',
						'value':'post_disembark_location__geo_location__value',
						'lat':'post_disembark_location__geo_location__latitude',
						'lon':'post_disembark_location__geo_location__longitude',
						'val':'post_disembark_location__geo_location__name'
					}
				}
			]
		},
		{
			'name':'region',
			'ordered_nodes':[
				{
					'tag':'origin',
					'values':{
						'pk':'language_group__id',
						'lat':'language_group__latitude',
						'lon':'language_group__longitude',
						'name':'language_group__name',
						'val':None
					}
				},
				{
					'tag':'embarkation',
					'values':{
						'pk':'voyage__voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__id',
						'name':'voyage__voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__name',
						'lat':'voyage__voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__latitude',
						'lon':'voyage__voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__longitude',
						'val':'voyage__voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__value'		
					}
				},
				'OCEANIC',
				{
					'tag':'disembarkation',
					'values':{
						'pk':'voyage__voyage_itinerary__imp_principal_region_slave_dis__geo_location__id',
						'name':'voyage__voyage_itinerary__imp_principal_region_slave_dis__geo_location__name',
						'lat':'voyage__voyage_itinerary__imp_principal_region_slave_dis__geo_location__latitude',
						'lon':'voyage__voyage_itinerary__imp_principal_region_slave_dis__geo_location__longitude',
						'val':'voyage__voyage_itinerary__imp_principal_region_slave_dis__geo_location__value'		
					}
				},
				{
					'tag':'post-disembarkation',
					'values':{
						'pk':'post_disembark_location__geo_location__id',
						'value':'post_disembark_location__geo_location__value',
						'lat':'post_disembark_location__geo_location__latitude',
						'lon':'post_disembark_location__geo_location__longitude',
						'val':'post_disembark_location__geo_location__name'
					}
				}
			]
		}
	],
	'oceanic_network_file':'maps/intraamerican_routes.json'
}