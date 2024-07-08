from django.contrib import admin
from .models import Items
# Register your models here.

admin.site.site_header="A-Z Easy shopping "
admin.site.index_title="Manage easy shopping"
class ItemAdmin(admin.ModelAdmin):
    list_display=('Name','price','desc')
    search_fields=('Name',)
    def set_price_to_zero(self,request,queryset):
        queryset.update(price=0)
    actions=(set_price_to_zero,)
    list_editable=('price','desc')


admin.site.register(Items,ItemAdmin)