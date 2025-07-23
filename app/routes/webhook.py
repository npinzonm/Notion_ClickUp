from typing import  List, Optional
from fastapi import APIRouter, Request, Header
from pydantic import BaseModel
from starlette.responses import JSONResponse
import os

from app.services.notion_service import get_notion_information

#Modelo de datos


class PrioridadModel(BaseModel):
    name: str


class SelectProperty(BaseModel):
    type: str
    label: str
    select: Optional[PrioridadModel] = None


class RelationItem(BaseModel):
    id: str


class RelationProperty(BaseModel):
    type: str
    label: str
    relation: List[RelationItem]
    

class TitleText(BaseModel):
    text: dict  # Puede ser más específico si querés
    plain_text: str


class TitleProperty(BaseModel):
    type: str
    label: str
    title: List[TitleText]


class StatusModel(BaseModel):
    name: str


class StatusProperty(BaseModel):
    type: str
    label: str
    status: StatusModel


class DateModel(BaseModel):
    start: str


class DateProperty(BaseModel):
    type: str
    label: str
    date: DateModel


class GenericProperty(BaseModel):
    id: str
    type: str
    label: str
    select: Optional[PrioridadModel] = None
    relation: Optional[List[RelationItem]] = None
    title: Optional[List[TitleText]] = None
    status: Optional[StatusModel] = None
    date: Optional[DateModel] = None 


class NotionPage(BaseModel):
    object: str
    id: str
    properties: List[GenericProperty]

router = APIRouter()

NOTION_VERIFICATION_TOKEN = os.getenv("NOTION_VERIFICATION_TOKEN")

@router.post("/notion")
async def receive_notion_event(
    request: Request,
    notion_token: str = Header(None)
):
    # Verificar el token de verificación de Notion
    if notion_token != NOTION_VERIFICATION_TOKEN:
        return JSONResponse(
            status_code=403,
            content={"message": "Forbidden: Invalid Notion verification token"}
        )
        
    # Procesar el evento de Notion
    try:
        payload = await request.json()
        
        for page_data in payload:
            page = NotionPage(**page_data)
            info_notion = prepare_clickup_informacion(page)
            print("Data preparada:", info_notion)
            
            info_click = await get_notion_information(info_notion)
            print("Información enriquecida:", info_click)

        return {"message": "Procesado correctamente"}
        
    except Exception as e:
        print(f"Error processing Notion event: {e}")
        
def prepare_clickup_informacion(data: NotionPage) -> dict:
    resultado = {}

    for prop in data.properties:
        if prop.label == "✅ Tarea" and prop.title:
            resultado["titulo"] = prop.title[0].plain_text
        elif prop.label == "Prioridad" and prop.select:
            resultado["prioridad"] = prop.select.name
        elif prop.label == "Subcategoría" and prop.relation:
            resultado["subcategorias_ids"] = [r.id for r in prop.relation]
        elif prop.label == "Descripción" and prop.title:
            resultado["descripcion"] = prop.title[0].plain_text
        elif prop.label == "Estado" and prop.status:
            resultado["estado"] = prop.status.name
        elif prop.label == "Fecha" and prop.date:
            resultado["fecha"] = prop.date.start
        elif prop.label == "Subarea" and prop.relation:
            resultado["subarea_ids"] = [r.id for r in prop.relation]

    return resultado