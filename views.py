import json

from django.db import transaction
from django.db.models import Prefetch
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Category, Dish, GalleryImage, Order, OrderItem, Table


def home(request):
    dishes_qs = Dish.objects.filter(is_available=True)
    categories = Category.objects.filter(is_active=True).prefetch_related(
        Prefetch("dishes", queryset=dishes_qs, to_attr="visible_dishes")
    )
    categories = [c for c in categories if c.visible_dishes]
    dish_map = {}
    for c in categories:
        for d in c.visible_dishes:
            dish_map[d.id] = {"name": d.name, "price": d.price, "photo": d.photo, "emoji": d.emoji}
    populars = dishes_qs.filter(is_popular=True)[:8]
    busy = set(
        Order.objects.filter(status__in=Order.ACTIVE, table__isnull=False).values_list("table_id", flat=True)
    )
    tables = list(Table.objects.filter(is_active=True))
    for t in tables:
        t.busy = t.id in busy
    ctx = {
        "categories": categories,
        "populars": populars,
        "dish_map": dish_map,
        "tables": tables,
        "gallery": GalleryImage.objects.filter(is_active=True),
        "dish_count": len(dish_map),
    }
    return render(request, "restaurant/home.html", ctx)


@require_POST
def create_order(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Noto‘g‘ri so‘rov"}, status=400)

    items = data.get("items") or []
    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()
    order_type = data.get("order_type")
    address = (data.get("address") or "").strip()
    comment = (data.get("comment") or "").strip()

    if not items:
        return JsonResponse({"ok": False, "error": "Savat bo‘sh"}, status=400)
    if not name or not phone:
        return JsonResponse({"ok": False, "error": "Ism va telefonni kiriting"}, status=400)
    if order_type not in dict(Order.TYPES):
        return JsonResponse({"ok": False, "error": "Buyurtma turini tanlang"}, status=400)

    table = None
    if order_type == Order.DINE:
        try:
            table = Table.objects.get(pk=int(data.get("table")), is_active=True)
        except (TypeError, ValueError, Table.DoesNotExist):
            return JsonResponse({"ok": False, "error": "Stolni tanlang"}, status=400)
    if order_type == Order.DELIVERY and not address:
        return JsonResponse({"ok": False, "error": "Yetkazib berish manzilini kiriting"}, status=400)

    try:
        wanted = {int(i["id"]): max(1, min(int(i["qty"]), 50)) for i in items}
    except (KeyError, TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "Savat noto‘g‘ri"}, status=400)
    dishes = Dish.objects.in_bulk(list(wanted.keys()))
    lines = [(dishes[i], q) for i, q in wanted.items() if i in dishes and dishes[i].is_available]
    if not lines:
        return JsonResponse({"ok": False, "error": "Tanlangan taomlar mavjud emas"}, status=400)

    with transaction.atomic():
        order = Order.objects.create(
            order_type=order_type, table=table, customer_name=name[:80], phone=phone[:30],
            address=address[:250], comment=comment[:500],
            total=sum(d.price * q for d, q in lines),
        )
        OrderItem.objects.bulk_create(
            [OrderItem(order=order, dish=d, name=d.name, price=d.price, qty=q) for d, q in lines]
        )
    return JsonResponse({"ok": True, "code": order.code, "url": reverse("order_status", args=[order.code])})


def track(request):
    code = (request.GET.get("code") or "").strip().lstrip("#")
    if Order.objects.filter(code=code).exists():
        return redirect("order_status", code=code)
    return render(request, "restaurant/order_status.html", {"not_found": True, "code": code})


STEP_INFO = {
    Order.NEW: ("Qabul kutilmoqda", "📝"),
    Order.ACCEPTED: ("Qabul qilindi", "✅"),
    Order.COOKING: ("Tayyorlanmoqda", "🔥"),
    Order.READY: ("Tayyor", "🍽️"),
    Order.DONE: ("Yakunlandi", "🎉"),
}


def order_status(request, code):
    order = get_object_or_404(Order.objects.prefetch_related("items"), code=code)
    steps = []
    if order.status != Order.CANCELLED:
        idx = Order.FLOW.index(order.status)
        for i, key in enumerate(Order.FLOW):
            label, icon = STEP_INFO[key]
            state = "done" if i < idx else "current" if i == idx else "todo"
            steps.append({"label": label, "icon": icon, "state": state})
    return render(request, "restaurant/order_status.html", {"order": order, "steps": steps})


def order_json(request, code):
    try:
        order = Order.objects.get(code=code)
    except Order.DoesNotExist:
        raise Http404
    return JsonResponse({"status": order.status, "label": order.get_status_display()})
