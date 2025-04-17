big_df={
	'endpoint':'voyage/dataframes/',
	'schema_name':'Voyage',
	'name':'big_df',
	"variables":{
		"id": {
			"type": "int"
		},
		"voyage_id": {
			"type": "int"
		},
		"voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year": {
			"type": "int"
		},
		"voyage_slaves_numbers__imp_total_num_slaves_disembarked": {
			"type": "int"
		},
		"voyage_slaves_numbers__imp_total_num_slaves_embarked": {
			"type": "int"
		},
		"voyage_dates__length_middle_passage_days": {
			"type": "int"
		},
		"voyage_dates__imp_length_home_to_disembark": {
			"type": "int"
		},
		"voyage_crew__crew_first_landing": {
			"type": "int"
		},
		"voyage_crew__crew_voyage_outset": {
			"type": "int"
		},
		"voyage_ship__tonnage_mod": {
			"type": "int"
		},
		"voyage_slaves_numbers__imp_jamaican_cash_price": {
			"type": "int"
		},
		"voyage_slaves_numbers__imp_mortality_ratio": {
			"type": "pct"
		},
		"voyage_slaves_numbers__percentage_women_among_embarked_slaves": {
			"type": "pct"
		},
		"voyage_outcome__vessel_captured_outcome__name": {
			"type": "str"
		},
		"voyage_ship__imputed_nationality__name": {
			"type": "str"
		},
		"voyage_itinerary__imp_region_voyage_begin__name": {
			"type": "str"
		},
		"voyage_ship__rig_of_vessel__name": {
			"type": "str"
		},
		"voyage_itinerary__place_voyage_ended__name": {
			"type": "str"
		},
		"voyage_dates__slave_purchase_began_sparsedate__month": {
			"type": "int"
		},
		"voyage_slaves_numbers__percentage_men": {
			"type": "pct"
		},
		"voyage_dates__voyage_completed_sparsedate__month": {
			"type": "int"
		},
		"voyage_itinerary__region_of_return__name": {
			"type": "str"
		},
		"voyage_slaves_numbers__percentage_boy": {
			"type": "pct"
		},
		"voyage_itinerary__imp_principal_region_slave_dis__name": {
			"type": "str"
		},
		"voyage_itinerary__imp_principal_region_of_slave_purchase__name": {
			"type": "str"
		},
		"voyage_dates__date_departed_africa_sparsedate__month": {
			"type": "int"
		},
		"voyage_dates__voyage_began_sparsedate__month": {
			"type": "int"
		},
		"voyage_itinerary__imp_port_voyage_begin__name": {
			"type": "str"
		},
		"voyage_dates__first_dis_of_slaves_sparsedate__month": {
			"type": "int"
		},
		"voyage_itinerary__imp_broad_region_slave_dis__name": {
			"type": "str"
		},
		"voyage_slaves_numbers__percentage_girl": {
			"type": "pct"
		},
		"voyage_outcome__particular_outcome__name": {
			"type": "str"
		},
		"voyage_itinerary__imp_principal_port_slave_dis__name": {
			"type": "str"
		},
		"voyage_slaves_numbers__percentage_child": {
			"type": "pct"
		},
		"voyage_slaves_numbers__percentage_women": {
			"type": "pct"
		},
		"voyage_dates__departure_last_place_of_landing_sparsedate__month": {
			"type": "int"
		},
		"voyage_outcome__outcome_owner__name": {
			"type": "str"
		},
		"voyage_outcome__outcome_slaves__name": {
			"type": "str"
		},
		"voyage_itinerary__imp_principal_place_of_slave_purchase__name": {
			"type": "str"
		},
		"voyage_outcome__resistance__name": {
			"type": "str"
		},
		"voyage_slaves_numbers__percentage_male": {
			"type": "pct"
		},
		"voyage_slaves_numbers__percentage_female": {
			"type": "pct"
		},
		"voyage_itinerary__imp_broad_region_voyage_begin__name": {
			"type": "str"
		},
		"voyage_itinerary__imp_broad_region_of_slave_purchase__name": {
			"type": "str"
		},
		"voyage_sources":{
			"type": "obj",
			"fields": [
				"voyage_source_connections__source__bib"
			]
		},
		"enslavers":{
			"type": "obj",
			"fields":[
				"voyage_enslavement_relations__relation_enslavers__roles__name",
				"voyage_enslavement_relations__relation_enslavers__enslaver_alias__identity__principal_alias"
			]
		}
	}


}

estimate_pivot_tables={
	'endpoint':'assessment/dataframes/',
	'schema_name':'Estimate',
	'name':'estimate_pivot_tables',
		'variables':{
	  "id": {
			"type": "int"
		},
		"nation__id": {
			"type": "int"
		},
		"nation__name": {
			"type": "str"
		},
		"nation__order_num": {
			"type": "int"
		},
		"embarkation_region__id": {
			"type": "int"
		},
		"embarkation_region__export_area__id": {
			"type": "int"
		},
		"embarkation_region__export_area__name": {
			"type": "str"
		},
		"embarkation_region__export_area__order_num": {
			"type": "int"
		},
		"embarkation_region__export_area__latitude": {
			"type": "int"
		},
		"embarkation_region__export_area__longitude": {
			"type": "int"
		},
		"embarkation_region__name": {
			"type": "str"
		},
		"embarkation_region__order_num": {
			"type": "int"
		},
		"embarkation_region__latitude": {
			"type": "int"
		},
		"embarkation_region__longitude": {
			"type": "int"
		},
		"disembarkation_region__id": {
			"type": "int"
		},
		"disembarkation_region__import_area__id": {
			"type": "int"
		},
		"disembarkation_region__import_area__name": {
			"type": "str"
		},
		"disembarkation_region__import_area__order_num": {
			"type": "int"
		},
		"disembarkation_region__import_area__latitude": {
			"type": "int"
		},
		"disembarkation_region__import_area__longitude": {
			"type": "int"
		},
		"disembarkation_region__name": {
			"type": "str"
		},
		"disembarkation_region__order_num": {
			"type": "int"
		},
		"disembarkation_region__latitude": {
			"type": "int"
		},
		"disembarkation_region__longitude": {
			"type": "int"
		},
		"year": {
			"type": "int"
		},
		"embarked_slaves": {
			"type": "int"
		},
		"disembarked_slaves": {
			"type": "int"
		}
	}

}

timelapse={
	'endpoint':'voyage/dataframes/',
	'schema_name':'Voyage',
	'name':'timelapse',
	'variables':{
		"id": {
			"type": "int"
		},
		"voyage_itinerary__imp_broad_region_of_slave_purchase__id": {
			"type": "int"
		},
		"voyage_itinerary__imp_principal_region_of_slave_purchase__id": {
			"type": "int"
		},
		"voyage_itinerary__imp_principal_place_of_slave_purchase__id": {
			"type": "int"
		},
		"voyage_itinerary__imp_broad_region_slave_dis__id": {
			"type": "int"
		},
		"voyage_itinerary__imp_principal_region_slave_dis__id": {
			"type": "int"
		},
		"voyage_itinerary__imp_principal_port_slave_dis__id": {
			"type": "int"
		},
		"voyage_slaves_numbers__imp_total_num_slaves_embarked": {
			"type": "int"
		},
		"voyage_slaves_numbers__imp_total_num_slaves_disembarked": {
			"type": "int"
		},
		"voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year": {
			"type": "int"
		},
		"voyage_dates__imp_arrival_at_port_of_dis_sparsedate__month": {
			"type": "int"
		},
		"voyage_ship__imputed_nationality__value": {
			"type": "int"
		},
		"voyage_ship__tonnage_mod": {
			"type": "int"
		},
		"voyage_ship__ship_name": {
			"type": "str"
		}
	}
}

