from django.urls import path,include
from . import views

urlpatterns = [
	path('',views.ZoteroSourceList.as_view()),
	path('gallery',views.Gallery),
	path('gallery/<int:collection_id>',views.Gallery,name="gallery"),
	path('gallery/<int:collection_id>/<int:pagenumber>',views.Gallery,name="gallery"),
	path('gallery/single',views.z_source_page,name="z_source_page"),
	path('gallery/single/<int:zotero_source_id>',views.z_source_page,name="z_source_page")
]
