Enslaver_options={'id': {'type': 'integer', 'many': False}, 'principal_location': {'geo_location': {'id': {'type': 'integer', 'many': False}, 'uuid': {'type': 'number', 'many': False}, 'name': {'type': 'string', 'many': False}, 'longitude': {'type': 'number', 'many': False}, 'latitude': {'type': 'number', 'many': False}, 'value': {'type': 'integer', 'many': False}, 'child_of': {'type': 'integer', 'many': False}, 'location_type': {'type': 'integer', 'many': False}, 'spatial_extent': {'type': 'integer', 'many': False}}}, 'enslaver_zotero_connections': {'id': {'type': 'integer', 'many': True}, 'zotero_source': {'id': {'type': 'integer', 'many': True}, 'page_connection': {'id': {'type': 'integer', 'many': True}, 'source_page': {'id': {'type': 'integer', 'many': True}, 'page_url': {'type': 'number', 'many': True}, 'iiif_manifest_url': {'type': 'number', 'many': True}, 'iiif_baseimage_url': {'type': 'number', 'many': True}, 'image_filename': {'type': 'string', 'many': True}, 'last_updated': {'type': 'number', 'many': True}, 'human_reviewed': {'type': 'boolean', 'many': True}}, 'zotero_source': {'type': 'integer', 'many': True}}, 'item_url': {'type': 'number', 'many': True}, 'zotero_url': {'type': 'number', 'many': True}, 'short_ref': {'type': 'string', 'many': True}, 'zotero_title': {'type': 'string', 'many': True}, 'zotero_date': {'type': 'string', 'many': True}, 'is_legacy_source': {'type': 'boolean', 'many': True}, 'last_updated': {'type': 'number', 'many': True}, 'human_reviewed': {'type': 'boolean', 'many': True}, 'notes': {'type': 'string', 'many': True}, 'legacy_source': {'type': 'integer', 'many': True}}, 'page_range': {'type': 'string', 'many': True}, 'enslaver': {'type': 'integer', 'many': True}}, 'aliases': {'id': {'type': 'integer', 'many': True}, 'enslaver_relations': {'relation': {'id': {'type': 'integer', 'many': True}, 'enslaved_in_relation': {'id': {'type': 'integer', 'many': True}, 'enslaved': {'id': {'type': 'integer', 'many': True}, 'documented_name': {'type': 'string', 'many': True}}, 'relation': {'type': 'integer', 'many': True}}, 'relation_type': {'id': {'type': 'integer', 'many': True}, 'name': {'type': 'string', 'many': True}}, 'place': {'geo_location': {'id': {'type': 'integer', 'many': True}, 'uuid': {'type': 'number', 'many': True}, 'name': {'type': 'string', 'many': True}, 'longitude': {'type': 'number', 'many': True}, 'latitude': {'type': 'number', 'many': True}, 'value': {'type': 'integer', 'many': True}, 'child_of': {'type': 'integer', 'many': True}, 'location_type': {'type': 'integer', 'many': True}, 'spatial_extent': {'type': 'integer', 'many': True}}}, 'voyage': {'voyage_id': {'type': 'integer', 'many': True}, 'id': {'type': 'integer', 'many': True}, 'dataset': {'type': 'integer', 'many': True}, 'voyage_itinerary': {'imp_port_voyage_begin': {'geo_location': {'id': {'type': 'integer', 'many': True}, 'uuid': {'type': 'number', 'many': True}, 'name': {'type': 'string', 'many': True}, 'longitude': {'type': 'number', 'many': True}, 'latitude': {'type': 'number', 'many': True}, 'value': {'type': 'integer', 'many': True}, 'child_of': {'type': 'integer', 'many': True}, 'location_type': {'type': 'integer', 'many': True}, 'spatial_extent': {'type': 'integer', 'many': True}}}, 'imp_principal_place_of_slave_purchase': {'geo_location': {'id': {'type': 'integer', 'many': True}, 'uuid': {'type': 'number', 'many': True}, 'name': {'type': 'string', 'many': True}, 'longitude': {'type': 'number', 'many': True}, 'latitude': {'type': 'number', 'many': True}, 'value': {'type': 'integer', 'many': True}, 'child_of': {'type': 'integer', 'many': True}, 'location_type': {'type': 'integer', 'many': True}, 'spatial_extent': {'type': 'integer', 'many': True}}}, 'imp_principal_port_slave_dis': {'geo_location': {'id': {'type': 'integer', 'many': True}, 'uuid': {'type': 'number', 'many': True}, 'name': {'type': 'string', 'many': True}, 'longitude': {'type': 'number', 'many': True}, 'latitude': {'type': 'number', 'many': True}, 'value': {'type': 'integer', 'many': True}, 'child_of': {'type': 'integer', 'many': True}, 'location_type': {'type': 'integer', 'many': True}, 'spatial_extent': {'type': 'integer', 'many': True}}}, 'imp_principal_region_of_slave_purchase': {'geo_location': {'id': {'type': 'integer', 'many': True}, 'uuid': {'type': 'number', 'many': True}, 'name': {'type': 'string', 'many': True}, 'longitude': {'type': 'number', 'many': True}, 'latitude': {'type': 'number', 'many': True}, 'value': {'type': 'integer', 'many': True}, 'child_of': {'type': 'integer', 'many': True}, 'location_type': {'type': 'integer', 'many': True}, 'spatial_extent': {'type': 'integer', 'many': True}}}, 'imp_principal_region_slave_dis': {'geo_location': {'id': {'type': 'integer', 'many': True}, 'uuid': {'type': 'number', 'many': True}, 'name': {'type': 'string', 'many': True}, 'longitude': {'type': 'number', 'many': True}, 'latitude': {'type': 'number', 'many': True}, 'value': {'type': 'integer', 'many': True}, 'child_of': {'type': 'integer', 'many': True}, 'location_type': {'type': 'integer', 'many': True}, 'spatial_extent': {'type': 'integer', 'many': True}}}, 'int_first_port_dis': {'geo_location': {'id': {'type': 'integer', 'many': True}, 'uuid': {'type': 'number', 'many': True}, 'name': {'type': 'string', 'many': True}, 'longitude': {'type': 'number', 'many': True}, 'latitude': {'type': 'number', 'many': True}, 'value': {'type': 'integer', 'many': True}, 'child_of': {'type': 'integer', 'many': True}, 'location_type': {'type': 'integer', 'many': True}, 'spatial_extent': {'type': 'integer', 'many': True}}}}, 'voyage_dates': {'imp_arrival_at_port_of_dis_sparsedate': {'day': {'type': 'integer', 'many': True}, 'month': {'type': 'integer', 'many': True}, 'year': {'type': 'integer', 'many': True}}}, 'voyage_ship': {'ship_name': {'type': 'string', 'many': True}}, 'voyage_name_outcome': {'particular_outcome': {'id': {'type': 'integer', 'many': True}, 'name': {'type': 'string', 'many': True}, 'value': {'type': 'integer', 'many': True}}}}, 'date': {'type': 'string', 'many': True}, 'amount': {'type': 'number', 'many': True}, 'is_from_voyages': {'type': 'boolean', 'many': True}, 'source': {'type': 'integer', 'many': True}}, 'role': {'id': {'type': 'integer', 'many': True}, 'name': {'type': 'string', 'many': True}}}, 'alias': {'type': 'string', 'many': True}, 'manual_id': {'type': 'string', 'many': True}, 'last_updated': {'type': 'number', 'many': True}, 'human_reviewed': {'type': 'boolean', 'many': True}, 'identity': {'type': 'integer', 'many': True}}, 'birth_place': {'geo_location': {'id': {'type': 'integer', 'many': False}, 'uuid': {'type': 'number', 'many': False}, 'name': {'type': 'string', 'many': False}, 'longitude': {'type': 'number', 'many': False}, 'latitude': {'type': 'number', 'many': False}, 'value': {'type': 'integer', 'many': False}, 'child_of': {'type': 'integer', 'many': False}, 'location_type': {'type': 'integer', 'many': False}, 'spatial_extent': {'type': 'integer', 'many': False}}}, 'death_place': {'geo_location': {'id': {'type': 'integer', 'many': False}, 'uuid': {'type': 'number', 'many': False}, 'name': {'type': 'string', 'many': False}, 'longitude': {'type': 'number', 'many': False}, 'latitude': {'type': 'number', 'many': False}, 'value': {'type': 'integer', 'many': False}, 'child_of': {'type': 'integer', 'many': False}, 'location_type': {'type': 'integer', 'many': False}, 'spatial_extent': {'type': 'integer', 'many': False}}}, 'principal_alias': {'type': 'string', 'many': False}, 'birth_year': {'type': 'integer', 'many': False}, 'birth_month': {'type': 'integer', 'many': False}, 'birth_day': {'type': 'integer', 'many': False}, 'death_year': {'type': 'integer', 'many': False}, 'death_month': {'type': 'integer', 'many': False}, 'death_day': {'type': 'integer', 'many': False}, 'father_name': {'type': 'string', 'many': False}, 'father_occupation': {'type': 'string', 'many': False}, 'mother_name': {'type': 'string', 'many': False}, 'probate_date': {'type': 'string', 'many': False}, 'will_value_pounds': {'type': 'string', 'many': False}, 'will_value_dollars': {'type': 'string', 'many': False}, 'will_court': {'type': 'string', 'many': False}, 'notes': {'type': 'string', 'many': False}, 'is_natural_person': {'type': 'boolean', 'many': False}, 'last_updated': {'type': 'number', 'many': False}, 'human_reviewed': {'type': 'boolean', 'many': False}}