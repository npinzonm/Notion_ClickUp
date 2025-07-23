import hashlib
import hmac
import json
import os

from fastapi import APIRouter, HTTPException, Request, Header

router = APIRouter()


def verify_signature(payload: str, signature: str) -> bool:
    try:
        with open(".notion_token", "r") as f:
            verification_token = f.read().strip()
    except FileNotFoundError:
        print("❌ No se encontró el token de verificación guardado")
        return False

    hmac_obj = hmac.new(
        verification_token.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    )
    calculated_signature = "sha256=" + hmac_obj.hexdigest()

    is_valid = hmac.compare_digest(calculated_signature, signature)

    if not is_valid:
        print("❌ Firma inválida")
        print("Esperada:", calculated_signature)
        print("Recibida:", signature)

    return is_valid


@router.post("/")
async def notion_webhook(
    request: Request,
    x_notion_signature: str = Header(None)
):
    print("🔗 Recibiendo webhook de Notion")

    body_bytes = await request.body()
    payload_str = body_bytes.decode("utf-8")

    print("🔗 Payload recibido:", payload_str)

    try:
        data = json.loads(payload_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="No se pudo decodificar el JSON")
    
    print("🔗 Datos decodificados:", data)
    # 📩 Procesar evento real
    print("📩 Webhook recibido:", data)

    return {"message": "Webhook recibido correctamente"}