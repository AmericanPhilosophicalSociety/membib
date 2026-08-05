from django.contrib import admin

from .models import Subject, Member, Creator, Publication, Edition


admin.site.register(Subject)
admin.site.register(Member)
admin.site.register(Creator)
admin.site.register(Publication)
admin.site.register(Edition)
