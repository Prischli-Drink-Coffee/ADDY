from typing import Optional, Dict, Any, List
from datetime import datetime
import json
from fastapi import HTTPException, status
from src.repository import agent_simulation_messages_repository
from src.database.models import AgentSimulationMessages
from src.utils.custom_logging import get_logger

log = get_logger(__name__)


class SimulationMessageNotFoundError(HTTPException):
    def __init__(self, message_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Simulation message with ID {message_id} not found'
        )


class SimulationMessageValidationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


def get_all_simulation_messages() -> List[AgentSimulationMessages]:
    """Получить все сообщения симуляций агентов"""
    messages_data = agent_simulation_messages_repository.get_all_simulation_messages()
    return [_convert_db_message(msg) for msg in messages_data]


def get_message_by_id(message_id: int) -> AgentSimulationMessages:
    """Получить сообщение симуляции по ID"""
    message_data = agent_simulation_messages_repository.get_message_by_id(message_id)
    if not message_data:
        raise SimulationMessageNotFoundError(message_id)
    return _convert_db_message(message_data)


def get_messages_by_simulation(simulation_id: int) -> List[AgentSimulationMessages]:
    """Получить все сообщения конкретной симуляции"""
    messages_data = agent_simulation_messages_repository.get_messages_by_simulation(simulation_id)
    return [_convert_db_message(msg) for msg in messages_data]


def create_simulation_message(
    simulation_id: int,
    message_content: str,
    role: str,
    message_type: str,
    metadata: Optional[Dict[str, Any]] = None
) -> AgentSimulationMessages:
    """Создать новое сообщение симуляции"""
    # Валидация входных данных
    if not message_content or len(message_content.strip()) == 0:
        raise SimulationMessageValidationError("Message content cannot be empty")
    
    if len(message_content) > 5000:
        raise SimulationMessageValidationError("Message is too long (max 5000 characters)")
    
    if role not in ['system', 'user', 'assistant', 'function']:
        raise SimulationMessageValidationError("Invalid message role")
    
    message = AgentSimulationMessages(
        SimulationID=simulation_id,
        MessageContent=message_content,
        Role=role,
        MessageType=message_type,
        Metadata=metadata,
        CreatedAt=datetime.now()
    )
    
    message_id = agent_simulation_messages_repository.create_message(message)
    return get_message_by_id(message_id)


def update_message(
    message_id: int,
    updates: Dict[str, Any]
) -> AgentSimulationMessages:
    """Обновить сообщение симуляции"""
    existing = get_message_by_id(message_id)
    
    # Валидация обновлений
    if 'MessageContent' in updates:
        if not updates['MessageContent'] or len(updates['MessageContent'].strip()) == 0:
            raise SimulationMessageValidationError("Message content cannot be empty")
        if len(updates['MessageContent']) > 5000:
            raise SimulationMessageValidationError("Message is too long (max 5000 characters)")
    
    if 'Role' in updates and updates['Role'] not in ['system', 'user', 'assistant', 'function']:
        raise SimulationMessageValidationError("Invalid message role")
    
    update_data = {
        'message_content': updates.get('MessageContent'),
        'role': updates.get('Role'),
        'message_type': updates.get('MessageType'),
        'metadata': updates.get('Metadata')
    }
    
    # Удаляем None значения
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    if not update_data:
        raise SimulationMessageValidationError("No valid fields to update")
    
    agent_simulation_messages_repository.update_message(message_id, update_data)
    return get_message_by_id(message_id)


def delete_message(message_id: int) -> Dict[str, str]:
    """Удалить сообщение симуляции"""
    get_message_by_id(message_id)  # Проверяем существование
    agent_simulation_messages_repository.delete_message(message_id)
    return {"message": f"Simulation message {message_id} deleted successfully"}


def delete_simulation_messages(simulation_id: int) -> Dict[str, int]:
    """Удалить все сообщения конкретной симуляции"""
    deleted_count = agent_simulation_messages_repository.delete_simulation_messages(simulation_id)
    return {"deleted_count": deleted_count}


def get_messages_by_role(simulation_id: int, role: str) -> List[AgentSimulationMessages]:
    """Получить сообщения симуляции по конкретной роли"""
    if role not in ['system', 'user', 'assistant', 'function']:
        raise SimulationMessageValidationError("Invalid message role")
    
    messages_data = agent_simulation_messages_repository.get_messages_by_role(simulation_id, role)
    return [_convert_db_message(msg) for msg in messages_data]


def get_messages_by_type(simulation_id: int, message_type: str) -> List[AgentSimulationMessages]:
    """Получить сообщения симуляции по типу сообщения"""
    messages_data = agent_simulation_messages_repository.get_messages_by_type(simulation_id, message_type)
    return [_convert_db_message(msg) for msg in messages_data]


def get_last_message(simulation_id: int) -> Optional[AgentSimulationMessages]:
    """Получить последнее сообщение в симуляции"""
    message_data = agent_simulation_messages_repository.get_last_message(simulation_id)
    return _convert_db_message(message_data) if message_data else None


def get_conversation_from_simulation(simulation_id: int) -> List[Dict[str, Any]]:
    """Получить все сообщения симуляции, отформатированные как диалог"""
    messages = get_messages_by_simulation(simulation_id)
    return [
        {
            "role": msg.Role,
            "content": msg.MessageContent,
            "timestamp": msg.CreatedAt.isoformat()
        }
        for msg in messages
    ]


def count_messages_by_simulation(simulation_id: int) -> Dict[str, int]:
    """Подсчитать количество сообщений в симуляции по ролям"""
    return agent_simulation_messages_repository.count_messages_by_simulation(simulation_id)


def get_message_stats_by_type(simulation_id: int) -> Dict[str, int]:
    """Подсчитать количество сообщений в симуляции по типам"""
    return agent_simulation_messages_repository.get_message_stats_by_type(simulation_id)


def search_simulation_messages(search_term: str) -> List[AgentSimulationMessages]:
    """Поиск сообщений симуляции по содержимому"""
    if not search_term or len(search_term.strip()) < 3:
        raise SimulationMessageValidationError("Search term must be at least 3 characters long")
    
    messages_data = agent_simulation_messages_repository.search_simulation_messages(search_term)
    return [_convert_db_message(msg) for msg in messages_data]


def get_recent_simulation_messages(hours: int = 24) -> List[AgentSimulationMessages]:
    """Получить недавние сообщения симуляций за указанное количество часов"""
    messages_data = agent_simulation_messages_repository.get_recent_simulation_messages(hours)
    return [_convert_db_message(msg) for msg in messages_data]


def get_messages_with_metadata_key(key: str) -> List[AgentSimulationMessages]:
    """Получить сообщения, содержащие определенный ключ в метаданных"""
    messages_data = agent_simulation_messages_repository.get_messages_with_metadata_key(key)
    return [_convert_db_message(msg) for msg in messages_data]


def add_message_to_simulation(
    simulation_id: int,
    role: str,
    content: str,
    message_type: str = "text",
    metadata: Optional[Dict[str, Any]] = None
) -> AgentSimulationMessages:
    """
    Добавить новое сообщение в симуляцию с автоматической валидацией
    """
    return create_simulation_message(
        simulation_id=simulation_id,
        message_content=content,
        role=role,
        message_type=message_type,
        metadata=metadata
    )


def _convert_db_message(message_data: Dict[str, Any]) -> AgentSimulationMessages:
    """Конвертировать данные из БД в Pydantic модель"""
    metadata = (
        json.loads(message_data['metadata'])
        if isinstance(message_data.get('metadata'), str)
        else message_data.get('metadata')
    )
    
    return AgentSimulationMessages(
        ID=message_data['id'],
        SimulationID=message_data['simulation_id'],
        MessageContent=message_data['message_content'],
        Role=message_data['role'],
        MessageType=message_data['message_type'],
        Metadata=metadata,
        CreatedAt=message_data['created_at']
    )