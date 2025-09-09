from fastapi import APIRouter, Depends, HTTPException
from project_management_core.domain.entities.user import User
from project_management_core.domain.services.project_service import (
    ProjectNotFoundError,
    ProjectService,
    ProjectServiceError,
)
from project_management_core.domain.services.user_service import UserNotFoundError, UserService
from project_management_core.infrastructure.repositories.db.connection import (
    get_async_session,
)
from project_management_core.infrastructure.repositories.db.project_repository_impl import (
    ProjectRepositoryImpl,
)

from project_management_core.infrastructure.repositories.db.user_repository_impl import (
    UserRepositoryImpl,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes_auth import get_current_user, get_user_service
from app.schemas import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])

def get_project_service(
    session: AsyncSession = Depends(get_async_session)) -> ProjectService:
    """
    Dependency provider for ProjectService.

    Args:
        session (AsyncSession): Asynchronous SQLAlchemy session.

    Returns:
        ProjectService: Service handling project-related operations.
    """
    repo = ProjectRepositoryImpl(session)
    return ProjectService(repo)




@router.post('')
async def create_project(payload: ProjectCreate, 
                        current_user : User = Depends(get_current_user),
                        service: ProjectService = Depends(get_project_service)):
    """
    Create a new project owned by the current user.

    Args:
        payload (ProjectCreate): Data for creating a project (name, description).
        current_user (User): Authenticated user (project owner).
        service (ProjectService): Project service dependency.

    Returns:
        Project: Created project object.

    Raises:
        HTTPException: If project creation fails.
    """
    try:
        return await service.create_project(
            name =payload.name, 
            description =payload.description, 
            owner_id = current_user.id)
    except ProjectServiceError:
        raise HTTPException(status_code=400, detail="Unable to create project")

@router.get("")
async def get_projects(
    current_user : User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)):
    """
    Retrieve all projects owned by the current user.

    Args:
        current_user (User): Authenticated user.
        service (ProjectService): Project service dependency.

    Returns:
        list[Project]: List of projects owned by the user.

    Raises:
        HTTPException: If user not found.
    """
    try:
        return await service.get_projects_for_user(current_user.id) 
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{project_id}")
async def get_project_by_id(
    project_id: int,
    current_user : User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    """
    Retrieve a project by its ID.

    Args:
        project_id (int): ID of the project to retrieve.
        current_user (User): Authenticated user.
        service (ProjectService): Project service dependency.

    Returns:
        ProjectResponse: Project details.

    Raises:
        HTTPException:
            - 404 if project not found.
            - 403 if user is not authorized to access the project.
    """
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, 
        detail="Not authorized to view this project")

    return ProjectResponse(**project.dict())
        

@router.put("/{project_id}")
async def update_project(project_id: int, payload: ProjectUpdate, 
            service: ProjectService = Depends(get_project_service)):
    """
    Update a project's details.

    Args:
        project_id (int): ID of the project to update.
        payload (ProjectUpdate): Updated project data (name, description).
        service (ProjectService): Project service dependency.

    Returns:
        ProjectResponse: Updated project details.

    Raises:
        HTTPException: If update fails.
    """
    try:
        result = await service.update_project(project_id, 
        payload.name, 
        payload.description)
        return ProjectResponse(**result.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current_user : User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)):
    """
    Delete a project by ID if owned by the current user.

    Args:
        project_id (int): ID of the project to delete.
        current_user (User): Authenticated user.
        service (ProjectService): Project service dependency.

    Returns:
        dict: Success message confirming deletion.

    Raises:
        HTTPException:
            - 403 if user not authorized to delete the project.
            - 404 if project not found.
            - 400 if deletion fails due to service error.
    """
    project = await service.get_project(project_id)
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, 
        detail="Not authorized to delete this project")
    try:
        await service.delete_project(project_id)
        return {"message": "Project deleted successfully"}
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ProjectServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
