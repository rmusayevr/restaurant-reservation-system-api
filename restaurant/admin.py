from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Image, Restaurant, Table, Reservation


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
admin.site.register(Category)
admin.site.register(Image)
admin.site.register(Restaurant)
admin.site.register(Table)
admin.site.register(Reservation)
