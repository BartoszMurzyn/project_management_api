from fastapi import FastAPI

from app.api import routes_auth, routes_document, routes_project

app = FastAPI(title="Project Management API")

app.include_router(routes_auth.router)
app.include_router(routes_project.router)
app.include_router(routes_document.router)
