from django.contrib import admin

# Register your models here.

from .models import *

# admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Tag)
admin.site.register(Order)
# admin.site.register(User_Balance)

class CustomerAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ['name', 'email', 'phone', 'date_created']
    list_filter = ['name', 'email', 'phone', 'date_created']
    
admin.site.register(Customer, CustomerAdmin)