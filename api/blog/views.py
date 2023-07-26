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

try:
	post_options=options_handler('post/post_options.json',hierarchical=False)
except:
	print("WARNING. BLANK POST OPTIONS.")
	post_options={}

class PostList(generics.GenericAPIView):
	# serializer_class=VoyageSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def options(self,request):
		j=options_handler('blog/post_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		print("VOYAGE LIST+++++++\nusername:",request.auth.user)
		queryset=Post.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,post_options,retrieve_all=False)
		if len(error_messages)==0:
			st=time.time()
			headers={"next_uri":next_uri,"prev_uri":prev_uri,"total_results_count":results_count}
			read_serializer=PostSerializer(queryset,many=True)
			serialized=read_serializer.data
			resp=JsonResponse(serialized,safe=False,headers=headers)
			resp.headers['total_results_count']=headers['total_results_count']
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return resp
		else:
			print("failed\n+++++++")
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)
