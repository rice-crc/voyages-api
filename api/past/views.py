from django.shortcuts import render
from django.db.models import Q,Prefetch
from django.http import HttpResponse, JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import generics
from rest_framework.metadata import SimpleMetadata
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
import urllib
import json
import requests
import time
from .models import *
from .serializers import *
import pprint
from common.nest import *
from common.reqs import *
import collections
# 
# 
# class SingleEnslaved(generics.GenericAPIView):
# 	def get(self,request,enslaved_id):
# 		enslaved_record=Enslaved.objects.get(pk=enslaved_id)
# 		serialized=EnslavedSerializer(enslaved_record,many=False).data
# 		return JsonResponse(serialized,safe=False)
# 
# class SingleEnslavedVar(TemplateView):
# 	template_name='singlevar.html'
# 	def get(self,request,enslaved_id,varname):
# 		enslaved_options=options_handler('past/enslaved_options.json',hierarchical=False)
# 		enslaved_record=Enslaved.objects.get(pk=enslaved_id)
# 		serialized=EnslavedSerializer(enslaved_record,many=False).data
# 		keychain=varname.split('__')
# 		bottomval=bottomout(serialized,list(keychain))
# 		var_options=enslaved_options[varname]
# 		data={
# 			'enslaved_id':enslaved_id,
# 			'variable_api_name':varname,
# 			'variable_label':var_options['flatlabel'],
# 			'variable_type':var_options['type'],
# 			'variable_value':bottomval
# 		}
# 		context = super(SingleEnslavedVar, self).get_context_data()
# 		context['data']=data
# 		return context
# 

#LONG-FORM TABULAR ENDPOINT. 

class EnslavedList(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
# 	serializer_class=EnslavedSerializer
	def options(self,request):
		j=options_handler('past/enslaved_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		st=time.time()
		times=[]
		labels=[]
		print("ENSLAVED LIST+++++++\nusername:",request.auth.user)
		print("FETCHING...")
# 		try:
		enslaved_options=options_handler('past/enslaved_options.json',hierarchical=False)
		queryset=Enslaved.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,enslaved_options,auto_prefetch=True)
		if len(error_messages)==0:
			headers={"next_uri":next_uri,"prev_uri":prev_uri,"total_results_count":results_count}
			read_serializer=EnslavedSerializer(queryset,many=True)
			serialized=read_serializer.data
		
			outputs=[]
	
			hierarchical=request.POST.get('hierarchical')
			if str(hierarchical).lower() in ['false','0','f','n']:
				hierarchical=False
			else:
				hierarchical=True
	
			if hierarchical==False:
		
				for s in serialized:
					d={}
					for selected_field in selected_fields:
						keychain=selected_field.split('__')
						bottomval=bottomout(s,list(keychain))
						d[selected_field]=bottomval
					outputs.append(d)
			else:
				outputs=serialized
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(outputs,safe=False,headers=headers)
		else:
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=500)
# 		except:
# 			return JsonResponse({'status':'false','message':'bad request'}, status=400)

# #This will only accept one field at a time
# #Should only be a text field
# #And it will only return max 10 results
# #It will therefore serve as an autocomplete endpoint
# #I should make all text queries into 'or' queries
# class EnslavedTextFieldAutoComplete(generics.GenericAPIView):
# 	authentication_classes=[TokenAuthentication]
# 	permission_classes=[IsAuthenticated]				
# 	def post(self,request):
# 		print("+++++++\nusername:",request.auth.user)
# 		try:
# 			st=time.time()
# 			params=dict(request.POST)
# 			acfieldparam=next(iter(params))
# 			v=params[acfieldparam][0]
# 			print("past/enslaved/autocomplete",acfieldparam,v)
# 			klist=acfieldparam.split(',')
# 			def flattenthis(l):
# 				fl=[]
# 				for i in l:
# 					if type(i)==tuple:
# 						for e in i:
# 							fl.append(e)
# 					else:
# 						fl.append(i)
# 				return fl
# 			retrieve_all=True
# 			total_results_count=0
# 			fetchcount=20
# 			candidates=[]
# 			for k in klist:
# 				#print(k)
# 				queryset=Enslaved.objects.all()
# 				#print("------->",k,v,re.sub("\\\\+","",v),"<---------")
# 				kwargs={'{0}__{1}'.format(k, 'icontains'):v}
# 				queryset=queryset.filter(**kwargs)
# 				queryset=queryset.prefetch_related(k)
# 				queryset=queryset.order_by(k)
# 				total_results_count+=queryset.count()
# 				vals=[]
# 				for v in queryset.values_list(k).iterator():
# 					if v not in vals:
# 						vals.append(v)
# 					if len(vals)>=fetchcount:
# 						break
# 				candidates += [i for i in flattenthis(l=vals)]
# 			val_list=[sorted(candidates)][:fetchcount]
# 			output_dict={
# 				"results":val_list,
# 				"total_results_count":total_results_count
# 			}
# 			print("Internal Response Time:",time.time()-st,"\n+++++++")
# 			return JsonResponse(output_dict,safe=False)
# 		except:
# 			print("failed\n+++++++")
# 			return JsonResponse({'status':'false','message':'bad autocomplete request'}, status=400)
# 
# 
# class EnslaverTextFieldAutoComplete(generics.GenericAPIView):
# 	authentication_classes=[TokenAuthentication]
# 	permission_classes=[IsAuthenticated]
# 	def post(self,request):
# 		print("+++++++\nusername:",request.auth.user)
# 		try:
# 			st=time.time()
# 			params=dict(request.POST)
# 			acfieldparam=next(iter(params))
# 			v=params[acfieldparam][0]
# 			print("past/enslavers/autocomplete",acfieldparam,v)
# 			klist=acfieldparam.split(',')
# 			def flattenthis(l):
# 				fl=[]
# 				for i in l:
# 					if type(i)==tuple:
# 						for e in i:
# 							fl.append(e)
# 					else:
# 						fl.append(i)
# 				return fl
# 			retrieve_all=True
# 			total_results_count=0
# 			fetchcount=20
# 			candidates=[]
# 			for k in klist:
# 				#print(k)
# 				queryset=EnslaverIdentity.objects.all()
# 				#print("------->",k,v,re.sub("\\\\+","",v),"<---------")
# 				kwargs={'{0}__{1}'.format(k, 'icontains'):v}
# 				queryset=queryset.filter(**kwargs)
# 				queryset=queryset.prefetch_related(k)
# 				queryset=queryset.order_by(k)
# 				total_results_count+=queryset.count()
# 				vals=[]
# 				for v in queryset.values_list(k).iterator():
# 					if v not in vals:
# 						vals.append(v)
# 					if len(vals)>=fetchcount:
# 						break
# 				candidates += [i for i in flattenthis(l=vals)]
# 			val_list=[sorted(candidates)][:fetchcount]
# 			output_dict={
# 				"results":val_list,
# 				"total_results_count":total_results_count
# 			}
# 			print("Internal Response Time:",time.time()-st,"\n+++++++")
# 			return JsonResponse(output_dict,safe=False)
# 		except:
# 			print("failed\n+++++++")
# 			return JsonResponse({'status':'false','message':'bad autocomplete request'}, status=400)
# 
# 
# 

#LONG-FORM TABULAR ENDPOINT.
class EnslaverList(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
# 	serializer_class=EnslaverSerializer
	def options(self,request):
		j=options_handler('past/enslaver_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		print("ENSLAVER LIST+++++++\nusername:",request.auth.user)# 
# 		try:
		st=time.time()
		enslaver_options=options_handler('past/enslaver_options.json',hierarchical=False)
		queryset=EnslaverIdentity.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,enslaver_options,auto_prefetch=True)
		if len(error_messages)==0:
			headers={"next_uri":next_uri,"prev_uri":prev_uri,"total_results_count":results_count}
			read_serializer=EnslaverSerializer(queryset,many=True)
			serialized=read_serializer.data
	
			outputs=[]

			hierarchical=request.POST.get('hierarchical')
			if str(hierarchical).lower() in ['false','0','f','n']:
				hierarchical=False
			else:
				hierarchical=True

			if hierarchical==False:
	
				for s in serialized:
					d={}
					for selected_field in selected_fields:
						keychain=selected_field.split('__')
						bottomval=bottomout(s,list(keychain))
						d[selected_field]=bottomval
					outputs.append(d)
			else:
				outputs=serialized
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(outputs,safe=False,headers=headers)
		else:
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=500)
# 		except:
# 			return JsonResponse({'status':'false','message':'bad request'}, status=400)
# 
# Basic statistics
## takes a numeric variable
## returns its sum, average, max, min, and stdv
class EnslavedAggregations(generics.GenericAPIView):
# 	serializer_class=EnslavedSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		try:
			st=time.time()
			print("+++++++\nusername:",request.auth.user)
			params=dict(request.POST)
			aggregations=params.get('aggregate_fields')
			print("aggregations:",aggregations)
			queryset=Enslaved.objects.all()
			enslaved_options=options_handler('past/enslaved_options.json',hierarchical=False)
			aggregation,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,enslaved_options,retrieve_all=True)
			output_dict={}
			if len(error_messages)==0:
				for a in aggregation:
					for k in a:
						v=a[k]
						fn=k.split('__')[-1]
						varname=k[:-len(fn)-2]
						if varname in output_dict:
							output_dict[varname][fn]=a[k]
						else:
							output_dict[varname]={fn:a[k]}
				print("Internal Response Time:",time.time()-st,"\n+++++++")
				return JsonResponse(output_dict,safe=False)
			else:
				print("failed\n+++++++")
				return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)
		except:
			return JsonResponse({'status':'false','message':'bad request'}, status=400)
# 
# #DATAFRAME ENDPOINT (experimental & a resource hog!)
# class EnslavedDataFrames(generics.GenericAPIView):
# # 	serializer_class=EnslavedSerializer
# 	authentication_classes=[TokenAuthentication]
# 	permission_classes=[IsAuthenticated]
# 	def options(self,request):
# 		j=options_handler('past/enslaved_options.json',request)
# 		return JsonResponse(j,safe=False)
# 	def post(self,request):
# 		
# 		print("+++++++\nusername:",request.auth.user)
# 		enslaved_options=options_handler('past/enslaved_options.json',hierarchical=False)
# 		try:
# 			st=time.time()
# 			params=dict(request.POST)
# 			retrieve_all=True
# 			if 'results_per_page' in params:
# 				retrieve_all=False
# 			queryset=Enslaved.objects.all()
# 			queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,enslaved_options,auto_prefetch=False,retrieve_all=retrieve_all,selected_fields_exception=True)
# 			if len(error_messages)==0:
# 				headers={"next_uri":next_uri,"prev_uri":prev_uri,"total_results_count":results_count}
# 			
# 				serialized=EnslavedSerializer(queryset,many=True,selected_fields=selected_fields)
# 			
# 				serialized=serialized.data
# 				output_dicts={}
# 				for selected_field in sf:
# 					keychain=selected_field.split('__')
# 					for s in serialized:
# 						bottomval=bottomout(s,list(keychain))
# 						if selected_field in output_dicts:
# 							output_dicts[selected_field].append(bottomval)
# 						else:
# 							output_dicts[selected_field]=[bottomval]
# 				print("Internal Response Time:",time.time()-st,"\n+++++++")
# 				return JsonResponse(output_dicts,safe=False,headers=headers)
# 			else:
# 				print("failed\n+++++++")
# 				return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)
# 		except:
# 			return JsonResponse({'status':'false','message':'bad request'}, status=400)
# 
# # Basic statistics
# ## takes a numeric variable
# ## returns its sum, average, max, min, and stdv
class EnslaverAggregations(generics.GenericAPIView):
# 	serializer_class=EnslaverSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		st=time.time()
		print("+++++++\nusername:",request.auth.user)
		try:
			enslaver_options=options_handler('past/enslaver_options.json',hierarchical=False)
			params=dict(request.POST)
			aggregations=params.get('aggregate_fields')
			print("aggregations:",aggregations)
			queryset=EnslaverIdentity.objects.all()
		
			aggregation,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,enslaver_options,retrieve_all=True)
			output_dict={}
			if len(error_messages)==0:
				for a in aggregation:
					for k in a:
						v=a[k]
						fn=k.split('__')[-1]
						varname=k[:-len(fn)-2]
						if varname in output_dict:
							output_dict[varname][fn]=a[k]
						else:
							output_dict[varname]={fn:a[k]}
				print("Internal Response Time:",time.time()-st,"\n+++++++")
				return JsonResponse(output_dict,safe=False)
			else:
				print("failed\n+++++++")
				return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)
		except:
			return JsonResponse({'status':'false','message':'bad request'}, status=400)