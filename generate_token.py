#!/usr/bin/env python3
"""
Script para generar token de Google Drive OAuth 2.0.
Ejecutar localmente para obtener token.json.
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def main():
    credentials_path = 'credentials/google-drive-credentials.json'
    token_path = 'credentials/token.json'

    creds = None

    # Cargar token existente si existe
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # Si no hay credenciales válidas, iniciar flujo OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES
            )
            creds = flow.run_local_server(port=8080)

        # Guardar credenciales
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    print("✅ Token generado exitosamente en credentials/token.json")

if __name__ == '__main__':
    main()