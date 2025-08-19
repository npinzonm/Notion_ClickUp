import json
import re
from typing import List
from fastapi import APIRouter, Request, Header
from fastapi.exceptions import HTTPException
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

from app.model.data_model import NotionPage
from app.services.notion_service import complete_data_notion
from app.routes.clickup import crear_tarea_clickup

load_dotenv()  

router = APIRouter()

SUBCATEGORIA = "Subcategoría"
SUBAREA = "Subarea"
CATEGORIA = "Categoría"
AREA = "Área"


NOTION_VERIFICATION_TOKEN = os.getenv("NOTION_VERIFICATION_TOKEN")

# @router.post("/notion")
# async def receive_notion_event(
#     request: Request,
#     notion_token: str = Header(None, alias="x-notion-token")
# ):

#     if notion_token != NOTION_VERIFICATION_TOKEN:
#         return JSONResponse(
#             status_code=403,
#             content={"message": "Forbidden: Invalid Notion verification token"}
#         )      


async def recibir_webhook_notion(payload_str: Request):

    payload_dict = json.loads(payload_str)  # 👈 convertir string a dict
    notion_page = NotionPage(**payload_dict)

    print("✅ Webhook parseado:", notion_page)
    
    try:
        
        # dataPrueba = {'Prioridad': 'Urgente e Importante', 'Subcategoría': 'Reading, Writing', 'Repetir': None, 'Categoría': 'Inglés', 'Migrar': None, 'Fecha': '2025-07-09', 'Día': None, 'Subarea': 'ActiveIT', 'Área': 'Laboral', 'Estado': 'Open', 'Tarea': 'PRUEBA 2', 'ID_ClickUp': None}
        

            
            # id_tarea = await crear_tarea_clickup(dataPrueba)
            
            # if not id_tarea:
            #     raise ValueError("No se pudo crear la tarea en ClickUp")
            # else:
            #     print("✅ Tarea creada en ClickUp con ID:", id_tarea)
                
        
        info_notion = prepare_clickup_informacion(notion_page)        
        complete_information_notion = await complete_data_notion(info_notion)        
        combined_data = join_data(info_notion, complete_information_notion)
        
        print("🔄 Datos combinados de Notion:", combined_data)
        


    except ValueError as e:
        print("❌ Error procesando Notion event:", e)
        return {"error": str(e)}

    return {"status": "ok"}

 
def extraer_valor(propiedad):
    tipo = propiedad.type

    manejadores = {
        "select": lambda p: p.select.name if p.select else None,
        "relation": lambda p: extraer_relation(p.relation),
        "status": lambda p: p.status.name if p.status else None,
        "date": lambda p: p.date.start if p.date else None,
        "title": lambda p: p.title[0].plain_text if p.title else None,
        "rich_text": lambda p: [text.plain_text for text in p.rich_text] if p.rich_text else None,
    }

    return manejadores.get(tipo, lambda p: None)(propiedad)


def extraer_relation(relacion):
    if not relacion:
        return None
    ids = [rel.id for rel in relacion]
    return ",".join(ids) if len(ids) > 1 else ids[0]

def prepare_clickup_informacion(notion_page: NotionPage) -> dict:
    propiedades = notion_page.data.properties.items()
    resultados = {
        campo: extraer_valor(propiedad)
        for campo, propiedad in propiedades
    }
    return resultados


def join_data(info_notion: dict, complete_information_notion: dict) -> dict:

    if not complete_information_notion:
        return info_notion

    if "categorias" in complete_information_notion:
        info_notion[CATEGORIA] = complete_information_notion["categorias"]

    if "subcategorias" in complete_information_notion and SUBCATEGORIA in info_notion:
        subcats = complete_information_notion["subcategorias"]
        info_notion[SUBCATEGORIA] = ", ".join(subcats) if isinstance(subcats, list) else subcats

    if "area" in complete_information_notion:
        info_notion[AREA] = complete_information_notion["area"]

    if "subarea" in complete_information_notion and SUBAREA in info_notion:
        subarea = complete_information_notion["subarea"]
        info_notion[SUBAREA] = ", ".join(subarea) if isinstance(subarea, list) else subarea

    return info_notion