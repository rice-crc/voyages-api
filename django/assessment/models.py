from django.db import models
from geo.models import Place

class ExportArea(Place):
	"""
	Class represents Export area entity.
	"""
	order_num = models.IntegerField()
	show_at_zoom = models.IntegerField()
	show_on_map = models.BooleanField()

class ExportRegion(Place):
	"""
	Class represents Export region entity.
	"""
	order_num = models.IntegerField()
	show_at_zoom = models.IntegerField()
	show_on_map = models.BooleanField()
	export_area = models.ForeignKey(ExportArea, on_delete=models.CASCADE)


class ImportArea(Place):
	"""
	Class represents Import area entity.
	"""
	order_num = models.IntegerField()
	show_at_zoom = models.IntegerField()
	show_on_map = models.BooleanField()


class ImportRegion(Place):
	"""
	Class represents Import region entity.
	"""
	order_num = models.IntegerField()
	show_at_zoom = models.IntegerField()
	show_on_map = models.BooleanField()
	import_area = models.ForeignKey(ImportArea, on_delete=models.CASCADE)


class Nation(Place):
	order_num = models.IntegerField()

class Estimate(models.Model):
	"""
	Class represents Estimate entity
	"""
	nation = models.ForeignKey(Nation, on_delete=models.CASCADE)
	year = models.IntegerField()
	embarkation_region = models.ForeignKey(
		ExportRegion, null=True, blank=True, on_delete=models.CASCADE)
	disembarkation_region = models.ForeignKey(
		ImportRegion, null=True, blank=True, on_delete=models.CASCADE)
	embarked_slaves = models.FloatField(null=True, blank=True)
	disembarked_slaves = models.FloatField(null=True, blank=True)