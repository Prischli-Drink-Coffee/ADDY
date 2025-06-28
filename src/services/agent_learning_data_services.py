from typing import Optional, Dict, Any, List
from datetime import datetime
import json
from fastapi import HTTPException, status
from src.database.models import AgentLearningData
from src.repository import agent_learning_data_repository
from src.utils.custom_logging import get_logger

log = get_logger(__name__)


class LearningDataNotFoundError(HTTPException):
    def __init__(self, data_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Learning data {data_id} not found'
        )


class AgentNotFoundError(HTTPException):
    def __init__(self, agent_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Agent {agent_id} not found'
        )


def get_all_learning_data() -> List[AgentLearningData]:
    """Get all agent learning data entries"""
    learning_data = agent_learning_data_repository.get_all_learning_data()
    return [AgentLearningData(**data) for data in learning_data]


def get_learning_data_by_id(data_id: int) -> AgentLearningData:
    """Get specific learning data by its ID"""
    data = agent_learning_data_repository.get_learning_data_by_id(data_id)
    if not data:
        raise LearningDataNotFoundError(data_id)
    return AgentLearningData(**data)


def get_learning_data_by_agent(agent_id: int) -> List[AgentLearningData]:
    """Get all learning data for a specific agent"""
    learning_data = agent_learning_data_repository.get_learning_data_by_agent(agent_id)
    return [AgentLearningData(**data) for data in learning_data]


def get_learning_data_by_type(data_type: str) -> List[AgentLearningData]:
    """Get learning data of specific type"""
    learning_data = agent_learning_data_repository.get_learning_data_by_type(data_type)
    return [AgentLearningData(**data) for data in learning_data]


def create_learning_data(learning_data: Dict[str, Any]) -> AgentLearningData:
    """Create new agent learning data entry"""
    # Validate required fields
    required_fields = ['agent_id', 'data_type', 'training_data']
    for field in required_fields:
        if field not in learning_data or learning_data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )

    # Validate training_data is a valid JSON-serializable structure
    try:
        training_data = json.dumps(learning_data['training_data'])
    except (TypeError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid training_data format: {str(e)}"
        )

    # Prepare metadata if provided
    metadata = None
    if 'metadata' in learning_data and learning_data['metadata'] is not None:
        try:
            metadata = json.dumps(learning_data['metadata'])
        except (TypeError, ValueError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid metadata format: {str(e)}"
            )

    # Prepare model
    data = AgentLearningData(
        AgentID=learning_data['agent_id'],
        DataType=learning_data['data_type'],
        TrainingData=learning_data['training_data'],
        Source=learning_data.get('source'),
        Metadata=learning_data.get('metadata'),
        CreatedBy=learning_data.get('created_by'),
        IsProcessed=False,
        CreatedAt=datetime.now(),
        UpdatedAt=datetime.now()
    )

    # Create in repository
    data_id = agent_learning_data_repository.create_learning_data(data)
    return get_learning_data_by_id(data_id)


def update_learning_data(data_id: int, updates: Dict[str, Any]) -> AgentLearningData:
    """Update existing learning data entry"""
    # Check if data exists
    existing_data = get_learning_data_by_id(data_id)
    
    # Validate JSON fields
    if 'training_data' in updates and updates['training_data'] is not None:
        try:
            json.dumps(updates['training_data'])
        except (TypeError, ValueError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid training_data format: {str(e)}"
            )
    
    if 'metadata' in updates and updates['metadata'] is not None:
        try:
            json.dumps(updates['metadata'])
        except (TypeError, ValueError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid metadata format: {str(e)}"
            )

    # Update in repository
    agent_learning_data_repository.update_learning_data(data_id, updates)
    return get_learning_data_by_id(data_id)


def mark_as_processed(data_id: int, processed_metadata: Dict[str, Any] = None) -> AgentLearningData:
    """Mark learning data as processed and update metadata"""
    updates = {"is_processed": True}
    
    if processed_metadata:
        try:
            json.dumps(processed_metadata)
            updates["metadata"] = processed_metadata
        except (TypeError, ValueError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid processed_metadata format: {str(e)}"
            )
    
    return update_learning_data(data_id, updates)


def delete_learning_data(data_id: int) -> Dict[str, str]:
    """Delete a learning data entry"""
    get_learning_data_by_id(data_id)  # Verify exists
    agent_learning_data_repository.delete_learning_data(data_id)
    return {"message": "Learning data deleted successfully"}


def delete_agent_learning_data(agent_id: int) -> Dict[str, str]:
    """Delete all learning data for a specific agent"""
    count = agent_learning_data_repository.delete_agent_learning_data(agent_id)
    return {"message": f"Deleted {count} learning data entries for agent {agent_id}"}


def get_unprocessed_learning_data() -> List[AgentLearningData]:
    """Get all unprocessed learning data"""
    learning_data = agent_learning_data_repository.get_unprocessed_learning_data()
    return [AgentLearningData(**data) for data in learning_data]


def get_learning_data_from_source(source: str) -> List[AgentLearningData]:
    """Get learning data from specific source"""
    learning_data = agent_learning_data_repository.get_learning_data_from_source(source)
    return [AgentLearningData(**data) for data in learning_data]


def get_recent_learning_data(hours: int = 24) -> List[AgentLearningData]:
    """Get recent learning data entries within specified hours"""
    if hours <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hours parameter must be positive"
        )
    
    learning_data = agent_learning_data_repository.get_recent_learning_data(hours)
    return [AgentLearningData(**data) for data in learning_data]


def get_learning_data_by_metadata_key(key: str, value: Any = None) -> List[AgentLearningData]:
    """Get learning data containing specific metadata key (and optionally value)"""
    if not key or not isinstance(key, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Key must be a non-empty string"
        )
    
    learning_data = agent_learning_data_repository.get_learning_data_by_metadata_key(key, value)
    return [AgentLearningData(**data) for data in learning_data]


def count_learning_data_by_agent(agent_id: int) -> Dict[str, Any]:
    """Count learning data statistics for specific agent"""
    return agent_learning_data_repository.count_learning_data_by_agent(agent_id)


def get_learning_data_stats() -> Dict[str, Any]:
    """Get overall learning data statistics"""
    return agent_learning_data_repository.get_learning_data_stats()