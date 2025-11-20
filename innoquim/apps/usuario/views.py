from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UsuarioSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

Usuario = get_user_model()


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_permissions(self):
        # Permitir que cualquiera pueda registrarse
        if self.action == "create":
            self.permission_classes = [AllowAny()]

        # Endpoints protegidos para usuarios autenticados
        return [IsAuthenticated()]

    @action(detail=False, methods=["get"])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
