Enslaved_options={'id': {'type': 'integer', 'many': False}, 'post_disembark_location__id': {'type': 'integer', 'many': False}, 'post_disembark_location__uuid': {'type': 'number', 'many': False}, 'post_disembark_location__name': {'type': 'string', 'many': False}, 'post_disembark_location__longitude': {'type': 'number', 'many': False}, 'post_disembark_location__latitude': {'type': 'number', 'many': False}, 'post_disembark_location__value': {'type': 'integer', 'many': False}, 'post_disembark_location__parent': {'type': 'integer', 'many': False}, 'post_disembark_location__location_type': {'type': 'integer', 'many': False}, 'post_disembark_location__spatial_extent': {'type': 'integer', 'many': False}, 'captive_fate__id': {'type': 'integer', 'many': False}, 'captive_fate__name': {'type': 'string', 'many': False}, 'enslaved_relations__id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__relation_type__id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__relation_type__name': {'type': 'string', 'many': True}, 'enslaved_relations__relation__relation_enslavers__id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__principal_alias': {'type': 'string', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__birth_year': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__birth_month': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__birth_day': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__death_year': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__death_month': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__death_day': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__father_name': {'type': 'string', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__father_occupation': {'type': 'string', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__mother_name': {'type': 'string', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__probate_date': {'type': 'string', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__will_value_pounds': {'type': 'string', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__will_value_dollars': {'type': 'string', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__will_court': {'type': 'string', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__notes': {'type': 'string', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__is_natural_person': {'type': 'boolean', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__last_updated': {'type': 'number', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__human_reviewed': {'type': 'boolean', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__legacy_id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__birth_place': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__death_place': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__identity__principal_location': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__alias': {'type': 'string', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__manual_id': {'type': 'string', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__last_updated': {'type': 'number', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__human_reviewed': {'type': 'boolean', 'many': True}, 'enslaved_relations__relation__relation_enslavers__enslaver_alias__legacy_id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__relation_enslavers__roles__id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__relation_enslavers__roles__name': {'type': 'string', 'many': True}, 'enslaved_relations__relation__relation_enslavers__relation': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__dataset': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_port_voyage_begin__id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_port_voyage_begin__uuid': {'type': 'number', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_port_voyage_begin__name': {'type': 'string', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_port_voyage_begin__longitude': {'type': 'number', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_port_voyage_begin__latitude': {'type': 'number', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_port_voyage_begin__value': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_port_voyage_begin__parent': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_port_voyage_begin__location_type': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_port_voyage_begin__spatial_extent': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__uuid': {'type': 'number', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__name': {'type': 'string', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__longitude': {'type': 'number', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__latitude': {'type': 'number', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__value': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__parent': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__location_type': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__spatial_extent': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_port_slave_dis__id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_port_slave_dis__uuid': {'type': 'number', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_port_slave_dis__name': {'type': 'string', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_port_slave_dis__longitude': {'type': 'number', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_port_slave_dis__latitude': {'type': 'number', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_port_slave_dis__value': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_port_slave_dis__parent': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_port_slave_dis__location_type': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_port_slave_dis__spatial_extent': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_of_slave_purchase__id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_of_slave_purchase__uuid': {'type': 'number', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_of_slave_purchase__name': {'type': 'string', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_of_slave_purchase__longitude': {'type': 'number', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_of_slave_purchase__latitude': {'type': 'number', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_of_slave_purchase__value': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_of_slave_purchase__parent': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_of_slave_purchase__location_type': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_of_slave_purchase__spatial_extent': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_slave_dis__id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_slave_dis__uuid': {'type': 'number', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_slave_dis__name': {'type': 'string', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_slave_dis__longitude': {'type': 'number', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_slave_dis__latitude': {'type': 'number', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_slave_dis__value': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_slave_dis__parent': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_slave_dis__location_type': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_slave_dis__spatial_extent': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__int_first_port_dis__id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__int_first_port_dis__uuid': {'type': 'number', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__int_first_port_dis__name': {'type': 'string', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__int_first_port_dis__longitude': {'type': 'number', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__int_first_port_dis__latitude': {'type': 'number', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__int_first_port_dis__value': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__int_first_port_dis__parent': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__int_first_port_dis__location_type': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_itinerary__int_first_port_dis__spatial_extent': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_dates__imp_arrival_at_port_of_dis_sparsedate__id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_dates__imp_arrival_at_port_of_dis_sparsedate__day': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_dates__imp_arrival_at_port_of_dis_sparsedate__month': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_ship__ship_name': {'type': 'string', 'many': True}, 'enslaved_relations__relation__voyage__voyage_outcome__particular_outcome__id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_outcome__particular_outcome__name': {'type': 'string', 'many': True}, 'enslaved_relations__relation__voyage__voyage_outcome__particular_outcome__value': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__source__id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__source__item_url': {'type': 'number', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__source__thumbnail': {'type': 'string', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__source__bib': {'type': 'string', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__source__manifest_content': {'type': 'object', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__source__zotero_group_id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__source__zotero_item_id': {'type': 'string', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__source__zotero_grouplibrary_name': {'type': 'string', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__source__zotero_url': {'type': 'number', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__source__title': {'type': 'string', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__source__is_british_library': {'type': 'boolean', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__source__last_updated': {'type': 'number', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__source__human_reviewed': {'type': 'boolean', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__source__has_published_manifest': {'type': 'boolean', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__source__notes': {'type': 'string', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__source__order_in_shortref': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__source__source_type': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__source__short_ref': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__source__date': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__page_range': {'type': 'string', 'many': True}, 'enslaved_relations__relation__voyage__voyage_source_connections__voyage': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__place__id': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__place__uuid': {'type': 'number', 'many': True}, 'enslaved_relations__relation__place__name': {'type': 'string', 'many': True}, 'enslaved_relations__relation__place__longitude': {'type': 'number', 'many': True}, 'enslaved_relations__relation__place__latitude': {'type': 'number', 'many': True}, 'enslaved_relations__relation__place__value': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__place__parent': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__place__location_type': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__place__spatial_extent': {'type': 'integer', 'many': True}, 'enslaved_relations__relation__date': {'type': 'string', 'many': True}, 'enslaved_relations__relation__amount': {'type': 'number', 'many': True}, 'enslaved_relations__relation__is_from_voyages': {'type': 'boolean', 'many': True}, 'enslaved_relations__enslaved': {'type': 'integer', 'many': True}, 'captive_status__id': {'type': 'integer', 'many': False}, 'captive_status__name': {'type': 'string', 'many': False}, 'language_group__id': {'type': 'integer', 'many': False}, 'language_group__name': {'type': 'string', 'many': False}, 'language_group__uuid': {'type': 'number', 'many': False}, 'language_group__longitude': {'type': 'number', 'many': False}, 'language_group__latitude': {'type': 'number', 'many': False}, 'language_group__shape': {'type': 'object', 'many': False}, 'enslaved_source_connections__id': {'type': 'integer', 'many': True}, 'enslaved_source_connections__source__id': {'type': 'integer', 'many': True}, 'enslaved_source_connections__source__item_url': {'type': 'number', 'many': True}, 'enslaved_source_connections__source__thumbnail': {'type': 'string', 'many': True}, 'enslaved_source_connections__source__bib': {'type': 'string', 'many': True}, 'enslaved_source_connections__source__manifest_content': {'type': 'object', 'many': True}, 'enslaved_source_connections__source__zotero_group_id': {'type': 'integer', 'many': True}, 'enslaved_source_connections__source__zotero_item_id': {'type': 'string', 'many': True}, 'enslaved_source_connections__source__zotero_grouplibrary_name': {'type': 'string', 'many': True}, 'enslaved_source_connections__source__zotero_url': {'type': 'number', 'many': True}, 'enslaved_source_connections__source__title': {'type': 'string', 'many': True}, 'enslaved_source_connections__source__is_british_library': {'type': 'boolean', 'many': True}, 'enslaved_source_connections__source__last_updated': {'type': 'number', 'many': True}, 'enslaved_source_connections__source__human_reviewed': {'type': 'boolean', 'many': True}, 'enslaved_source_connections__source__has_published_manifest': {'type': 'boolean', 'many': True}, 'enslaved_source_connections__source__notes': {'type': 'string', 'many': True}, 'enslaved_source_connections__source__order_in_shortref': {'type': 'integer', 'many': True}, 'enslaved_source_connections__source__source_type': {'type': 'integer', 'many': True}, 'enslaved_source_connections__source__short_ref': {'type': 'integer', 'many': True}, 'enslaved_source_connections__source__date': {'type': 'integer', 'many': True}, 'enslaved_source_connections__page_range': {'type': 'string', 'many': True}, 'enslaved_source_connections__enslaved': {'type': 'integer', 'many': True}, 'enslaved_id': {'type': 'integer', 'many': False}, 'documented_name': {'type': 'string', 'many': False}, 'name_first': {'type': 'string', 'many': False}, 'name_second': {'type': 'string', 'many': False}, 'name_third': {'type': 'string', 'many': False}, 'modern_name': {'type': 'string', 'many': False}, 'editor_modern_names_certainty': {'type': 'string', 'many': False}, 'age': {'type': 'integer', 'many': False}, 'gender': {'type': 'string', 'many': False}, 'height': {'type': 'number', 'many': False}, 'skin_color': {'type': 'string', 'many': False}, 'dataset': {'type': 'integer', 'many': False}, 'notes': {'type': 'string', 'many': False}, 'last_updated': {'type': 'number', 'many': False}, 'human_reviewed': {'type': 'boolean', 'many': False}, 'register_country': {'type': 'integer', 'many': False}, 'last_known_date': {'type': 'integer', 'many': False}}