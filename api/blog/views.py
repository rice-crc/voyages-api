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
from common.serializers import *

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




class PostTextFieldAutoComplete(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	queryset=Enslaved.objects.all()
	@extend_schema(
		description="The autocomplete endpoints provide paginated lists of values on fields related to the endpoints primary entity (here, the blog post). It also accepts filters.",
		request=autocompleterequestserializer,
		responses=autocompleteresponseserializer,
		examples = [
			OpenApiExample(
				'Autocomplete on any blog-related field',
				summary='Autocomplete for blog tags like "ma"',
				description='Here, we search blog tags for values like "ma". We request the first 10 of these.',
				value={
					"varname":"tags__name",
					"querystr":"ma",
					"limit":10,
					"offset":0,
					"filter":{}
				},
				request_only=True,
				response_only=False
			),
			OpenApiExample(
				'Suggested values are returned',
				summary='Autocomplete for blog tags like "ma"',
				description='Here, we see the first and only 2 blog tags that are like "ma"',
				value={
					"varname": "tags__name",
					"querystr": "ma",
					"offset": 0,
					"limit": 10,
					"filter": {},
					"suggested_values": [
						{
							"value": "Diaspora Maps"
						},
						{
							"value": "Introductory Maps"
						}
					]
				},
				request_only=False,
				response_only=True
			)
		]
	)
	def post(self,request):
		st=time.time()
		queryset=Post.objects.all()
		print("BLOG POST CHAR FIELD AUTOCOMPLETE+++++++\nusername:",request.auth.user)
		
		options=Post_options
		
		rdata=request.data

		varname=str(rdata.get('varname'))
		querystr=str(rdata.get('querystr'))
		offset=int(rdata.get('offset'))
		limit=int(rdata.get('limit'))
	
		max_offset=500
	
		if offset>max_offset:
			final_vals=[]
		else:
			queryset,selected_fields,results_count,error_messages=post_req(
				queryset,
				self,
				request,
				options,
				auto_prefetch=False,
				retrieve_all=True
			)
			final_vals=autocomplete_req(queryset,varname,querystr,offset,max_offset,limit)
		
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		
		resp=dict(rdata)
		resp['suggested_values']=final_vals
		
		read_serializer=autocompleteresponseserializer(resp)
		serialized=read_serializer.data
		
		return JsonResponse(serialized,safe=False)



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
