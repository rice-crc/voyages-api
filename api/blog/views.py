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
from common.static.Institution_options import Institution_options
from common.static.Post_options import Post_options
from common.static.Author_options import Author_options


class PostList(generics.GenericAPIView):
	'''
	The Voyages team launched its new blog interface in 2022, in order to allow for richer humanities content to be integrated into the site, and to allow for more rapid publication of project-related news.
	
	These blog posts come in 3 languages: English, Spanish, and Portuguese. The author writes in one language, and when they are posted, the text is sent to the Google Translate API. The translated content is then published as three separate posts. This allows the team to go back in and fine-tune translations. The output format is HTML.
	
	Blog posts also contain hyperlinks to images hosted by SlaveVoyages for making the posts visually appealing.
	'''
	serializer_class=PostSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		print("BLOG POST LIST+++++++\nusername:",request.auth.user)
		queryset=Post.objects.all()
		params=dict(request.data)
		queryset,selected_fields,results_count,error_messages=post_req(
			queryset,self,request,Post_options,retrieve_all=True
		)
		print(len(queryset))
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
		print("BLOG AUTOCOMPLETE+++++++\nusername:",request.auth.user)
# 		try:
		st=time.time()
		params=dict(request.data)
		k=list(params.keys())[0]
		v=params[k][0]
		print("past/enslavers/autocomplete",k,v)
		queryset=Post.objects.all()
		if '__' in k:
			kstub='__'.join(k.split('__')[:-1])
			queryset=queryset.prefetch_related(kstub)
		kwargs={'{0}__{1}'.format(k, 'icontains'):v}
		queryset=queryset.filter(**kwargs)
		queryset=queryset.order_by(k)
		total_results_count=queryset.count()
		candidates=[]
		candidate_vals=[]
		fetchcount=30
		## Have to use this ugliness b/c we're not in postgres
		## https://docs.djangoproject.com/en/4.2/ref/models/querysets/#django.db.models.query.QuerySet.distinct
		for v in queryset.values_list(k).iterator():
			if v[1] not in candidate_vals:
				candidates.append(v)
				candidate_vals.append(v[1])
			if len(candidates)>=fetchcount:
				break
		res={
			"total_results_count":total_results_count,
			"results":candidates
		}
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		return JsonResponse(res,safe=False)

class AuthorList(generics.GenericAPIView):
	'''
		Blog authors are allowed to add a user profile image, affiliate themselves with a university, and give a brief bio of themselves (under the "description") field.
		
		The posts authored by the author are included in the response as an array of nested objects.
	'''
	serializer_class=AuthorSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		print("AUTHOR LIST+++++++\nusername:",request.auth.user)
		queryset=Author.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(queryset,self,request,Author_options,retrieve_all=False)
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

class InstitutionList(generics.GenericAPIView):
	'''
		The institutions that the blog authors are affiliated with can be searched in their own right.
		
		The authors associated with these institutions are included as nested objects, and the posts by those authors are nested within these author objects.
	'''
	serializer_class=InstitutionSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		print("INSTITUTION LIST+++++++\nusername:",request.auth.user)
		queryset=Institution.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(
			queryset,self,request,Institution_options,retrieve_all=False
		)
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
