from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from src.utils.logger import get_logger
from src.database.config import get_db
from src.models.topic import Topic
from src.models.user import User
from src.auth.jwt_handler import get_current_active_user


class TopicCreate(BaseModel):
    label: str
    description: Optional[str] = None


router = APIRouter()
logger = get_logger(__name__)


@router.get("/all")
async def get_topics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a list of all active topics sorted by creation date.
    Returns a JSON object with topics array and success status.
    """
    try:
        topics = (
            db.query(Topic.id, Topic.label, Topic.description)
            .filter(Topic.is_active.is_(True))
            .order_by(Topic.created_at)
            .all()
        )
        return {
            "topics": [
                {"id": topic[0], "label": topic[1], "description": topic[2]}
                for topic in topics
            ],
            "success": True,
        }
    except Exception as e:
        logger.error(f"Error fetching topics: {str(e)}")
        raise


@router.post("/create")
async def create_topic(
    topic: TopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new topic.
    Returns the created topic with success status.
    """
    try:
        topic.label = topic.label.lower()
        existing_topic = db.query(Topic).filter(Topic.label == topic.label).first()
        if existing_topic:
            raise HTTPException(
                status_code=400, detail="Topic with this label already exists"
            )

        db_topic = Topic(label=topic.label, description=topic.description)
        db.add(db_topic)
        db.commit()
        db.refresh(db_topic)

        return {
            "topic": {
                "id": db_topic.id,
                "label": db_topic.label,
                "description": db_topic.description,
            },
            "success": True,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating topic: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create topic")


@router.delete("/{topic_id}")
async def delete_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Soft delete a topic by setting is_active to False.
    Returns success status.
    """
    try:
        topic = (
            db.query(Topic)
            .filter(Topic.id == topic_id, Topic.is_active.is_(True))
            .first()
        )
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")

        topic.is_active = False
        db.commit()

        return {
            "success": True,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating topic: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to deactivate topic")
