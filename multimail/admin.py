from django.contrib import admin
import models

class EmailAddressAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.EmailAddress, EmailAddressAdmin)
