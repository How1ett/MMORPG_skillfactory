from django.contrib import admin
from .models import Advertisement


class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ['title', 'content', 'author', 'time_create']
    list_filter = ('author', 'time_create')


admin.site.register(Advertisement, AdvertisementAdmin)
