from fastapi import APIRouter, Request, Header, HTTPException
import hashlib
import hmac
import json
import os
from dotenv import load_dotenv

load_dotenv()  

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

@router.post("/webhook")
async def notion_webhook(
    request: Request,
    x_notion_signature: str = Header(None)  
):

    body = await request.body()  # Obtiene el cuerpo de la solicitud
    payload = body.decode("utf-8")  # Convierte bytes a string
    
    if not x_notion_signature:
        raise HTTPException(status_code=400, detail="Falta la firma en la cabecera")

    # Verifica la firma del payload
    if not verify_signature(payload, x_notion_signature):
        raise HTTPException(status_code=400, detail="Firma inválida")

    # Convertimos el payload a JSON
    data = json.loads(payload)

    print("📩 Webhook recibido:", data)  # Debug, puedes guardarlo en logs o BD

    return {"message": "Webhook recibido correctamente"}