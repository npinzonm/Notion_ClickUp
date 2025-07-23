import asyncio
from app.routes.clickup import get_team_id, get_spaces, get_folders, get_tasks



if __name__ == "__main__":
    try:
        team_id = asyncio.run(get_team_id())
        
        spaces = asyncio.run(get_spaces(team_id))
        print(f"✅ Espacios encontrados para el Team ID '{team_id}': {[space.name for space in spaces]}")
        
        folder = asyncio.run(get_folders(spaces[2].id))
        print(f"✅ Folders encontrados para {spaces[2].name}: {folder}")
        
        task =  asyncio.run(get_tasks(folder[0].id))
        print(f"✅ Tareas encontradas para {folder[0].name}: {task}")
        
    except Exception as e:
        print(str(e))