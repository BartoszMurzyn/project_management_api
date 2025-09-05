from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.responses import FileResponse

from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

from app.schemas import DocumentResponse, DocumentMetadata

from project_management_core.domain.services.document_service import DocumentService
from project_management_core.infrastructure.repositories.db.document_repository_impl import DocumentRepositoryImpl
from project_management_core.infrastructure.repositories.db.connection import get_async_session

router = APIRouter(prefix='/projects', tags=["documents"])

def get_document_service(session: AsyncSession = Depends(get_async_session)) -> DocumentService:
    repo = DocumentRepositoryImpl(session)
    return DocumentService(repo)


@router.get("/{project_id}/documents")
async def get_documents_from_project(project_id: int, service: DocumentService = Depends(get_document_service)):
    try:
        result = await service.get_documents_for_project(project_id)
        if result is None:
            return []
        return [DocumentResponse(**res.dict()) for res in result]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/{project_id}/documents')
async def upload_document(project_id: int, uploaded_by: int, file: UploadFile = File(...), service: DocumentService = Depends(get_document_service)):
    try:
        document = await service.upload_document(file.file, file.filename, file.content_type, project_id, uploaded_by)
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
async def get_document_from_project(project_id: int, document_id: int, service: DocumentService = Depends(get_document_service)):
        try:
            documents = await service.get_documents_for_project(project_id)
            for doc in documents:
                if doc.id == document_id:
                    return DocumentResponse(**doc.dict())
            raise HTTPException(status_code=404, detail="Document not found")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

@router.delete('/{project_id}/documents/{document_id}')
async def delete_document_from_project(project_id: int, document_id: int, uploaded_by: int, service: DocumentService = Depends(get_document_service)):
    try:
        result = await service.delete_document(document_id, uploaded_by)
        return {"message": "Document deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/{project_id}/documents/{document_id}/metadata')
async def get_document_metadata(project_id: int, document_id: int, service: DocumentService = Depends(get_document_service)):
    try:
        documents = await service.get_documents_for_project(project_id)
        for doc in documents:
            if doc.id == document_id:
                return DocumentMetadata(**doc.get_metadata())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
