from typing import Optional, Dict, Any, List
from datetime import datetime
from src.database.my_connector import db
from src.database.models import ChatConversations


def get_all_conversations() -> List[Dict[str, Any]]:
    """Получить все беседы"""
    query = "SELECT * FROM chat_conversations"
    return db.fetch_all(query)


def get_conversation_by_id(conversation_id: int) -> Optional[Dict[str, Any]]:
    """Получить беседу по ID"""
    query = "SELECT * FROM chat_conversations WHERE id = %s"
    return db.fetch_one(query, (conversation_id,))


def get_conversation_by_match_id(match_id: int) -> Optional[Dict[str, Any]]:
    """Получить беседу по ID матча"""
    query = "SELECT * FROM chat_conversations WHERE match_id = %s"
    return db.fetch_one(query, (match_id,))


def create_conversation(conversation: ChatConversations) -> int:
    """Создать новую беседу"""
    # Проверяем, не существует ли уже беседа для этого матча
    existing = get_conversation_by_match_id(conversation.MatchID)
    if existing:
        # Беседа уже существует
        return existing['id']
    
    query = """
        INSERT INTO chat_conversations 
        (match_id, last_message_at)
        VALUES (%s, %s)
    """
    params = (
        conversation.MatchID,
        conversation.LastMessageAt or datetime.utcnow()
    )
    cursor = db.execute_query(query, params)
    return cursor.lastrowid


def update_conversation(conversation_id: int, updates: Dict[str, Any]) -> None:
    """Обновить беседу"""
    set_clauses = []
    params = []

    field_mapping = {
        "last_message_at": "LastMessageAt"
    }

    for db_field, value in updates.items():
        if db_field in field_mapping and value is not None:
            set_clauses.append(f"{db_field} = %s")
            params.append(value)

    if not set_clauses:
        return

    params.append(conversation_id)
    query = f"UPDATE chat_conversations SET {', '.join(set_clauses)} WHERE id = %s"
    db.execute_query(query, params)


def update_last_message_time(conversation_id: int) -> None:
    """Обновить время последнего сообщения в беседе (прямо сейчас)"""
    query = "UPDATE chat_conversations SET last_message_at = NOW() WHERE id = %s"
    db.execute_query(query, (conversation_id,))


def delete_conversation(conversation_id: int) -> None:
    """Удалить беседу по ID"""
    # Примечание: это может привести к потере связанных сообщений,
    # в зависимости от настроек внешних ключей в базе данных
    query = "DELETE FROM chat_conversations WHERE id = %s"
    db.execute_query(query, (conversation_id,))


def get_user_conversations(user_id: int) -> List[Dict[str, Any]]:
    """Получить все беседы пользователя"""
    query = """
        SELECT c.*, 
               m.user1_id, m.user2_id, m.match_status,
               CASE 
                 WHEN m.user1_id = %s THEN m.user2_id 
                 ELSE m.user1_id 
               END as other_user_id,
               u.first_name as other_user_name,
               p.profile_photo_url as other_user_photo,
               (SELECT COUNT(*) FROM chat_messages msg 
                WHERE msg.conversation_id = c.id AND msg.is_read = FALSE AND msg.sender_id != %s) as unread_count
        FROM chat_conversations c
        JOIN matches m ON c.match_id = m.id
        JOIN users u ON (CASE WHEN m.user1_id = %s THEN m.user2_id ELSE m.user1_id END) = u.id
        LEFT JOIN profile_details p ON u.id = p.user_id
        WHERE m.user1_id = %s OR m.user2_id = %s
        ORDER BY c.last_message_at DESC
    """
    return db.fetch_all(query, (user_id, user_id, user_id, user_id, user_id))


def get_active_conversations() -> List[Dict[str, Any]]:
    """Получить все активные беседы (в которых есть сообщения)"""
    query = """
        SELECT c.*, 
               m.user1_id, m.user2_id, m.match_status,
               u1.first_name as user1_name,
               u2.first_name as user2_name,
               COUNT(msg.id) as message_count,
               MAX(msg.created_at) as last_message_at
        FROM chat_conversations c
        JOIN matches m ON c.match_id = m.id
        JOIN users u1 ON m.user1_id = u1.id
        JOIN users u2 ON m.user2_id = u2.id
        LEFT JOIN chat_messages msg ON c.id = msg.conversation_id
        GROUP BY c.id, m.user1_id, m.user2_id, m.match_status, u1.first_name, u2.first_name
        HAVING message_count > 0
        ORDER BY last_message_at DESC
    """
    return db.fetch_all(query)


def get_empty_conversations() -> List[Dict[str, Any]]:
    """Получить все пустые беседы (без сообщений)"""
    query = """
        SELECT c.*, 
               m.user1_id, m.user2_id, m.match_status,
               u1.first_name as user1_name,
               u2.first_name as user2_name
        FROM chat_conversations c
        JOIN matches m ON c.match_id = m.id
        JOIN users u1 ON m.user1_id = u1.id
        JOIN users u2 ON m.user2_id = u2.id
        LEFT JOIN (
            SELECT conversation_id, COUNT(*) as msg_count 
            FROM chat_messages 
            GROUP BY conversation_id
        ) msg_count ON c.id = msg_count.conversation_id
        WHERE msg_count.msg_count IS NULL OR msg_count.msg_count = 0
    """
    return db.fetch_all(query)


def get_conversations_with_recent_activity(hours: int = 24) -> List[Dict[str, Any]]:
    """Получить беседы с активностью за последние часы"""
    query = """
        SELECT c.*, 
               m.user1_id, m.user2_id, m.match_status,
               u1.first_name as user1_name,
               u2.first_name as user2_name
        FROM chat_conversations c
        JOIN matches m ON c.match_id = m.id
        JOIN users u1 ON m.user1_id = u1.id
        JOIN users u2 ON m.user2_id = u2.id
        WHERE c.last_message_at >= DATE_SUB(NOW(), INTERVAL %s HOUR)
        ORDER BY c.last_message_at DESC
    """
    return db.fetch_all(query, (hours,))


def get_conversation_with_messages(conversation_id: int, limit: int = 50) -> Dict[str, Any]:
    """Получить беседу вместе с ее сообщениями"""
    # Получаем информацию о беседе
    conversation_query = """
        SELECT c.*, 
               m.user1_id, m.user2_id, m.match_status,
               u1.first_name as user1_name,
               u2.first_name as user2_name
        FROM chat_conversations c
        JOIN matches m ON c.match_id = m.id
        JOIN users u1 ON m.user1_id = u1.id
        JOIN users u2 ON m.user2_id = u2.id
        WHERE c.id = %s
    """
    conversation = db.fetch_one(conversation_query, (conversation_id,))
    
    if not conversation:
        return {}
    
    # Получаем сообщения беседы
    messages_query = """
        SELECT m.*, u.first_name as sender_name
        FROM chat_messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.conversation_id = %s
        ORDER BY m.created_at DESC
        LIMIT %s
    """
    messages = db.fetch_all(messages_query, (conversation_id, limit))
    
    # Объединяем все в один результат
    result = conversation.copy()
    result['messages'] = messages
    
    return result


def get_conversation_statistics() -> Dict[str, Any]:
    """Получить статистику по беседам"""
    query = """
        SELECT 
            COUNT(*) as total_conversations,
            SUM(CASE WHEN last_message_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR) THEN 1 ELSE 0 END) as active_24h,
            SUM(CASE WHEN last_message_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 ELSE 0 END) as active_7d,
            AVG(msg_count.count) as avg_messages_per_conversation
        FROM chat_conversations c
        LEFT JOIN (
            SELECT conversation_id, COUNT(*) as count 
            FROM chat_messages 
            GROUP BY conversation_id
        ) msg_count ON c.id = msg_count.conversation_id
    """
    
    result = db.fetch_one(query) or {}
    
    # Дополнительный запрос для подсчета бесед с агентскими сообщениями
    agent_query = """
        SELECT COUNT(DISTINCT c.id) as agent_conversations
        FROM chat_conversations c
        JOIN chat_messages m ON c.id = m.conversation_id
        WHERE m.message_type = 'agent_simulation'
    """
    
    agent_result = db.fetch_one(agent_query) or {}
    
    return {
        "total_conversations": result.get("total_conversations", 0),
        "active_last_24h": result.get("active_24h", 0),
        "active_last_7d": result.get("active_7d", 0),
        "avg_messages_per_conversation": float(result.get("avg_messages_per_conversation", 0)),
        "conversations_with_agent_messages": agent_result.get("agent_conversations", 0)
    }