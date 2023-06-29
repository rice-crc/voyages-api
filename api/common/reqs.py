import json
import pprint
import urllib
from django.db.models import Avg,Sum,Min,Max,Count,Q,F
from django.db.models.aggregates import StdDev
from .nest import *
from django.core.paginator import Paginator
import html
#GENERIC FUNCTION TO RUN A CALL ON REST SERIALIZERS
##Default is to auto prefetch, but need to be able to turn it off.
##For instance, on our PAST graph-like data, the prefetch can overwhelm the system if you try to get everything
##can also just pass an array of prefetch vars


def post_req(queryset,s,r,options_dict,auto_prefetch=True,retrieve_all=False):
	
	errormessages=[]
	next_uri=None
	prev_uri=None
	results_count=None
	all_fields={i:options_dict[i] for i in options_dict if 'type' in options_dict[i]}
	
	try:
		params=dict(r.POST)
		pp = pprint.PrettyPrinter(indent=4)
		print("--post req params--")
		pp.pprint(params)
	except:
		errormessages.append("error parsing parameters")
	
	selected_fields=params.get('selected_fields') or list(all_fields.keys())
	bad_fields=[f for f in selected_fields if f not in all_fields]
	if len(bad_fields)>0:
		errormessages.append("the following fields are not in the models: %s" %', '.join(bad_fields))
	
	try:
		###FILTER RESULTS
		##select text and numeric fields, ignoring those without a type
		text_fields=[i for i in all_fields if 'CharField' in all_fields[i]['type']]
		numeric_fields=[i for i in all_fields if 'IntegerField' in all_fields[i]['type'] or 'DecimalField' in all_fields[i]['type'] or 'FloatField' in all_fields[i]['type']]
		boolean_fields=[i for i in all_fields if 'BooleanField' in all_fields[i]['type']]

		##build filters
		kwargs={}
		###numeric filters -- only accepting one range per field right now
		active_numeric_search_fields=[i for i in set(params).intersection(set(numeric_fields))]
		if len(active_numeric_search_fields)>0:
			for field in active_numeric_search_fields:
				fieldvals=params.get(field)
				if '*' in fieldvals:
					kwargs[field+'__in']=[int(i) for i in fieldvals if i!='*']
				elif '**' in fieldvals and len(fieldvals)==2:
					if fieldvals[0]=='**':
						kwargs['{0}__{1}'.format(field, 'lte')]=max
					else:
						kwargs['{0}__{1}'.format(field, 'gte')]=min
				else:
					range=fieldvals
					vals=[float(i) for i in range]
					vals.sort()
					min,max=vals
					kwargs['{0}__{1}'.format(field, 'lte')]=max
					kwargs['{0}__{1}'.format(field, 'gte')]=min
		###text filters (exact match, and allow for multiple entries joined by an or)
		###this hard eval is not ideal but I can't quite see how else to do it just now?
		active_text_search_fields=[i for i in set(params).intersection(set(text_fields))]
		if len(active_text_search_fields)>0:
			for field in active_text_search_fields:
				vals=params.get(field)
				qobjstrs=["Q({0}={1})".format(field,json.dumps(re.sub("\\\\+","",val))) for val in vals]
				#print(vals,qobjstrs)
				queryset=queryset.filter(eval('|'.join(qobjstrs)))
				#print(queryset)
		##boolean filters -- only accepting one range per field right now
		active_boolean_search_fields=[i for i in set(params).intersection(set(boolean_fields))]
		if len(active_boolean_search_fields)>0:
			for field in active_boolean_search_fields:
				searchstring=params.get(field)[0]
				if searchstring.lower() in ["true","t","1","yes"]:
					searchstring=True
				elif searchstring.lower() in ["false","f","0","no"]:
					searchstring=False
	
				if searchstring in [True,False]:
					kwargs[field]=searchstring
		#print(kwargs)
		###apply filters
		queryset=queryset.filter(**kwargs)
		results_count=queryset.count()
		print('--counts--')
		print("resultset size:",results_count)
	except:
 		errormessages.append("search/filter error")
	 
	try:
		#PREFETCH REQUISITE FIELDS
		
		if auto_prefetch:
			prefetch_fields=all_fields
		else:
			prefetch_fields=selected_fields
		
		#print(prefetch_keys)
		##ideally, I'd run this list against the model and see
		##which were m2m relationships (prefetch_related) and which were 1to1 (select_related)
		prefetch_vars=list(set(['__'.join(i.split('__')[:-1]) for i in prefetch_fields if '__' in i]))
		print('--prefetching %d vars--' %len(prefetch_vars))
# 		print(prefetch_vars)
		
		for p in prefetch_vars:
			queryset=queryset.prefetch_related(p)
		
	except:
		errormessages.append("prefetch error")
	
	
	#AGGREGATIONS
	##e.g. voyage_slaves_numbers__imp_total_num_slaves_embarked__sum
	##This *SHOULD* aggregate on the filtered queryset, which means
	###you could filter the dataset and then update rangeslider min & max
	###BUT ALSO!!
	####1. autocomplete suggestions
	####2. geo tree selects
	
	#INCLUDE AGGREGATION FIELDS
	aggregation_fields=params.get('aggregate_fields')

	if aggregation_fields is not None:
		valid_aggregation_fields=[f for f in options_dict if 'Integer' in options_dict[f]['type'] or 'Decimal' in options_dict[f]['type']]
		bad_aggregation_fields=[f for f in aggregation_fields if f not in valid_aggregation_fields]
		if bad_aggregation_fields!=[]:
			errormessages.append("bad aggregation fields: "+",".join(bad_aggregation_fields))
			print(errormessages)
		else:
			try:
				aggqueryset=[]
				for aggfield in aggregation_fields:
					for aggsuffix in ["min","max"]:
						selected_fields.append(aggfield+"_"+aggsuffix)
					aggqueryset.append(queryset.aggregate(Min(aggfield)))
					aggqueryset.append(queryset.aggregate(Max(aggfield)))
				queryset=aggqueryset
				auto_prefetch=True		
			except:
				errormessages.append("aggregation error")

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
	except:
		errormessages.append("ordering error")
	
	#PAGINATION/LIMITS
# 	try:
	if retrieve_all==False:
		results_per_page=params.get('results_per_page',[10])
		results_page=params.get('results_page',[1])
		paginator=Paginator(queryset, results_per_page[0])
		res=paginator.get_page(results_page[0])
		print("-->page",results_page[0],"-->@",results_per_page[0],"per page")
	else:
		res=queryset
	
	
	
# 	except:
# 		errormessages.append("ordering or pagination error")
	
	return res,selected_fields,next_uri,prev_uri,results_count,errormessages

def options_handler(flatfilepath,request=None,hierarchical=True):
	if request is not None:
		if 'hierarchical' in request.query_params:
			if request.query_params['hierarchical'].lower() in ['false','0','n']:
				hierarchical=False
	d=open(flatfilepath,'r')
	t=d.read()
	j=json.loads(t)
	d.close()
	if hierarchical:
		j=nest_django_dict(j)
	return j