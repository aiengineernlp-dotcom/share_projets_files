from multiprocessing.resource_tracker import register
from .models import Item
from django.contrib import admin

# Register your models here.
admin.site.register(Item)