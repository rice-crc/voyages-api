Currently, the IIIF generation script has two modes:

1. regenerate all manifests
1. regenerate only those that lack manifests but have source page connections

Therefore in order to rebuild on a targeted collection, like OMNO (which is a common need), you'll have to flip the sources in that collection to not having a manifest. I'm working on a better fix but for the time being, here's that flip script.

	from document.models import *
	sources=Source.objects.all()
	clements_sources=sources.filter(short_ref__name__icontains="clement")
	clements_sources.count()
	for source in clements_sources:
		source.has_published_manifest=False
		source.save()
	
	
	from document.models import *
	sources=Source.objects.all()
	omno_sources=sources.filter(short_ref__name__icontains="OMNO")
	omno_sources.count()
	for source in omno_sources:
		source.has_published_manifest=True
		source.save()