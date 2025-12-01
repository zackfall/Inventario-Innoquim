from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import (
    UsuarioSerializer, 
    UsuarioPublicSerializer,
    CustomTokenObtainPairSerializer
)

Usuario = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vista personalizada para login con JWT"""
    serializer_class = CustomTokenObtainPairSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    
    def get_permissions(self):
        """Permitir registro sin autenticación"""
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Obtener información del usuario actual"""
        serializer = UsuarioPublicSerializer(request.user)
        return Response(serializer.data)