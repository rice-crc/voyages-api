import time
import json
import pprint
import urllib
from django.db.models import Avg,Sum,Min,Max,Count,Q,F
from django.db.models.aggregates import StdDev
from voyages3.localsettings import OPEN_API_BASE_API,DEBUG,SOLR_ENDPOINT
import requests
from django.core.paginator import Paginator
import html
import re
import pysolr
import os
import uuid
from past.models import EnslaverRole,EnslaverAlias
from document.models import Source

def clean_long_df(rows,selected_fields):
	'''
	JSON Serialization doesn't fly when you fetch the raw value of certain data types
	e.g., uuid.UUID, decimal.Decimal.....
	'''
	
	resp={sf:[] for sf in selected_fields}
	
	for i in range(len(selected_fields)):
		sf=selected_fields[i]
		column=[r[i] for r in rows]
		
		for r in rows:
			val=r[i]
			if type(val) == uuid.UUID:
				val=str(val)
			
			resp[sf].append(val)
	
	return resp
	
def paginate_queryset(queryset,request):
	'''
		Customized pagination for post requests. Params are:
		page_size (int)
		page (int)
	'''
	params=request.data
	page_size=params.get('page_size',10)
	page=params.get('page',1)
	paginator=Paginator(queryset, page_size)
	results_page=paginator.get_page(page)
	total_results_count=queryset.count()
	return results_page,total_results_count,page,page_size
	
def get_fieldstats(queryset,aggregation_field,options_dict):
	'''
		Used to get the min and max of a numeric field
		Takes a queryset (can be filtered), a field to be filtered on,
		and the list of valid variables for the queryset's base object class
		then uses django's aggregation functions to pull the min & max
		The mean is also available if we choose to extend this later
	'''
	res=None
	errormessages=[]
	if aggregation_field is None:
		errormessages.append("you must supply a field to aggregate on")
	else:
		valid_aggregation_fields=[f for f in options_dict if options_dict[f]['type'] in ['integer','number']]
		if aggregation_field not in valid_aggregation_fields:
			errormessages.append("bad aggregation field: " + aggregation_field)
		else:
			if '__' in aggregation_field:
				prefetch_name='__'.join(aggregation_field.split('__')[:-1])
				queryset=queryset.prefetch_related(prefetch_name)
				if DEBUG:
					print("prefetching:",prefetch_name)
			min=queryset.aggregate(Min(aggregation_field)).popitem()[1]
			max=queryset.aggregate(Max(aggregation_field)).popitem()[1]
			res={
				'varName':aggregation_field,
				'min':min,
				'max':max
			}
	return res,errormessages

def post_req(queryset,s,r,options_dict,auto_prefetch=True):
	'''
		This function handles:
		1. ensuring that all the fields that will be called are valid on the model
		2. applying filters to the queryset
		3. bypassing the normal usage and going to solr for pk's if 'global_search' is in the query data
		4. ordering the queryset
		5. attempting to intelligently prefetch related fields for performance
	'''
	errormessages=[]
	results_count=None
	
	all_fields={i:options_dict[i] for i in options_dict if options_dict[i]['type']!='table'}
	if type(r)==dict:
		params=r
	else:
		params=dict(r.data)
	
	if DEBUG:
		print("----\npost req params:",json.dumps(params,indent=1))
	filter_obj=params.get('filter') or {}
	
	#global search bypasses the normal filtering process
	#hits solr with a search string (which currently is applied across all text fields on a model)
	#and then creates its filtered queryset on the basis of the pk's returned by solr
	print("PRE FILTER COUNT",queryset.count())
	if 'global_search' in params:
		qsetclassstr=str(queryset[0].__class__)
		
		solrcorenamedict={
			"<class 'voyage.models.Voyage'>":'voyages',
			"<class 'past.models.EnslaverIdentity'>":'enslavers',
			"<class 'past.models.Enslaved'>":'enslaved',
			"<class 'blog.models.Post'>":'blog'
		}
		
		core_name=solrcorenamedict[qsetclassstr]
		
		if DEBUG:
			print("CLASS",qsetclassstr,core_name)
		
		solr = pysolr.Solr(
			f'{SOLR_ENDPOINT}/{core_name}/',
			always_commit=True,
			timeout=10
		)
		search_string=params['global_search']
		search_string=re.sub("\s+"," ",search_string)
		search_string=search_string.strip()
		searchstringcomponents=[''.join(filter(str.isalnum,s)) for s in search_string.split(' ')]
		finalsearchstring="(%s)" %(" ").join(searchstringcomponents)
		results=solr.search('text:%s' %finalsearchstring,**{'rows':10000000,'fl':'id'})
		ids=[doc['id'] for doc in results.docs]
		filter_queryset=queryset.filter(id__in=ids)
	else:
		kwargs={}
		for item in filter_obj:
			op=item['op']
			searchTerm=item["searchTerm"]
			varName=item["varName"]
			if varName in all_fields and op in ['lte','gte','exact','in','icontains']:
				django_filter_term='__'.join([varName,op])
				kwargs[django_filter_term]=searchTerm
			elif varName in all_fields and op =='btw' and type(searchTerm)==list and len(searchTerm)==2:
				searchTerm.sort()
				min,max=searchTerm
				kwargs['{0}__{1}'.format(varName, 'lte')]=max
				kwargs['{0}__{1}'.format(varName, 'gte')]=min		
			else:
				if varName not in all_fields:
					errormessages.append("var %s not in model" %varName)
				if op not in ['lte','gte','exact','in','icontains']:
					errormessages.append("%s is not a valid django search operation" %op)
		filter_queryset=queryset.filter(**kwargs)
	
	#dedupe m2m filters
	ids=list(set([v[0] for v in filter_queryset.values_list('id')]))
	queryset=queryset.filter(id__in=ids)
	print("POST FILTER COUNT",queryset.count())
	results_count=queryset.count()
	if DEBUG:
		print("resultset size:",results_count)
	
	
	
	#PREFETCH REQUISITE FIELDS
	prefetch_fields=params.get('selected_fields') or []
	if prefetch_fields==[] and auto_prefetch:
		prefetch_fields=list(all_fields.keys())
	prefetch_vars=list(set(['__'.join(i.split('__')[:-1]) for i in prefetch_fields if '__' in i]))
	
	if DEBUG:
		print('--prefetching %d vars--' %len(prefetch_vars))
	for p in prefetch_vars:
		queryset=queryset.prefetch_related(p)
	
	#ORDER RESULTS
	#queryset=queryset.order_by('-voyage_slaves_numbers__imp_total_num_slaves_embarked','-voyage_id')
	order_by=params.get('order_by')
	if order_by is not None:
		if DEBUG:
			print("---->order by---->",order_by)
		for ob in order_by:
			if ob.startswith('-'):
				k=ob[1:]
				asc=False
			else:
				asc=True
				k=ob
			
			if k in all_fields:
				if asc:
					queryset=queryset.order_by(F(k).asc(nulls_last=True))
				else:
					queryset=queryset.order_by(F(k).desc(nulls_last=True))
			else:
				queryset=queryset.order_by('id')
	else:
		queryset=queryset.order_by('id')
						
	return queryset,results_count

def getJSONschema(base_obj_name,hierarchical=False,rebuild=False):
	'''
	Recursively walks the OpenAPI schemas to build flat json files that we can later use for indexing, serializer population and validation, etc.
	Its best friend is the rebuild_options management command.
	Why do this? It turns out that the OpenAPI endpoint is a little touchy, so we can't route live requests through it.
	'''
	if hierarchical in [True,"true","True",1,"t","T","yes","Yes","y","Y"]:
		hierarchical=True
	else:
		hierarchical=False
	r=requests.get(url=OPEN_API_BASE_API+"schema/?format=json")
	j=json.loads(r.text)
	schemas=j['components']['schemas']
	base_obj_name=base_obj_name
	def walker(output,schemas,obj_name,ismany=False):
		obj=schemas[obj_name]
		if 'properties' in obj:
			for fieldname in obj['properties']:
				thisfield=obj['properties'][fieldname]
				if 'allOf' in thisfield:
					thisfield=thisfield['allOf'][0]
# 					print(fieldname,'allof') ## OK THESE ARE M2M
					ismany=True
				if '$ref' in thisfield:
					next_obj_name=thisfield['$ref'].replace('#/components/schemas/','')
					output[fieldname]=walker({},schemas,next_obj_name,ismany)
# 					print(fieldname,'ref')
				elif 'type' in thisfield:
					if thisfield['type']!='array':
						thistype=thisfield['type']
						if 'format' in thisfield:
							if thisfield['format']:
								thistype='number'
						output[fieldname]={
							'type':thistype,
							'many':ismany
						}
# 						print(fieldname,'bottomval')
					else:
						thisfield_items=thisfield['items']
						if 'type' in thisfield_items:
# 							print('array otherbottomvalue',thisfield)
							output[fieldname]={
								'type':thisfield_items['type'],
								'many':ismany
							}
						elif '$ref'	in thisfield_items:
# 							print("array, ref???",thisfield)
							next_obj_name=thisfield_items['$ref'].replace('#/components/schemas/','')
							output[fieldname]=walker({},schemas,next_obj_name,ismany=True)
			ismany=False
		else:
			print(obj)
		return output
	
	output=walker({},schemas,base_obj_name)
		
	if not hierarchical:
		def flatten_this(input_dict,output_dict,keychain=[]):
			for k in input_dict:
				if 'type' in input_dict[k]:
					thiskey='__'.join(keychain+[k])
					output_dict[thiskey]=input_dict[k]
				else:
					output_dict=flatten_this(input_dict[k],output_dict,keychain+[k])
			return output_dict		
		output=flatten_this(output,{},[])
	
	if rebuild or not os.path.exists('./common/static/'+base_obj_name+"_options.json") or not os.path.exists('./common/static/'+base_obj_name+"_options.py"):
		flat_output=flatten_this(output,{},[])
		d=open('./common/static/'+base_obj_name+"_options.json",'w')
		d.write(json.dumps(flat_output))
		d.close()
		
		d=open('./common/static/'+base_obj_name+"_options.py",'w')
		d.write(base_obj_name+'_options='+str(flat_output))
		d.close()

	
	return output



#m2m autocomplete variables that simply cannot be fetched through my preferred route

def autocomplete_req(queryset,request):
	
	'''
		autocomplete search any related text/char field
		
		args---->
		queryset: what we are searching within
		varName: the fully-qualified (double-underscored) related field
		querystr: the substring we are searching for on that field
		offset, max_offset, and limit: pagination
		<----
		
		it works by
			* creating a values list query on the related field
			* and then running through these as quickly as possible until
				* it gets the requested new page length of unique new hits
				* or hits the end of the values list
		
		why is this a pain in the ass?
			* because mysql does not have distinct on related field functionality
		
		when will it hit a wall?
			* on values with lots of duplicates
			* like geo vars on voyages
			* or like rig types on voyageso
		
		it times out after 5 seconds just in case
		going to need caching
	'''

	autocomplete_m2m_bypass={
		'aliases__enslaver_relations__roles__name':(EnslaverRole,'name'),
		'enslaved_relations__relation__relation_enslavers__enslaver_alias__alias':(EnslaverAlias,'alias')
	}
	#hard-coded internal pagination for deduping
	pagesize=500
	rdata=request.data
	varName=str(rdata.get('varName'))
	querystr=str(rdata.get('querystr'))
	offset=int(rdata.get('offset'))
	limit=int(rdata.get('limit'))
	max_offset=500
	if offset>max_offset:
		return []
	if varName in autocomplete_m2m_bypass:
		#The m2m autocomplete with querying is just not going to cut it with some fields.
		objclass,varName=autocomplete_m2m_bypass[varName]
		queryset=objclass.objects.all()
	elif '__source__' in varName:
		#and others will straight up require solr
		core_name='sources'
		solr = pysolr.Solr(
			f'{SOLR_ENDPOINT}/{core_name}/',
			always_commit=True,
			timeout=10
		)
		
		print("QUERYSTRING",querystr)
		queryset=Source.objects.all()
		if querystr=='':
			queryset=Source.objects.all()
		else:
				
			search_string=querystr
			search_string=re.sub("\s+"," ",search_string)
			search_string=search_string.strip()
			searchstringcomponents=[''.join(filter(str.isalnum,s)) for s in search_string.split(' ')]
			finalsearchstring="(%s)" %(" ").join(searchstringcomponents)
			results=solr.search('text:%s' %finalsearchstring,**{'rows':10000000,'fl':'id'})
			ids=[doc['id'] for doc in results.docs]
			queryset=Source.objects.all().filter(id__in=ids)
		queryset.order_by('title')
		varName='title'
	else:
		if '__' in varName:
			kstub='__'.join(varName.split('__')[:-1])
			queryset=queryset.prefetch_related(kstub)
		kwargs={'{0}__{1}'.format(varName, 'icontains'):querystr}
		queryset=queryset.filter(**kwargs)
	queryset=queryset.order_by(varName)
	allcandidates=queryset.values_list(varName)
	allcandidatescount=allcandidates.count()
	st=time.time()
	
	if allcandidatescount < limit:
		final_vals=list(set([i[0] for i in allcandidates]))
	else:
		candidate_vals=[]
		start=0
		end=pagesize
		c=0
		while len(candidate_vals)<end:
			candidates=allcandidates[start:end]
			candidate_vals+=list(set([i[0] for i in candidates]))
			candidate_vals=list(set(candidate_vals))
			candidates_count=candidates.count()
			if candidates_count>=allcandidatescount or end >= allcandidatescount or len(candidate_vals)>=(offset+limit) or time.time()-st>5:
				break
			end+=pagesize
			start+=pagesize
		candidate_vals.sort()
		start=offset
		end=offset+limit
		if start >= candidates_count:
			final_vals=[]
		else:
			if end >= candidates_count:
				final_vals=candidate_vals[start:]
			else:
				final_vals=candidate_vals[start:end]
	response=[{"value":v} for v in final_vals]
	print(final_vals)
	return response