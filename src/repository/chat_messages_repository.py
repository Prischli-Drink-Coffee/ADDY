from typing import Optional, Dict, Any, List
from datetime import datetime
from src.database.my_connector import db
from src.database.models import ChatMessages


def get_all_messages() -> List[Dict[str, Any]]:
    """Получить все сообщения"""
    query = "SELECT * FROM chat_messages"
    return db.fetch_all(query)


def get_message_by_id(message_id: int) -> Optional[Dict[str, Any]]:
    """Получить сообщение по ID"""
    query = "SELECT * FROM chat_messages WHERE id = %s"
    return db.fetch_one(query, (message_id,))


def get_messages_by_conversation(conversation_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Получить сообщения из конкретной беседы с пагинацией"""
    query = """
        SELECT m.*, u.first_name as sender_name
        FROM chat_messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.conversation_id = %s
        ORDER BY m.created_at DESC
        LIMIT %s OFFSET %s
    """
    return db.fetch_all(query, (conversation_id, limit, offset))


def create_message(message: ChatMessages) -> int:
    """Создать новое сообщение"""
    query = """
        INSERT INTO chat_messages 
        (conversation_id, sender_id, message_text, is_read, message_type)
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (
        message.ConversationID,
        message.SenderID,
        message.MessageText,
        message.IsRead,
        message.MessageType
    )
    cursor = db.execute_query(query, params)
    
    # Обновляем время последнего сообщения в беседе
    update_conversation_last_message(message.ConversationID)
    
    return cursor.lastrowid


def update_message(message_id: int, updates: Dict[str, Any]) -> None:
    """Обновить сообщение"""
    set_clauses = []
    params = []

    field_mapping = {
        "message_text": "MessageText",
        "is_read": "IsRead",
        "message_type": "MessageType"
    }

    for db_field, value in updates.items():
        if db_field in field_mapping and value is not None:
            set_clauses.append(f"{db_field} = %s")
            params.append(value)

    if not set_clauses:
        return

    params.append(message_id)
    query = f"UPDATE chat_messages SET {', '.join(set_clauses)} WHERE id = %s"
    db.execute_query(query, params)


def update_conversation_last_message(conversation_id: int) -> None:
    """Обновить время последнего сообщения в беседе"""
    query = "UPDATE chat_conversations SET last_message_at = NOW() WHERE id = %s"
    db.execute_query(query, (conversation_id,))


def delete_message(message_id: int) -> None:
    """Удалить сообщение по ID"""
    query = "DELETE FROM chat_messages WHERE id = %s"
    db.execute_query(query, (message_id,))


def mark_messages_as_read(conversation_id: int, user_id: int) -> int:
    """
    Отметить все непрочитанные сообщения в беседе как прочитанные
    для указанного пользователя (исключая его собственные сообщения)
    """
    query = """
        UPDATE chat_messages 
        SET is_read = TRUE 
        WHERE conversation_id = %s AND sender_id != %s AND is_read = FALSE
    """
    cursor = db.execute_query(query, (conversation_id, user_id))
    return cursor.rowcount


def count_unread_messages(user_id: int) -> Dict[str, Any]:
    """
    Подсчитать непрочитанные сообщения для пользователя 
    по всем беседам и для каждой беседы
    """
    total_query = """
        SELECT COUNT(*) as total_unread
        FROM chat_messages m
        JOIN chat_conversations c ON m.conversation_id = c.id
        JOIN matches mt ON c.match_id = mt.id
        WHERE m.is_read = FALSE AND m.sender_id != %s
        AND (mt.user1_id = %s OR mt.user2_id = %s)
    """
    
    by_conversation_query = """
        SELECT m.conversation_id, COUNT(*) as unread_count
        FROM chat_messages m
        JOIN chat_conversations c ON m.conversation_id = c.id
        JOIN matches mt ON c.match_id = mt.id
        WHERE m.is_read = FALSE AND m.sender_id != %s
        AND (mt.user1_id = %s OR mt.user2_id = %s)
        GROUP BY m.conversation_id
    """
    
    total_result = db.fetch_one(total_query, (user_id, user_id, user_id)) or {}
    conversations = db.fetch_all(by_conversation_query, (user_id, user_id, user_id))
    
    return {
        "total_unread": total_result.get("total_unread", 0),
        "by_conversation": {conv['conversation_id']: conv['unread_count'] for conv in conversations}
    }


def get_agent_simulation_messages(conversation_id: int) -> List[Dict[str, Any]]:
    """Получить сообщения агентов в конкретной беседе"""
    query = """
        SELECT m.*, u.first_name as sender_name
        FROM chat_messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.conversation_id = %s AND m.message_type = 'agent_simulation'
        ORDER BY m.created_at ASC
    """
    return db.fetch_all(query, (conversation_id,))


def get_user_messages(user_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Получить все сообщения, отправленные пользователем"""
    query = """
        SELECT m.*, c.match_id, u.first_name as sender_name
        FROM chat_messages m
        JOIN chat_conversations c ON m.conversation_id = c.id
        JOIN users u ON m.sender_id = u.id
        WHERE m.sender_id = %s
        ORDER BY m.created_at DESC
        LIMIT %s OFFSET %s
    """
    return db.fetch_all(query, (user_id, limit, offset))


def get_conversation_statistics(conversation_id: int) -> Dict[str, Any]:
    """Получить статистику сообщений для беседы"""
    query = """
        SELECT 
            COUNT(*) as total_messages,
            SUM(CASE WHEN message_type = 'user' THEN 1 ELSE 0 END) as user_messages,
            SUM(CASE WHEN message_type = 'agent_simulation' THEN 1 ELSE 0 END) as agent_messages,
            MIN(created_at) as first_message_at,
            MAX(created_at) as last_message_at,
            SUM(CASE WHEN is_read = TRUE THEN 1 ELSE 0 END) as read_messages,
            COUNT(DISTINCT sender_id) as unique_senders
        FROM chat_messages
        WHERE conversation_id = %s
    """
    
    result = db.fetch_one(query, (conversation_id,)) or {}
    total = result.get("total_messages", 0)
    
    # Если нет сообщений, возвращаем нули
    if total == 0:
        return {
            "total_messages": 0,
            "user_messages": 0,
            "agent_messages": 0,
            "first_message_at": None,
            "last_message_at": None,
            "read_percentage": 0,
            "unique_senders": 0
        }
    
    return {
        "total_messages": total,
        "user_messages": result.get("user_messages", 0),
        "agent_messages": result.get("agent_messages", 0),
        "first_message_at": result.get("first_message_at"),
        "last_message_at": result.get("last_message_at"),
        "read_percentage": round(result.get("read_messages", 0) * 100 / total, 1),
        "unique_senders": result.get("unique_senders", 0)
    }


def get_recent_messages(hours: int = 24) -> List[Dict[str, Any]]:
    """Получить сообщения за последние часы"""
    query = """
        SELECT m.*, c.match_id, u.first_name as sender_name
        FROM chat_messages m
        JOIN chat_conversations c ON m.conversation_id = c.id
        JOIN users u ON m.sender_id = u.id
        WHERE m.created_at >= DATE_SUB(NOW(), INTERVAL %s HOUR)
        ORDER BY m.created_at DESC
    """
    return db.fetch_all(query, (hours,))


def search_messages(search_term: str, conversation_id: int = None) -> List[Dict[str, Any]]:
    """Поиск сообщений по тексту"""
    query_parts = [
        """
        SELECT m.*, c.match_id, u.first_name as sender_name
        FROM chat_messages m
        JOIN chat_conversations c ON m.conversation_id = c.id
        JOIN users u ON m.sender_id = u.id
        WHERE m.message_text LIKE %s
        """
    ]
    
    params = [f"%{search_term}%"]
    
    if conversation_id:
        query_parts.append("AND m.conversation_id = %s")
        params.append(conversation_id)
    
    query_parts.append("ORDER BY m.created_at DESC")
    
    query = " ".join(query_parts)
    return db.fetch_all(query, tuple(params))