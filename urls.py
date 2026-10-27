from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("order/create/", views.create_order, name="create_order"),
    path("track/", views.track, name="track"),
    path("order/<str:code>/", views.order_status, name="order_status"),
    path("order/<str:code>/json/", views.order_json, name="order_json"),
]
