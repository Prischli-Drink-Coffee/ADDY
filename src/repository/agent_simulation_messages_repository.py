from typing import Optional, Dict, Any, List
from datetime import datetime
import json
from src.database.my_connector import db
from src.database.models import AgentSimulationMessages


def get_all_simulation_messages() -> List[Dict[str, Any]]:
    """Получить все сообщения симуляций агентов"""
    query = "SELECT * FROM agent_simulation_messages"
    return db.fetch_all(query)


def get_message_by_id(message_id: int) -> Optional[Dict[str, Any]]:
    """Получить сообщение симуляции по ID"""
    query = "SELECT * FROM agent_simulation_messages WHERE id = %s"
    return db.fetch_one(query, (message_id,))


def get_messages_by_simulation(simulation_id: int) -> List[Dict[str, Any]]:
    """Получить все сообщения конкретной симуляции"""
    query = """
        SELECT asm.*, as.agent_id, as.conversation_id
        FROM agent_simulation_messages asm
        JOIN agents_simulations as ON asm.simulation_id = as.id
        WHERE asm.simulation_id = %s
        ORDER BY asm.created_at ASC
    """
    return db.fetch_all(query, (simulation_id,))


def create_message(message: AgentSimulationMessages) -> int:
    """Создать новое сообщение симуляции"""
    # Сериализуем JSON-поле с метаданными
    metadata = json.dumps(message.Metadata) if message.Metadata else None
    
    query = """
        INSERT INTO agent_simulation_messages 
        (simulation_id, message_content, role, message_type, metadata)
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (
        message.SimulationID,
        message.MessageContent,
        message.Role,
        message.MessageType,
        metadata
    )
    cursor = db.execute_query(query, params)
    return cursor.lastrowid


def update_message(message_id: int, updates: Dict[str, Any]) -> None:
    """Обновить сообщение симуляции"""
    set_clauses = []
    params = []

    # Особая обработка для JSON поля metadata
    if 'metadata' in updates and updates['metadata'] is not None:
        set_clauses.append("metadata = %s")
        params.append(json.dumps(updates['metadata']))
        updates.pop('metadata')
    
    # Обработка остальных полей
    field_mapping = {
        "message_content": "MessageContent",
        "role": "Role",
        "message_type": "MessageType"
    }

    for db_field, value in updates.items():
        if db_field in field_mapping and value is not None:
            set_clauses.append(f"{db_field} = %s")
            params.append(value)

    if not set_clauses:
        return

    # Автоматическое обновление поля updated_at
    set_clauses.append("updated_at = NOW()")
    
    params.append(message_id)
    query = f"UPDATE agent_simulation_messages SET {', '.join(set_clauses)} WHERE id = %s"
    db.execute_query(query, params)


def delete_message(message_id: int) -> None:
    """Удалить сообщение симуляции"""
    query = "DELETE FROM agent_simulation_messages WHERE id = %s"
    db.execute_query(query, (message_id,))


def delete_simulation_messages(simulation_id: int) -> int:
    """Удалить все сообщения конкретной симуляции"""
    query = "DELETE FROM agent_simulation_messages WHERE simulation_id = %s"
    cursor = db.execute_query(query, (simulation_id,))
    return cursor.rowcount


def get_messages_by_role(simulation_id: int, role: str) -> List[Dict[str, Any]]:
    """Получить сообщения симуляции по конкретной роли"""
    query = """
        SELECT * 
        FROM agent_simulation_messages
        WHERE simulation_id = %s AND role = %s
        ORDER BY created_at ASC
    """
    return db.fetch_all(query, (simulation_id, role))


def get_messages_by_type(simulation_id: int, message_type: str) -> List[Dict[str, Any]]:
    """Получить сообщения симуляции по типу сообщения"""
    query = """
        SELECT * 
        FROM agent_simulation_messages
        WHERE simulation_id = %s AND message_type = %s
        ORDER BY created_at ASC
    """
    return db.fetch_all(query, (simulation_id, message_type))


def get_last_message(simulation_id: int) -> Optional[Dict[str, Any]]:
    """Получить последнее сообщение в симуляции"""
    query = """
        SELECT * 
        FROM agent_simulation_messages
        WHERE simulation_id = %s
        ORDER BY created_at DESC
        LIMIT 1
    """
    return db.fetch_one(query, (simulation_id,))


def get_conversation_from_simulation(simulation_id: int) -> List[Dict[str, Any]]:
    """Получить все сообщения симуляции, отформатированные как диалог"""
    query = """
        SELECT role, message_content, created_at
        FROM agent_simulation_messages
        WHERE simulation_id = %s
        ORDER BY created_at ASC
    """
    return db.fetch_all(query, (simulation_id,))


def count_messages_by_simulation(simulation_id: int) -> Dict[str, int]:
    """Подсчитать количество сообщений в симуляции по ролям"""
    query = """
        SELECT 
            COUNT(*) as total_messages,
            SUM(CASE WHEN role = 'system' THEN 1 ELSE 0 END) as system_messages,
            SUM(CASE WHEN role = 'user' THEN 1 ELSE 0 END) as user_messages,
            SUM(CASE WHEN role = 'assistant' THEN 1 ELSE 0 END) as assistant_messages,
            SUM(CASE WHEN role = 'function' THEN 1 ELSE 0 END) as function_messages
        FROM agent_simulation_messages
        WHERE simulation_id = %s
    """
    
    result = db.fetch_one(query, (simulation_id,)) or {}
    
    return {
        "всего_сообщений": result.get("total_messages", 0),
        "system": result.get("system_messages", 0),
        "user": result.get("user_messages", 0),
        "assistant": result.get("assistant_messages", 0),
        "function": result.get("function_messages", 0)
    }


def get_message_stats_by_type(simulation_id: int) -> Dict[str, int]:
    """Подсчитать количество сообщений в симуляции по типам"""
    query = """
        SELECT message_type, COUNT(*) as count
        FROM agent_simulation_messages
        WHERE simulation_id = %s
        GROUP BY message_type
    """
    
    results = db.fetch_all(query, (simulation_id,))
    
    # Преобразуем результат в словарь
    stats = {}
    for row in results:
        stats[row.get('message_type', 'unknown')] = row.get('count', 0)
    
    return stats


def search_simulation_messages(search_term: str) -> List[Dict[str, Any]]:
    """Поиск сообщений симуляции по содержимому"""
    query = """
        SELECT asm.*, as.agent_id, as.conversation_id
        FROM agent_simulation_messages asm
        JOIN agents_simulations as ON asm.simulation_id = as.id
        WHERE asm.message_content LIKE %s
        ORDER BY asm.created_at DESC
    """
    return db.fetch_all(query, (f"%{search_term}%",))


def get_recent_simulation_messages(hours: int = 24) -> List[Dict[str, Any]]:
    """Получить недавние сообщения симуляций за указанное количество часов"""
    query = """
        SELECT asm.*, as.agent_id
        FROM agent_simulation_messages asm
        JOIN agents_simulations as ON asm.simulation_id = as.id
        WHERE asm.created_at >= DATE_SUB(NOW(), INTERVAL %s HOUR)
        ORDER BY asm.created_at DESC
    """
    return db.fetch_all(query, (hours,))


def get_messages_with_metadata_key(key: str) -> List[Dict[str, Any]]:
    """Получить сообщения, содержащие определенный ключ в метаданных"""
    query = """
        SELECT *
        FROM agent_simulation_messages
        WHERE JSON_CONTAINS_PATH(metadata, 'one', %s)
        ORDER BY created_at DESC
    """
    return db.fetch_all(query, (f"$.{key}",))