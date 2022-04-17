from django.db import models
# Create your models here.

	
class InputRestore(models.Model):
	img = models.ImageField(upload_to = "UWIE/static/Input/MIP/")
	def __str__(self):
		return self.img

class InputEnhance(models.Model):
	img = models.ImageField(upload_to = "UWIE/static/Input/RGHS/")
	def __str__(self):
		return self.img

class InputClassify(models.Model):
	img = models.ImageField(upload_to = "UWIE/static/Input/CLASSIFY/")
	def __str__(self):
		return self.img