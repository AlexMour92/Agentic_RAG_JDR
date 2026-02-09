import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.endpoints import router as api_router
from app.core.config import settings

app = FastAPI(title="L'Archiviste")

# Inclusion des routes
app.include_router(api_router, prefix="/api")

# Fichiers statiques
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)