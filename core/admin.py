from django.contrib import admin
from django.utils.html import format_html

from .models import (
    SiteSettings, Category, NailDesign, Enquiry,
    NailShape, NailSize, NailSizeSet, Order, OrderItem,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fields = ['site_name', 'logo', 'logo_preview']
    readonly_fields = ['logo_preview']

    @admin.display(description='Current logo')
    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-height:120px;border-radius:8px;" />'
                '<br><small>{}</small>',
                obj.logo.url,
                obj.logo.name,
            )
        return 'No logo uploaded'

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(NailShape)
class NailShapeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(NailSize)
class NailSizeAdmin(admin.ModelAdmin):
    list_display = ['width_mm']


@admin.register(NailSizeSet)
class NailSizeSetAdmin(admin.ModelAdmin):
    list_display = ['name', 'thumb', 'index', 'middle', 'ring', 'pinky']
    list_select_related = ['thumb', 'index', 'middle', 'ring', 'pinky']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(NailDesign)
class NailDesignAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price', 'featured', 'image_preview', 'created_at']
    list_filter = ['category', 'featured']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['price', 'featured']
    fields = [
        'title', 'slug', 'category', 'description', 'price',
        'image', 'current_image', 'featured',
        'available_shapes', 'available_size_sets',
    ]
    readonly_fields = ['current_image']
    filter_horizontal = ['available_shapes', 'available_size_sets']

    @admin.display(description='Preview')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:4px;" />',
                obj.image.url,
            )
        return '-'

    @admin.display(description='Current image')
    def current_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:200px;border-radius:6px;" />'
                '<br><small>{}</small>',
                obj.image.url,
                obj.image.name,
            )
        return 'No image uploaded'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = [
        'design', 'design_slug', 'design_title', 'design_image_url',
        'shape_name', 'size_name', 'custom_label', 'unit_price', 'qty',
    ]
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'customer_email', 'total', 'currency', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer_email', 'customer_name', 'stripe_session_id']
    readonly_fields = [
        'lookup_token', 'stripe_session_id', 'stripe_payment_intent_id', 'customer_email',
        'customer_name', 'shipping_address', 'subtotal', 'shipping', 'total',
        'currency', 'created_at', 'paid_at',
    ]
    fields = [
        'status', 'tracking_number', 'tracking_url',
        'customer_email', 'customer_name', 'shipping_address',
        'subtotal', 'shipping', 'total', 'currency',
        'stripe_session_id', 'stripe_payment_intent_id',
        'lookup_token', 'created_at', 'paid_at',
    ]
    inlines = [OrderItemInline]


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'design', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['name', 'email', 'phone', 'design', 'message', 'created_at']
