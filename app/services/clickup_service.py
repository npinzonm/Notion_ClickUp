import asyncio
import logging
from typing import List, Optional
from fastapi import APIRouter, Request, Header
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, Field, ValidationError
from starlette.responses import JSONResponse
import os, httpx
from dotenv import load_dotenv

router = APIRouter()

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Modelo para representar un espacio
class Status(BaseModel):
    status: str
    
class Space(BaseModel):
    id: str
    name: str
    statuses: Optional[List[Status]] = Field(default_factory=list)

class ListFolder(BaseModel):
    id: str
    name: str

class Folder(BaseModel):
    id: str
    name: str
    lists: Optional[List[ListFolder]] = Field(default_factory=list)


#Carga de variables de entorno    
load_dotenv()
CLICKUP_VERIFICATION_TOKEN = os.getenv("CLICKUP_VERIFICATION_TOKEN")

if( not CLICKUP_VERIFICATION_TOKEN):
    logging.critical("🚨 ERROR: CLICKUP_VERIFICATION_TOKEN no está configurado. Por favor, configúralo en tu archivo .env")
    raise ValueError("🚨 CLICKUP_VERIFICATION_TOKEN no está configurado")

headers = {
    "Authorization": f"{CLICKUP_VERIFICATION_TOKEN}",
    "Content-Type": "application/json"
}


# Obtener el ID del team
async def get_team_id(workspace_name: str = "Nathalie Pinzon's Workspace") -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.clickup.com/api/v2/team", headers=headers)
            response.raise_for_status() # Lanza un error si la respuesta no es 200 OK
            
            if response.status_code == 200:
                data = response.json()
                for team in data.get("teams", []):
                    if team.get("name") == workspace_name:
                        return team.get("id")
                raise ValueError(f"Team '{workspace_name}' not found")
            else:
                raise ValueError(f"Error al obtener el team ID: {response.text}")
    except httpx.HTTPStatusError as e:
        raise httpx.HTTPStatusError(
            f"HTTP error occurred: {e.response.status_code} - {e.response.text}",
            request=e.request,
            response=e.response
        ) from e
        
        
# Obtener espacios
async def get_spaces(team_id: str) -> list:
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.clickup.com/api/v2/team/{team_id}/space", headers=headers)
            # response.raise_for_status() 
            
            if response.status_code == 200:
                raw_spaces = response.json().get("spaces", [])
                spaces = []
                for space_data in raw_spaces:
                    try:
                        spaces.append(Space(**space_data))
                    except ValidationError as e:
                        logging.error(f"Error de validación Pydantic al parsear un espacio: {e} - Datos: {space_data}")
                        # Puedes decidir si quieres ignorar este espacio o lanzar una excepción
                        continue 
                
                logging.info(f"Se obtuvieron {len(spaces)} espacios para el Team ID: '{team_id}'")
                return spaces
                
            else:
                raise ValueError(f"Error al obtener los espacios: {response.text}")
    except httpx.HTTPStatusError as e:
        raise httpx.HTTPStatusError(
            f"HTTP error occurred: {e.response.status_code} - {e.response.text}",
            request=e.request,
            response=e.response
        ) from e
        
#Obtener folders de un espacio
async def get_folders(space_id: str) -> list:
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.clickup.com/api/v2/space/{space_id}/folder", headers=headers)
            response.raise_for_status()
            
            if response.status_code == 200:
                raw_folders = response.json().get("folders", [])
                
                folders = []
                for folder_data in raw_folders:
                    try:
                        folders.append(Folder(**folder_data))
                    except ValidationError as e:
                        logging.error(f"Error de validación Pydantic al parsear un folder: {e} - Datos: {folder_data}")
                        continue
                    
                logging.info(f"Se obtuvieron {len(folders)} folders para el Space ID: '{space_id}'")
                return folders

            else:
                raise ValueError(f"Error al obtener los folders: {response.text}")
    except httpx.HTTPStatusError as e:
        raise httpx.HTTPStatusError(
            f"HTTP error occurred: {e.response.status_code} - {e.response.text}",
            request=e.request,
            response=e.response
        ) from e


    
#Obenter tareas y verificar si existen
async def get_tasks(list_id: str) -> list:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.clickup.com/api/v2/list/{list_id}/task", headers=headers)
            response.raise_for_status()
            
            if response.status_code == 200:
                tasks = response.json().get("tasks", [])
                logging.info(f"Se obtuvieron {len(tasks)} tareas para el List ID: '{list_id}'")
                return tasks
            else:
                raise ValueError(f"Error al obtener las tareas: {response.text}")
    except httpx.HTTPStatusError as e:
        raise httpx.HTTPStatusError(
            f"HTTP error occurred: {e.response.status_code} - {e.response.text}",
            request=e.request,
            response=e.response
        ) from e