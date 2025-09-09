from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import ProjectCreate, ProjectResponse, ProjectUpdate
from project_management_core.domain.services.project_service import ProjectService, ProjectServiceError, ProjectNotFoundError
from project_management_core.domain.services.user_service import  UserNotFoundError

from project_management_core.infrastructure.repositories.db.project_repository_impl import ProjectRepositoryImpl
from project_management_core.infrastructure.repositories.db.connection import get_async_session


router = APIRouter(prefix="/projects", tags=["projects"])

def get_project_service(session: AsyncSession = Depends(get_async_session)) -> ProjectService:
    repo = ProjectRepositoryImpl(session)
    return ProjectService(repo)


@router.post('')
async def create_project(payload: ProjectCreate, service: ProjectService = Depends(get_project_service)):
    try:
        return await service.create_project(payload.name, payload.description, payload.owner_id)
    except ProjectServiceError:
        raise HTTPException(status_code=400, detail="Unable to create project")

@router.get("/user/{user_id}")
async def get_projects(user_id: int, service: ProjectService = Depends(get_project_service)):
    try:
        return await service.get_projects_for_user(user_id) 
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{project_id}")
async def get_project_by_id(
    project_id: int,
    service: ProjectService = Depends(get_project_service)
):
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ProjectResponse(**project.dict())

@router.put("/{project_id}")
async def update_project(project_id: int, payload: ProjectUpdate, service: ProjectService = Depends(get_project_service)):
    try:
        result = await service.update_project(project_id, payload.name, payload.description)
        return ProjectResponse(**result.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{project_id}")
async def delete_project(project_id: int, service: ProjectService = Depends(get_project_service)):
    try:
        return await service.delete_project(project_id) 
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ProjectServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
