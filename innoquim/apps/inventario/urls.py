from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KardexViewSet

router = DefaultRouter()
router.register(r"kardex", KardexViewSet, basename="kardex")

urlpatterns = [
    path("", include(router.urls)),
]
