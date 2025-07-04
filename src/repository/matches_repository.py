from typing import Optional, Dict, Any, List
from datetime import datetime
from src.database.my_connector import db
from src.database.models import Matches


def get_all_matches() -> List[Dict[str, Any]]:
    """Получить все совпадения (матчи)"""
    query = "SELECT * FROM matches"
    return db.fetch_all(query)


def get_match_by_id(match_id: int) -> Optional[Dict[str, Any]]:
    """Получить матч по ID"""
    query = "SELECT * FROM matches WHERE id = %s"
    return db.fetch_one(query, (match_id,))


def check_match_exists(user1_id: int, user2_id: int) -> Optional[Dict[str, Any]]:
    """Проверить существование матча между двумя пользователями"""
    query = """
        SELECT * FROM matches 
        WHERE (user1_id = %s AND user2_id = %s) 
           OR (user1_id = %s AND user2_id = %s)
    """
    return db.fetch_one(query, (user1_id, user2_id, user2_id, user1_id))


def get_match_by_users(user1_id: int, user2_id: int) -> Optional[Dict[str, Any]]:
    """Получить матч между двумя пользователями"""
    # Проверяем в обе стороны, так как пользователи могут быть в любом порядке
    query = """
        SELECT * FROM matches 
        WHERE (user1_id = %s AND user2_id = %s) 
            OR (user1_id = %s AND user2_id = %s)
    """
    return db.fetch_one(query, (user1_id, user2_id, user2_id, user1_id))


def create_match(match: Matches) -> int:
    """Создать новый матч между пользователями"""
    # Проверяем, существует ли уже матч между этими пользователями
    existing = check_match_exists(match.user1_id, match.user2_id)
    if existing:
        # Если матч уже существует и не активен, можем его активировать
        if existing['match_status'] != 'active':
            update_match_status(existing['id'], 'active')
        return existing['id']
    
    query = """
        INSERT INTO matches 
        (user1_id, user2_id, match_status)
        VALUES (%s, %s, %s)
    """
    params = (
        match.user1_id,
        match.user2_id,
        match.match_status
    )
    cursor = db.execute_query(query, params)
    return cursor.lastrowid


def update_match(match_id: int, updates: Dict[str, Any]) -> None:
    """Обновить данные матча"""
    set_clauses = []
    params = []

    field_mapping = {
        "match_status": "MatchStatus"
    }

    for db_field, value in updates.items():
        if db_field in field_mapping and value is not None:
            set_clauses.append(f"{db_field} = %s")
            params.append(value)

    if not set_clauses:
        return

    # Автоматическое обновление поля updated_at
    set_clauses.append("updated_at = NOW()")
    
    params.append(match_id)
    query = f"UPDATE matches SET {', '.join(set_clauses)} WHERE id = %s"
    db.execute_query(query, params)


def update_match_status(match_id: int, status: str) -> None:
    """Обновить статус матча"""
    query = "UPDATE matches SET match_status = %s, updated_at = NOW() WHERE id = %s"
    db.execute_query(query, (status, match_id))


def delete_match(match_id: int) -> None:
    """Удалить матч по ID"""
    query = "DELETE FROM matches WHERE id = %s"
    db.execute_query(query, (match_id,))


def get_user_matches(user_id: int, status: str = None) -> List[Dict[str, Any]]:
    """
    Получить все матчи пользователя.
    Опционально можно указать статус для фильтрации.
    """
    query_parts = [
        """
        SELECT m.*, 
               CASE 
                 WHEN m.user1_id = %s THEN m.user2_id 
                 ELSE m.user1_id 
               END as matched_user_id,
               u.first_name as matched_user_name,
               p.profile_photo_url as matched_user_photo
        FROM matches m
        JOIN users u ON (CASE WHEN m.user1_id = %s THEN m.user2_id ELSE m.user1_id END) = u.id
        LEFT JOIN profile_details p ON u.id = p.user_id
        WHERE (m.user1_id = %s OR m.user2_id = %s)
        """
    ]
    
    params = [user_id, user_id, user_id, user_id]
    
    if status:
        query_parts.append("AND m.match_status = %s")
        params.append(status)
    
    query_parts.append("ORDER BY m.updated_at DESC")
    
    query = " ".join(query_parts)
    return db.fetch_all(query, tuple(params))


def get_active_matches(user_id: int) -> List[Dict[str, Any]]:
    """Получить активные матчи пользователя"""
    return get_user_matches(user_id, 'active')


def get_paused_matches(user_id: int) -> List[Dict[str, Any]]:
    """Получить приостановленные матчи пользователя"""
    return get_user_matches(user_id, 'paused')


def get_ended_matches(user_id: int) -> List[Dict[str, Any]]:
    """Получить завершенные матчи пользователя"""
    return get_user_matches(user_id, 'ended')


def create_match_from_likes(from_user_id: int, to_user_id: int) -> Optional[int]:
    """
    Создать матч между пользователями, если есть взаимные лайки.
    Возвращает ID созданного матча или None, если нет взаимных лайков.
    """
    # Проверяем наличие взаимных лайков
    query = """
        SELECT COUNT(*) as mutual_likes
        FROM user_likes l1
        JOIN user_likes l2 ON l1.from_user_id = l2.to_user_id AND l1.to_user_id = l2.from_user_id
        WHERE (l1.from_user_id = %s AND l1.to_user_id = %s)
    """
    result = db.fetch_one(query, (from_user_id, to_user_id))
    mutual_likes = result.get('mutual_likes', 0) if result else 0
    
    if mutual_likes == 0:
        return None
    
    # Проверяем, не существует ли уже матч
    existing = check_match_exists(from_user_id, to_user_id)
    if existing:
        return existing['id']
    
    # Создаем новый матч
    match = Matches(
        User1ID=from_user_id,
        User2ID=to_user_id,
        MatchStatus='active'
    )
    return create_match(match)


def get_recent_matches(hours: int = 24) -> List[Dict[str, Any]]:
    """Получить недавние матчи за указанное количество часов"""
    query = """
        SELECT m.*, 
               u1.first_name as user1_name, 
               u2.first_name as user2_name,
               p1.profile_photo_url as user1_photo,
               p2.profile_photo_url as user2_photo
        FROM matches m
        JOIN users u1 ON m.user1_id = u1.id
        JOIN users u2 ON m.user2_id = u2.id
        LEFT JOIN profile_details p1 ON u1.id = p1.user_id
        LEFT JOIN profile_details p2 ON u2.id = p2.user_id
        WHERE m.created_at >= DATE_SUB(NOW(), INTERVAL %s HOUR)
        ORDER BY m.created_at DESC
    """
    return db.fetch_all(query, (hours,))


def get_matches_with_conversations() -> List[Dict[str, Any]]:
    """Получить матчи, которые имеют активные беседы"""
    query = """
        SELECT m.*, c.id as conversation_id,
               u1.first_name as user1_name,
               u2.first_name as user2_name,
               COUNT(msg.id) as message_count,
               MAX(msg.created_at) as last_message_at
        FROM matches m
        JOIN users u1 ON m.user1_id = u1.id
        JOIN users u2 ON m.user2_id = u2.id
        JOIN chat_conversations c ON m.id = c.match_id
        LEFT JOIN chat_messages msg ON c.id = msg.conversation_id
        GROUP BY m.id, c.id, u1.first_name, u2.first_name
        HAVING message_count > 0
        ORDER BY last_message_at DESC
    """
    return db.fetch_all(query)


def get_matches_without_conversations() -> List[Dict[str, Any]]:
    """Получить матчи, которые не имеют активных бесед"""
    query = """
        SELECT m.*, 
               u1.first_name as user1_name, 
               u2.first_name as user2_name
        FROM matches m
        JOIN users u1 ON m.user1_id = u1.id
        JOIN users u2 ON m.user2_id = u2.id
        LEFT JOIN chat_conversations c ON m.id = c.match_id
        WHERE c.id IS NULL AND m.match_status = 'active'
        ORDER BY m.created_at DESC
    """
    return db.fetch_all(query)


def get_matches_count() -> Dict[str, int]:
    """Получить статистику по количеству матчей в разных статусах"""
    query = """
        SELECT 
            COUNT(*) as total_matches,
            SUM(CASE WHEN match_status = 'active' THEN 1 ELSE 0 END) as active_matches,
            SUM(CASE WHEN match_status = 'paused' THEN 1 ELSE 0 END) as paused_matches,
            SUM(CASE WHEN match_status = 'ended' THEN 1 ELSE 0 END) as ended_matches
        FROM matches
    """
    
    result = db.fetch_one(query) or {}
    
    return {
        "total": result.get("total_matches", 0),
        "active": result.get("active_matches", 0),
        "paused": result.get("paused_matches", 0),
        "ended": result.get("ended_matches", 0)
    }


def get_user_match_stats(user_id: int) -> Dict[str, Any]:
    """Получить статистику матчей для конкретного пользователя"""
    query = """
        SELECT 
            COUNT(*) as total_matches,
            SUM(CASE WHEN match_status = 'active' THEN 1 ELSE 0 END) as active_matches,
            SUM(CASE WHEN match_status = 'ended' THEN 1 ELSE 0 END) as ended_matches,
            MIN(created_at) as first_match_date,
            MAX(created_at) as last_match_date
        FROM matches
        WHERE user1_id = %s OR user2_id = %s
    """
    
    result = db.fetch_one(query, (user_id, user_id)) or {}
    
    # Дополнительный запрос для получения конверсии в диалоги
    conversations_query = """
        SELECT COUNT(DISTINCT c.id) as conversations_count
        FROM matches m
        JOIN chat_conversations c ON m.id = c.match_id
        WHERE (m.user1_id = %s OR m.user2_id = %s)
    """
    
    conv_result = db.fetch_one(conversations_query, (user_id, user_id)) or {}
    
    total = result.get("total_matches", 0)
    conversations = conv_result.get("conversations_count", 0)
    
    return {
        "total_matches": total,
        "active_matches": result.get("active_matches", 0),
        "ended_matches": result.get("ended_matches", 0),
        "first_match_date": result.get("first_match_date"),
        "last_match_date": result.get("last_match_date"),
        "conversations_count": conversations,
        "conversation_rate": round(conversations * 100 / total, 1) if total > 0 else 0
    }