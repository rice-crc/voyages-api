from django.shortcuts import render
from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import generics
from rest_framework.metadata import SimpleMetadata
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from voyages3.localsettings import REDIS_HOST,REDIS_PORT,GEO_NETWORKS_BASE_URL,STATS_BASE_URL,DEBUG,USE_REDIS_CACHE
from common.reqs import autocomplete_req,post_req,get_fieldstats,paginate_queryset,clean_long_df
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, extend_schema_view
from drf_spectacular.types import OpenApiTypes
import urllib
import json
import requests
import time
from .models import *
from .serializers import *
import pprint
import redis
import hashlib
from common.static.Voyage_options import Voyage_options

redis_cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

def get_compiled_routes(request):
    network_name = request.GET.get('networkName')
    route_type = request.GET.get('routeType')
    names = ['trans', 'intra']
    if network_name is None or network_name not in names:
        return JsonResponse({
            "error":
                "Value of 'networkName' parameter should be in " + str(names)
        })
    route_types = ['port', 'regional']
    if route_type is None or route_type not in route_types:
        return JsonResponse({
            "error":
                f"Value of 'routeType' parameter should be in {route_types}"
        })
    fpath = os.path.join(settings.STATIC_ROOT, "maps/js", network_name,
                         route_type + "_routes.json")
    return HttpResponse(content=open(fpath, 'rb'),
                        content_type='application/json')

def get_timelapse_port_regions(_):
    # Generate a simple JSON that reports the broad regions.
    VoyageCache.load()
    regions = {
        'src': {
            pk: {
                'value': r.value,
                'name': r.name
            } for pk, r in list(VoyageCache.regions.items()) if r.parent == 1
        },
        'dst': {
            pk: {
                'value': r.value,
                'name': r.name
            } for pk, r in list(VoyageCache.broad_regions.items())
        }
    }
    return JsonResponse(regions)

class VoyageAnimation(generics.GenericAPIView):
	permission_classes=[IsAuthenticated]
	authentication_classes=[TokenAuthentication]
	@extend_schema(
		description="Port-over for the legacy timelapse feature. To be replaced in 2024.",
		request=TimeLapaseRequestSerializer,
		responses=TimeLapseResponseItemSerializer
	)
	def post(self,request):	
		st=time.time()
		print("TIMELAPSE+++++++\nusername:",request.auth.user)
		#VALIDATE THE REQUEST
		serialized_req = TimeLapaseRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)
		
		#AND ATTEMPT TO RETRIEVE A REDIS-CACHED RESPONSE
		if USE_REDIS_CACHE:
			srd=serialized_req.data
			hashdict={
				'req_name':str(self.request),
				'req_data':srd
			}
			hashed=hashlib.sha256(json.dumps(hashdict,sort_keys=True,indent=1).encode('utf-8')).hexdigest()
			cached_response = redis_cache.get(hashed)
		else:
			cached_response=None
		
		#RUN THE QUERY IF NOVEL, RETRIEVE IT IF CACHED
		if cached_response is None:
			#FILTER THE VOYAGES BASED ON THE REQUEST'S FILTER OBJECT
			queryset=Voyage.objects.all()
			queryset,results_count=post_req(
				queryset,
				self,
				request,
				Voyage_options,
				auto_prefetch=True
			)
			#MAKE THE CROSSTABS REQUEST TO VOYAGES-STATS
			ids=[i[0] for i in queryset.values_list('id')]
			u2=STATS_BASE_URL+'timelapse/'
			params=dict(request.data)
			stats_req_data=params
			stats_req_data['ids']=ids
			stats_req_data['cachename']='timelapse'
			r=requests.post(url=u2,data=json.dumps(stats_req_data),headers={"Content-type":"application/json"})
			
			#VALIDATE THE RESPONSE
			if r.ok:
				j=json.loads(r.text)
				print(j[0])
				serialized_resp=TimeLapseResponseItemSerializer(data=j,many=True)
			if not serialized_resp.is_valid():
				return JsonResponse(serialized_resp.errors,status=400,safe=False)
			else:
				resp=serialized_resp.data
			#SAVE THIS NEW RESPONSE TO THE REDIS CACHE
			if USE_REDIS_CACHE:
				redis_cache.set(hashed,json.dumps(resp))			
		else:
			if DEBUG:
				print("cached:",hashed)
			resp=json.loads(cached_response)
		
		if DEBUG:
			print("Internal Response Time:",time.time()-st,"\n+++++++")
		
		return JsonResponse(resp,safe=False,status=200)

# 
# def get_results_map_animation(results, allow_no_numbers=False):
#     VoyageCache.load()
#     all_voyages = VoyageCache.voyages
# 
#     keys = get_pks_from_haystack_results(results)
#     items = []
#     for pk in keys:
#         voyage = all_voyages.get(pk)
#         if voyage is None:
#             print("Missing voyage with PK" + str(pk))
#             continue
# 
#         def can_show(ph):
#             return ph is not None and (ph[0].show or ph[1].show)
# 
#         if ok_to_show_animation(voyage, can_show, allow_no_numbers):
#             # flag = VoyageCache.nations.get(voyage.ship_nat_pk) or ''
#             source = CachedGeo.get_hierarchy(voyage.emb_pk)
#             destination = CachedGeo.get_hierarchy(voyage.dis_pk)
#             items.append({
#                 "voyage_id": voyage.voyage_id,
#                 "src": voyage.emb_pk,
#                 "dst": voyage.dis_pk,
#                 "regsrc": source[1].pk,
#                 "bregsrc": source[2].pk,
#                 "bregdst": destination[2].pk,
#                 "embarked": voyage.embarked or 0,
#                 "disembarked": voyage.disembarked or 0,
#                 "year": voyage.year,
#                 "month": voyage.month,
#                 "ship_ton": voyage.ship_ton or 0,
#                 "nat_id": voyage.ship_nat_pk or 0,
#                 "ship_name": str(voyage.ship_name or ''),
#             })
#     return JsonResponse(items, safe=False)