from typing import Optional, Dict, Any, List
from datetime import datetime
import json
from fastapi import HTTPException, status
from src.repository import user_agents_repository
from src.database.models import UserAgents, LearningStatusEnum
from src.utils.custom_logging import get_logger

log = get_logger(__name__)


class AgentNotFoundError(HTTPException):
    def __init__(self, agent_id: int = None, user_id: int = None):
        detail = f'Agent {f"with ID {agent_id}" if agent_id else f"for user {user_id}"} not found'
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class AgentValidationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


def get_all_agents() -> List[UserAgents]:
    """Получить всех агентов пользователей"""
    agents_data = user_agents_repository.get_all_agents()
    return [_convert_db_agent(agent) for agent in agents_data]


def get_agent_by_id(agent_id: int) -> UserAgents:
    """Получить агента по ID"""
    agent_data = user_agents_repository.get_agent_by_id(agent_id)
    if not agent_data:
        raise AgentNotFoundError(agent_id=agent_id)
    return _convert_db_agent(agent_data)


def get_agent_by_user_id(user_id: int) -> UserAgents:
    """Получить агента по ID пользователя"""
    agent_data = user_agents_repository.get_agent_by_user_id(user_id)
    if not agent_data:
        raise AgentNotFoundError(user_id=user_id)
    return _convert_db_agent(agent_data)


def create_agent(user_id: int, personality_data: Dict[str, Any]) -> UserAgents:
    """Создать нового агента для пользователя"""
    # Проверяем, не существует ли уже агент для этого пользователя
    try:
        existing = get_agent_by_user_id(user_id)
        raise AgentValidationError(f"Agent already exists for user {user_id} (ID: {existing.ID})")
    except AgentNotFoundError:
        pass
    
    # Валидация данных личности
    if not personality_data or not isinstance(personality_data, dict):
        raise AgentValidationError("Personality data must be a non-empty dictionary")
    
    agent = UserAgents(
        UserID=user_id,
        PersonalityData=personality_data,
        LearningStatus=LearningStatusEnum.LEARNING,
        LastUpdatedAt=datetime.now(),
        CreatedAt=datetime.now()
    )
    
    agent_id = user_agents_repository.create_agent(agent)
    return get_agent_by_id(agent_id)


def update_agent(agent_id: int, updates: Dict[str, Any]) -> UserAgents:
    """Обновить данные агента"""
    agent = get_agent_by_id(agent_id)
    
    # Подготовка данных для обновления
    update_data = {}
    
    if 'PersonalityData' in updates:
        if not isinstance(updates['PersonalityData'], dict):
            raise AgentValidationError("Personality data must be a dictionary")
        update_data['personality_data'] = updates['PersonalityData']
    
    if 'LearningStatus' in updates:
        if updates['LearningStatus'] not in LearningStatusEnum.__members__.values():
            raise AgentValidationError(f"Invalid learning status. Must be one of: {list(LearningStatusEnum.__members__.values())}")
        update_data['learning_status'] = updates['LearningStatus']
    
    if not update_data:
        raise AgentValidationError("No valid fields to update")
    
    # Всегда обновляем last_updated_at
    update_data['last_updated_at'] = datetime.now()
    
    user_agents_repository.update_agent(agent_id, update_data)
    return get_agent_by_id(agent_id)


def update_agent_status(agent_id: int, status: LearningStatusEnum) -> UserAgents:
    """Обновить статус обучения агента"""
    return update_agent(agent_id, {'LearningStatus': status})


def update_agent_personality(agent_id: int, personality_data: Dict[str, Any]) -> UserAgents:
    """Обновить данные о личности агента"""
    return update_agent(agent_id, {'PersonalityData': personality_data})


def delete_agent(agent_id: int) -> Dict[str, str]:
    """Удалить агента"""
    get_agent_by_id(agent_id)  # Проверяем существование
    user_agents_repository.delete_agent(agent_id)
    return {"message": f"Agent {agent_id} deleted successfully"}


def delete_user_agent(user_id: int) -> Dict[str, str]:
    """Удалить агента по ID пользователя"""
    agent = get_agent_by_user_id(user_id)
    return delete_agent(agent.ID)


def get_ready_agents() -> List[UserAgents]:
    """Получить всех агентов со статусом 'ready'"""
    agents_data = user_agents_repository.get_ready_agents()
    return [_convert_db_agent(agent) for agent in agents_data]


def get_learning_agents() -> List[UserAgents]:
    """Получить всех агентов со статусом 'learning'"""
    agents_data = user_agents_repository.get_learning_agents()
    return [_convert_db_agent(agent) for agent in agents_data]


def get_agents_requiring_update(days_threshold: int = 7) -> List[UserAgents]:
    """Получить агентов, требующих обновления (не обновлялись более N дней)"""
    agents_data = user_agents_repository.get_agents_requiring_update(days_threshold)
    return [_convert_db_agent(agent) for agent in agents_data]


def get_agents_stats() -> Dict[str, Any]:
    """Получить статистику по агентам"""
    return user_agents_repository.get_agents_stats()


def find_similar_agents(agent_id: int, threshold: float = 0.5, limit: int = 10) -> List[Dict[str, Any]]:
    """Найти агентов с похожими характеристиками личности"""
    try:
        agent = get_agent_by_id(agent_id)
        return user_agents_repository.find_similar_agents(
            agent.PersonalityData,
            threshold,
            limit
        )
    except AgentNotFoundError:
        return []


def train_agent(agent_id: int, training_data: Dict[str, Any]) -> UserAgents:
    """Обучить агента на новых данных"""
    agent = get_agent_by_id(agent_id)
    
    # Здесь должна быть логика обработки тренировочных данных
    # В реальном приложении это может включать вызов ML модели
    
    # Обновляем данные личности (упрощенный пример)
    updated_personality = {**agent.PersonalityData, **training_data}
    
    return update_agent_personality(agent_id, updated_personality)


def reset_agent_learning(agent_id: int) -> UserAgents:
    """Сбросить обучение агента"""
    agent = get_agent_by_id(agent_id)
    
    # Создаем базовые данные личности
    base_personality = {
        "communication_style": "neutral",
        "response_patterns": [],
        "interests": []
    }
    
    return update_agent(agent_id, {
        'PersonalityData': base_personality,
        'LearningStatus': LearningStatusEnum.LEARNING
    })


def _convert_db_agent(agent_data: Dict[str, Any]) -> UserAgents:
    """Конвертировать данные из БД в Pydantic модель"""
    personality_data = json.loads(agent_data['personality_data']) if isinstance(agent_data['personality_data'], str) else agent_data['personality_data']
    
    return UserAgents(
        ID=agent_data['id'],
        UserID=agent_data['user_id'],
        PersonalityData=personality_data,
        LearningStatus=agent_data['learning_status'],
        LastUpdatedAt=agent_data['last_updated_at'],
        CreatedAt=agent_data['created_at']
    )