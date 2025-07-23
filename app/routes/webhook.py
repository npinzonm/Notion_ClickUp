import hashlib
import hmac
from fastapi import APIRouter, HTTPException, Request, Header
import os
import json

from dotenv import load_dotenv
load_dotenv()

#Modelo de datos

    
router = APIRouter()

NOTION_VERIFICATION_TOKEN = os.getenv("NOTION_VERIFICATION_TOKEN")


def verify_signature(payload: str, signature: str) -> bool:
    if NOTION_VERIFICATION_TOKEN is None:
        raise HTTPException(status_code=500, detail="Falta el NOTION_VERIFICATION_TOKEN en el .env")

    calculated_signature = "sha256=" + hmac.new(
        bytes(NOTION_VERIFICATION_TOKEN, 'utf-8'),
        bytes(payload, 'utf-8'),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(calculated_signature, signature)


@router.post("/")
async def notion_webhook(
    request: Request,
    x_notion_signature: str = Header(None)
):
    body_bytes = await request.body()
    payload_str = body_bytes.decode("utf-8")

    try:
        data = json.loads(payload_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="No se pudo decodificar el JSON")

    # 🔐 1. Si viene el verification_token (es la primera vez que Notion llama al webhook)
    if "verification_token" in data:
        verification_token = data["verification_token"]

        # Opción: guardar el token en archivo temporal
        with open(".notion_token", "w") as f:
            f.write(verification_token)

        print("✅ Token de verificación recibido y guardado:", verification_token)
        return {"message": "Token de verificación recibido y almacenado"}

    # 🔒 2. Validación normal de la firma
    if not x_notion_signature:
        raise HTTPException(status_code=400, detail="Falta la firma en la cabecera")

    if not verify_signature(payload_str, x_notion_signature):
        raise HTTPException(status_code=400, detail="Firma inválida")

    # 📩 3. Procesar evento real
    print("📩 Webhook recibido:", data)

    return {"message": "Webhook recibido correctamente"}