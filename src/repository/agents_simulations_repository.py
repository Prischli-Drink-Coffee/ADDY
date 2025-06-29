from typing import Optional, Dict, Any, List
from datetime import datetime
import json
from src.database.my_connector import db
from src.database.models import AgentSimulations


def get_all_simulations() -> List[Dict[str, Any]]:
    """Получить все симуляции агентов"""
    query = "SELECT * FROM agents_simulations"
    return db.fetch_all(query)


def get_simulation_by_id(simulation_id: int) -> Optional[Dict[str, Any]]:
    """Получить симуляцию по ID"""
    query = "SELECT * FROM agents_simulations WHERE id = %s"
    return db.fetch_one(query, (simulation_id,))


def get_simulations_by_agent(agent_id: int) -> List[Dict[str, Any]]:
    """Получить все симуляции конкретного агента"""
    query = """
        SELECT s.*, u.first_name as agent_owner_name
        FROM agents_simulations s
        JOIN user_agents a ON s.agent_id = a.id
        JOIN users u ON a.user_id = u.id
        WHERE s.agent_id = %s
        ORDER BY s.created_at DESC
    """
    return db.fetch_all(query, (agent_id,))


def get_simulations_by_conversation(conversation_id: int) -> List[Dict[str, Any]]:
    """Получить все симуляции для конкретной беседы"""
    query = """
        SELECT s.*, a.user_id as agent_owner_id, u.first_name as agent_owner_name
        FROM agents_simulations s
        JOIN user_agents a ON s.agent_id = a.id
        JOIN users u ON a.user_id = u.id
        WHERE s.conversation_id = %s
        ORDER BY s.created_at DESC
    """
    return db.fetch_all(query, (conversation_id,))


def create_simulation(simulation: AgentSimulations) -> int:
    """Создать новую симуляцию агента"""
    # Сериализуем JSON поле с данными симуляции
    simulation_data = json.dumps(simulation.SimulationData) if simulation.SimulationData else None
    
    query = """
        INSERT INTO agents_simulations 
        (agent_id, conversation_id, simulation_status, start_time, end_time, simulation_data)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (
        simulation.AgentID,
        simulation.ConversationID,
        simulation.SimulationStatus,
        simulation.StartTime or datetime.utcnow(),
        simulation.EndTime,
        simulation_data
    )
    cursor = db.execute_query(query, params)
    return cursor.lastrowid


def update_simulation(simulation_id: int, updates: Dict[str, Any]) -> None:
    """Обновить симуляцию агента"""
    set_clauses = []
    params = []

    # Особая обработка для JSON поля simulation_data
    if 'simulation_data' in updates and updates['simulation_data'] is not None:
        set_clauses.append("simulation_data = %s")
        params.append(json.dumps(updates['simulation_data']))
        updates.pop('simulation_data')
    
    # Обработка остальных полей
    field_mapping = {
        "simulation_status": "SimulationStatus",
        "start_time": "StartTime",
        "end_time": "EndTime"
    }

    for db_field, value in updates.items():
        if db_field in field_mapping and value is not None:
            set_clauses.append(f"{db_field} = %s")
            params.append(value)

    if not set_clauses:
        return

    # Автоматическое обновление поля updated_at
    set_clauses.append("updated_at = NOW()")
    
    params.append(simulation_id)
    query = f"UPDATE agents_simulations SET {', '.join(set_clauses)} WHERE id = %s"
    db.execute_query(query, params)


def update_simulation_status(simulation_id: int, status: str) -> None:
    """Обновить статус симуляции агента"""
    query = """
        UPDATE agents_simulations 
        SET simulation_status = %s, updated_at = NOW()
        WHERE id = %s
    """
    db.execute_query(query, (status, simulation_id))


def complete_simulation(simulation_id: int, simulation_data: Dict[str, Any] = None) -> None:
    """Завершить симуляцию агента и сохранить данные результата"""
    updates = {
        "simulation_status": "completed",
        "end_time": datetime.utcnow()
    }
    
    if simulation_data:
        updates["simulation_data"] = simulation_data
    
    update_simulation(simulation_id, updates)


def fail_simulation(simulation_id: int, error_data: Dict[str, Any] = None) -> None:
    """Отметить симуляцию как неудачную с данными об ошибке"""
    updates = {
        "simulation_status": "failed",
        "end_time": datetime.utcnow()
    }
    
    if error_data:
        # Получаем текущие данные симуляции и добавляем информацию об ошибке
        simulation = get_simulation_by_id(simulation_id)
        if simulation and simulation.get('simulation_data'):
            current_data = json.loads(simulation['simulation_data']) if isinstance(simulation['simulation_data'], str) else simulation['simulation_data']
            current_data["error"] = error_data
            updates["simulation_data"] = current_data
        else:
            updates["simulation_data"] = {"error": error_data}
    
    update_simulation(simulation_id, updates)


def delete_simulation(simulation_id: int) -> None:
    """Удалить симуляцию агента"""
    query = "DELETE FROM agents_simulations WHERE id = %s"
    db.execute_query(query, (simulation_id,))


def get_active_simulations() -> List[Dict[str, Any]]:
    """Получить все активные симуляции агентов"""
    query = """
        SELECT s.*, 
               a.user_id as agent_owner_id, 
               u.first_name as agent_owner_name,
               c.match_id
        FROM agents_simulations s
        JOIN user_agents a ON s.agent_id = a.id
        JOIN users u ON a.user_id = u.id
        JOIN chat_conversations c ON s.conversation_id = c.id
        WHERE s.simulation_status = 'active'
        ORDER BY s.start_time DESC
    """
    return db.fetch_all(query)


def get_completed_simulations(limit: int = 100) -> List[Dict[str, Any]]:
    """Получить завершенные симуляции агентов"""
    query = """
        SELECT s.*, 
               TIMESTAMPDIFF(SECOND, s.start_time, s.end_time) as duration_seconds,
               a.user_id as agent_owner_id, 
               u.first_name as agent_owner_name
        FROM agents_simulations s
        JOIN user_agents a ON s.agent_id = a.id
        JOIN users u ON a.user_id = u.id
        WHERE s.simulation_status = 'completed'
        ORDER BY s.end_time DESC
        LIMIT %s
    """
    return db.fetch_all(query, (limit,))


def get_failed_simulations(limit: int = 100) -> List[Dict[str, Any]]:
    """Получить неудачные симуляции агентов"""
    query = """
        SELECT s.*, 
               TIMESTAMPDIFF(SECOND, s.start_time, s.end_time) as duration_seconds,
               a.user_id as agent_owner_id, 
               u.first_name as agent_owner_name
        FROM agents_simulations s
        JOIN user_agents a ON s.agent_id = a.id
        JOIN users u ON a.user_id = u.id
        WHERE s.simulation_status = 'failed'
        ORDER BY s.end_time DESC
        LIMIT %s
    """
    return db.fetch_all(query, (limit,))


def get_recent_simulations(hours: int = 24) -> List[Dict[str, Any]]:
    """Получить недавние симуляции за указанное количество часов"""
    query = """
        SELECT s.*, 
               a.user_id as agent_owner_id, 
               u.first_name as agent_owner_name,
               CASE 
                 WHEN s.end_time IS NOT NULL THEN TIMESTAMPDIFF(SECOND, s.start_time, s.end_time)
                 ELSE TIMESTAMPDIFF(SECOND, s.start_time, NOW())
               END as duration_seconds
        FROM agents_simulations s
        JOIN user_agents a ON s.agent_id = a.id
        JOIN users u ON a.user_id = u.id
        WHERE s.created_at >= DATE_SUB(NOW(), INTERVAL %s HOUR)
        ORDER BY s.created_at DESC
    """
    return db.fetch_all(query, (hours,))


def get_simulation_stats() -> Dict[str, Any]:
    """Получить статистику по симуляциям агентов"""
    query = """
        SELECT 
            COUNT(*) as total_simulations,
            SUM(CASE WHEN simulation_status = 'active' THEN 1 ELSE 0 END) as active_count,
            SUM(CASE WHEN simulation_status = 'completed' THEN 1 ELSE 0 END) as completed_count,
            SUM(CASE WHEN simulation_status = 'failed' THEN 1 ELSE 0 END) as failed_count,
            AVG(CASE 
                WHEN simulation_status = 'completed' AND end_time IS NOT NULL 
                THEN TIMESTAMPDIFF(SECOND, start_time, end_time) 
                ELSE NULL 
            END) as avg_duration_seconds
        FROM agents_simulations
    """
    
    result = db.fetch_one(query) or {}
    
    # Дополнительный запрос для получения статистики по последним 24 часам
    recent_query = """
        SELECT 
            COUNT(*) as recent_simulations,
            SUM(CASE WHEN simulation_status = 'completed' THEN 1 ELSE 0 END) as recent_completed
        FROM agents_simulations
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
    """
    
    recent = db.fetch_one(recent_query) or {}
    
    return {
        "всего_симуляций": result.get("total_simulations", 0),
        "активных": result.get("active_count", 0),
        "завершенных": result.get("completed_count", 0),
        "неудачных": result.get("failed_count", 0),
        "средняя_продолжительность_сек": float(result.get("avg_duration_seconds", 0)),
        "за_последние_24ч": {
            "всего": recent.get("recent_simulations", 0),
            "завершенных": recent.get("recent_completed", 0)
        }
    }


def get_top_agent_simulations(limit: int = 10) -> List[Dict[str, Any]]:
    """Получить топ агентов по количеству успешных симуляций"""
    query = """
        SELECT 
            a.id as agent_id,
            u.id as user_id,
            u.first_name,
            COUNT(*) as total_simulations,
            SUM(CASE WHEN s.simulation_status = 'completed' THEN 1 ELSE 0 END) as successful_simulations,
            AVG(CASE 
                WHEN s.simulation_status = 'completed' AND s.end_time IS NOT NULL 
                THEN TIMESTAMPDIFF(SECOND, s.start_time, s.end_time) 
                ELSE NULL 
            END) as avg_duration_seconds
        FROM agents_simulations s
        JOIN user_agents a ON s.agent_id = a.id
        JOIN users u ON a.user_id = u.id
        GROUP BY a.id, u.id, u.first_name
        ORDER BY successful_simulations DESC
        LIMIT %s
    """
    return db.fetch_all(query, (limit,))