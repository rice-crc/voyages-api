import time
import json
import pprint
import urllib
from django.db.models import Avg,Sum,Min,Max,Count,Q,F
from django.db.models.aggregates import StdDev
from voyages3.localsettings import OPEN_API_BASE_API,DEBUG,SOLR_ENDPOINT,REDIS_HOST,REDIS_PORT,USE_REDIS_CACHE
import requests
from django.core.paginator import Paginator
import html
import re
import pysolr
import redis
import os
import uuid
from past.models import EnslaverRole,EnslaverAlias
from document.models import Source
from common.autocomplete_indices import get_inverted_autocomplete_indices,autocomplete_indices
import hashlib


redis_cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)


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

def post_req(queryset,r,options_dict,auto_prefetch=True):
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
			if op in ['lte','gte','exact','in','icontains']:
				django_filter_term='__'.join([varName,op])
				kwargs[django_filter_term]=searchTerm
			elif op =='btw' and type(searchTerm)==list and len(searchTerm)==2:
				searchTerm.sort()
				min,max=searchTerm
				kwargs['{0}__{1}'.format(varName, 'lte')]=max
				kwargs['{0}__{1}'.format(varName, 'gte')]=min		
			else:
				errormessages.append(f"{op} is not a valid django search operation")
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

def autocomplete_req(queryset,request,options):
	
	#first, get the reqdata
	rdata=request.data
	varName=str(rdata.get('varName'))
	querystr=str(rdata.get('querystr'))
	offset=int(rdata.get('offset'))
	limit=int(rdata.get('limit'))
	
	#then load the appropriate solr core to assist
	inverted_autocomplete_indices=get_inverted_autocomplete_indices()
	inverted_autocomplete_index=inverted_autocomplete_indices[varName]
	core_name=inverted_autocomplete_index['core_name']
	ac_field_model=inverted_autocomplete_index['model']
	ac_index_fields=inverted_autocomplete_index['fields']
	
	#now get the pk's of the object from solr
	if querystr=='':
		#... unless we have an empty search
		#if we have an empty search
		#then go ahead and fetch the pk's for the unfiltered queryset of that model
		#however, this will only ever happen once -- because otherwise we will have those pk's sitting in redis for us
		if USE_REDIS_CACHE:
			hashdict={
				'modelname':str(ac_field_model),
				'req':rdata,
				'req_type':"WE WANT THE FULL PK LIST ON THE TARGET MODEL"
			}
			hashed_full_req=hashlib.sha256(json.dumps(hashdict,sort_keys=True,indent=1).encode('utf-8')).hexdigest()
			cached_response = redis_cache.get(hashed_full_req)
		else:
			cached_response=None
		
		if cached_response is None:
			solr_ids=[i[0] for i in ac_field_model.objects.all().values_list('id')]
			if USE_REDIS_CACHE:
				redis_cache.set(hashed_full_req,json.dumps(solr_ids))
		else:
			solr_ids=cached_response
		solr_ids=set(solr_ids)
	else:
		#if we do have some text to work with, then run the solr search
		solr = pysolr.Solr(
			f'{SOLR_ENDPOINT}/{core_name}/',
			always_commit=True,
			timeout=10
		)
		querystr=re.sub("\s+"," ",querystr)
		querystr=querystr.strip()
		searchstringcomponents=[''.join(filter(str.isalnum,s)) for s in querystr.split(' ')]
		finalsearchstring="(%s)" %(" ").join(searchstringcomponents)
		results=solr.search('text:%s' %finalsearchstring,**{'rows':10000000,'fl':'id'})
		solr_ids=set([doc['id'] for doc in results.docs])
		solr_ids=set(solr_ids)
	
	#now we get the primary keys of that variable name from the filtered queryset
	#for example, if i'm searching in the trans-atlantic database, then I shouln't get any hits for 'OMNO'
	model_searchfield=[a for a in ac_index_fields if a in varName][0]
	varName_pkfield=re.sub("_[a-z]+$","_id",varName)
	#again, use redis internally if possible
	if USE_REDIS_CACHE:
		hashdict={
			'modelname':str(queryset),
			'req':rdata,
			'req_type':"WE WANT THE FILTERED PK LIST FOR THE NESTED VARNAME"
		}
		hashed_full_req=hashlib.sha256(json.dumps(hashdict,sort_keys=True,indent=1).encode('utf-8')).hexdigest()
		cached_response = redis_cache.get(hashed_full_req)
	else:
		cached_response=None
	if cached_response is None:

		filtered_queryset,results_count=post_req(
			queryset,
			request,
			options,
			auto_prefetch=False
		)
		varName_pks=[i[0] for i in filtered_queryset.values_list(varName_pkfield)]
		if USE_REDIS_CACHE:
			redis_cache.set(hashed_full_req,json.dumps(varName_pks))
	else:
		varName_pks=cached_response
	varName_pks=set(varName_pks)
	
	#now take the intersection of those sets
	##to recap, i've, for example,
	####used solr to get the full list of sources on a text search for 'omno'
	####hit the orm to get all the full list of applicable source pk's, say, in the intra-american db
	####and now i want to see where the overlap is
	results_id=list(solr_ids & varName_pks)
	
	#we're almost done. now we are going to pull the actual field the user asked for
	#and again, cache it
	if USE_REDIS_CACHE:
		hashdict={
			'modelname':str(queryset),
			'req':rdata,
			'req_type':"WE WANT THE AC SUGGESTIONS"
		}
		hashed_full_req=hashlib.sha256(json.dumps(hashdict,sort_keys=True,indent=1).encode('utf-8')).hexdigest()
		cached_response = redis_cache.get(hashed_full_req)
	else:
		cached_response=None
	
	if cached_response is None:
		ac_suggestions=[v[0] for v in ac_field_model.objects.all().filter(id__in=results_id).order_by(model_searchfield).values_list(model_searchfield)]
		if USE_REDIS_CACHE:
			redis_cache.set(hashed_full_req,json.dumps(ac_suggestions))
	else:
		ac_suggestions=cached_response

	paginated_ac_suggestions=ac_suggestions[offset:(offset+limit)]
	
	response=[{"value":v} for v in paginated_ac_suggestions]
	
	return response