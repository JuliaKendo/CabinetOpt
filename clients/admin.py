import pdb

from contextlib import suppress
from django.contrib import admin
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from .models import (
    PriorityDirection,
    RegistrationOrder,
    Client,
    Manager,
    ContactDetail
)
from .forms import CustomRegOrderForm
from .utils import parse_of_name


class ManagerInLine(admin.TabularInline):
    model = Client.manager.through
    extra = 0
    verbose_name = "Персональный менеджер"
    verbose_name_plural = "Персональные менеджеры"


@admin.register(PriorityDirection)
class PriorityDirectionAdmin(admin.ModelAdmin):
    search_fields = ['name',]
    list_display = ['name',]


@admin.register(RegistrationOrder)
class RegistrationOrderAdmin(admin.ModelAdmin):
    form = CustomRegOrderForm
    search_fields = [
        'name',
        'inn',
        'name_of_manager',
        'email',
        'phone',
        'status',
    ]
    list_display = [
        'name',
        'inn',
        'name_of_manager',
        'email',
        'phone',
        'status',
    ]
    fields = [
        'status',
        ('name', 'inn'),
        (
            'name_of_manager',
            'email',
            'phone',
        ),
        ('login', 'password'),
        'priority_direction',
    ]

    def check_registration(self, obj):
        return obj.status == 'registered' and \
            Client.objects.filter(registration_order=obj).exists()

    def get_readonly_fields(self, request, obj=None):
        if self.check_registration(obj):
            return [f.name for f in self.model._meta.fields]
        return self.readonly_fields

    def get_fieldsets(self, request, obj=None):

        def remove_login_group(fields):
            if ('login', 'password') in fields:
                fields.remove(('login', 'password'))
            return fields
        
        fieldsets = super().get_fieldsets(request, obj)
        if self.check_registration(obj): 
            return [
                tuple((
                    lambda f: {
                        'fields': remove_login_group(f['fields'])
                    } if f else f
                )(fields) for fields in fieldset) for fieldset in fieldsets
            ]
        
        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def save_model(self, request, obj, form, change):
        registration_order = form.cleaned_data
        if not registration_order.get('status') or registration_order.get('status') != 'registered':
            return super().save_model(request, obj, form, change)
        
        parsed_manager_name = parse_of_name(registration_order.get('name_of_manager'))
        if not parsed_manager_name:
            raise ValidationError('Не указано ФИО персонального менеджера', code='')
        
        with transaction.atomic():
            personal_manager, _ = Manager.objects.get_or_create(
                last_name = parsed_manager_name['last_name'],
                first_name = parsed_manager_name['first_name'],
                defaults = {
                    key: value for key, value  in registration_order.items() if \
                        key in ['email', 'phone', 'login', 'password']
                } | parsed_manager_name
            )
            client = Client.objects.create(**{
                'name'              : registration_order['name'],
                'inn'               : registration_order['inn'],
                'registration_order': obj,
                'approved_by'       : request.user,
            })
            client.manager.add(personal_manager)
            return super().save_model(request, obj, form, change)


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    pass


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'inn',
        'registration_order',
        'approved_by',
        'updated_by',
    ]
    list_display = [
        'name',
        'inn',
        'registration_order',
        'created_at',
        'approved_by',
    ]
    fields = [
        ('name', 'inn'),
        'registration_order',
        ('created_at', 'approved_by'),
        ('updated_at', 'updated_by'),
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'registration_order',
        'approved_by',
        'updated_by',
    ]
    inlines = [ManagerInLine]


@admin.register(ContactDetail)
class ContactDetailAdmin(admin.ModelAdmin):
    search_fields = [
        'client',
        'city',
        'legal_address',
        'shoping_address',
        'payment_type',
    ]
    list_display = [
        f.name for f in ContactDetail._meta.get_fields() if f.name != 'id'
    ]
    fields = [('client', 'city'), ('legal_address', 'shoping_address'), 'payment_type']
