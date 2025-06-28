from typing import Optional, Dict, Any, List
from datetime import datetime
import json
from fastapi import HTTPException, status
from src.database.models import AgentSimulationFeedback
from src.repository import agent_simulation_feedback_repository
from src.utils.custom_logging import get_logger

log = get_logger(__name__)


class FeedbackNotFoundError(HTTPException):
    def __init__(self, feedback_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Feedback {feedback_id} not found'
        )


class SimulationNotFoundError(HTTPException):
    def __init__(self, simulation_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Simulation {simulation_id} not found'
        )


def get_all_feedback() -> List[AgentSimulationFeedback]:
    """Get all agent simulation feedback entries"""
    feedback_data = agent_simulation_feedback_repository.get_all_feedback()
    return [AgentSimulationFeedback(**feedback) for feedback in feedback_data]


def get_feedback_by_id(feedback_id: int) -> AgentSimulationFeedback:
    """Get specific feedback entry by its ID"""
    feedback_data = agent_simulation_feedback_repository.get_feedback_by_id(feedback_id)
    if not feedback_data:
        raise FeedbackNotFoundError(feedback_id)
    return AgentSimulationFeedback(**feedback_data)


def get_feedback_by_simulation(simulation_id: int) -> List[AgentSimulationFeedback]:
    """Get all feedback for a specific simulation"""
    feedback_data = agent_simulation_feedback_repository.get_feedback_by_simulation(simulation_id)
    return [AgentSimulationFeedback(**feedback) for feedback in feedback_data]


def get_feedback_by_user(user_id: int) -> List[AgentSimulationFeedback]:
    """Get all feedback submitted by a specific user"""
    feedback_data = agent_simulation_feedback_repository.get_feedback_by_user(user_id)
    return [AgentSimulationFeedback(**feedback) for feedback in feedback_data]


def get_feedback_by_agent(agent_id: int) -> List[AgentSimulationFeedback]:
    """Get all feedback for simulations of a specific agent"""
    feedback_data = agent_simulation_feedback_repository.get_feedback_by_agent(agent_id)
    return [AgentSimulationFeedback(**feedback) for feedback in feedback_data]


def create_feedback(feedback_data: Dict[str, Any]) -> AgentSimulationFeedback:
    """Create new feedback for an agent simulation"""
    # Validate required fields
    required_fields = ['simulation_id', 'user_id', 'rating']
    for field in required_fields:
        if field not in feedback_data or feedback_data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )

    # Validate rating range
    if not (1 <= feedback_data['rating'] <= 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )

    # Prepare feedback model
    feedback = AgentSimulationFeedback(
        SimulationID=feedback_data['simulation_id'],
        UserID=feedback_data['user_id'],
        Rating=feedback_data['rating'],
        FeedbackText=feedback_data.get('feedback_text'),
        FeedbackDetails=feedback_data.get('feedback_details'),
        CreatedAt=datetime.now(),
        UpdatedAt=datetime.now()
    )

    # Create feedback in repository
    feedback_id = agent_simulation_feedback_repository.create_feedback(feedback)
    return get_feedback_by_id(feedback_id)


def update_feedback(feedback_id: int, updates: Dict[str, Any]) -> AgentSimulationFeedback:
    """Update existing feedback entry"""
    # Check if feedback exists
    existing_feedback = get_feedback_by_id(feedback_id)
    
    # Validate rating if present in updates
    if 'rating' in updates and updates['rating'] is not None:
        if not (1 <= updates['rating'] <= 5):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )

    # Prepare update data
    update_data = {}
    if 'rating' in updates and updates['rating'] is not None:
        update_data['rating'] = updates['rating']
    if 'feedback_text' in updates:
        update_data['feedback_text'] = updates['feedback_text']
    if 'feedback_details' in updates:
        update_data['feedback_details'] = updates['feedback_details']

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields to update"
        )

    # Update in repository
    agent_simulation_feedback_repository.update_feedback(feedback_id, update_data)
    return get_feedback_by_id(feedback_id)


def delete_feedback(feedback_id: int) -> Dict[str, str]:
    """Delete a feedback entry"""
    get_feedback_by_id(feedback_id)  # Verify feedback exists
    agent_simulation_feedback_repository.delete_feedback(feedback_id)
    return {"message": "Feedback deleted successfully"}


def delete_simulation_feedback(simulation_id: int) -> Dict[str, str]:
    """Delete all feedback for a specific simulation"""
    count = agent_simulation_feedback_repository.delete_simulation_feedback(simulation_id)
    return {"message": f"Deleted {count} feedback entries for simulation {simulation_id}"}


def get_average_rating_by_simulation(simulation_id: int) -> Dict[str, float]:
    """Get average rating for a specific simulation"""
    avg_rating = agent_simulation_feedback_repository.get_average_rating_by_simulation(simulation_id)
    return {"average_rating": avg_rating}


def get_average_rating_by_agent(agent_id: int) -> Dict[str, float]:
    """Get average rating across all simulations for a specific agent"""
    avg_rating = agent_simulation_feedback_repository.get_average_rating_by_agent(agent_id)
    return {"average_rating": avg_rating}


def get_agent_feedback_stats(agent_id: int) -> Dict[str, Any]:
    """Get detailed feedback statistics for an agent"""
    return agent_simulation_feedback_repository.get_agent_feedback_stats(agent_id)


def get_recent_feedback(hours: int = 24) -> List[AgentSimulationFeedback]:
    """Get recent feedback entries within specified hours"""
    if hours <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hours parameter must be positive"
        )
    
    feedback_data = agent_simulation_feedback_repository.get_recent_feedback(hours)
    return [AgentSimulationFeedback(**feedback) for feedback in feedback_data]


def get_feedback_with_comments() -> List[AgentSimulationFeedback]:
    """Get all feedback entries that include text comments"""
    feedback_data = agent_simulation_feedback_repository.get_feedback_with_comments()
    return [AgentSimulationFeedback(**feedback) for feedback in feedback_data]


def get_feedback_stats() -> Dict[str, Any]:
    """Get overall feedback statistics"""
    return agent_simulation_feedback_repository.get_feedback_stats()