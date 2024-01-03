import time
import json
import pprint
import urllib
from django.db.models import Avg,Sum,Min,Max,Count,Q,F
from django.db.models.aggregates import StdDev
from voyages3.localsettings import *
import requests
from django.core.paginator import Paginator
import html
import re
import pysolr
import os
#GENERIC FUNCTION TO RUN A CALL ON REST SERIALIZERS
##Default is to auto prefetch, but need to be able to turn it off.
##For instance, on our PAST graph-like data, the prefetch can overwhelm the system if you try to get everything
##can also just pass an array of prefetch vars


def parse_filter_obj(filter_obj_in,all_fields):
	filter_obj_out={}
	errors=[]
	for suffixedvarname in filter_obj_in:
		if not re.match('[a-z|_]+[__exact|__gte|__lte|__in]$',suffixedvarname):
			errors.append("BAD FILTER: %s" %suffixedvarname)
		else:
			varnamedecomposed=suffixedvarname.split('__')
			varname='__'.join(varnamedecomposed[:-1])
			suffix=varnamedecomposed[-1]
			queryval=filter_obj_in[suffixedvarname]
			if varname not in filter_obj_out:
				filter_obj_out[varname]={suffixedvarname:queryval}
			else:
				filter_obj_out[varname][suffixedvarname]=queryval
	return filter_obj_out,errors

def post_req(queryset,s,r,options_dict,auto_prefetch=True,retrieve_all=False):
	
	errormessages=[]
	results_count=None
	
	all_fields={i:options_dict[i] for i in options_dict if options_dict[i]['type']!='table'}
	try:
		if type(r)==dict:
			params=r
		else:
			params=dict(r.data)
	except:
		errormessages.append("error parsing request")
		return None,None,None,errormessages
	
	print("----\npost req params:",json.dumps(params,indent=1))
	
	try:
		filter_obj=params.get('filter')
	
		if filter_obj is not None:
			filter_obj,errors=parse_filter_obj(filter_obj,all_fields)
			errormessages+=errors
		else:
			filter_obj={}
	except:
		errormessages.append("error parsing filter obj")
	
	print("----\nfilter obj:",json.dumps(filter_obj,indent=1))

	
	if 'global_search' in params:
		qsetclassstr=str(queryset[0].__class__)
		
		solrcorenamedict={
			"<class 'voyage.models.Voyage'>":'voyages',
			"<class 'past.models.EnslaverIdentity'>":'enslavers',
			"<class 'past.models.Enslaved'>":'enslaved',
			"<class 'blog.models.Post'>":'blog'
		}
		
		solrcorename=solrcorenamedict[qsetclassstr]
		print("CLASS",qsetclassstr,solrcorename)
		
		solr = pysolr.Solr(
			'http://voyages-solr:8983/solr/%s/' %solrcorename,
			always_commit=True,
			timeout=10
		)
		search_string=params['global_search'][0]
		search_string=re.sub("\s+"," ",search_string)
		search_string=search_string.strip()
		searchstringcomponents=[''.join(filter(str.isalnum,s)) for s in search_string.split(' ')]
		finalsearchstring="(%s)" %(" ").join(searchstringcomponents)
		results=solr.search('text:%s' %finalsearchstring,**{'rows':10000000,'fl':'id'})
		ids=[doc['id'] for doc in results.docs]
		queryset=queryset.filter(id__in=ids)
		
	selected_fields=params.get('selected_fields') or list(all_fields.keys())
	bad_fields=[f for f in selected_fields if f not in all_fields]
	if len(bad_fields)>0:
		errormessages.append("the following fields are not in the models: %s" %', '.join(bad_fields))
	
# 	try:
	kwargs={}
	for varname in filter_obj:
		for suffixedvarname in filter_obj[varname]:
			queryval=filter_obj[varname][suffixedvarname]
			kwargs[suffixedvarname]=queryval
	queryset=queryset.filter(**kwargs)
	results_count=queryset.count()
	print('--counts--')
	print("resultset size:",results_count)
# 	except:
#  		errormessages.append("search/filter error")
	 
	try:
		aggregation_fields=params.get('aggregate_fields')
		if aggregation_fields is not None:
			selected_fields=aggregation_fields
	#PREFETCH REQUISITE FIELDS
		if auto_prefetch:
			prefetch_fields=selected_fields
			#print(prefetch_keys)
			##ideally, I'd run this list against the model and see
			##which were m2m relationships (prefetch_related) and which were 1to1 (select_related)
			prefetch_vars=list(set(['__'.join(i.split('__')[:-1]) for i in prefetch_fields if '__' in i]))
			print('--prefetching %d vars--' %len(prefetch_vars))
			for p in prefetch_vars:
				queryset=queryset.prefetch_related(p)
		else:
			print("not prefetching")
	except:
		errormessages.append("prefetch error")
	
	
	#AGGREGATIONS
	##e.g. voyage_slaves_numbers__imp_total_num_slaves_embarked__sum
	##This *SHOULD* aggregate on the filtered queryset, which means
	###you could filter the dataset and then update rangeslider min & max
	###BUT ALSO!!
	####1. autocomplete suggestions
	####2. geo tree selects
	
	#ORDER RESULTS
	#queryset=queryset.order_by('-voyage_slaves_numbers__imp_total_num_slaves_embarked','-voyage_id')	
	try:
		order_by=params.get('order_by')
		if order_by is not None:
			print("---->order by---->",order_by)
			for ob in order_by:
				if ob.startswith('-'):
					queryset=queryset.order_by(F(ob[1:]).desc(nulls_last=True))
				else:
					queryset=queryset.order_by(F(ob).asc(nulls_last=True))
		else:
			queryset=queryset.order_by('id')
	except:
		errormessages.append("ordering error")
	
	#PAGINATION/LIMITS
	if retrieve_all==False:
		results_per_page=params.get('results_per_page',[10])
		results_page=params.get('results_page',[1])
		paginator=Paginator(queryset, results_per_page[0])
		res=paginator.get_page(results_page[0])
		print("-->page",results_page[0],"-->@",results_per_page[0],"per page")
	else:
		res=queryset
	
		#INCLUDE AGGREGATION FIELDS
	aggregation_fields=params.get('aggregate_fields')

	if aggregation_fields is not None:
		valid_aggregation_fields=[f for f in options_dict if options_dict[f]['type'] in ['integer','number']]
		bad_aggregation_fields=[f for f in aggregation_fields if f not in valid_aggregation_fields]
		if bad_aggregation_fields!=[]:
			errormessages.append("bad aggregation fields: "+",".join(bad_aggregation_fields))
			print(errormessages)
		else:
			try:
				aggqueryset=[]
				selected_fields=[]
				for aggfield in aggregation_fields:
					for aggsuffix in ["min","max"]:
						selected_fields.append(aggfield+"_"+aggsuffix)
					aggqueryset.append(queryset.aggregate(Min(aggfield)))
					aggqueryset.append(queryset.aggregate(Max(aggfield)))
				queryset=aggqueryset
				res=aggqueryset
			except:
				errormessages.append("aggregation error")
					
	return res,selected_fields,results_count,errormessages

def getJSONschema(base_obj_name,hierarchical=False,rebuild=False):
	if hierarchical in [True,"true","True",1,"t","T","yes","Yes","y","Y"]:
		hierarchical=True
	else:
		hierarchical=False
	r=requests.get(url=OPEN_API_BASE_API)
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


def autocomplete_req(queryset,varname,querystr,offset,max_offset,limit):
	
	'''
		autocomplete search any related text/char field
		
		args---->
		queryset: what we are searching within
		varname: the fully-qualified (double-underscored) related field
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
	
	#hard-coded internal pagination for deduping
	pagesize=500

	if '__' in varname:
		kstub='__'.join(varname.split('__')[:-1])
		queryset=queryset.prefetch_related(kstub)

	kwargs={'{0}__{1}'.format(varname, 'icontains'):querystr}
	queryset=queryset.filter(**kwargs)
	queryset=queryset.order_by(varname)
	allcandidates=queryset.values_list(varname)
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
	return response