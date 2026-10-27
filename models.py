import random

from django.db import models
from django.utils.html import format_html


class Category(models.Model):
    name = models.CharField("Nomi", max_length=80)
    icon = models.CharField("Emoji belgisi", max_length=8, default="🍽️", blank=True)
    order = models.PositiveIntegerField("Tartib raqami", default=0)
    is_active = models.BooleanField("Saytda ko‘rinsin", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

    def __str__(self):
        return self.name


class Dish(models.Model):
    category = models.ForeignKey(Category, verbose_name="Kategoriya", on_delete=models.CASCADE, related_name="dishes")
    name = models.CharField("Taom nomi", max_length=120)
    description = models.TextField("Tavsif", blank=True)
    price = models.PositiveIntegerField("Narxi (so‘m)")
    weight = models.CharField("Porsiya (masalan: 350 g)", max_length=40, blank=True)
    image = models.ImageField("Rasm (yuklash)", upload_to="dishes/", blank=True)
    image_url = models.URLField("Yoki rasm havolasi", blank=True, help_text="Rasm yuklamasangiz, internetdagi rasm havolasini qo‘ying")
    emoji = models.CharField("Rasm yo‘q bo‘lsa belgisi", max_length=8, default="🍽️", blank=True)
    is_popular = models.BooleanField("Mashhur taom (bosh sahifada)", default=False)
    is_new = models.BooleanField("Yangi", default=False)
    is_available = models.BooleanField("Mavjud", default=True)
    order = models.PositiveIntegerField("Tartib raqami", default=0)

    class Meta:
        ordering = ["category__order", "order", "id"]
        verbose_name = "Taom"
        verbose_name_plural = "Taomlar"

    def __str__(self):
        return self.name

    @property
    def photo(self):
        if self.image:
            return self.image.url
        return self.image_url or ""

    def thumb(self):
        if self.photo:
            return format_html('<img src="{}" style="width:54px;height:54px;object-fit:cover;border-radius:10px">', self.photo)
        return self.emoji
    thumb.short_description = "Rasm"


class Table(models.Model):
    ZONES = [("hall", "Asosiy zal"), ("terrace", "Terrasa"), ("vip", "VIP xona"), ("choyxona", "Choyxona (so‘ri)")]
    number = models.PositiveIntegerField("Stol raqami", unique=True)
    seats = models.PositiveIntegerField("O‘rinlar soni", default=4)
    zone = models.CharField("Joylashuvi", max_length=20, choices=ZONES, default="hall")
    is_active = models.BooleanField("Faol", default=True)

    class Meta:
        ordering = ["number"]
        verbose_name = "Stol"
        verbose_name_plural = "Stollar"

    def __str__(self):
        return f"Stol №{self.number} ({self.get_zone_display()}, {self.seats} kishilik)"


class Order(models.Model):
    NEW, ACCEPTED, COOKING, READY, DONE, CANCELLED = "new", "accepted", "cooking", "ready", "done", "cancelled"
    STATUS = [
        (NEW, "Yangi"),
        (ACCEPTED, "Qabul qilindi"),
        (COOKING, "Tayyorlanmoqda"),
        (READY, "Tayyor"),
        (DONE, "Yakunlandi"),
        (CANCELLED, "Bekor qilindi"),
    ]
    FLOW = [NEW, ACCEPTED, COOKING, READY, DONE]
    ACTIVE = [NEW, ACCEPTED, COOKING, READY]

    DINE, TAKEAWAY, DELIVERY = "dine", "takeaway", "delivery"
    TYPES = [(DINE, "Zalda (stolga)"), (TAKEAWAY, "Olib ketish"), (DELIVERY, "Yetkazib berish")]

    code = models.CharField("Buyurtma kodi", max_length=6, unique=True, editable=False)
    order_type = models.CharField("Turi", max_length=10, choices=TYPES, default=DINE)
    table = models.ForeignKey(Table, verbose_name="Stol", null=True, blank=True, on_delete=models.SET_NULL)
    customer_name = models.CharField("Mijoz ismi", max_length=80)
    phone = models.CharField("Telefon", max_length=30)
    address = models.CharField("Manzil", max_length=250, blank=True)
    comment = models.TextField("Izoh", blank=True)
    total = models.PositiveIntegerField("Jami (so‘m)", default=0)
    status = models.CharField("Holati", max_length=12, choices=STATUS, default=NEW)
    created_at = models.DateTimeField("Vaqti", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"

    def __str__(self):
        return f"#{self.code} — {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.code:
            while True:
                code = str(random.randint(100000, 999999))
                if not Order.objects.filter(code=code).exists():
                    self.code = code
                    break
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    dish = models.ForeignKey(Dish, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Taom")
    name = models.CharField("Nomi", max_length=120)
    price = models.PositiveIntegerField("Narxi")
    qty = models.PositiveIntegerField("Soni", default=1)

    class Meta:
        verbose_name = "Buyurtma qatori"
        verbose_name_plural = "Buyurtma tarkibi"

    def __str__(self):
        return f"{self.name} × {self.qty}"

    @property
    def subtotal(self):
        return self.price * self.qty


class GalleryImage(models.Model):
    caption = models.CharField("Izoh", max_length=120, blank=True)
    image = models.ImageField("Rasm (yuklash)", upload_to="gallery/", blank=True)
    image_url = models.URLField("Yoki rasm havolasi", blank=True)
    order = models.PositiveIntegerField("Tartib", default=0)
    is_active = models.BooleanField("Ko‘rinsin", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Galereya rasmi"
        verbose_name_plural = "Galereya"

    def __str__(self):
        return self.caption or f"Rasm {self.pk}"

    @property
    def photo(self):
        if self.image:
            return self.image.url
        return self.image_url or ""
