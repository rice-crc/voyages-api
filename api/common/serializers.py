from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
import pprint
import gc

class SparseDateSerializer(serializers.ModelSerializer):
	class Meta:
		model=SparseDate
		fields='__all__'