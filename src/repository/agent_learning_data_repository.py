from typing import Optional, Dict, Any, List
from datetime import datetime
import json
from src.database.my_connector import db
from src.database.models import AgentLearningData


def get_all_learning_data() -> List[Dict[str, Any]]:
    """Получить все данные для обучения агентов"""
    query = "SELECT * FROM agent_learning_data"
    return db.fetch_all(query)


def get_learning_data_by_id(data_id: int) -> Optional[Dict[str, Any]]:
    """Получить данные обучения по ID"""
    query = "SELECT * FROM agent_learning_data WHERE id = %s"
    return db.fetch_one(query, (data_id,))


def get_learning_data_by_agent(agent_id: int) -> List[Dict[str, Any]]:
    """Получить все данные обучения для конкретного агента"""
    query = """
        SELECT ald.*, u.first_name as creator_name
        FROM agent_learning_data ald
        LEFT JOIN users u ON ald.created_by = u.id
        WHERE ald.agent_id = %s
        ORDER BY ald.created_at DESC
    """
    return db.fetch_all(query, (agent_id,))


def get_learning_data_by_type(data_type: str) -> List[Dict[str, Any]]:
    """Получить данные обучения определённого типа"""
    query = """
        SELECT ald.*, u.first_name as creator_name, ua.user_id as agent_owner_id
        FROM agent_learning_data ald
        LEFT JOIN users u ON ald.created_by = u.id
        JOIN user_agents ua ON ald.agent_id = ua.id
        WHERE ald.data_type = %s
        ORDER BY ald.created_at DESC
    """
    return db.fetch_all(query, (data_type,))


def create_learning_data(learning_data: AgentLearningData) -> int:
    """Создать новую запись данных обучения"""
    # Сериализуем JSON поля
    training_data = json.dumps(learning_data.TrainingData) if learning_data.TrainingData else None
    metadata = json.dumps(learning_data.Metadata) if learning_data.Metadata else None
    
    query = """
        INSERT INTO agent_learning_data 
        (agent_id, data_type, training_data, source, metadata, created_by)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (
        learning_data.AgentID,
        learning_data.DataType,
        training_data,
        learning_data.Source,
        metadata,
        learning_data.CreatedBy
    )
    cursor = db.execute_query(query, params)
    return cursor.lastrowid


def update_learning_data(data_id: int, updates: Dict[str, Any]) -> None:
    """Обновить запись данных обучения"""
    set_clauses = []
    params = []

    # Особая обработка для JSON полей
    if 'training_data' in updates and updates['training_data'] is not None:
        set_clauses.append("training_data = %s")
        params.append(json.dumps(updates['training_data']))
        updates.pop('training_data')
    
    if 'metadata' in updates and updates['metadata'] is not None:
        set_clauses.append("metadata = %s")
        params.append(json.dumps(updates['metadata']))
        updates.pop('metadata')
    
    # Обработка остальных полей
    field_mapping = {
        "data_type": "DataType",
        "source": "Source",
        "is_processed": "IsProcessed"
    }

    for db_field, value in updates.items():
        if db_field in field_mapping and value is not None:
            set_clauses.append(f"{db_field} = %s")
            params.append(value)

    if not set_clauses:
        return

    # Автоматическое обновление поля updated_at
    set_clauses.append("updated_at = NOW()")
    
    params.append(data_id)
    query = f"UPDATE agent_learning_data SET {', '.join(set_clauses)} WHERE id = %s"
    db.execute_query(query, params)


def mark_as_processed(data_id: int, processed_metadata: Dict[str, Any] = None) -> None:
    """Отметить данные как обработанные и обновить метаданные"""
    updates = {"is_processed": True}
    
    if processed_metadata:
        # Получаем текущие метаданные и объединяем их с новыми
        current_data = get_learning_data_by_id(data_id)
        if current_data and current_data.get('metadata'):
            current_metadata = json.loads(current_data['metadata']) if isinstance(current_data['metadata'], str) else current_data['metadata']
            current_metadata.update(processed_metadata)
            updates["metadata"] = current_metadata
        else:
            updates["metadata"] = processed_metadata
    
    update_learning_data(data_id, updates)


def delete_learning_data(data_id: int) -> None:
    """Удалить запись данных обучения"""
    query = "DELETE FROM agent_learning_data WHERE id = %s"
    db.execute_query(query, (data_id,))


def delete_agent_learning_data(agent_id: int) -> int:
    """Удалить все данные обучения для конкретного агента"""
    query = "DELETE FROM agent_learning_data WHERE agent_id = %s"
    cursor = db.execute_query(query, (agent_id,))
    return cursor.rowcount


def get_unprocessed_learning_data() -> List[Dict[str, Any]]:
    """Получить необработанные данные обучения"""
    query = """
        SELECT ald.*, u.first_name as creator_name, ua.user_id as agent_owner_id
        FROM agent_learning_data ald
        LEFT JOIN users u ON ald.created_by = u.id
        JOIN user_agents ua ON ald.agent_id = ua.id
        WHERE ald.is_processed = FALSE
        ORDER BY ald.created_at ASC
    """
    return db.fetch_all(query)


def get_learning_data_from_source(source: str) -> List[Dict[str, Any]]:
    """Получить данные обучения из определенного источника"""
    query = """
        SELECT ald.*, u.first_name as creator_name
        FROM agent_learning_data ald
        LEFT JOIN users u ON ald.created_by = u.id
        WHERE ald.source = %s
        ORDER BY ald.created_at DESC
    """
    return db.fetch_all(query, (source,))


def get_recent_learning_data(hours: int = 24) -> List[Dict[str, Any]]:
    """Получить недавние данные обучения за указанное количество часов"""
    query = """
        SELECT ald.*, u.first_name as creator_name
        FROM agent_learning_data ald
        LEFT JOIN users u ON ald.created_by = u.id
        WHERE ald.created_at >= DATE_SUB(NOW(), INTERVAL %s HOUR)
        ORDER BY ald.created_at DESC
    """
    return db.fetch_all(query, (hours,))


def get_learning_data_by_metadata_key(key: str, value: Any = None) -> List[Dict[str, Any]]:
    """
    Получить данные обучения, содержащие определенный ключ в метаданных
    Опционально можно указать значение для фильтрации
    """
    if value is not None:
        # Поиск по ключу и значению
        query = """
            SELECT ald.*, u.first_name as creator_name
            FROM agent_learning_data ald
            LEFT JOIN users u ON ald.created_by = u.id
            WHERE JSON_EXTRACT(ald.metadata, %s) = %s
            ORDER BY ald.created_at DESC
        """
        return db.fetch_all(query, (f"$.{key}", json.dumps(value)))
    else:
        # Поиск только по наличию ключа
        query = """
            SELECT ald.*, u.first_name as creator_name
            FROM agent_learning_data ald
            LEFT JOIN users u ON ald.created_by = u.id
            WHERE JSON_CONTAINS_PATH(ald.metadata, 'one', %s)
            ORDER BY ald.created_at DESC
        """
        return db.fetch_all(query, (f"$.{key}",))


def count_learning_data_by_agent(agent_id: int) -> Dict[str, int]:
    """Подсчитать количество данных обучения для агента по типам"""
    query = """
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN is_processed = TRUE THEN 1 ELSE 0 END) as processed_count,
            SUM(CASE WHEN is_processed = FALSE THEN 1 ELSE 0 END) as unprocessed_count,
            COUNT(DISTINCT data_type) as unique_types
        FROM agent_learning_data
        WHERE agent_id = %s
    """
    
    result = db.fetch_one(query, (agent_id,)) or {}
    
    # Дополнительный запрос для подсчета по типам данных
    types_query = """
        SELECT data_type, COUNT(*) as count
        FROM agent_learning_data
        WHERE agent_id = %s
        GROUP BY data_type
    """
    
    types = db.fetch_all(types_query, (agent_id,))
    types_dict = {record['data_type']: record['count'] for record in types}
    
    return {
        "всего": result.get("total", 0),
        "обработано": result.get("processed_count", 0),
        "не_обработано": result.get("unprocessed_count", 0),
        "уникальных_типов": result.get("unique_types", 0),
        "по_типам": types_dict
    }


def get_learning_data_stats() -> Dict[str, Any]:
    """Получить общую статистику по данным обучения"""
    query = """
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT agent_id) as unique_agents,
            COUNT(DISTINCT data_type) as unique_data_types,
            COUNT(DISTINCT source) as unique_sources,
            SUM(CASE WHEN is_processed = TRUE THEN 1 ELSE 0 END) as processed_count,
            MIN(created_at) as oldest_record,
            MAX(created_at) as newest_record
        FROM agent_learning_data
    """
    
    result = db.fetch_one(query) or {}
    
    # Дополнительный запрос для статистики по типам данных
    types_query = """
        SELECT data_type, COUNT(*) as count
        FROM agent_learning_data
        GROUP BY data_type
        ORDER BY count DESC
    """
    
    types = db.fetch_all(types_query)
    
    # Дополнительный запрос для статистики по источникам
    sources_query = """
        SELECT source, COUNT(*) as count
        FROM agent_learning_data
        GROUP BY source
        ORDER BY count DESC
    """
    
    sources = db.fetch_all(sources_query)
    
    return {
        "всего_записей": result.get("total_records", 0),
        "уникальных_агентов": result.get("unique_agents", 0),
        "уникальных_типов_данных": result.get("unique_data_types", 0),
        "уникальных_источников": result.get("unique_sources", 0),
        "обработанных_записей": result.get("processed_count", 0),
        "процент_обработки": round(result.get("processed_count", 0) * 100 / result.get("total_records", 1), 1),
        "самая_старая_запись": result.get("oldest_record"),
        "самая_новая_запись": result.get("newest_record"),
        "по_типам_данных": [{"тип": t["data_type"], "количество": t["count"]} for t in types],
        "по_источникам": [{"источник": s["source"], "количество": s["count"]} for s in sources]
    }