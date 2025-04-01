import hmac
import hashlib
import json
import os
from fastapi import APIRouter, Request, Header, HTTPException
from hmac import compare_digest

router = APIRouter()

@router.post("/webhook")
async def notion_webhook(request: Request, x_notion_signature: str = Header(None)):
    # Obtener el cuerpo de la solicitud como un diccionario
    body = await request.json()

    # Serializar el cuerpo a JSON sin espacios innecesarios
    body_json = json.dumps(body, separators=(",", ":"))

    # Obtener el token de verificación de las variables de entorno
    verification_token = os.getenv("NOTION_VERIFICATION_TOKEN")
    
    # Verificar que el token de verificación esté configurado
    if not verification_token:
        raise HTTPException(status_code=500, detail="Token de verificación no configurado")

    # Calcular la firma esperada (HMAC-SHA256) usando la cadena JSON del cuerpo
    calculated_signature = "sha256=" + hmac.new(
        verification_token.encode(), body_json.encode(), hashlib.sha256
    ).hexdigest()

    # Comparar la firma calculada con la firma recibida usando comparación segura
    if not compare_digest(calculated_signature.encode(), x_notion_signature.encode()):
        raise HTTPException(status_code=401, detail="Firma no válida")

    # Si la firma es válida, procesamos el webhook
    print("Webhook recibido:", body)
    
    # Responder con un mensaje de éxito
    return {"message": "Webhook recibido correctamente"}