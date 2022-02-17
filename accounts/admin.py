from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Tag)
admin.site.register(Order)
# admin.site.register(User_Balance)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'balance')
    
admin.site.register(User_Balance, CustomerAdmin)