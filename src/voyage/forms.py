from django.db import models
from django.forms import ModelForm
from .models import *

class VoyageForm(ModelForm):
	class Meta:
		model=Voyage
		fields='__all__'

