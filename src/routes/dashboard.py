from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.utils.logger import get_logger
from src.database.config import get_db
from src.models.user import User
from src.services.search_service import SearchService, get_search_service
from src.auth.jwt_handler import get_current_active_user

router = APIRouter()
logger = get_logger(__name__)


@router.get("/statistics")
async def get_dashboard_statistics(
    db: Session = Depends(get_db),
    search_service: SearchService = Depends(get_search_service),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get statistics including total document count from OpenSearch and active topics.
    Returns a JSON object with statistics and success status.
    """
    try:
        # Get statistics from OpenSearch
        search_stats = search_service.get_dashboard_statistics()

        return {
            "statistics": {
                "num_messages": search_stats["num_messages"],
                "num_positive_messages": search_stats["num_positive_messages"],
                "num_negative_messages": search_stats["num_negative_messages"],
                "num_neutral_messages": search_stats["num_neutral_messages"],
                "top_topics": search_stats["top_topics"],
            },
            "success": True,
        }
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        raise


@router.get("/wordcount-analysis")
async def get_wordcount_analysis(
    db: Session = Depends(get_db),
    search_service: SearchService = Depends(get_search_service),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get statistics including total document count from OpenSearch and active topics.
    Returns a JSON object with statistics and success status.
    """
    try:
        # Get statistics from OpenSearch
        search_stats = search_service.get_wordcount_analysis()

        return {
            "words": search_stats["words"],
            "success": True,
        }
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        raise


@router.get("/messages")
async def get_dashboard_messages(
    db: Session = Depends(get_db),
    search_service: SearchService = Depends(get_search_service),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get messages from the feedback analysis index.
    Returns a JSON object with messages and success status.
    """
    try:
        messages = search_service.get_dashboard_messages()

        return {
            **messages,
            "success": True,
        }
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        raise
