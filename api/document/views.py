from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.template import loader
from django.shortcuts import redirect,render
from django.core.paginator import Paginator
from document.models import *
import re
from django.db.models import Q


#######################
# default view will be a paginated gallery
def index(request,collection_id=None,pagenumber=1):
	
	if request.user.is_authenticated:
		
		#let's only get the zotero objects that have pages
		#otherwise, no need for the gallery -- and it lards the gallery up
		docs=ZoteroSource.objects.all().filter(~Q(page_connection=None))
		
		other_collections=[]
		for collection_tuple in docs.values_list(
			"legacy_source__id",
			"legacy_source__short_ref"
		).distinct():
			
			this_collection_id,this_collection_label=collection_tuple
			
			if this_collection_id==collection_id:
				page_collection_label=this_collection_label
				page_collection_id=this_collection_id
			else:
				other_collections.append({
					"id":this_collection_id,
					"label":this_collection_label
				})
			
		if collection_id is None:
			
			page_collection_id=min(docs.values_list('legacy_source__id'))[0]
			
			page_collection_label=docs.filter(legacy_source__id=page_collection_id).first().legacy_source.short_ref
			
		docs=docs.filter(legacy_source__id=collection_id).distinct()
		docs=docs.order_by('id')
		docs_paginator=Paginator(docs, 12)
		this_page=docs_paginator.get_page(pagenumber)
		
# 		print(other_collections)
		
		return render(
			request,
			"gallery.html",
			{
				"page_obj": this_page,
				"other_collections":other_collections,
				"page_collection_label":page_collection_label,
				"page_collection_id":page_collection_id
			}
		)
	else:
		return HttpResponseForbidden("Forbidden")
		

#######################
# then the individual page view
def z_source_page(request,zotero_source_id=1):
	
	if request.user.is_authenticated:
# 		print(zotero_source_id)
		doc=ZoteroSource.objects.get(id=zotero_source_id)
		
# 		print(doc)
		return render(request, "single_doc.html", {'zs':doc})
	else:
		return HttpResponseForbidden("Forbidden")