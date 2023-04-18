from __future__ import unicode_literals

from builtins import str

from django.db import models

class NamedModelAbstractBase(models.Model):
	name = models.CharField(max_length=255,blank=False,null=False)
	def __str__(self):
		return self.name
	class Meta:
		abstract = True
		
class Route(models.Model):
	"""
	Route json store
	"""
	source=models.ForeignKey(
		'Place',
		verbose_name="Alice",
		null=False,
		on_delete=models.CASCADE,
		related_name='sourceofroute'
	)
	target=models.ForeignKey(
		'Place',
		verbose_name="Bob",
		null=False,
		on_delete=models.CASCADE,
		related_name='targetofroute'
	)
	dataset= models.IntegerField(
		"Dataset",
		null=False,
		blank=False
	)
	shortest_route=models.JSONField(
		"Endpoint to endpoint route",
		null=True
	)
	class Meta:
		unique_together=(['source','target','dataset'])
		verbose_name = "Route"
		verbose_name_plural = "Routes"

class Adjacency(models.Model):
	"""
	Simplified network linkages -- simple a/b connections
	"""
	source=models.ForeignKey(
		'Place',
		verbose_name="Alice",
		null=False,
		on_delete=models.CASCADE,
		related_name='sourceof'
	)
	target=models.ForeignKey(
		'Place',
		verbose_name="Bob",
		null=False,
		on_delete=models.CASCADE,
		related_name='targetof'
	)
	dataset= models.IntegerField(
		"Dataset",
		null=True
	)
	
	distance=models.DecimalField(
		"Distance",
		null=True,
		blank=True,
		max_digits=8,
		decimal_places=5
	)
	
	class Meta:
		unique_together=(['source','target','dataset'])
		verbose_name = "Location Adjacency"
		verbose_name_plural = "Location Adjacencies"

# Voyage Regions and Places
class LocationType(NamedModelAbstractBase):
	"""
	Geographic Location Type
	We will default to points, but open up onto a polygons model for when we want to show countries etc
	"""
	class Meta:
		verbose_name = "Geographic Location Type"
		verbose_name_plural = "Geographic Location Types"

# Voyage Regions and Places
class Place(models.Model):
	"""
	Place. Unifying:
		* Ports, Regions, Broad Regions
		* Import Areas, Export Areas
		* Geo-coded language groups
		* Places of birth, death, origin, last-known locations
	"""
	longitude = models.DecimalField(
		"Longitude of Centroid",
		max_digits=10,
		decimal_places=7,
		null=True,
		blank=True
	)
	latitude = models.DecimalField(
		"Latitude of Centroid",
		max_digits=10,
		decimal_places=7,
		null=True,
		blank=True
	)
	
	child_of = models.ForeignKey(
		'self',
		null=True,
		on_delete=models.CASCADE,
		related_name='parent_of'
	)
	
	location_type = models.ForeignKey(
		'LocationType',
		verbose_name="Location Type",
		null=True,
		on_delete=models.CASCADE,
		related_name='type_location'
	)
	
	spatial_extent = models.JSONField(
		"Geojson Polygon",
		null=True
	)
	
	uid = models.IntegerField(null=False,blank=False,unique=True)

	class Meta:
		verbose_name = "Geographic Location"
		verbose_name_plural = "Geographic Locations"