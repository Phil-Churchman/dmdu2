from django.db import models
from django.contrib.auth.models import User
import json
from .validator import *

# Create your models here.

class Version(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default="default") 
    notes = models.TextField(max_length=2048, null=True, blank=True)
    archive = models.BooleanField(default=False)
    simple_view = models.BooleanField(default=False)
    value_1 = models.IntegerField(default=50)
    value_2 = models.IntegerField(default=50)
    value_3 = models.IntegerField(default=50)
    value_4 = models.IntegerField(default=50)
    value_5 = models.IntegerField(default=50)
    value_6 = models.IntegerField(default=50)
    value_7 = models.IntegerField(default=50)
    value_8 = models.IntegerField(default=50)
    value_9 = models.IntegerField(default=50)
    value_10 = models.IntegerField(default=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_user_name'),
        ]        
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"

class CurrentVersion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)
    version = models.ForeignKey(Version, on_delete=models.CASCADE, null=True, blank=True)
    state = models.CharField(max_length=50, default="/versions/")

class Method(models.Model):
    version = models.ForeignKey(Version, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50)
    index = models.CharField(max_length=3)
    description = models.CharField(max_length=1000, blank=True, null=True)
    long_description = models.CharField(max_length=10000, blank=True, null=True)
    links  = models.CharField(max_length=10000, blank=True, null=True, default="[]")
    dmdu = models.BooleanField(default=False)
    management = models.CharField(max_length=50, default="Undefined")
    process = models.CharField(max_length=50, default="Undefined")
    enabled = models.BooleanField(default=True)
    value_1 = models.IntegerField(default=0, validators=[pos_int, max_100])
    value_2 = models.IntegerField(default=0, validators=[pos_int, max_100])
    value_3 = models.IntegerField(default=0, validators=[pos_int, max_100])
    value_4 = models.IntegerField(default=0, validators=[pos_int, max_100])
    value_5 = models.IntegerField(default=0, validators=[pos_int, max_100])
    value_6 = models.IntegerField(default=0, validators=[pos_int, max_100])
    value_7 = models.IntegerField(default=0, validators=[pos_int, max_100])
    value_8 = models.IntegerField(default=0, validators=[pos_int, max_100])
    value_9 = models.IntegerField(default=0, validators=[pos_int, max_100])
    value_10 = models.IntegerField(default=0, validators=[pos_int, max_100])    

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['version', 'index'], name='unique_version_index'),
            models.UniqueConstraint(fields=['version', 'name'], name='unique_version_name'),
        ]
        ordering = ["name"]

class Master(models.Model):
    ref = models.CharField(max_length=10, default="default", unique = True)
    methods = models.CharField(max_length=10000, blank=True, null=True)
    lookup = models.CharField(max_length=1000, blank=True, null=True)

class Lookup(models.Model):
    version = models.ForeignKey(Version, on_delete=models.CASCADE, null=True, blank=True)
    value_1 = models.CharField(max_length=1000, blank=True, null=True, default="NONE")
    value_1_is_option_reqt = models.BooleanField(default=True)
    value_2 = models.CharField(max_length=1000, blank=True, null=True, default="NONE")
    value_2_is_option_reqt = models.BooleanField(default=True)
    value_3 = models.CharField(max_length=1000, blank=True, null=True, default="NONE")
    value_3_is_option_reqt = models.BooleanField(default=True)
    value_4 = models.CharField(max_length=1000, blank=True, null=True, default="NONE")
    value_4_is_option_reqt = models.BooleanField(default=True)
    value_5 = models.CharField(max_length=1000, blank=True, null=True, default="NONE")
    value_5_is_option_reqt = models.BooleanField(default=True)
    value_6 = models.CharField(max_length=1000, blank=True, null=True, default="NONE")
    value_6_is_option_reqt = models.BooleanField(default=True)
    value_7 = models.CharField(max_length=1000, blank=True, null=True, default="NONE")
    value_7_is_option_reqt = models.BooleanField(default=True)
    value_8 = models.CharField(max_length=1000, blank=True, null=True, default="NONE")
    value_8_is_option_reqt = models.BooleanField(default=True)
    value_9 = models.CharField(max_length=1000, blank=True, null=True, default="NONE")
    value_9_is_option_reqt = models.BooleanField(default=True)
    value_10 = models.CharField(max_length=1000, blank=True, null=True, default="NONE")
    value_10_is_option_reqt = models.BooleanField(default=True)