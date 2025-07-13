import mysql.connector
import requests
import json
from django.core.management.base import BaseCommand, CommandError
from common.reqs import  getJSONschema
from voyage.models import *
from geo.models import *
import pytz


class Command(BaseCommand):
	help = 'publishes the schema as flat json and python files, \
	which are used to populate the options avaiable in the model serializers. \
	this should be run any time you alter the serializers or models. \
	outputs go to api/common/static and are included in the git repo.'
	def handle(self, *args, **options):

		#connect to legacy db
		cnx = mysql.connector.connect(
			host="voyages-mysql",
			port=3306,
			user="root",
			password="voyages",
			database="voyages_legacy")
			
		cur = cnx.cursor()
		
		#validate connection
		result = cur.execute("SELECT * FROM voyage_voyage LIMIT 1")
		row = cur.fetchone()
		
		# VOYAGE GROUPINGS
		# so the way I set up the new system is to have voyages be where all the other tables point to
		# except in the case of the obscure "voyage groupings" table
		
		result=cur.execute("SELECT id,label,value from voyage_voyagegroupings;")
		
		# VALUE field is the spss permanent key
		# overwrite api data
		# "label" field has been renamed to "name" field
		voyage_grouping_pk_map={}
		for row in cur.fetchall():
			id,label,value=row
			vg,vg_isnew=VoyageGroupings.objects.get_or_create(
				value=value
			)
			vg.name=label
			voyage_grouping_pk_map[id]=vg.id
			vg.save()
		
		# CRUCIAL SPSS TABLES
		
		## GEO

		def location_get_create_or_update(name,longitude,latitude,value):
			try:
				location=Location.objects.get(value=value)
			except:
				location=None
			
			if not location:
				location=Location.objects.create(
					name=name,
					longitude=longitude,
					latitude=latitude,
					value=value
				)
			else:
				location.name=name
				location.longitude=longitude
				location.latitude=latitude
				location.value=value
				location.save()
			return location

		## got to do them in this order because it's 3 hierarchical tables in legacy
		
		### voyage_broadregion
		
		broad_region_id_map={}
		result=cur.execute("SELECT \
			id,\
			broad_region,\
			longitude,\
			latitude,\
			value\
		from voyage_broadregion;")
		
		for row in cur.fetchall():
			id,name,longitude,latitude,value=row
			location=location_get_create_or_update(name,longitude,latitude,value)
			broad_region_id_map[id]=location.id
		
		### voyage_region
		
		region_id_map={}
		result=cur.execute("SELECT \
			id,\
			region,\
			broad_region_id,\
			longitude,\
			latitude,\
			value\
		from voyage_region;")
		
		for row in cur.fetchall():
			id,name,broad_region_id,longitude,latitude,value=row
			location=location_get_create_or_update(name,longitude,latitude,value)
			broad_region_id=broad_region_id_map[broad_region_id]
			broad_region=Location.objects.get(id=broad_region_id)
			location.broad_region=broad_region
			location.save()
			region_id_map[id]=location.id
			
		### voyage_place
		
		place_id_map={}
		result=cur.execute("SELECT \
			id,\
			place,\
			region_id,\
			longitude,\
			latitude,\
			value\
		from voyage_place;")
		
		for row in cur.fetchall():
			id,name,region_id,longitude,latitude,value=row
			location=location_get_create_or_update(name,longitude,latitude,value)
			region_id=region_id_map[region_id]
			region=Location.objects.get(id=region_id)
			location.region=region
			location.save()
			place_id_map[id]=location.id
		
		
		def spss_controlled_vocab(model,table,cur,label_or_name='label',value_field=True,extra_fields=[]):
			print(f"updating controlled vocab model {model}")
			if value_field:
				result=cur.execute(f"SELECT id,{label_or_name},value from {table};")
			else:
				result=cur.execute(f"SELECT id,{label_or_name} from {table};")
			model_id_map={}
			for row in cur.fetchall():
				if value_field:
					id,name,value=row
					try:
						obj=model.objects.get(value=value)
					except:
						obj=None
				
					if not obj:
						#check to see if there's a conflicting named entry
						try:
							name_obj=model.objects.get(
								name=name
							)
						except:
							name_obj=None
						
						if name_obj:
							name_obj.delete()
						obj=model.objects.create(
							name=name,
							value=value
						)
					else:
						#check to see if there's an existing valued entry
						
						try:
							name_obj=model.objects.get(
								name=name
							)
						except:
							name_obj=None
						if name_obj:
							if name_obj!=obj:
								name_obj.delete()
						
						obj.name=name
						obj.value=value
						obj.save()
				else:
					id,name=row
					try:
						obj=model.objects.get(name=name)
					except:
						obj=None
				
					if not obj:
						obj=model.objects.create(
							name=name
						)
					else:
						obj.name=name
				obj.save()
				model_id_map[id]=obj.id
			for f in extra_fields:
				result=cur.execute(f"SELECT id,{f} from {table};")
				for row in cur.fetchall():
					id,val=row
					id=model_id_map[id]
					obj=model.objects.get(id=id)
					if type(val)==str:
						fstr=f'obj.{f}="{val}"'
					else:
						fstr=f'obj.{f}={val}'
					obj.save()
			return model_id_map,cur
		
		nationality_id_map,cur=spss_controlled_vocab(
			Nationality,
			'voyage_nationality',
			cur
		)
		tontype_id_map,cur=spss_controlled_vocab(
			TonType,
			'voyage_tontype',
			cur
		)
		rigofvessel_id_map,cur=spss_controlled_vocab(
			RigOfVessel,
			'voyage_rigofvessel',
			cur
		)
		particularoutcome_id_map,cur=spss_controlled_vocab(
			ParticularOutcome,
			'voyage_particularoutcome',
			cur
		)
		slavesoutcome_id_map,cur=spss_controlled_vocab(
			SlavesOutcome,
			'voyage_slavesoutcome',
			cur
		)
		vesselcapturedoutcome_id_map,cur=spss_controlled_vocab(
			VesselCapturedOutcome,
			'voyage_vesselcapturedoutcome',
			cur
		)
		owneroutcome_id_map,cur=spss_controlled_vocab(
			OwnerOutcome,
			'voyage_owneroutcome',
			cur
		)
		resistance_id_map,cur=spss_controlled_vocab(
			Resistance,
			'voyage_resistance',
			cur
		)

		## those without spss codes
		cargotype_id_map,cur=spss_controlled_vocab(
			CargoType,
			'voyage_cargotype',
			cur,
			label_or_name='name',
			value_field=False
		)
		cargounit_id_map,cur=spss_controlled_vocab(
			CargoUnit,
			'voyage_cargounit',
			cur,
			label_or_name='name',
			value_field=False
		)
		africaninfo_id_map,cur=spss_controlled_vocab(
			AfricanInfo,
			'voyage_africaninfo',
			cur,
			label_or_name='name',
			value_field=False,
			extra_fields=['possibly_offensive']
		)		
		
		# VOYAGES
		
		result=cur.execute("SELECT\
			id,\
			voyage_id,\
			voyage_in_cd_rom,\
			last_update,\
			dataset,\
			comments,\
			voyage_groupings_id\
		from voyage_voyage;")
		
		# VALUE field is the spss permanent key
		# overwrite api data
		voyage_pk_map={}
		utc=pytz.UTC
		
		vrs=[r for r in cur.fetchall()]
		
		print("deleting all voyage sparse dates")
		VoyageSparseDate.objects.all().delete()
		
		for row in vrs:
			id,voyage_id,voyage_in_cd_rom,last_update,dataset,comments,voyage_groupings_id=row
			print(f'--> voyage {voyage_id}')
			if voyage_groupings_id is not None:
				voyage_groupings_id=voyage_grouping_pk_map[voyage_groupings_id]
				voyage_grouping=VoyageGroupings.objects.get(id=voyage_groupings_id)
			else:
				voyage_grouping=None
			
			last_update=utc.localize(last_update)
			
			try:
				v=Voyage.objects.get(voyage_id=voyage_id)
			except:
				v=None
			
			if not v:
				print(f"voyage {voyage_id} is new: {last_update}")
				#we should be able to keep pk & voyage_id aligned, as I was pretty careful about that...
				v=Voyage.objects.create(
					id=id,
					voyage_id=voyage_id,
					voyage_in_cd_rom=voyage_in_cd_rom,
					dataset=dataset,
					comments=comments,
					voyage_groupings=voyage_grouping
				)
			else:
				v.id=id
				v.voyage_id=voyage_id
				v.voyage_in_cd_rom=voyage_in_cd_rom
				v.dataset=dataset
				v.comments=comments
				v.voyage_groupings=voyage_grouping
				v.save()
			
			
			
			
			
# 			
# 			### VOYAGE DATES
# 			
# 			result=cur.execute(f"SELECT\
# 				voyage_began,\
# 				slave_purchase_began,\
# 				vessel_left_port,\
# 				first_dis_of_slaves,\
# 				date_departed_africa,\
# 				arrival_at_second_place_landing,\
# 				third_dis_of_slaves,\
# 				departure_last_place_of_landing,\
# 				voyage_completed,\
# 				length_middle_passage_days,\
# 				imp_voyage_began,\
# 				imp_departed_africa,\
# 				imp_arrival_at_port_of_dis,\
# 				imp_length_home_to_disembark,\
# 				imp_length_leaving_africa_to_disembark,\
# 				voyage_id\
# 			from voyage_voyagedates where voyage_id={id};")
# 			
# 			def intornone(i):
# 				try:
# 					return int(i)
# 				except:
# 					return None
# 
# 			try:
# 				vd=VoyageDates.objects.get(voyage=v)
# 			except:
# 				vd=None
# 			
# 			if vd:
# 				vd.delete()
# 				
# 			
# 			vd=VoyageDates.objects.create(
# 				voyage=v
# 			)
# 
# 			for row in cur.fetchall():
# 				voyage_began, slave_purchase_began, vessel_left_port, first_dis_of_slaves, date_departed_africa, arrival_at_second_place_landing, third_dis_of_slaves, departure_last_place_of_landing, voyage_completed, length_middle_passage_days, imp_voyage_began, imp_departed_africa, imp_arrival_at_port_of_dis, imp_length_home_to_disembark, imp_length_leaving_africa_to_disembark,voyage_id=row
# 				
# 				vd.length_middle_passage_days=length_middle_passage_days
# 				vd.imp_length_home_to_disembark=imp_length_home_to_disembark
# 				vd.imp_length_leaving_africa_to_disembark=imp_length_leaving_africa_to_disembark
# 				vd.save()
# 				for vf in ['voyage_began', 'slave_purchase_began', 'vessel_left_port', 'first_dis_of_slaves', 'date_departed_africa', 'arrival_at_second_place_landing', 'third_dis_of_slaves', 'departure_last_place_of_landing', 'voyage_completed', 'imp_voyage_began', 'imp_departed_africa', 'imp_arrival_at_port_of_dis']:
# 					print(vf)
# 					val=eval(vf)
# 					if len(val.split(','))==3:
# 						m,d,y=[intornone(i) for i in val.split(',')]
# 						sd=VoyageSparseDate.objects.create(month=m,day=d,year=y)
# 						exec(f"vd.{vf}=sd")
# 			vd.save()
# 			
			
			
			
			
			
			### VOYAGE ITINERARIES

# 			itinerary_var_types={
# 				'port_of_departure_id':'Place',
# 				'int_first_port_emb_id':'Place',
# 				'int_second_port_emb_id':'Place',
# 				'int_first_region_purchase_slaves_id':'Region',
# 				'int_second_region_purchase_slaves_id':'Region',
# 				'int_first_port_dis_id':'Place',
# 				'int_second_port_dis_id':'Place',
# 				'int_third_port_dis_id':'Place',
# 				'int_fourth_port_dis_id':'Place',
# 				'int_first_region_slave_landing_id':'Region',
# 				'int_second_place_region_slave_landing_id':'Region',
# 				'int_third_place_region_slave_landing_id':'Region',
# 				'int_fourth_place_region_slave_landing_id':'Region',
# 				'first_place_slave_purchase_id':'Place',
# 				'second_place_slave_purchase_id':'Place',
# 				'third_place_slave_purchase_id':'Place',
# 				'first_region_slave_emb_id':'Region',
# 				'second_region_slave_emb_id':'Region',
# 				'third_region_slave_emb_id':'Region',
# 				'port_of_call_before_atl_crossing_id':'Place',
# 				'first_landing_place_id':'Place',
# 				'second_landing_place_id':'Place',
# 				'third_landing_place_id':'Place',
# 				'first_landing_region_id':'Region',
# 				'second_landing_region_id':'Region',
# 				'third_landing_region_id':'Region',
# 				'place_voyage_ended_id':'Place',
# 				'region_of_return_id':'Region',
# 				'broad_region_of_return_id':'BroadRegion',
# 				'imp_port_voyage_begin_id':'Place',
# 				'imp_region_voyage_begin_id':'Region',
# 				'imp_broad_region_voyage_begin_id':'BroadRegion',
# 				'principal_place_of_slave_purchase_id':'Place',
# 				'imp_principal_place_of_slave_purchase_id':'Place',
# 				'imp_principal_region_of_slave_purchase_id':'Region',
# 				'imp_broad_region_of_slave_purchase_id':'BroadRegion',
# 				'principal_port_of_slave_dis_id':'Place',
# 				'imp_principal_port_slave_dis_id':'Place',
# 				'imp_principal_region_slave_dis_id':'Region',
# 				'imp_broad_region_slave_dis_id':'BroadRegion',
# 				'voyage_id':None
# 			}
# 			
# 			fstr=f"SELECT {','.join([k for k in itinerary_var_types])}\
# 				from voyage_voyageitinerary where voyage_id={id};"
# 			result=cur.execute(fstr)
# 			
# 			try:
# 				VoyageItinerary.objects.get(voyage=v).delete()
# 			except:
# 				pass
# 			
# 			vi=VoyageItinerary.objects.create(voyage=v)
# 			
# 			for row in cur.fetchall():
# 				rowdict={list(itinerary_var_types)[i]:row[i] for i in range(len(itinerary_var_types))}
# 				for v in itinerary_var_types:
# 					if v!='voyage_id':
# 						vtype=itinerary_var_types[v]
# 						vname=v[:-3]
# 						loc_map={
# 							'Place':place_id_map,
# 							'Region':region_id_map,
# 							'BroadRegion':broad_region_id_map
# 						}[vtype]
# 						
# 						if v!='voyage_id':
# 							loc_id=rowdict[v]
# 							if loc_id is not None:
# 								loc_id=loc_map[loc_id]
# 							if loc_id is not None:
# 								location=Location.objects.get(id=loc_id)
# 								exec(f"vi.{vname}=location")
# 				vi.save()
# 				print(vi.__dict__)
					
					
			
			### VOYAGE OUTCOMES
# 			
# 			try:
# 				v.voyage_outcome.delete()
# 			except:
# 				pass
# 			
# 			vo=VoyageOutcome.objects.create(
# 				voyage=v
# 			)
# 			
# 			result=cur.execute(f"SELECT\
# 				outcome_owner_id,\
# 				outcome_slaves_id,\
# 				particular_outcome_id,\
# 				resistance_id,\
# 				vessel_captured_outcome_id,\
# 				voyage_id\
# 			from voyage_voyageoutcome where voyage_id={id};")
# 
# 			for row in cur.fetchall():
# 				owner_outcome_id,outcome_slaves_id,particular_outcome_id,resistance_id,vessel_captured_outcome_id,voyage_id=row
# 				
# 				if owner_outcome_id is not None:
# 					owner_outcome_id=owneroutcome_id_map[owner_outcome_id]
# 					oo=OwnerOutcome.objects.get(id=owner_outcome_id)
# 					vo.owner_outcome=oo
# 				if outcome_slaves_id is not None:
# 					outcome_slaves_id=slavesoutcome_id_map[outcome_slaves_id]
# 					os=SlavesOutcome.objects.get(id=outcome_slaves_id)
# 					vo.outcome_slaves=os
# 				if particular_outcome_id is not None:	
# 					particular_outcome_id=particularoutcome_id_map[particular_outcome_id]
# 					po=ParticularOutcome.objects.get(id=particular_outcome_id)
# 					vo.particular_outcome=po
# 				if resistance_id is not None:
# 					resistance_id=resistance_id_map[resistance_id]
# 					ro=Resistance.objects.get(id=resistance_id)
# 					vo.resistance=ro
# 				if vessel_captured_outcome_id is not None:
# 					vessel_captured_outcome_id=vesselcapturedoutcome_id_map[vessel_captured_outcome_id]
# 					vco=VesselCapturedOutcome.objects.get(id=vessel_captured_outcome_id)
# 					vo.vessel_captured_outcome=vco
# 				vo.save()


			try:
				v.voyage_ship.delete()
			except:
				pass
			
			ship=VoyageShip.objects.create(
				voyage=v
			)
			
			result=cur.execute(f"SELECT\
				ship_name,\
				tonnage,\
				guns_mounted,\
				year_of_construction,\
				registered_year,\
				tonnage_mod,\
				imputed_nationality_id,\
				nationality_ship_id,\
				registered_place_id,\
				registered_region_id,\
				rig_of_vessel_id,\
				ton_type_id,\
				vessel_construction_place_id,\
				vessel_construction_region_id,\
				voyage_id\
			from voyage_voyageship where voyage_id={id};")
			
			for row in cur.fetchall():
				ship_name,tonnage,guns_mounted,year_of_construction,registered_year,tonnage_mod,imputed_nationality_id,nationality_ship_id,registered_place_id,registered_region_id,rig_of_vessel_id,ton_type_id,vessel_construction_place_id,vessel_construction_region_id,voyage_id=row
				ship.ship_name=ship_name
				ship.tonnage=tonnage
				ship.guns_mounted=guns_mounted
				ship.year_of_construction=year_of_construction
				ship.registered_year=registered_year
				ship.tonnage_mod=tonnage_mod
				
				if nationality_ship_id is not None:
					nationality_ship_id=nationality_id_map[nationality_ship_id]
					nationality=Nationality.objects.get(id=nationality_ship_id)
					ship.imputed_nationality=nationality
				
				if imputed_nationality_id is not None:
					imputed_nationality_id=nationality_id_map[imputed_nationality_id]
					nationality=Nationality.objects.get(id=imputed_nationality_id)
					ship.imputed_nationality=nationality
				
				if registered_place_id is not None:
					registered_place_id=place_id_map[registered_place_id]
					registered_place=Location.objects.get(id=registered_place_id)
					ship.registered_place=registered_place
				
				if registered_region_id is not None:
					registered_region_id=region_id_map[registered_region_id]
					registered_region=Location.objects.get(id=registered_region_id)
					ship.registered_region=registered_region
				
				if rig_of_vessel_id is not None:
					rig_of_vessel_id=rigofvessel_id_map[rig_of_vessel_id]
					rig_of_vessel=RigOfVessel.objects.get(id=rig_of_vessel_id)
					ship.rig_of_vessel=rig_of_vessel
				
				if ton_type_id is not None:
					ton_type_id=tontype_id_map[ton_type_id]
					ton_type=TonType.objects.get(id=ton_type_id)
					ship.ton_type=ton_type
				
				if vessel_construction_place_id is not None:
					vessel_construction_place_id=place_id_map[vessel_construction_place_id]
					construction_place=Location.objects.get(id=vessel_construction_place_id)
					ship.vessel_construction_place=construction_place
				
				if vessel_construction_region_id is not None:
					vessel_construction_region_id=region_id_map[vessel_construction_region_id]
					vessel_construction_region=Location.objects.get(id=vessel_construction_region_id)
					ship.vessel_construction_region=vessel_construction_region

				ship.save()
		
		
		
		
		cnx.close()

