from django.contrib import admin
from .models import Area, User, BoxType, DocType, Box, Documentation

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'area')
    list_filter = ('role', 'area')

@admin.register(BoxType)
class BoxTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(DocType)
class DocTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('box_type', 'description')

@admin.register(Documentation)
class DocumentationAdmin(admin.ModelAdmin):
    list_display = ('doc_type', 'description')
