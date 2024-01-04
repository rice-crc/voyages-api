from django.urls import path,include
from . import views

urlpatterns = [
	path('',views.SourceList.as_view()),
	path('GENERIC/',views.SourceListGENERIC.as_view()),
	path('shortref/CREATE/',views.ShortRefCREATE.as_view()),
	path('shortref/<str:name>',views.ShortRefRETRIEVE.as_view()),
	path('shortref/UPDATE/<str:name>',views.ShortRefUPDATE.as_view()),
	path('shortref/DESTROY/<str:name>',views.ShortRefDESTROY.as_view()),
	path('CREATE/',views.SourceCREATE.as_view()),
	path('<int:id>',views.SourceRETRIEVE.as_view()),
	path('UPDATE/<int:id>',views.SourceUPDATE.as_view()),
	path('DESTROY/<int:id>',views.SourceDESTROY.as_view()),
# 	path('page/CREATE/',views.PageCREATE.as_view()),
# 	path('SHORTREF/GET/<str:name>',views.ShortRefGET.as_view()),
	path('gallery',views.Gallery),
	path('gallery/<int:collection_id>',views.Gallery,name="gallery"),
	path('gallery/<int:collection_id>/<int:pagenumber>',views.Gallery,name="gallery"),
	path('gallery/single/',views.source_page,name="source_page"),
	path('gallery/single/<int:source_id>',views.source_page,name="source_page")
]
