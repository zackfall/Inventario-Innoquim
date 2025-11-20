from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import LoginSerializer

Usuario = get_user_model()


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "name": user.name,
                    "rol": user.rol,
                },
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    def post(self, request):
        """Logout usando blacklist"""
        try:
            refresh = request.data["refresh"]
            token = RefreshToken(refresh)
            token.blacklist()
            return Response({"detail": "Logout exitoso"})
        except Exception:
            return Response({"detail": "Token inválido"}, status=400)
