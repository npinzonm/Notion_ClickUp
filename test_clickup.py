import asyncio
from app.routes.clickup import click_service



if __name__ == "__main__":
    try:

        data = {'Prioridad': 'Urgente e Importante', 'Subcategoría': 'Reading, Writing', 'Repetir': None, 'Categoría': 'Inglés', 'Migrar': None, 'Fecha': '2025-07-09', 'Día': None, 'Subarea': 'ActiveIT', 'Área': 'Laboral', 'Estado': 'No Iniciado', 'Tarea': 'PRUEBA 2', 'ID_ClickUp': None}

        #llamar a clickup
        asyncio.run(click_service(data))

    except ValueError as e:
        print(str(e))