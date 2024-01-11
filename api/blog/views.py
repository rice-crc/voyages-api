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
from common.serializers import autocompleterequestserializer, autocompleteresponseserializer

class PostList(generics.GenericAPIView):
	'''
	The Voyages team launched its new blog interface in 2022, in order to allow for richer humanities content to be integrated into the site, and to allow for more rapid publication of project-related news.
	
	These blog posts come in 3 languages: English, Spanish, and Portuguese. The author writes in one language, and when they are posted, the text is sent to the Google Translate API. The translated content is then published as three separate posts. This allows the team to go back in and fine-tune translations. The output format is HTML.
	
	Blog posts also contain hyperlinks to images hosted by SlaveVoyages for making the posts visually appealing.
	'''
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		request=PostListRequestSerializer,
		responses=PostListResponseSerializer
	)
	def post(self,request):
		print("BLOG POST LIST+++++++\nusername:",request.auth.user)
		
		#VALIDATE THE REQUEST
		serialized_req = PostListRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)
		
		#FILTER THE VOYAGES BASED ON THE REQUEST'S FILTER OBJECT
		queryset=Post.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Post_options,
			auto_prefetch=True
		)
		results,total_results_count,page_num,page_size=paginate_queryset(queryset,request)
		resp=PostListResponseSerializer({
			'count':total_results_count,
			'page':page_num,
			'page_size':page_size,
			'results':results
		}).data
		#I'm having the most difficult time in the world validating this nested paginated response
		#And I cannot quite figure out how to just use the built-in paginator without moving to urlparams
		return JsonResponse(resp,safe=False,status=200)

class PostTextFieldAutoComplete(generics.GenericAPIView):
	'''
	The autocomplete endpoints provide paginated lists of values on fields related to the endpoints primary entity (here, the blog post). It also accepts filters.
	'''
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		request=PostAutoCompleteRequestSerializer,
		responses=PostAutoCompleteResponseSerializer
	)
	def post(self,request):
		st=time.time()
		print("BLOG POST CHAR FIELD AUTOCOMPLETE+++++++\nusername:",request.auth.user)
		
		#VALIDATE THE REQUEST
		serialized_req = PostAutoCompleteRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)
		
		#FILTER THE VOYAGES BASED ON THE REQUEST'S FILTER OBJECT
		queryset=Post.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Post_options,
			auto_prefetch=False
		)
		
		#RUN THE AUTOCOMPLETE ALGORITHM
		final_vals=autocomplete_req(queryset,request)
		resp=dict(request.data)
		resp['suggested_values']=final_vals
		
		#VALIDATE THE RESPONSE
		serialized_resp=PostAutoCompleteResponseSerializer(data=resp)
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		if not serialized_resp.is_valid():
			return JsonResponse(serialized_resp.errors,status=400)
		else:
			return JsonResponse(serialized_resp.data,safe=False)



class AuthorList(generics.GenericAPIView):
	'''
		Blog authors are allowed to add a user profile image, affiliate themselves with a university, and give a brief bio of themselves (under the "description") field.
		
		The posts authored by the author are included in the response as an array of nested objects.
	'''
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		request=AuthorListRequestSerializer,
		responses=AuthorListResponseSerializer
	)
	def post(self,request):
		print("AUTHOR LIST+++++++\nusername:",request.auth.user)
		
		#VALIDATE THE REQUEST
		serialized_req = AuthorListRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)
		
		#FILTER THE VOYAGES BASED ON THE REQUEST'S FILTER OBJECT
		queryset=Author.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Author_options,
			auto_prefetch=True
		)
		results,total_results_count,page_num,page_size=paginate_queryset(queryset,request)
		resp=AuthorListResponseSerializer({
			'count':total_results_count,
			'page':page_num,
			'page_size':page_size,
			'results':results
		}).data
		#I'm having the most difficult time in the world validating this nested paginated response
		#And I cannot quite figure out how to just use the built-in paginator without moving to urlparams
		return JsonResponse(resp,safe=False,status=200)

class InstitutionList(generics.GenericAPIView):
	'''
		The institutions that the blog authors are affiliated with can be searched in their own right.
		
		The authors associated with these institutions are included as nested objects, and the posts by those authors are nested within these author objects.
	'''
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		request=InstitutionListRequestSerializer,
		responses=InstitutionListResponseSerializer
	)
	def post(self,request):
		print("INSTITUTION LIST+++++++\nusername:",request.auth.user)
		
		#VALIDATE THE REQUEST
		serialized_req = InstitutionListRequestSerializer(data=request.data)
		
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)
		
		#FILTER THE VOYAGES BASED ON THE REQUEST'S FILTER OBJECT
		queryset=Institution.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Institution_options,
			auto_prefetch=True
		)
		results,total_results_count,page_num,page_size=paginate_queryset(queryset,request)
		resp=InstitutionListResponseSerializer({
			'count':total_results_count,
			'page':page_num,
			'page_size':page_size,
			'results':results
		},read_only=True).data
		#I'm having the most difficult time in the world validating this nested paginated response
		#And I cannot quite figure out how to just use the built-in paginator without moving to urlparams
		return JsonResponse(resp,safe=False,status=200)
