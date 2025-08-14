import asyncio
import logging
import re
from typing import List, Literal
from fastapi import APIRouter, Request, Header
from fastapi.exceptions import HTTPException
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import httpx
from pydantic import BaseModel

from app.services.clickup_service import get_spaces, get_tasks, get_team_id, get_folders


load_dotenv()  

router = APIRouter()

class Status(BaseModel):
    status: Literal['Open', 'in progress', 'completed', 'closed']

#Carga de variables de entorno    
load_dotenv()
CLICKUP_VERIFICATION_TOKEN = os.getenv("CLICKUP_VERIFICATION_TOKEN")

if( not CLICKUP_VERIFICATION_TOKEN):
    logging.critical("🚨 ERROR: CLICKUP_VERIFICATION_TOKEN no está configurado.")
    raise ValueError("🚨 CLICKUP_VERIFICATION_TOKEN no está configurado")

headers = {
    "Authorization": f"{CLICKUP_VERIFICATION_TOKEN}",
    "Content-Type": "application/json"
}



async def crear_tarea_clickup(notion_page):
    try:
        id_team = await get_team_id()
        if not id_team:
            raise ValueError("No se pudo obtener el ID del equipo")
        else: 
            print("✅ ID del equipo obtenido:", id_team)
            spaces = await get_spaces(id_team)
            if not spaces:
                raise ValueError("No se pudo obtener los espacios")
            else:
               informaciion_area_filtrada = filtrar_areas(spaces, notion_page['Área'])     
               folders = await get_folders(informaciion_area_filtrada['id'])
               
            if not folders:
                raise ValueError("No se pudo obtener las carpetas")
            else:
                list_id = filtrar_folders(folders, notion_page['Subarea'])  
                
                prioridad_notion = notion_page['Prioridad']
                
                print("🔄 Mapeando prioridad de Notion a ClickUp:", prioridad_notion)

                match prioridad_notion:
                    case "Urgente e Importante":
                        prioridad = 1
                    case "Urgente pero no Importante":
                        prioridad = 2
                    case "No Urgente pero Importante":
                        prioridad = 3
                    case "No Urgente y no Importante":
                        prioridad = 4
                    case _:
                        prioridad = 0


                #Preparar Data para enviar a ClickUp
                data = {
                    'name': notion_page['Tarea'],
                    'archived': False,
                    'tags': ['trabajo'],
                    'status': notion_page['Estado'],
                    'priority': prioridad,
                }
                
                print("🔄 Preparando datos para ClickUp:", data)
                
                
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(f"https://api.clickup.com/api/v2/list/{list_id['list']}/task", headers=headers, json=data)
                        print("🔄 Creando tarea en ClickUp...", response.status_code)

                        if response.status_code == 200:
                            id_tareas_creada = response.json().get("id", None)
                            return id_tareas_creada
                        else:
                            raise ValueError(f"Error al crear la tarea: {response.text}")
                        
                except httpx.HTTPStatusError as e:
                    raise httpx.HTTPStatusError(
                        f"HTTP error occurred: {e.response.status_code} - {e.response.text}",
                        request=e.request,
                        response=e.response
                    ) from e
                        

    except ValueError as e:
        print(str(e))
        return None
    
def filtrar_areas(spaces: List[dict], area_notion: str) -> List[dict]:
    
    info_area = {
        "id": None,
        "name": None,
    }
    
    for space in spaces:
       if space.name == area_notion:           
           info_area["id"] = space.id
           info_area["name"] = space.name
        
    return info_area
                 
def filtrar_folders(folders: List[dict], subarea_notion: str) -> List[dict]:
    
    informacion_folder = {
        "id": None,
        "name": None,
        "list": []
    }
    
    for folder in folders:
        if folder.name == subarea_notion:
            informacion_folder["id"] = folder.id
            informacion_folder["name"] = folder.name
            informacion_folder["list"] = folder.lists[0].id
            break

    return informacion_folder

def actualizar_tarea_clickup(id_clickup):
    print("🔄 Actualizando tarea en ClickUp")

   