from typing import List, Optional
from fastapi import APIRouter
import httpx
from pydantic import BaseModel
from starlette.responses import JSONResponse
import os

from dotenv import load_dotenv

load_dotenv()


NOMBRE_CATEGORIA_KEY = "Nombre Categoría"
NAME_KEY = "Name"
NOMBRE_AREA_KEY = "Nombre area"
NAME_KEY = "Name"


# Modelo de datos
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
    "Content-Type": "application/json",
}


async def complete_data_notion(data_preparada: dict) -> dict:

    # Sacar Id de subcategoría y Subárea
    ids = consultar_ids(data_preparada)

    consulta_notion = await consulta_notion_api(ids)

    return consulta_notion


def es_lista_no_vacia(valor):
    return isinstance(valor, list) and len(valor) > 0

def normalizar_valor(valor):
    """Convierte un valor único o lista en lista"""
    if es_lista_no_vacia(valor):
        return valor
    elif valor is not None:
        return [valor]
    return []

def formatear_lista(lista):
    if not lista:
        return None
    return lista[0] if len(lista) == 1 else ",".join(lista)

def consultar_ids(data: dict) -> dict:
    subcategorias = normalizar_valor(data.get("Subcategoría"))
    subareas = normalizar_valor(data.get("Subarea"))

    return {
        "subcategorias": formatear_lista(subcategorias),
        "subareas": formatear_lista(subareas)
    }


# Funciones llamado a api para consulta
async def consulta_notion_api(data: dict):
    url_pages = "https://api.notion.com/v1/pages/"

    subcategorias = data.get("subcategorias")
    subareas = data.get("subareas")


    categoria = await consulta_notion_api_categoria(subcategorias, url_pages)
    area = await consulta_notion_api_area(subareas, url_pages)


    resultado_final = {
        "categorias": categoria.get("categoria"),
        "subcategorias": categoria.get("subcategoria"),
        "area": area.get("area"),
        "subarea": area.get("subarea"),
    }
    return resultado_final


async def consulta_notion_api_categoria(data: dict, url_pages: str):
    lista_ids = data.split(",")
    resultados = {"categoria": [], "subcategoria": []}

    async with httpx.AsyncClient() as client:
        for id in lista_ids:
            categoria, subcategoria = await procesar_pagina(id, client, url_pages)
            if categoria and categoria not in resultados["categoria"]:
                resultados["categoria"].append(categoria)
            if subcategoria and subcategoria not in resultados["subcategoria"]:
                resultados["subcategoria"].append(subcategoria)

    return {
        "categoria": unir_valores(resultados["categoria"]),
        "subcategoria": unir_valores(resultados["subcategoria"])
    }


async def procesar_pagina(id: str, client: httpx.AsyncClient, url_pages: str):
    url = f"{url_pages}{id}"
    try:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(f"Error al consultar Notion API para ID {id}: {e.response.status_code} - {e.response.text}")
        return None, None

    try:
        json_data = response.json()
        categoria = json_data["properties"][NOMBRE_CATEGORIA_KEY]["formula"]["string"]
        subcategoria = json_data["properties"][NAME_KEY]["title"][0]["text"]["content"]
        return categoria, subcategoria
    except (KeyError, IndexError) as e:
        print(f"No se encontró alguna propiedad esperada para el ID: {id}")
        return None, None


def unir_valores(lista: list) -> str | None:
    if not lista:
        return None
    return lista[0] if len(lista) == 1 else ", ".join(lista)


async def consulta_notion_api_area(data: dict, url_pages: str):
    list_ids = data.split(",")
    resultados = {"area": [], "subarea": []}

    async with httpx.AsyncClient() as client:
        for id in list_ids:
            area, subarea = await procesar_pagina_area(id, client, url_pages)
            if area and area not in resultados["area"]:
                resultados["area"].append(area)
            if subarea and subarea not in resultados["subarea"]:
                resultados["subarea"].append(subarea)

    return {
        "area": unir_valores(resultados["area"]),
        "subarea": unir_valores(resultados["subarea"])
    }


async def procesar_pagina_area(id: str, client: httpx.AsyncClient, url_pages: str):
    url = f"{url_pages}{id}"
    try:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(f"Error al consultar Notion API para ID {id}: {e.response.status_code} - {e.response.text}")
        return None, None

    try:
        json_data = response.json()
        area = json_data["properties"][NOMBRE_AREA_KEY]["formula"]["string"]
        subarea = json_data["properties"][NAME_KEY]["title"][0]["text"]["content"]
        return area, subarea
    except (KeyError, IndexError):
        print(f"No se encontró alguna propiedad esperada para el ID: {id}")
        return None, None


def unir_valores(lista: list) -> str | None:
    if not lista:
        return None
    return lista[0] if len(lista) == 1 else ", ".join(lista)