from django.db import models
from datetime import datetime
from django.utils import timezone


class Request(models.Model):
	date = models.DateTimeField('date requested')
	status = models.CharField(max_length=10)

	#Prevents requests from saving without the date
	def save(self, *args, **kwargs):
		if self.date is None:
			self.date = timezone.now()
		super(self.__class__, self).save(*args, **kwargs)
		
class Species(models.Model):
	name = models.CharField(max_length=200)

class Request_Species(models.Model):
	request = models.ForeignKey(Request)
	species = models.ForeignKey(Species)

class CachedURL(models.Model):
    species = models.CharField(max_length = 300)
    database = models.CharField(max_length = 100)
    url = models.CharField(max_length = 500)
    date = models.DateTimeField(default=timezone.now)

class ImageDataBase(models.Model):
	name = models.CharField(max_length = 200)

class QueryForm(models.Model):
	name = models.CharField(max_length = 200)

class QueryHistory(models.Model):
	form_source = models.ForeignKey(QueryForm)
	created = models.DateTimeField(default=timezone.now)
	query_string = models.TextField()

class LocalImage(models.Model):
	url = models.CharField(max_length = 500)
	local_file_name = models.CharField(max_length = 200)
	last_modified = models.DateTimeField(default=timezone.now)


