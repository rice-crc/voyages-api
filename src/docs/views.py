from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import generics
from rest_framework.metadata import SimpleMetadata
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.generic.list import ListView
from collections import Counter
import networkx as nx
import urllib
import json
import requests
import time
from .models import *
import pprint
from tools.nest import *
from tools.reqs import *
import collections
import gc
from .serializers import *
from voyages2021.localsettings import *

pp = pprint.PrettyPrinter(indent=4)

try:
	doc_options=options_handler('docs/doc_options.json',hierarchical=False)
except:
	print("WARNING. BLANK DOCS OPTIONS.")
	doc_options={}


#LONG-FORM TABULAR ENDPOINT. PAGINATION IS A NECESSITY HERE!
##HAVE NOT YET BUILT IN ORDER-BY FUNCTIONALITY
class DocList(generics.GenericAPIView):
	serializer_class=DocSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def options(self,request):
		j=options_handler('docs/doc_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		print("+++++++\nusername:",request.auth.user)
		queryset=Doc.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,doc_options,auto_prefetch=True)
		if len(error_messages)==0:
			st=time.time()
			headers={"next_uri":next_uri,"prev_uri":prev_uri,"total_results_count":results_count}
			read_serializer=DocSerializer(queryset,many=True)
			serialized=read_serializer.data
			#if the user hasn't selected any fields (default), then get the fully-qualified var names as the full list
			if selected_fields==[]:
				selected_fields=list(doc_options.keys())
			else:
				selected_fields=[i for i in selected_fields if i in list(doc_options.keys())]
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
						#In this flattened view, the reverse relationship breaks the references to the outcome variables in the serializer
						#not badly -- you just get some repeat, nested data -- but that's unhelpful
						#The fix will be to make it a through table relationship
						keychain=selected_field.split('__')
						bottomval=bottomout(s,list(keychain))
						d[selected_field]=bottomval
					outputs.append(d)
			else:
				outputs=serialized
			
			resp=JsonResponse(outputs,safe=False,headers=headers)
			resp.headers['total_results_count']=headers['total_results_count']
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return resp
		else:
			print("failed\n+++++++")
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)
