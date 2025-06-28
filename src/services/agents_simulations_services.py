from typing import Optional, Dict, Any, List
from datetime import datetime
import json
from fastapi import HTTPException, status
from src.repository import agents_simulations_repository
from src.database.models import AgentsSimulations, SimulationStatusEnum
from src.utils.custom_logging import get_logger

log = get_logger(__name__)


class SimulationNotFoundError(HTTPException):
    def __init__(self, simulation_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Simulation with ID {simulation_id} not found'
        )


class SimulationValidationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


def get_all_simulations() -> List[AgentsSimulations]:
    """Получить все симуляции агентов"""
    simulations_data = agents_simulations_repository.get_all_simulations()
    return [_convert_db_simulation(sim) for sim in simulations_data]


def get_simulation_by_id(simulation_id: int) -> AgentsSimulations:
    """Получить симуляцию по ID"""
    simulation_data = agents_simulations_repository.get_simulation_by_id(simulation_id)
    if not simulation_data:
        raise SimulationNotFoundError(simulation_id)
    return _convert_db_simulation(simulation_data)


def get_simulations_by_agent(agent_id: int) -> List[AgentsSimulations]:
    """Получить все симуляции конкретного агента"""
    simulations_data = agents_simulations_repository.get_simulations_by_agent(agent_id)
    return [_convert_db_simulation(sim) for sim in simulations_data]


def get_simulations_by_conversation(conversation_id: int) -> List[AgentsSimulations]:
    """Получить все симуляции для конкретной беседы"""
    simulations_data = agents_simulations_repository.get_simulations_by_conversation(conversation_id)
    return [_convert_db_simulation(sim) for sim in simulations_data]


def create_simulation(
    agent_id: int,
    conversation_id: int,
    simulation_data: Optional[Dict[str, Any]] = None
) -> AgentsSimulations:
    """Создать новую симуляцию агента"""
    from src.services import user_agents_services, chat_conversations_services
    
    # Проверяем существование агента и беседы
    user_agents_services.get_agent_by_id(agent_id)
    chat_conversations_services.get_conversation_by_id(conversation_id)
    
    simulation = AgentsSimulations(
        AgentID=agent_id,
        ConversationID=conversation_id,
        SimulationStatus=SimulationStatusEnum.PENDING,
        StartTime=datetime.now(),
        SimulationData=simulation_data
    )
    
    simulation_id = agents_simulations_repository.create_simulation(simulation)
    return get_simulation_by_id(simulation_id)


def update_simulation(simulation_id: int, updates: Dict[str, Any]) -> AgentsSimulations:
    """Обновить симуляцию агента"""
    existing = get_simulation_by_id(simulation_id)
    
    # Валидация обновлений
    if 'SimulationStatus' in updates:
        if updates['SimulationStatus'] not in SimulationStatusEnum.__members__.values():
            raise SimulationValidationError(
                f"Invalid status. Must be one of: {list(SimulationStatusEnum.__members__.values())}"
            )
    
    update_data = {
        'simulation_status': updates.get('SimulationStatus'),
        'start_time': updates.get('StartTime'),
        'end_time': updates.get('EndTime'),
        'simulation_data': updates.get('SimulationData')
    }
    
    # Удаляем None значения
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    if update_data:
        agents_simulations_repository.update_simulation(simulation_id, update_data)
    
    return get_simulation_by_id(simulation_id)


def start_simulation(simulation_id: int) -> AgentsSimulations:
    """Начать симуляцию (изменить статус на 'in_progress')"""
    return update_simulation(
        simulation_id,
        {
            'SimulationStatus': SimulationStatusEnum.IN_PROGRESS,
            'StartTime': datetime.now()
        }
    )


def complete_simulation(
    simulation_id: int,
    simulation_data: Optional[Dict[str, Any]] = None
) -> AgentsSimulations:
    """Завершить симуляцию успешно"""
    updates = {
        'SimulationStatus': SimulationStatusEnum.COMPLETED,
        'EndTime': datetime.now()
    }
    
    if simulation_data:
        updates['SimulationData'] = simulation_data
    
    return update_simulation(simulation_id, updates)


def fail_simulation(
    simulation_id: int,
    error_message: str,
    error_details: Optional[Dict[str, Any]] = None
) -> AgentsSimulations:
    """Завершить симуляцию с ошибкой"""
    simulation = get_simulation_by_id(simulation_id)
    
    # Обновляем данные симуляции с информацией об ошибке
    error_data = {
        'error': {
            'message': error_message,
            'details': error_details,
            'timestamp': datetime.now().isoformat()
        }
    }
    
    if simulation.SimulationData:
        updated_data = {**simulation.SimulationData, **error_data}
    else:
        updated_data = error_data
    
    return update_simulation(
        simulation_id,
        {
            'SimulationStatus': SimulationStatusEnum.FAILED,
            'EndTime': datetime.now(),
            'SimulationData': updated_data
        }
    )


def delete_simulation(simulation_id: int) -> Dict[str, str]:
    """Удалить симуляцию"""
    get_simulation_by_id(simulation_id)  # Проверяем существование
    agents_simulations_repository.delete_simulation(simulation_id)
    return {"message": f"Simulation {simulation_id} deleted successfully"}


def get_active_simulations() -> List[AgentsSimulations]:
    """Получить все активные симуляции агентов"""
    simulations_data = agents_simulations_repository.get_active_simulations()
    return [_convert_db_simulation(sim) for sim in simulations_data]


def get_completed_simulations(limit: int = 100) -> List[AgentsSimulations]:
    """Получить завершенные симуляции агентов"""
    simulations_data = agents_simulations_repository.get_completed_simulations(limit)
    return [_convert_db_simulation(sim) for sim in simulations_data]


def get_failed_simulations(limit: int = 100) -> List[AgentsSimulations]:
    """Получить неудачные симуляции агентов"""
    simulations_data = agents_simulations_repository.get_failed_simulations(limit)
    return [_convert_db_simulation(sim) for sim in simulations_data]


def get_recent_simulations(hours: int = 24) -> List[AgentsSimulations]:
    """Получить недавние симуляции за указанное количество часов"""
    simulations_data = agents_simulations_repository.get_recent_simulations(hours)
    return [_convert_db_simulation(sim) for sim in simulations_data]


def get_simulation_stats() -> Dict[str, Any]:
    """Получить статистику по симуляциям агентов"""
    return agents_simulations_repository.get_simulation_stats()


def get_top_agent_simulations(limit: int = 10) -> List[Dict[str, Any]]:
    """Получить топ агентов по количеству успешных симуляций"""
    return agents_simulations_repository.get_top_agent_simulations(limit)


def run_agent_simulation(
    agent_id: int,
    conversation_id: int,
    simulation_data: Optional[Dict[str, Any]] = None
) -> AgentsSimulations:
    """
    Запустить новую симуляцию агента и автоматически начать ее
    """
    simulation = create_simulation(agent_id, conversation_id, simulation_data)
    return start_simulation(simulation.ID)


def _convert_db_simulation(simulation_data: Dict[str, Any]) -> AgentsSimulations:
    """Конвертировать данные из БД в Pydantic модель"""
    simulation_data_json = (
        json.loads(simulation_data['simulation_data'])
        if isinstance(simulation_data.get('simulation_data'), str)
        else simulation_data.get('simulation_data')
    )
    
    return AgentsSimulations(
        ID=simulation_data['id'],
        AgentID=simulation_data['agent_id'],
        ConversationID=simulation_data['conversation_id'],
        SimulationStatus=simulation_data['simulation_status'],
        StartTime=simulation_data['start_time'],
        EndTime=simulation_data['end_time'],
        SimulationData=simulation_data_json,
        CreatedAt=simulation_data['created_at'],
        UpdatedAt=simulation_data['updated_at']
    )