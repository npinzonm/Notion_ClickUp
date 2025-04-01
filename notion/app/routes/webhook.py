from fastapi import APIRouter, Request, Header
import hashlib
import hmac
import os

router = APIRouter()

router = APIRouter()

@router.post("/webhook")
async def notion_webhook(request: Request, x_notion_signature: str = Header(None)):
    body = await request.body()
    verification_token = os.getenv("NOTION_VERIFICATION_TOKEN")

    if not verification_token:
        return {"error": "Token de verificación no configurado"}

    computed_signature = "sha256=" + hmac.new(
        verification_token.encode(), body, hashlib.sha256
    ).hexdigest()

    if computed_signature != x_notion_signature:
        return {"error": "Firma no válida"}

    data = await request.json()
    print("Webhook recibido:", data)
    
    return {"message": "Webhook recibido correctamente"}