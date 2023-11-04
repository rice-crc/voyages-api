from django.urls import path,include
from . import views

urlpatterns = [
	path('',views.SourceList.as_view()),
	path('RUD/<int:id>',views.SourceRUD.as_view()),
	path('CREATE/',views.SourceCREATE.as_view()),
# 	path('page/CREATE/',views.PageCREATE.as_view()),
# 	path('SHORTREF/GET/<str:name>',views.ShortRefGET.as_view()),
	path('gallery',views.Gallery),
	path('gallery/<int:collection_id>',views.Gallery,name="gallery"),
	path('gallery/<int:collection_id>/<int:pagenumber>',views.Gallery,name="gallery"),
	path('gallery/single/',views.source_page,name="source_page"),
	path('gallery/single/<int:source_id>',views.source_page,name="source_page")
]
