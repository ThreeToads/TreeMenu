from django.contrib import admin
from .models import Menu, MenuItem


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    fields = (
        'title',
        'parent',
        'named_url',
        'url',
        'order',
    )
    show_change_link = True


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = (MenuItemInline,)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'menu',
        'parent',
        'order',
        'named_url',
        'url',
    )
    list_filter = ('menu',)
    search_fields = (
        'title',
        'named_url',
        'url',
    )
