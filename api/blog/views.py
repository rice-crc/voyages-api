from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import generics
import time
from rest_framework.metadata import SimpleMetadata
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.generic.list import ListView
from common.reqs import *
from .models import *
from .serializers import *
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

try:
	post_options=options_handler('blog/post_options.json',hierarchical=False)
except:
	print("WARNING. BLANK POST OPTIONS.")
	post_options={}

try:
	author_options=options_handler('blog/author_options.json',hierarchical=False)
except:
	print("WARNING. BLANK POST OPTIONS.")
	author_options={}
	
try:
	institution_options=options_handler('blog/institution_options.json',hierarchical=False)
except:
	print("WARNING. BLANK POST OPTIONS.")
	author_options={}

@extend_schema(exclude=True)
class PostList(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def options(self,request):
		j=options_handler('blog/post_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		print("VOYAGE LIST+++++++\nusername:",request.auth.user)
		queryset=Post.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(queryset,self,request,post_options,retrieve_all=False)
		if len(error_messages)==0:
			st=time.time()
			headers={"total_results_count":results_count}
			read_serializer=PostSerializer(queryset,many=True)
			serialized=read_serializer.data
			resp=JsonResponse(serialized,safe=False,headers=headers)
			resp.headers['total_results_count']=headers['total_results_count']
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return resp
		else:
			print("failed\n+++++++")
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)
@extend_schema(exclude=True)
class PostTextFieldAutoComplete(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		print("POST LIST+++++++\nusername:",request.auth.user)
# 		try:
		st=time.time()
		params=dict(request.POST)
		params=dict(request.POST)
		k=list(params.keys())[0]
		v=params[k][0]
		
		print("past/enslavers/autocomplete",k,v)
		queryset=Post.objects.all()
		if '__' in k:
			kstub='__'.join(k.split('__')[:-1])
			k_id_field=kstub+"__id"
			queryset=queryset.prefetch_related(kstub)
		else:
			k_id_field="id"
		kwargs={'{0}__{1}'.format(k, 'icontains'):v}
		queryset=queryset.filter(**kwargs)
		queryset=queryset.order_by(k)
		total_results_count=queryset.count()
		candidates=[]
		candidate_vals=[]
		fetchcount=30
		## Have to use this ugliness b/c we're not in postgres
		## https://docs.djangoproject.com/en/4.2/ref/models/querysets/#django.db.models.query.QuerySet.distinct
		for v in queryset.values_list(k_id_field,k).iterator():
			if v[1] not in candidate_vals:
				candidates.append(v)
				candidate_vals.append(v[1])
			if len(candidates)>=fetchcount:
				break
		res={
			"total_results_count":total_results_count,
			"results":[
				{
					"id":c[0],
					"label":c[1]
				} for c in candidates
			]
		}
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		return JsonResponse(res,safe=False)
@extend_schema(exclude=True)
class AuthorList(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def options(self,request):
		j=options_handler('blog/author_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		print("AUTHOR LIST+++++++\nusername:",request.auth.user)
		queryset=Author.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(queryset,self,request,author_options,retrieve_all=False)
		if len(error_messages)==0:
			st=time.time()
			headers={"total_results_count":results_count}
			read_serializer=AuthorSerializer(queryset,many=True)
			serialized=read_serializer.data
			resp=JsonResponse(serialized,safe=False,headers=headers)
			resp.headers['total_results_count']=headers['total_results_count']
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return resp
		else:
			print("failed\n+++++++")
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)
@extend_schema(exclude=True)
class InstitutionList(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def options(self,request):
		j=options_handler('blog/institution_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		print("INSTITUTION LIST+++++++\nusername:",request.auth.user)
		queryset=Institution.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(queryset,self,request,institution_options,retrieve_all=False)
		if len(error_messages)==0:
			st=time.time()
			headers={"total_results_count":results_count}
			read_serializer=InstitutionSerializer(queryset,many=True)
			serialized=read_serializer.data
			resp=JsonResponse(serialized,safe=False,headers=headers)
			resp.headers['total_results_count']=headers['total_results_count']
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return resp
		else:
			print("failed\n+++++++")
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)
