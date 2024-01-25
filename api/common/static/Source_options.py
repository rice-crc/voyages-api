Source_options={'id': {'type': 'integer', 'many': False}, 'source_type__id': {'type': 'integer', 'many': False}, 'source_type__name': {'type': 'string', 'many': False}, 'page_connections__id': {'type': 'integer', 'many': True}, 'page_connections__page__id': {'type': 'integer', 'many': True}, 'page_connections__page__page_url': {'type': 'number', 'many': True}, 'page_connections__page__iiif_manifest_url': {'type': 'number', 'many': True}, 'page_connections__page__iiif_baseimage_url': {'type': 'number', 'many': True}, 'page_connections__page__image_filename': {'type': 'string', 'many': True}, 'page_connections__page__transcription': {'type': 'string', 'many': True}, 'page_connections__page__last_updated': {'type': 'number', 'many': True}, 'page_connections__page__human_reviewed': {'type': 'boolean', 'many': True}, 'page_connections__page__is_british_library': {'type': 'boolean', 'many': True}, 'page_connections__page__transkribus_pageid': {'type': 'integer', 'many': True}, 'page_connections__order': {'type': 'integer', 'many': True}, 'page_connections__source': {'type': 'integer', 'many': True}, 'source_enslaver_connections__id': {'type': 'integer', 'many': True}, 'source_enslaver_connections__enslaver__id': {'type': 'integer', 'many': True}, 'source_enslaver_connections__enslaver__principal_alias': {'type': 'string', 'many': True}, 'source_enslaver_connections__enslaver__birth_year': {'type': 'integer', 'many': True}, 'source_enslaver_connections__enslaver__birth_month': {'type': 'integer', 'many': True}, 'source_enslaver_connections__enslaver__birth_day': {'type': 'integer', 'many': True}, 'source_enslaver_connections__enslaver__death_year': {'type': 'integer', 'many': True}, 'source_enslaver_connections__enslaver__death_month': {'type': 'integer', 'many': True}, 'source_enslaver_connections__enslaver__death_day': {'type': 'integer', 'many': True}, 'source_enslaver_connections__enslaver__father_name': {'type': 'string', 'many': True}, 'source_enslaver_connections__enslaver__father_occupation': {'type': 'string', 'many': True}, 'source_enslaver_connections__enslaver__mother_name': {'type': 'string', 'many': True}, 'source_enslaver_connections__enslaver__probate_date': {'type': 'string', 'many': True}, 'source_enslaver_connections__enslaver__will_value_pounds': {'type': 'string', 'many': True}, 'source_enslaver_connections__enslaver__will_value_dollars': {'type': 'string', 'many': True}, 'source_enslaver_connections__enslaver__will_court': {'type': 'string', 'many': True}, 'source_enslaver_connections__enslaver__notes': {'type': 'string', 'many': True}, 'source_enslaver_connections__enslaver__is_natural_person': {'type': 'boolean', 'many': True}, 'source_enslaver_connections__enslaver__last_updated': {'type': 'number', 'many': True}, 'source_enslaver_connections__enslaver__human_reviewed': {'type': 'boolean', 'many': True}, 'source_enslaver_connections__enslaver__legacy_id': {'type': 'integer', 'many': True}, 'source_enslaver_connections__enslaver__birth_place': {'type': 'integer', 'many': True}, 'source_enslaver_connections__enslaver__death_place': {'type': 'integer', 'many': True}, 'source_enslaver_connections__enslaver__principal_location': {'type': 'integer', 'many': True}, 'source_enslaver_connections__page_range': {'type': 'string', 'many': True}, 'source_enslaver_connections__source': {'type': 'integer', 'many': True}, 'source_voyage_connections__id': {'type': 'integer', 'many': True}, 'source_voyage_connections__voyage__id': {'type': 'integer', 'many': True}, 'source_voyage_connections__voyage__voyage_id': {'type': 'integer', 'many': True}, 'source_voyage_connections__voyage__voyage_in_cd_rom': {'type': 'boolean', 'many': True}, 'source_voyage_connections__voyage__last_update': {'type': 'number', 'many': True}, 'source_voyage_connections__voyage__human_reviewed': {'type': 'boolean', 'many': True}, 'source_voyage_connections__voyage__dataset': {'type': 'integer', 'many': True}, 'source_voyage_connections__voyage__comments': {'type': 'string', 'many': True}, 'source_voyage_connections__voyage__voyage_groupings': {'type': 'integer', 'many': True}, 'source_voyage_connections__voyage__african_info': {'type': 'integer', 'many': True}, 'source_voyage_connections__page_range': {'type': 'string', 'many': True}, 'source_voyage_connections__source': {'type': 'integer', 'many': True}, 'source_enslaved_connections__id': {'type': 'integer', 'many': True}, 'source_enslaved_connections__enslaved__id': {'type': 'integer', 'many': True}, 'source_enslaved_connections__enslaved__enslaved_id': {'type': 'integer', 'many': True}, 'source_enslaved_connections__enslaved__documented_name': {'type': 'string', 'many': True}, 'source_enslaved_connections__enslaved__name_first': {'type': 'string', 'many': True}, 'source_enslaved_connections__enslaved__name_second': {'type': 'string', 'many': True}, 'source_enslaved_connections__enslaved__name_third': {'type': 'string', 'many': True}, 'source_enslaved_connections__enslaved__modern_name': {'type': 'string', 'many': True}, 'source_enslaved_connections__enslaved__editor_modern_names_certainty': {'type': 'string', 'many': True}, 'source_enslaved_connections__enslaved__age': {'type': 'integer', 'many': True}, 'source_enslaved_connections__enslaved__gender': {'type': 'integer', 'many': True}, 'source_enslaved_connections__enslaved__height': {'type': 'number', 'many': True}, 'source_enslaved_connections__enslaved__skin_color': {'type': 'string', 'many': True}, 'source_enslaved_connections__enslaved__dataset': {'type': 'integer', 'many': True}, 'source_enslaved_connections__enslaved__notes': {'type': 'string', 'many': True}, 'source_enslaved_connections__enslaved__last_updated': {'type': 'number', 'many': True}, 'source_enslaved_connections__enslaved__human_reviewed': {'type': 'boolean', 'many': True}, 'source_enslaved_connections__enslaved__language_group': {'type': 'integer', 'many': True}, 'source_enslaved_connections__enslaved__register_country': {'type': 'integer', 'many': True}, 'source_enslaved_connections__enslaved__post_disembark_location': {'type': 'integer', 'many': True}, 'source_enslaved_connections__enslaved__last_known_date': {'type': 'integer', 'many': True}, 'source_enslaved_connections__enslaved__captive_fate': {'type': 'integer', 'many': True}, 'source_enslaved_connections__enslaved__captive_status': {'type': 'integer', 'many': True}, 'source_enslaved_connections__page_range': {'type': 'string', 'many': True}, 'source_enslaved_connections__source': {'type': 'integer', 'many': True}, 'source_enslavement_relation_connections__id': {'type': 'integer', 'many': True}, 'source_enslavement_relation_connections__enslavement_relation__id': {'type': 'integer', 'many': True}, 'source_enslavement_relation_connections__enslavement_relation__date': {'type': 'string', 'many': True}, 'source_enslavement_relation_connections__enslavement_relation__amount': {'type': 'number', 'many': True}, 'source_enslavement_relation_connections__enslavement_relation__is_from_voyages': {'type': 'boolean', 'many': True}, 'source_enslavement_relation_connections__enslavement_relation__relation_type': {'type': 'integer', 'many': True}, 'source_enslavement_relation_connections__enslavement_relation__place': {'type': 'integer', 'many': True}, 'source_enslavement_relation_connections__enslavement_relation__voyage': {'type': 'integer', 'many': True}, 'source_enslavement_relation_connections__page_range': {'type': 'string', 'many': True}, 'source_enslavement_relation_connections__source': {'type': 'integer', 'many': True}, 'short_ref__id': {'type': 'integer', 'many': False}, 'short_ref__name': {'type': 'string', 'many': False}, 'date__id': {'type': 'integer', 'many': True}, 'date__day': {'type': 'integer', 'many': True}, 'date__month': {'type': 'integer', 'many': True}, 'date__year': {'type': 'integer', 'many': True}, 'zotero_group_id': {'type': 'integer', 'many': True}, 'zotero_item_id': {'type': 'string', 'many': True}, 'uid': {'type': 'string', 'many': True}, 'item_url': {'type': 'number', 'many': True}, 'thumbnail': {'type': 'string', 'many': True}, 'bib': {'type': 'string', 'many': True}, 'manifest_content': {'type': 'object', 'many': True}, 'zotero_grouplibrary_name': {'type': 'string', 'many': True}, 'zotero_url': {'type': 'number', 'many': True}, 'title': {'type': 'string', 'many': True}, 'is_british_library': {'type': 'boolean', 'many': True}, 'last_updated': {'type': 'number', 'many': True}, 'human_reviewed': {'type': 'boolean', 'many': True}, 'has_published_manifest': {'type': 'boolean', 'many': True}, 'notes': {'type': 'string', 'many': True}, 'order_in_shortref': {'type': 'integer', 'many': True}}