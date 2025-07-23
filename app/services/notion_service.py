from typing import  List, Optional
from fastapi import APIRouter, Request, Header
import httpx
from pydantic import BaseModel
from starlette.responses import JSONResponse
import os

from dotenv import load_dotenv
load_dotenv()

#Modelo de datos

class ClickupTaskModel(BaseModel):
    id: str
    name: str
    status: str
    priority: Optional[str] = None
    due_date: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    description: Optional[str] = None



router = APIRouter()

NOTION_VERIFICATION_TOKEN = os.getenv("NOTION_VERIFICATION_TOKEN")
NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")

headers = {
    "Authorization": f"Bearer {NOTION_VERIFICATION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

async def get_notion_information(data_preparada: dict) -> dict:
    enriched_data = data_preparada.copy()
    
    print("Enriched data:", enriched_data)
    
    # Verificar si categoría y subcategoría están presentes y tiene valores
    if len(enriched_data.get("subcategorias_ids", [])) > 0:
        if(len(enriched_data.get("subarea_ids", [])) > 0):
            lista_subcategorias : List[str] = enriched_data.get("subcategorias_ids", [])
            lista_subareas : List[str] = enriched_data.get("subarea_ids", [])
        else:
            print("No se encontraron subáreas")
            return
    else:
        print("No se encontraron subcategorías")
        return
        
    # Consultar páginas a partir de ID de la subárea
 


    return enriched_data


# async def get_information(page_id: str) -> dict:
#     url = f"https://api.notion.com/v1/pages/{page_id}"
    
#     async with httpx.AsyncClient() as client:
#         response = await client.get(url, headers=headers)
#         response.raise_for_status()  # Lanza un error si la respuesta no es 200 OK
        
#         if response.status_code == 200:
#             return response.json()
#         else:
#             raise Exception(f"Error al obtener la página: {response.status_code} - {response.text}")