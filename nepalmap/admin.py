from django.contrib import admin
from . models import District,Municipality,Province,City

# Register your models here.
admin.site.register(Province)
admin.site.register(District)
admin.site.register(Municipality)
admin.site.register(City)