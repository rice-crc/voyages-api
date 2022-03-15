from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import generics
from rest_framework.metadata import SimpleMetadata
from rest_framework.response import Response
from django.views.generic.list import ListView
import urllib
import json
import requests
import time
from .models import *
#from .serializers import *
import pprint
from tools.nest import *
from tools.reqs import *
from tools.timer import timer
import collections
import gc
from .serializers import *
from .forms import *
from django.forms import modelformset_factory,inlineformset_factory




d=open('voyage/voyage_options.json','r')
voyage_options=(json.loads(d.read()))
d.close()

d=open('voyage/geo_options.json','r')
geo_options=(json.loads(d.read()))
d.close()

#LONG-FORM TABULAR ENDPOINT. PAGINATION IS A NECESSITY HERE!
##HAVE NOT YET BUILT IN ORDER-BY FUNCTIONALITY
class VoyageList(generics.GenericAPIView):
	serializer_class=VoyageSerializer
	def options(self,request):
		schema=options_handler(self,request,voyage_options)
		return JsonResponse(schema)
	def get(self,request):
		t=timer('FETCHING...',[])
		queryset=Voyage.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count=get_req(queryset,self,request,voyage_options)
		headers={"next_uri":next_uri,"prev_uri":prev_uri,"total_results_count":results_count}
		#read_serializer=VoyageSerializer(queryset,many=True,selected_fields=selected_fields)
		t=timer('building query',t)
		read_serializer=VoyageSerializer(queryset,many=True)
		t=timer('sql execution',t)
		serialized=read_serializer.data
		t=timer('serializing',t)

		#if the user hasn't selected any fields (default), then get the fully-qualified var names as the full list
		if selected_fields==[]:
			r=requests.options("http://127.0.0.1:8000/voyage/?hierarchical=False&auto=True")
			selected_fields=list(json.loads(r.text).keys())
		outputs=[]
		
		hierarchical=True
		if 'hierarchical' in request.query_params:
			if request.query_params['hierarchical'].lower() in ['false','0','n']:
				hierarchical=False
		
		if hierarchical==False:
			for s in serialized:
				d={}
				for selected_field in selected_fields:
					#In this flattened view, the reverse relationship breaks the references to the outcome variables in the serializer
					#not badly -- you just get some repeat, nested data -- but that's unhelpful
					#The fix will be to make it a through table relationship
					keychain=selected_field.split('__')
					bottomval=bottomout(s,list(keychain))
					d[selected_field]=bottomval
				outputs.append(d)
		else:
			outputs=serialized
		t=timer('flattening',t,done=True)
		return JsonResponse(outputs,safe=False,headers=headers)

#VOYAGES SCATTER DATAFRAME ENDPOINT (experimental and going to be a resource hog!)
class VoyageAggregations(generics.GenericAPIView):
	serializer_class=VoyageSerializer
	def get(self,request):
		params=request.GET
		aggregations=params.get('aggregate_fields')
		queryset=Voyage.objects.all()
		aggregation,selected_fields,next_uri,prev_uri,results_count=get_req(queryset,self,request,voyage_options,retrieve_all=True)
		output_dict={}
		for a in aggregation:
			for k in a:
				v=a[k]
				fn=k.split('__')[-1]
				varname=k[:-len(fn)-2]
				if varname in output_dict:
					output_dict[varname][fn]=a[k]
				else:
					output_dict[varname]={fn:a[k]}
		return JsonResponse(output_dict,safe=False)

#VOYAGES SCATTER DATAFRAME ENDPOINT (experimental and going to be a resource hog!)
class VoyageDataFrames(generics.GenericAPIView):
	serializer_class=VoyageSerializer
	def get(self,request):
		t=timer("FETCHING...",[])
		params=request.GET
		retrieve_all=True
		if 'results_per_page' in params:
			retrieve_all=False
		queryset=Voyage.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count=get_req(queryset,self,request,voyage_options,auto_prefetch=False,retrieve_all=retrieve_all)
		headers={"next_uri":next_uri,"prev_uri":prev_uri,"total_results_count":results_count}
		sf=list(selected_fields)
		t=timer('building query',t)
		serialized=VoyageSerializer(queryset,many=True,selected_fields=selected_fields)
		t=timer('sql execution',t)
		serialized=serialized.data
		r=requests.options("http://127.0.0.1:8000/voyage/?hierarchical=False&auto=True")
		t=timer('serialization',t)
		output_dicts={}
		for selected_field in sf:
			keychain=selected_field.split('__')
			for s in serialized:
				bottomval=bottomout(s,list(keychain))
				if selected_field in output_dicts:
					output_dicts[selected_field].append(bottomval)
				else:
					output_dicts[selected_field]=[bottomval]
		t=timer('flattening',t,done=True)
		return JsonResponse(output_dicts,safe=False,headers=headers)

#Get data on Places
#Default structure is places::region::broad_region
#By passing it the req param 'inverse=True', you'll get back broad_regions::regions::places
class VoyagePlaceList(generics.GenericAPIView):
	serializer_class=PlaceSerializer
	def options(self,request):
		schema=options_handler(self,request,geo_options)
		return JsonResponse(schema,safe=False)
	def get(self,request):
		t=timer("FETCHING...",[])
		queryset=Place.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count=get_req(queryset,self,request,geo_options,retrieve_all=True)
		t=timer('building query',t)
		read_serializer=PlaceSerializer(queryset,many=True)
		t=timer('sql execution',t)
		serialized=read_serializer.data
		t=timer('serialization',t)
		params=request.GET
		tree={}
		hierarchical=True
		if 'hierarchical' in request.query_params:
			if request.query_params['hierarchical'].lower() in ['false','0','n']:
				hierarchical=False
		if hierarchical:
			for place in serialized:
				broadregion_id=place['region']['broad_region']['id']
				region_id=place['region']['id']
				place_id=place['id']
				minimal_place_dict=dict(place)
				del(minimal_place_dict['region'])
				minimal_region_dict=dict(place['region'])
				del(minimal_region_dict['broad_region'])
				if broadregion_id not in tree:
					tree[broadregion_id]=place['region']['broad_region']
					tree[broadregion_id]['regions']={region_id:minimal_region_dict}
					tree[broadregion_id]['regions'][region_id]['places']={place_id:minimal_place_dict}
				else:
					if region_id not in tree[broadregion_id]['regions']:
						tree[broadregion_id]['regions'][region_id]=minimal_region_dict
						tree[broadregion_id]['regions'][region_id]['places']={place_id:minimal_place_dict}
					else:
						tree[broadregion_id]['regions'][region_id]['places'][place_id]=minimal_place_dict
			tree_list=[]
			for broadregion_id in tree:
				item=dict(tree[broadregion_id])
				item['regions']=[]
				for region_id in tree[broadregion_id]['regions']:
					region=dict(tree[broadregion_id]['regions'][region_id])
					places=[]
					for place_id in region['places']:
						places.append(region['places'][place_id])
					region['places']=places
					item['regions'].append(region)
				tree_list.append(item)						
			outputs=tree_list
		else:
			#if the user hasn't selected any fields (default), then get the fully-qualified var names as the full list
			if selected_fields==[]:
				r=requests.options("http://127.0.0.1:8000/voyage/geo?hierarchical=False&auto=True")
				selected_fields=list(json.loads(r.text).keys())
			outputs=[]
			for s in serialized:
				d={}
				for selected_field in selected_fields:
					#In this flattened view, the reverse relationship breaks the references to the outcome variables in the serializer
					#not badly -- you just get some repeat, nested data -- but that's unhelpful
					#The fix will be to make it a through table relationship
					keychain=selected_field.split('__')
					bottomval=bottomout(s,list(keychain))
					d[selected_field]=bottomval
				outputs.append(d)
			
		t=timer('flattening',t,True)
		return JsonResponse(outputs,safe=False)


def manage_voyage(request,pk):
	voyage_instance = get_object_or_404(Voyage, pk=pk)

	# If this is a POST request then process the Form data
	if request.method == 'POST':

		# Create a form instance and populate it with data from the request (binding):
		form = VoyageForm(request.POST)

		# Check if the form is valid:
		'''if form.is_valid():
			# process the data in form.cleaned_data as required (here we just write it to the model due_back field)
			book_instance.due_back = form.cleaned_data['renewal_date']
			book_instance.save()

			# redirect to a new URL:
			return HttpResponseRedirect(reverse('all-borrowed') )'''

	# If this is a GET (or any other method) create the default form.
	else:
		#proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
		form = VoyageForm()

	context = {
		'form': form,
		'voyage_instance': voyage_instance,
	}

	return render(request, 'manage_voyages.html', context)

def manage_voyage_inlineformset(request,pk):
	voyage=Voyage.objects.get(pk=pk)
	VoyageInlineFormset=inlineformset_factory(Voyage,VoyageDates,fields='__all__')

	# If this is a POST request then process the Form data
	if request.method == 'POST':

		# Create a form instance and populate it with data from the request (binding):
		form = VoyageForm(request.POST)

		# Check if the form is valid:
		'''if form.is_valid():
			# process the data in form.cleaned_data as required (here we just write it to the model due_back field)
			book_instance.due_back = form.cleaned_data['renewal_date']
			book_instance.save()

			# redirect to a new URL:
			return HttpResponseRedirect(reverse('all-borrowed') )'''

	# If this is a GET (or any other method) create the default form.
	else:
		#proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
		formset = VoyageInlineFormset(instance=voyage)

	context = {
		'formset': formset
	}

	return render(request, 'manage_voyages.html', context)