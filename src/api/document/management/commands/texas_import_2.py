import csv
import re
from pyzotero import zotero
from django.core.management.base import BaseCommand, CommandError
from document.models import *
from past.models import *
from voyage.models import *
from voyages3.settings import *

class Command(BaseCommand):
	help = '\
	imports dd41 csvs -- purpose-built. again.\
	the issue we had is that it does not seem to have imported all the enslaver roles properly.\
	i\'m pretty sure that i didn not read the enslavers off the enslaved spreadsheet -- only the voyages spreadsheet.\
	'
	def handle(self, *args, **options):
		csvpath='document/management/commands/texas_enslaved_enslavers.csv'
		
		texas_voyage_enslaved={}
		
		with open(csvpath,'r',encoding='utf-8-sig') as csvfile:
			reader=csv.DictReader(csvfile)
			for row in reader:
				vid=row['VOYAGEID'].strip()
				if vid in texas_voyage_enslaved:
					texas_voyage_enslaved[vid].append(row)
				else:
					texas_voyage_enslaved[vid]=[row]
		
		csvpath='document/management/commands/texas_voyage_enslavers.csv'
		
		texas_voyage_enslavers={}
		
		with open(csvpath,'r',encoding='utf-8-sig') as csvfile:
			reader=csv.DictReader(csvfile)
			for row in reader:
				vid=row['VOYAGEID'].strip()
				texas_voyage_enslavers[vid]=row
		
		combined_voyage_ids=list(set(
			list(texas_voyage_enslavers.keys())+
			list(texas_voyage_enslaved.keys())
		))
		
		# 0. Run through all of Daniel's Texas voyages and blow away
		# 	A. All connected enslavementrelations (and of course enslaverroles)
		# 	B. The enslaver aliases and identities
		
		voyages=Voyage.objects.all().filter(voyage_id__in=combined_voyage_ids)

		for voyage in voyages:
			enslavementrelations=voyage.voyage_enslavement_relations.all()
			
			for enslavementrelation in enslavementrelations:
# 				print(enslavementrelation)
				if enslavementrelation.id != None:
					
					relations_enslavers=enslavementrelation.relation_enslavers.all()
					for relation_enslavers in relations_enslavers:
						try:
							alias=relation_enslavers.enslaver_alias
							identity=alias.identity
							identity.delete()
							alias.delete()
							relation_enslavers.delete()
							try:
								enslavementrelation.delete()
							except:
								pass
						except:
							pass
			
		EnslaverAlias.objects.all().filter(
			manual_id__icontains='TEXAS_ENSLAVER'
		).delete()
				
				
							
		# 1. Run through the two spreadsheets
		# 	A. & create new enslaver identities off each unique name, keeping an alias id for each
		# 		1. texas_voyage_enslavers:
		# 			OWNERA, CAPTAINA, CAPTAINB, CAPTAINC
		# 		2. texas_voyage_enslaved:
		# 			Shipper, Owner A, Owner B
		##AGAIN. WE ARE TREATING THE NAMES AS UNIQUE HERE
		
		texas_enslavers={}
		c=1
		for vid in texas_voyage_enslavers:
			voyage_enslavers=texas_voyage_enslavers[vid]
			voyage_enslaved_rows=texas_voyage_enslaved[vid]
			
			voyage_enslavernamekeys=['OWNERA', 'CAPTAINA', 'CAPTAINB', 'CAPTAINC']
			voyage_enslaver_names=list(set(
				[
					voyage_enslavers[n].strip() for n in voyage_enslavernamekeys
					if voyage_enslavers[n].strip() not in [None,""]
				]
			))
			
			enslaved_enslavernamekeys=['Shipper', 'Owner A', 'Owner B']
			
			enslaved_enslaver_names=[]
			
			for ve in voyage_enslaved_rows:
				for n in enslaved_enslavernamekeys:
					if ve[n].strip() not in [None,""]:
						enslaved_enslaver_names.append(ve[n].strip())
			
			enslaved_enslaver_names=list(set(enslaved_enslaver_names))
			
			enslaver_names=list(set(enslaved_enslaver_names+voyage_enslaver_names))
			
			for enslaver_name in enslaver_names:
				texas_id=f"TEXAS_ENSLAVER_{c}"
				
				identities=EnslaverIdentity.objects.all().filter(principal_alias=enslaver_name)
				
				if identities.count()>1:
					for ident in identities:
						ident.delete()
				
				identity,identity_isnew=EnslaverIdentity.objects.get_or_create(
					principal_alias=enslaver_name,
# 					manual_id=texas_id
				)
				
				
# 				if vid=='135509':
# 					print("AAA",enslaver_name)
				
				alias,alias_isnew=EnslaverAlias.objects.get_or_create(
					alias=enslaver_name,
					identity=identity
				)
				
				alias.manual_id=texas_id
				alias.save()
				
				texas_enslavers[enslaver_name]=alias.id
			
				c+=1
		
		# B. then for each voyage create a transportation enslavement relation
		# 	1. run through texas_voyage_enslavers and connect the enslavers to this relation with their appropriate roles ("captain" or "investor")
		# 	2. run through texas_voyage_enslaved and connect
		# 		a. each enslaved person to this relation
		# 		b. each shipper to this relation with the role "shipper"
		# 		c. each owner to this relation with the role "owner"
		
# 		
# 		
# 		texas_voyage_enslaved
# 		
# 		texas_voyage_enslavers
		relation_type=EnslavementRelationType.objects.get(name="Transportation")
		for vid in texas_voyage_enslavers:
			voyage_row = texas_voyage_enslavers[vid]
			voyage=Voyage.objects.get(voyage_id=vid)
			owner_a=voyage_row['OWNERA']
			captain_a=voyage_row['CAPTAINA']
			captain_b=voyage_row['CAPTAINB']
			captain_c=voyage_row['CAPTAINC']
			
			er = EnslavementRelation.objects.create(
				relation_type=relation_type,
				voyage=voyage
			)
			
			def connect_enslaver(name,role,er):
				name=name.strip()
				
				role=EnslaverRole.objects.get(name=role)
				
				if name not in ['',None]:
					
					enslaver_aliases=EnslaverAlias.objects.all().filter(
						alias=name,
						manual_id__icontains='TEXAS_ENSLAVER'
					)
# 					if enslaver_aliases.count()>1:
# 						for ea in enslaver_aliases:
# 							print(ea)
# 						exit()
					
					enslaver_alias=EnslaverAlias.objects.get(
						alias=name,
						manual_id__icontains='TEXAS_ENSLAVER'
					)
				
					eir,eir_isnew=EnslaverInRelation.objects.get_or_create(
						enslaver_alias=enslaver_alias,
						relation=er
					)
					
					eir_role_labels=[r.name for r in eir.roles.all()]
					
					if role not in eir_role_labels:
						eir.roles.add(role)
						eir.save()
				else:
					eir=None
				
				return eir
			
			row_enslavers=[
				[owner_a,'Investor'],
				[captain_a,'Captain'],
				[captain_b,'Captain'],
				[captain_c,'Captain']
			]
			
			for row_enslaver in row_enslavers:
				name,role=row_enslaver
				connect_enslaver(name,role,er)
			
			voyage_enslaved=texas_voyage_enslaved[vid]
# 			if vid=='135509':
# 				print(voyage_enslaved)
			
			for enslaved_row in voyage_enslaved:
				eid=enslaved_row["ID"]
				enslaved=Enslaved.objects.get(id=eid)
				
				shipper=enslaved_row["Shipper"]
				owner_a=enslaved_row["Owner A"]
				owner_b=enslaved_row["Owner B"]
				
				if shipper not in ['',None]:
					relation_type=EnslavementRelationType.objects.get(name="Transportation")
					name=shipper
					role="Shipper"
					EnslavedInRelation.objects.create(
						enslaved=enslaved,
						relation=er
					)
					connect_enslaver(name,role,er)
				
				row_owners=[
					[owner_a,'Owner'],
					[owner_b,'Owner']
				]
				
				relation_type=EnslavementRelationType.objects.get(name="Ownership")
				enslaver_role=EnslaverRole.objects.get(name="Owner")
				for row_owner in row_owners:
					name,role=row_owner
					role=enslaver_role.name
					name=name.strip()
					if name not in ['',None]:
						
# 						enslaver_aliases=EnslaverAlias.objects.all().filter(
# 							alias=name,
# 							manual_id__icontains='TEXAS_ENSLAVER'
# 						)
# 						if enslaver_aliases.count()>1:
# 							for ea in enslaver_aliases:
# 								print(ea)
# 							exit()
						
# 						if vid=='135509':
# 							print(name)
						
						enslaver_alias=EnslaverAlias.objects.get(
							alias=name,
							manual_id__icontains='TEXAS_ENSLAVER'
						)
						
						candidate_enslavement_relations=EnslavementRelation.objects.all().filter(
							voyage=voyage,
							relation_enslavers__enslaver_alias=enslaver_alias,
							relation_enslavers__roles__name=role
						)
						
						if len(candidate_enslavement_relations)>=1:
							er=candidate_enslavement_relations[0]
						else:
							er=EnslavementRelation.objects.create(
								voyage=voyage,
								relation_type=relation_type
							)
							
						EnslavedInRelation.objects.create(
							enslaved=enslaved,
							relation=er
						)
						
						candidate_eirs,candidate_eirs_isnew=EnslaverInRelation.objects.get_or_create(
							enslaver_alias=enslaver_alias,
							relation=er
						)
						
						if not candidate_eirs_isnew:
							eir=candidate_eirs
						else:
							eir=EnslaverInRelation.objects.get(
								enslaver_alias=enslaver_alias,
								relation=er
							)
						eir_role_labels=[r.name for r in eir.roles.all()]
# 						
						if role not in eir_role_labels:
							eir.roles.add(enslaver_role)
							eir.save()
						# 
# 						
# 						
# 						eir,eir_isnew=EnslaverInRelation.objects.get_or_create(
# 							enslaver_alias=enslaver_alias,
# 							relation=er
# 						)
# 						
# 						eir_role_labels=[r.name for r in eir.roles.all()]
# 						
# 						if role not in eir_role_labels:
# 							eir.roles.add(enslaver_role)
# 							eir.save()
# 				
# 				
# 				
				
				