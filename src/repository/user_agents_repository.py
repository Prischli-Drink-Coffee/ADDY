from typing import Optional, Dict, Any, List
from datetime import datetime
import json
from src.database.my_connector import db
from src.database.models import UserAgents


def get_all_agents() -> List[Dict[str, Any]]:
    """Получить всех агентов пользователей"""
    query = "SELECT * FROM user_agents"
    return db.fetch_all(query)


def get_agent_by_id(agent_id: int) -> Optional[Dict[str, Any]]:
    """Получить агента по ID"""
    query = "SELECT * FROM user_agents WHERE id = %s"
    return db.fetch_one(query, (agent_id,))


def get_agent_by_user_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Получить агента по ID пользователя"""
    query = "SELECT * FROM user_agents WHERE user_id = %s"
    return db.fetch_one(query, (user_id,))


def create_agent(agent: UserAgents) -> int:
    """Создать нового агента"""
    # Проверяем, не существует ли уже агент для этого пользователя
    existing = get_agent_by_user_id(agent.user_id)
    if existing:
        # Если агент уже существует, возвращаем его ID
        return existing['id']
    
    # Сериализуем JSON данные о личности
    personality_data = json.dumps(agent.personality_data)
    
    query = """
        INSERT INTO user_agents 
        (user_id, personality_data, learning_status, last_updated_at)
        VALUES (%s, %s, %s, %s)
    """
    params = (
        agent.user_id,
        personality_data,
        agent.learning_status,
        agent.last_updated_at or datetime.utcnow()
    )
    cursor = db.execute_query(query, params)
    return cursor.lastrowid


def update_agent(agent_id: int, updates: Dict[str, Any]) -> None:
    """Обновить агента"""
    set_clauses = []
    params = []

    # Особая обработка для JSON поля personality_data
    if 'personality_data' in updates and updates['personality_data'] is not None:
        set_clauses.append("personality_data = %s")
        params.append(json.dumps(updates['personality_data']))
        updates.pop('personality_data')
    
    # Обработка остальных полей
    field_mapping = {
        "learning_status": "LearningStatus"
    }

    for db_field, value in updates.items():
        if db_field in field_mapping and value is not None:
            set_clauses.append(f"{db_field} = %s")
            params.append(value)

    # Всегда обновляем last_updated_at при любом обновлении
    set_clauses.append("last_updated_at = NOW()")
    
    if not set_clauses:
        return

    params.append(agent_id)
    query = f"UPDATE user_agents SET {', '.join(set_clauses)} WHERE id = %s"
    db.execute_query(query, params)


def update_agent_status(agent_id: int, learning_status: str) -> None:
    """Обновить статус обучения агента"""
    query = "UPDATE user_agents SET learning_status = %s, last_updated_at = NOW() WHERE id = %s"
    db.execute_query(query, (learning_status, agent_id))


def update_agent_personality(agent_id: int, personality_data: Dict[str, Any]) -> None:
    """Обновить данные о личности агента"""
    query = "UPDATE user_agents SET personality_data = %s, last_updated_at = NOW() WHERE id = %s"
    db.execute_query(query, (json.dumps(personality_data), agent_id))


def delete_agent(agent_id: int) -> None:
    """Удалить агента"""
    query = "DELETE FROM user_agents WHERE id = %s"
    db.execute_query(query, (agent_id,))


def delete_user_agent(user_id: int) -> None:
    """Удалить агента по ID пользователя"""
    query = "DELETE FROM user_agents WHERE user_id = %s"
    db.execute_query(query, (user_id,))


def get_ready_agents() -> List[Dict[str, Any]]:
    """Получить всех агентов со статусом 'ready'"""
    query = """
        SELECT a.*, u.first_name 
        FROM user_agents a
        JOIN users u ON a.user_id = u.id
        WHERE a.learning_status = 'ready'
        ORDER BY a.last_updated_at DESC
    """
    return db.fetch_all(query)


def get_learning_agents() -> List[Dict[str, Any]]:
    """Получить всех агентов со статусом 'learning'"""
    query = """
        SELECT a.*, u.first_name 
        FROM user_agents a
        JOIN users u ON a.user_id = u.id
        WHERE a.learning_status = 'learning'
        ORDER BY a.created_at ASC
    """
    return db.fetch_all(query)


def get_agents_requiring_update(days_threshold: int = 7) -> List[Dict[str, Any]]:
    """Получить агентов, требующих обновления (не обновлялись более N дней)"""
    query = """
        SELECT a.*, u.first_name, u.last_activity
        FROM user_agents a
        JOIN users u ON a.user_id = u.id
        WHERE a.last_updated_at < DATE_SUB(NOW(), INTERVAL %s DAY)
        AND u.last_activity > a.last_updated_at
        ORDER BY a.last_updated_at ASC
    """
    return db.fetch_all(query, (days_threshold,))


def get_agents_stats() -> Dict[str, Any]:
    """Получить статистику по агентам"""
    query = """
        SELECT 
            COUNT(*) as total_agents,
            SUM(CASE WHEN learning_status = 'learning' THEN 1 ELSE 0 END) as learning_count,
            SUM(CASE WHEN learning_status = 'ready' THEN 1 ELSE 0 END) as ready_count,
            SUM(CASE WHEN learning_status = 'updating' THEN 1 ELSE 0 END) as updating_count,
            AVG(JSON_LENGTH(personality_data)) as avg_personality_attributes
        FROM user_agents
    """
    
    result = db.fetch_one(query) or {}
    
    # Дополнительный запрос для получения обновленной статистики
    recent_query = """
        SELECT COUNT(*) as recent_updates
        FROM user_agents
        WHERE last_updated_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
    """
    
    recent = db.fetch_one(recent_query) or {}
    
    return {
        "total_agents": result.get("total_agents", 0),
        "learning_agents": result.get("learning_count", 0),
        "ready_agents": result.get("ready_count", 0),
        "updating_agents": result.get("updating_count", 0),
        "avg_personality_attributes": float(result.get("avg_personality_attributes", 0)),
        "recent_updates": recent.get("recent_updates", 0)
    }


def find_similar_agents(agent_id: int, threshold: float = 0.5, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Найти агентов с похожими характеристиками личности
    Примечание: Это упрощенная версия - в реальном приложении
    может потребоваться более сложная логика для определения сходства
    """
    agent = get_agent_by_id(agent_id)
    if not agent or 'personality_data' not in agent:
        return []
    
    # Предполагается, что в personality_data есть ключи с характеристиками личности
    # В реальном приложении здесь должна быть логика сравнения
    # Для примера используем простой подход с поиском по ключевым словам
    personality = json.loads(agent['personality_data']) if isinstance(agent['personality_data'], str) else agent['personality_data']
    
    # Предполагаемые ключи для сравнения
    key_traits = ['communication_style', 'interests', 'response_patterns']
    
    conditions = []
    params = []
    
    for trait in key_traits:
        if trait in personality:
            conditions.append("JSON_CONTAINS_PATH(personality_data, 'one', %s)")
            params.append(f"$.{trait}")
    
    if not conditions:
        return []
    
    # Исключаем текущего агента из результатов
    params.append(agent_id)
    
    query = f"""
        SELECT a.*, u.first_name
        FROM user_agents a
        JOIN users u ON a.user_id = u.id
        WHERE ({' OR '.join(conditions)})
        AND a.id != %s
        AND a.learning_status = 'ready'
        LIMIT {limit}
    """
    
    return db.fetch_all(query, tuple(params))