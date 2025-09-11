
from app.api.routes_auth import get_current_user
from app.api.routes_project import get_project_service
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from project_management_core.domain.entities.user import User
from project_management_core.domain.services.document_service import DocumentService
from project_management_core.domain.services.project_service import ProjectService
from project_management_core.infrastructure.repositories.db.connection import (
    get_async_session,
)
from project_management_core.infrastructure.repositories.db.document_repository_impl import (
    DocumentRepositoryImpl,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import DocumentMetadata, DocumentResponse

router = APIRouter(prefix='/projects', tags=["documents"])

def get_document_service(session: AsyncSession = 
        Depends(get_async_session)) -> DocumentService:
    """
    Dependency provider for DocumentService.

    Args:
        session (AsyncSession): Asynchronous SQLAlchemy session.

    Returns:
        DocumentService: Service handling document-related operations.
    """
    repo = DocumentRepositoryImpl(session)
    return DocumentService(repo)

async def ensure_project_owner_helper(
    project_id: int,
    current_user: User,
    project_service: ProjectService):
    """
    Ensure that the current user is the owner of the given project.

    Args:
        project_id (int): ID of the project.
        current_user (User): Currently authenticated user.
        project_service (ProjectService): Service for managing projects.

    Returns:
        Project: The project entity if found and owned by the user.

    Raises:
        HTTPException: If project not found or user is not the owner.
    """
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id and current_user.id not in project.participants:
        raise HTTPException(status_code=403, detail="Not authorized to view this project")
    return project



@router.get("/{project_id}/documents")
async def get_documents_from_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
    project_service: ProjectService = Depends(get_project_service)):
    """
    Get all documents for a project owned by the current user.

    Args:
        project_id (int): ID of the project.
        current_user (User): Authenticated user.
        service (DocumentService): Document service dependency.
        project_service (ProjectService): Project service dependency.

    Returns:
        list[DocumentResponse]: List of documents for the project.

    Raises:
        HTTPException: If project not found, not owned by user, or invalid query.
    """
    await ensure_project_owner_helper(project_id, current_user, project_service)
    try:
        result = await service.get_documents_for_project(project_id)
        if result is None:
            return []
        return [DocumentResponse(**res.dict()) for res in result]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/{project_id}/documents')
async def upload_document(
    project_id: int,
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    service: DocumentService = Depends(get_document_service),
    project_service: ProjectService = Depends(get_project_service)):
    """
    Upload a new document to a project.

    Args:
        project_id (int): ID of the project.
        current_user (User): Authenticated user.
        file (UploadFile): File uploaded by user.
        service (DocumentService): Document service dependency.
        project_service (ProjectService): Project service dependency.

    Returns:
        DocumentResponse: Metadata of the uploaded document.

    Raises:
        HTTPException: If project is invalid or upload fails.
    """
    await ensure_project_owner_helper(project_id, current_user, project_service)

    try:
        document = await service.upload_document(file.file, file.filename, 
                            file.content_type, project_id, current_user.id)
        return DocumentResponse(
            id=document.id,
            original_filename=document.original_filename,
            file_size=document.file_size,
            content_type=document.content_type,
            project_id=document.project_id,
            uploaded_by=document.uploaded_by,
            uploaded_at=document.uploaded_at
        )
    except ValueError as e:
        raise HTTPException(status_code= 400, detail=str(e))

@router.get('/{project_id}/documents/{document_id}')
async def get_document_from_project(
    project_id: int,
    document_id: int,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
    project_service: ProjectService = Depends(get_project_service)):
    """
    Retrieve a single document from a project.

    Args:
        project_id (int): ID of the project.
        document_id (int): ID of the document.
        current_user (User): Authenticated user.
        service (DocumentService): Document service dependency.
        project_service (ProjectService): Project service dependency.

    Returns:
        DocumentResponse: The requested document.

    Raises:
        HTTPException: If project not found, not owned by user, or document not found.
    """
    await ensure_project_owner_helper(project_id, current_user, project_service)
    try:
        documents = await service.get_documents_for_project(project_id)
        for doc in documents:
            if doc.id == document_id:
                return DocumentResponse(**doc.dict())
        raise HTTPException(status_code=404, detail="Document not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete('/{project_id}/documents/{document_id}')
async def delete_document_from_project(
    project_id: int,
    document_id: int,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
    project_service: ProjectService = Depends(get_project_service)):
    """
    Delete a document from a project.

    Args:
        project_id (int): ID of the project.
        document_id (int): ID of the document.
        current_user (User): Authenticated user.
        service (DocumentService): Document service dependency.
        project_service (ProjectService): Project service dependency.

    Returns:
        dict: Success message confirming deletion.

    Raises:
        HTTPException: If deletion fails or project not owned by user.
    """
    await ensure_project_owner_helper(project_id, current_user, project_service)
    try:
        await service.delete_document(document_id, current_user.id)
        return {"message": "Document deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/{project_id}/documents/{document_id}/metadata')
async def get_document_metadata(
    project_id: int,
    document_id: int,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
    project_service: ProjectService = Depends(get_project_service)):
    """
    Retrieve metadata for a specific document in a project.

    Args:
        project_id (int): ID of the project.
        document_id (int): ID of the document.
        current_user (User): Authenticated user.
        service (DocumentService): Document service dependency.
        project_service (ProjectService): Project service dependency.

    Returns:
        DocumentMetadata: Metadata of the requested document.

    Raises:
        HTTPException: If project not found, not owned by user, or document not found.
    """
    await ensure_project_owner_helper(project_id, current_user, project_service)
    try:
        documents = await service.get_documents_for_project(project_id)
        for doc in documents:
            if doc.id == document_id:
                return DocumentMetadata(**doc.get_metadata())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
