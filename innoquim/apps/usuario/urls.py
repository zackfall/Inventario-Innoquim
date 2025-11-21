from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet
from rest_framework_simplejwt.views import TokenRefreshView
from .views_auth import LoginView, LogoutView

router = DefaultRouter()
router.register("usuarios", UsuarioViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/refresh/token/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
]
