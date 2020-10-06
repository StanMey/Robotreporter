from django.contrib import admin
from .models import Stocks, Articles, Observations

admin.site.register(Stocks)
admin.site.register(Observations)
admin.site.register(Articles)