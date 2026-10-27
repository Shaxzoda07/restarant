from django.contrib import admin

from .models import Category, Dish, GalleryImage, Order, OrderItem, Table

admin.site.site_header = "NOVZA — boshqaruv paneli"
admin.site.site_title = "NOVZA admin"
admin.site.index_title = "Restoranni boshqarish"


class AdminAssets:
    class Media:
        css = {"all": ("restaurant/css/admin.css",)}
        js = ("restaurant/js/admin.js",)


@admin.register(Category)
class CategoryAdmin(AdminAssets, admin.ModelAdmin):
    list_display = ("icon", "name", "order", "is_active")
    list_display_links = ("name",)
    list_editable = ("order", "is_active")


@admin.register(Dish)
class DishAdmin(AdminAssets, admin.ModelAdmin):
    list_display = ("thumb", "name", "category", "price", "is_popular", "is_new", "is_available")
    list_display_links = ("thumb", "name")
    list_editable = ("price", "is_popular", "is_new", "is_available")
    list_filter = ("category", "is_available", "is_popular")
    search_fields = ("name", "description")
    list_per_page = 40


@admin.register(Table)
class TableAdmin(AdminAssets, admin.ModelAdmin):
    list_display = ("number", "zone", "seats", "is_active")
    list_editable = ("zone", "seats", "is_active")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("dish", "name", "price", "qty")


@admin.register(Order)
class OrderAdmin(AdminAssets, admin.ModelAdmin):
    list_display = ("code", "created_at", "order_type", "table", "customer_name", "phone", "total_som", "status")
    list_editable = ("status",)
    list_filter = ("status", "order_type", "created_at")
    search_fields = ("code", "customer_name", "phone")
    readonly_fields = ("code", "created_at")
    inlines = [OrderItemInline]
    date_hierarchy = "created_at"
    actions = ["mark_accepted", "mark_cooking", "mark_ready", "mark_done", "mark_cancelled"]

    @admin.display(description="Jami")
    def total_som(self, obj):
        return f"{obj.total:,}".replace(",", " ") + " so‘m"

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        order = form.instance
        order.total = sum(i.price * i.qty for i in order.items.all())
        order.save(update_fields=["total"])

    def _set(self, request, queryset, status):
        queryset.update(status=status)

    @admin.action(description="Qabul qilindi deb belgilash")
    def mark_accepted(self, request, queryset):
        self._set(request, queryset, Order.ACCEPTED)

    @admin.action(description="Tayyorlanmoqda deb belgilash")
    def mark_cooking(self, request, queryset):
        self._set(request, queryset, Order.COOKING)

    @admin.action(description="Tayyor deb belgilash")
    def mark_ready(self, request, queryset):
        self._set(request, queryset, Order.READY)

    @admin.action(description="Yakunlandi deb belgilash")
    def mark_done(self, request, queryset):
        self._set(request, queryset, Order.DONE)

    @admin.action(description="Bekor qilish")
    def mark_cancelled(self, request, queryset):
        self._set(request, queryset, Order.CANCELLED)


@admin.register(GalleryImage)
class GalleryAdmin(AdminAssets, admin.ModelAdmin):
    list_display = ("__str__", "order", "is_active")
    list_editable = ("order", "is_active")
