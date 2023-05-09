from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class NamedModelAbstractBase(models.Model):
	id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=255)

	def __str__(self):
		return self.__unicode__()

	def __unicode__(self):
		return str(self.id) + ", " + self.name

	class Meta:
		abstract = True

class SparseDate(models.Model):
	m = models.IntegerField(null=True,blank=False,validators=[MinValueValidator(1), MaxValueValidator(12)])
	d = models.IntegerField(null=True,blank=False,validators=[MinValueValidator(1), MaxValueValidator(31)])
	y = models.IntegerField(null=True,blank=False,validators=[MinValueValidator(1), MaxValueValidator(3000)])
	hh = models.IntegerField(null=True,blank=False,validators=[MinValueValidator(0), MaxValueValidator(23)])
	mm = models.IntegerField(null=False,blank=False,validators=[MinValueValidator(1), MaxValueValidator(60)])
	text=models.CharField(max_length=12, null=True, help_text="Date in MM,DD,YYYY format with optional fields.")
	
	def __str__(self):
		if self.mm is not None and self.hh is not None:
			tstr=':'.join(['00' if i is None else str(i) for i in [self.hh,self.mm]])
		else:
			tstr=[]
		
		def intbuffer(i):
			i=str(i)
			if len(i)==0 or i==None:
				return ''
			if len(i)==1:
				return '0'+i
			else:
				return i
		
		dstr=','.join([intbuffer(i) for i in [self.m,self.d,self.y]])
		return ' '.join([dstr,tstr])

	class Meta:
		unique_together=[['m','d','y'],['m','d','y','hh','mm']]