"""
Resource management API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from src.data.database import get_db
from src.data.models import Resource, ResourceCreate, ResourceResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=ResourceResponse)
async def create_resource(resource: ResourceCreate, db: Session = Depends(get_db)):
    """Create a new resource"""
    try:
        db_resource = Resource(**resource.dict())
        db.add(db_resource)
        db.commit()
        db.refresh(db_resource)
        
        logger.info(f"Resource created: {db_resource.id}")
        return db_resource
        
    except Exception as e:
        logger.error(f"Error creating resource: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ResourceResponse])
async def get_resources(
    resource_type: Optional[str] = None,
    available: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of resources with optional filters"""
    try:
        query = db.query(Resource)
        
        if resource_type:
            query = query.filter(Resource.type == resource_type)
        if available is not None:
            query = query.filter(Resource.is_available == available)
        
        resources = query.offset(skip).limit(limit).all()
        return resources
        
    except Exception as e:
        logger.error(f"Error fetching resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(resource_id: int, db: Session = Depends(get_db)):
    """Get specific resource by ID"""
    try:
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        return resource
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching resource {resource_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: int,
    resource_update: dict,
    db: Session = Depends(get_db)
):
    """Update resource status and details"""
    try:
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        # Update fields
        for field, value in resource_update.items():
            if hasattr(resource, field):
                setattr(resource, field, value)
        
        db.commit()
        db.refresh(resource)
        
        logger.info(f"Resource updated: {resource_id}")
        return resource
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating resource {resource_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
