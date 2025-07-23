from typing import List
from fastapi import APIRouter, Request, Header, HTTPException
import hashlib
import hmac
import json
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

from app.model.data_model import NotionPage
from app.services.notion_service import get_notion_information

load_dotenv()  

router = APIRouter()

NOTION_VERIFICATION_TOKEN = os.getenv("NOTION_VERIFICATION_TOKEN")

@router.post("/notion")
async def receive_notion_event(
    request: Request,
    notion_token: str = Header(None, alias="x-notion-token")
):

    if notion_token != NOTION_VERIFICATION_TOKEN:
        return JSONResponse(
            status_code=403,
            content={"message": "Forbidden: Invalid Notion verification token"}
        )      
        
    # Leer el body completo de la solicitud
    body = await request.body()

    try:
        organized_data = organize_data(body)
    except Exception as e:
        print("❌ Error organizando datos:", e)
        return {"error": str(e)}

    try:
        info_notion = prepare_clickup_informacion(organized_data)
        complete_information_notion = await get_notion_information(info_notion)
        print("Información enriquecida de Notion:", complete_information_notion)

        
        

    except Exception as e:
        print("❌ Error procesando Notion event:", e)
        return {"error": str(e)}

    return {"status": "ok"}
        

        
def prepare_clickup_informacion(data: NotionPage) -> dict:
    
    resultado = {}

    for key, prop in data[0]["properties"].items():
        if key == "Prioridad" and "name" in prop:
            resultado["prioridad"] = prop["name"]
        elif key == "Subcategoría" and "list" in prop:
            resultado["subcategorias_ids"] = [item["id"] for item in prop["list"]]
        elif key == "Repetir" and "boolean" in prop:
            resultado["repetir"] = prop["boolean"]
        elif key == "Día" and "string" in prop:
            resultado["dia"] = prop["string"]
        elif key == "Subárea" and "list" in prop:
            resultado["subarea_ids"] = [item["id"] for item in prop["list"]]
        elif key == "Estado" and "name" in prop:
            resultado["estado"] = prop["name"]
        elif key == "Tarea" and "list" in prop:
            if prop["list"]:
                resultado["titulo"] = prop["list"][0]["plain_text"]

    return resultado


def organize_data(raw_data: bytes) -> List[dict]:
    decoded = raw_data.decode("utf-8")
    
    # Extraer ID de página
    page_id_match = re.match(r'^page([a-f0-9\-]+)', decoded)
    if not page_id_match:
        raise ValueError("No se encontró el ID de la página")
    page_id = page_id_match.group(1)    

    # Extraer objetos JSON
    json_matches = re.findall(r'\{.*?\}(?=\{|\Z)', decoded)
    if len(json_matches) < 2:
        raise ValueError("No se encontraron los objetos JSON")
    
    created_by = json.loads(json_matches[0])
    properties_raw = json.loads(json_matches[1])
    
    

    # Solo conservar propiedades que sean tipo dict
    clean_properties = {}
    
    for key, value in properties_raw.items():
        if isinstance(value, list):
            # Asumimos que son relaciones o títulos
            clean_properties[key] = {
                "type": "list",
                "list": value
            }
        elif isinstance(value, bool):
            clean_properties[key] = {
                "type": "boolean",
                "boolean": value
            }
        else:
            clean_properties[key] = value
            

    return [{
        "object": "page",
        "id": f"page_{page_id}",
        "created_by": created_by,
        "properties": clean_properties
    }]