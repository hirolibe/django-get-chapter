from django.contrib import admin

# Register your models here.
from .models import ChapterInfo, VideoInfo
admin.site.register(ChapterInfo)
admin.site.register(VideoInfo)