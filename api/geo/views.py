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
from .models import *

class GeoTree(generics.GenericAPIView):
	# serializer_class=VoyageSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		st=time.time()
		print("GEO TREE+++++++\nusername:",request.auth.user)
		broadregions=Location.objects.all().filter(location_type__name='Broad Region')
		regions=Location.objects.all().filter(location_type__name='Region')
		places=Location.objects.all().filter(location_type__name='Place')
		
		locationtree=[]
		
		def locationdict(l):
			ld={
				'id':l.id,
				'name':l.name,
				'longitude':l.longitude,
				'latitude':l.latitude,
				'value':l.value
			}
			return ld
		
		for br in broadregions:
			brdict=locationdict(br)
			brdict['children']=[]
			childregions=regions.filter(child_of=br)
			for cr in childregions:
				crdict=locationdict(cr)
				childplaces=places.filter(child_of=cr)
				crdict['children']=[locationdict(p) for p in childplaces]
				brdict['children'].append(crdict)
			locationtree.append(brdict)
		
		resp=JsonResponse(locationtree,safe=False)
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		return resp