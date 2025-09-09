from fastapi import FastAPI

from app.api import routes_auth, routes_document, routes_project

from project_management_core.infrastructure.repositories.db.connection import init_models


app = FastAPI(title="Project Management API")

app.include_router(routes_auth.router)
app.include_router(routes_project.router)
app.include_router(routes_document.router)



@app.on_event("startup")
async def on_startup():
    # Create tables before serving requests
    await init_models()

