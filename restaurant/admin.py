from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Image, Restaurant, 
    Table, Reservation, Map, WorkingTime, 
    OnlineReservTime, Tag, Cuisine, RestaurantType,
    MenuCategory, MenuCategoryProduct, Wishlist
)


class CustomerUserAdmin(UserAdmin):
    ordering = ('email',)
    list_display = ('email', )
    readonly_fields = ["date_joined"]
    add_fieldsets = (
        (None, {
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'phone_number'),
        }),
    )
    fieldsets = (
        (None, {
            'fields': ('email', 'first_name', 'last_name', 'password', 'phone_number', 'is_client'),
        }),
    )

admin.site.register(User, CustomerUserAdmin)
admin.site.register(Image)
admin.site.register(Restaurant)
admin.site.register(WorkingTime)
admin.site.register(OnlineReservTime)
admin.site.register(Table)
admin.site.register(Map)
admin.site.register(Tag)
admin.site.register(Cuisine)
admin.site.register(RestaurantType)
admin.site.register(Reservation)
admin.site.register(MenuCategory)
admin.site.register(MenuCategoryProduct)
admin.site.register(Wishlist)
