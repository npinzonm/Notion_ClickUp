from fastapi import FastAPI
from dotenv import load_dotenv
import os
from app.routes import webhook, clickup, notion

# Cargar variables de entorno
load_dotenv()

# Verificar que el token está presente
NOTION_VERIFICATION_TOKEN = os.getenv("NOTION_VERIFICATION_TOKEN")
if not NOTION_VERIFICATION_TOKEN:
    raise ValueError("🚨 NOTION_VERIFICATION_TOKEN no está configurado en .env")

print("🔑 Token de verificación cargado correctamente")

app = FastAPI()

# Incluir los routers
app.include_router(webhook.router)
app.include_router(notion.router, prefix="/notion", tags=["notion"])


@app.get("/")
async def root():
    return {"message": "Welcome to the Notion ClickUp Integration API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)