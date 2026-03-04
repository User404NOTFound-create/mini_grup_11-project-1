from django.contrib import admin
from django.utils.html import format_html
from django.db import models as dj_models
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (
    Article, ArticleCategory
)

class BaseAdmin(admin.ModelAdmin):
    list_per_page = 10

    class Meta:
        abstract = True

def register_model(model):
    resource_class = type(
        f"{model.__name__}Resource",
        (resources.ModelResource,),
        {
            "Meta": type("Meta", (), {"model": model}),
        }
    )

    image_fields = [f.name for f in model._meta.fields if isinstance(f, dj_models.ImageField)]
    text_fields = [f.name for f in model._meta.fields if isinstance(f, dj_models.TextField)]
    fields = tuple(
        f.name for f in model._meta.fields
        if f.name != 'id' and f.name not in image_fields and f.name not in text_fields
    )

    admin_attrs = {
        "resource_classes": [resource_class],
        "list_display": list(fields),
        "list_filter": fields,
        "search_fields": fields,
    }

    if model == Article:
        # Muallifni avtomatik qo'shish
        def save_model(self, request, obj, form, change):
            if not change:  # Yangi article yaratilayotganda
                obj.author = request.user
            super().save_model(request, obj, form, change)

        admin_attrs['save_model'] = save_model

        # ManyToMany field uchun filter_horizontal
        admin_attrs['filter_horizontal'] = ['category']

        # Readonly fields
        admin_attrs['readonly_fields'] = ['author', 'date']

        # List display ga qo'shimchalar
        if 'author' not in admin_attrs['list_display']:
            admin_attrs['list_display'].append('author')
        if 'date' not in admin_attrs['list_display']:
            admin_attrs['list_display'].append('date')

        # List filter ga qo'shimchalar
        admin_attrs['list_filter'] = list(admin_attrs['list_filter']) + ['category', 'date']
    for field in text_fields:
        method_name = f"short_{field}"

        def make_text_preview(field_name):
            def short_text(self, obj):
                val = getattr(obj, field_name)
                return (val[:47] + "...") if val and len(val) > 50 else val
            short_text.short_description = field_name
            return short_text

        admin_attrs[method_name] = make_text_preview(field)
        admin_attrs["list_display"].insert(0, method_name)

    for field in image_fields:
        method_name = f"show_{field}"

        def make_thumb_func(field_name):
            def thumb(self, obj):
                val = getattr(obj, field_name)
                if val and hasattr(val, 'url'):
                    return format_html(
                        '<a href="{0}" target="_blank">'
                        '<img src="{0}" width="100" height="100" style="object-fit: cover; border-radius: 4px;" />'
                        '</a>',
                        val.url
                    )
                return "-"
            thumb.short_description = field_name
            thumb.allow_tags = True  # optional in modern Django
            return thumb

        admin_attrs[method_name] = make_thumb_func(field)
        admin_attrs["list_display"].append(method_name)

    admin_class = type(
        f"{model.__name__}Admin",
        (ImportExportModelAdmin, BaseAdmin),
        admin_attrs
    )

    admin.site.register(model, admin_class)

registered_models = [
    Article, ArticleCategory
]

for model in registered_models:
    register_model(model)
