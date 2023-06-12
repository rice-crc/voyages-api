from django.urls import path,include
from . import views

urlpatterns = [
	path('',views.index,name="index"),
	path('<int:collection_id>',views.index,name="index"),
	path('<int:collection_id>/<int:pagenumber>',views.index,name="index"),
	path('single',views.z_source_page,name="z_source_page"),
	path('single/<int:zotero_source_id>',views.z_source_page,name="z_source_page")
]
