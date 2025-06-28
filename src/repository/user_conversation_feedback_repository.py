from typing import Optional, Dict, Any, List
from datetime import datetime
from src.database.my_connector import db
from src.database.models import UserConversationFeedback


def get_all_feedback() -> List[Dict[str, Any]]:
    """Получить все записи обратной связи о беседах"""
    query = "SELECT * FROM user_conversation_feedback"
    return db.fetch_all(query)


def get_feedback_by_id(feedback_id: int) -> Optional[Dict[str, Any]]:
    """Получить запись обратной связи по ID"""
    query = "SELECT * FROM user_conversation_feedback WHERE id = %s"
    return db.fetch_one(query, (feedback_id,))


def get_feedback_by_user_conversation(user_id: int, conversation_id: int) -> Optional[Dict[str, Any]]:
    """Получить обратную связь конкретного пользователя о конкретной беседе"""
    query = "SELECT * FROM user_conversation_feedback WHERE user_id = %s AND conversation_id = %s"
    return db.fetch_one(query, (user_id, conversation_id))


def create_feedback(feedback: UserConversationFeedback) -> int:
    """Создать новую запись обратной связи"""
    # Проверяем, не оставлял ли пользователь уже отзыв на эту беседу
    existing = get_feedback_by_user_conversation(feedback.UserID, feedback.ConversationID)
    if existing:
        # Если отзыв уже есть, обновим его
        update_feedback(existing['id'], {
            'rating': feedback.Rating,
            'feedback_text': feedback.FeedbackText
        })
        return existing['id']
    
    query = """
        INSERT INTO user_conversation_feedback 
        (user_id, conversation_id, rating, feedback_text)
        VALUES (%s, %s, %s, %s)
    """
    params = (
        feedback.UserID,
        feedback.ConversationID,
        feedback.Rating,
        feedback.FeedbackText
    )
    cursor = db.execute_query(query, params)
    return cursor.lastrowid


def update_feedback(feedback_id: int, updates: Dict[str, Any]) -> None:
    """Обновить запись обратной связи"""
    set_clauses = []
    params = []

    field_mapping = {
        "rating": "Rating",
        "feedback_text": "FeedbackText"
    }

    for db_field, value in updates.items():
        if db_field in field_mapping and value is not None:
            set_clauses.append(f"{db_field} = %s")
            params.append(value)

    if not set_clauses:
        return

    params.append(feedback_id)
    query = f"UPDATE user_conversation_feedback SET {', '.join(set_clauses)} WHERE id = %s"
    db.execute_query(query, params)


def delete_feedback(feedback_id: int) -> None:
    """Удалить запись обратной связи"""
    query = "DELETE FROM user_conversation_feedback WHERE id = %s"
    db.execute_query(query, (feedback_id,))


def get_conversation_feedback(conversation_id: int) -> List[Dict[str, Any]]:
    """Получить все отзывы о конкретной беседе"""
    query = """
        SELECT f.*, u.first_name
        FROM user_conversation_feedback f
        JOIN users u ON f.user_id = u.id
        WHERE f.conversation_id = %s
        ORDER BY f.created_at DESC
    """
    return db.fetch_all(query, (conversation_id,))


def get_user_feedback(user_id: int) -> List[Dict[str, Any]]:
    """Получить все отзывы, оставленные пользователем"""
    query = """
        SELECT f.*, c.match_id
        FROM user_conversation_feedback f
        JOIN chat_conversations c ON f.conversation_id = c.id
        WHERE f.user_id = %s
        ORDER BY f.created_at DESC
    """
    return db.fetch_all(query, (user_id,))


def get_average_conversation_rating(conversation_id: int) -> float:
    """Получить среднюю оценку беседы"""
    query = "SELECT AVG(rating) as avg_rating FROM user_conversation_feedback WHERE conversation_id = %s"
    result = db.fetch_one(query, (conversation_id,))
    return float(result["avg_rating"]) if result and result["avg_rating"] is not None else 0.0


def get_user_average_rating(user_id: int) -> float:
    """Получить среднюю оценку бесед пользователя"""
    query = """
        SELECT AVG(f.rating) as avg_rating
        FROM user_conversation_feedback f
        JOIN chat_conversations c ON f.conversation_id = c.id
        JOIN matches m ON c.match_id = m.id
        WHERE m.user1_id = %s OR m.user2_id = %s
    """
    result = db.fetch_one(query, (user_id, user_id))
    return float(result["avg_rating"]) if result and result["avg_rating"] is not None else 0.0


def get_conversations_with_highest_ratings(limit: int = 10) -> List[Dict[str, Any]]:
    """Получить беседы с самыми высокими оценками"""
    query = """
        SELECT c.id as conversation_id, c.match_id, 
               AVG(f.rating) as avg_rating, 
               COUNT(f.id) as feedback_count,
               MAX(f.created_at) as last_feedback_at
        FROM chat_conversations c
        JOIN user_conversation_feedback f ON c.id = f.conversation_id
        GROUP BY c.id
        HAVING feedback_count > 0
        ORDER BY avg_rating DESC, feedback_count DESC
        LIMIT %s
    """
    return db.fetch_all(query, (limit,))


def get_feedback_statistics() -> Dict[str, Any]:
    """Получить статистику по обратной связи"""
    stats_query = """
        SELECT 
            COUNT(*) as total_feedback,
            AVG(rating) as average_rating,
            SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END) as positive_count,
            SUM(CASE WHEN rating <= 2 THEN 1 ELSE 0 END) as negative_count
        FROM user_conversation_feedback
    """
    
    recent_query = """
        SELECT COUNT(*) as recent_count
        FROM user_conversation_feedback
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    """
    
    stats = db.fetch_one(stats_query) or {}
    recent = db.fetch_one(recent_query) or {}
    
    return {
        "total_feedback": stats.get("total_feedback", 0),
        "average_rating": float(stats.get("average_rating", 0)),
        "positive_feedback": stats.get("positive_count", 0),
        "negative_feedback": stats.get("negative_count", 0),
        "recent_feedback": recent.get("recent_count", 0)
    }