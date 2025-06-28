from typing import Optional, Dict, Any, List
from datetime import datetime
import json
from src.database.my_connector import db
from src.database.models import AgentSimulationFeedback


def get_all_feedback() -> List[Dict[str, Any]]:
    """Получить всю обратную связь по симуляциям агентов"""
    query = "SELECT * FROM agent_simulation_feedback"
    return db.fetch_all(query)


def get_feedback_by_id(feedback_id: int) -> Optional[Dict[str, Any]]:
    """Получить обратную связь по ID"""
    query = "SELECT * FROM agent_simulation_feedback WHERE id = %s"
    return db.fetch_one(query, (feedback_id,))


def get_feedback_by_simulation(simulation_id: int) -> List[Dict[str, Any]]:
    """Получить всю обратную связь для конкретной симуляции"""
    query = """
        SELECT f.*, u.first_name as user_name
        FROM agent_simulation_feedback f
        JOIN users u ON f.user_id = u.id
        WHERE f.simulation_id = %s
        ORDER BY f.created_at DESC
    """
    return db.fetch_all(query, (simulation_id,))


def get_feedback_by_user(user_id: int) -> List[Dict[str, Any]]:
    """Получить всю обратную связь от конкретного пользователя"""
    query = """
        SELECT f.*, s.agent_id, s.conversation_id
        FROM agent_simulation_feedback f
        JOIN agents_simulations s ON f.simulation_id = s.id
        WHERE f.user_id = %s
        ORDER BY f.created_at DESC
    """
    return db.fetch_all(query, (user_id,))


def get_feedback_by_agent(agent_id: int) -> List[Dict[str, Any]]:
    """Получить всю обратную связь для конкретного агента"""
    query = """
        SELECT f.*, s.conversation_id, u.first_name as user_name
        FROM agent_simulation_feedback f
        JOIN agents_simulations s ON f.simulation_id = s.id
        JOIN users u ON f.user_id = u.id
        WHERE s.agent_id = %s
        ORDER BY f.created_at DESC
    """
    return db.fetch_all(query, (agent_id,))


def create_feedback(feedback: AgentSimulationFeedback) -> int:
    """Создать новую запись обратной связи по симуляции агента"""
    # Проверяем, не оставлял ли пользователь уже отзыв на эту симуляцию
    existing_query = """
        SELECT id FROM agent_simulation_feedback 
        WHERE simulation_id = %s AND user_id = %s
    """
    existing = db.fetch_one(existing_query, (feedback.SimulationID, feedback.UserID))
    
    if existing:
        # Если отзыв уже существует, обновляем его
        update_feedback(existing['id'], {
            'rating': feedback.Rating,
            'feedback_text': feedback.FeedbackText,
            'feedback_details': feedback.FeedbackDetails
        })
        return existing['id']
    
    # Сериализуем JSON-поле с деталями обратной связи
    feedback_details = json.dumps(feedback.FeedbackDetails) if feedback.FeedbackDetails else None
    
    query = """
        INSERT INTO agent_simulation_feedback 
        (simulation_id, user_id, rating, feedback_text, feedback_details)
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (
        feedback.SimulationID,
        feedback.UserID,
        feedback.Rating,
        feedback.FeedbackText,
        feedback_details
    )
    cursor = db.execute_query(query, params)
    return cursor.lastrowid


def update_feedback(feedback_id: int, updates: Dict[str, Any]) -> None:
    """Обновить запись обратной связи"""
    set_clauses = []
    params = []

    # Особая обработка для JSON поля feedback_details
    if 'feedback_details' in updates and updates['feedback_details'] is not None:
        set_clauses.append("feedback_details = %s")
        params.append(json.dumps(updates['feedback_details']))
        updates.pop('feedback_details')
    
    # Обработка остальных полей
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

    # Автоматическое обновление поля updated_at
    set_clauses.append("updated_at = NOW()")
    
    params.append(feedback_id)
    query = f"UPDATE agent_simulation_feedback SET {', '.join(set_clauses)} WHERE id = %s"
    db.execute_query(query, params)


def delete_feedback(feedback_id: int) -> None:
    """Удалить запись обратной связи"""
    query = "DELETE FROM agent_simulation_feedback WHERE id = %s"
    db.execute_query(query, (feedback_id,))


def delete_simulation_feedback(simulation_id: int) -> int:
    """Удалить всю обратную связь для конкретной симуляции"""
    query = "DELETE FROM agent_simulation_feedback WHERE simulation_id = %s"
    cursor = db.execute_query(query, (simulation_id,))
    return cursor.rowcount


def get_average_rating_by_simulation(simulation_id: int) -> float:
    """Получить среднюю оценку для симуляции"""
    query = "SELECT AVG(rating) as average_rating FROM agent_simulation_feedback WHERE simulation_id = %s"
    result = db.fetch_one(query, (simulation_id,))
    return float(result.get('average_rating', 0)) if result and result.get('average_rating') else 0.0


def get_average_rating_by_agent(agent_id: int) -> float:
    """Получить среднюю оценку для агента по всем симуляциям"""
    query = """
        SELECT AVG(f.rating) as average_rating 
        FROM agent_simulation_feedback f
        JOIN agents_simulations s ON f.simulation_id = s.id
        WHERE s.agent_id = %s
    """
    result = db.fetch_one(query, (agent_id,))
    return float(result.get('average_rating', 0)) if result and result.get('average_rating') else 0.0


def get_agent_feedback_stats(agent_id: int) -> Dict[str, Any]:
    """Получить статистику обратной связи для агента"""
    query = """
        SELECT 
            COUNT(*) as total_feedback,
            AVG(f.rating) as average_rating,
            SUM(CASE WHEN f.rating >= 4 THEN 1 ELSE 0 END) as positive_feedback,
            SUM(CASE WHEN f.rating <= 2 THEN 1 ELSE 0 END) as negative_feedback,
            MIN(f.rating) as min_rating,
            MAX(f.rating) as max_rating
        FROM agent_simulation_feedback f
        JOIN agents_simulations s ON f.simulation_id = s.id
        WHERE s.agent_id = %s
    """
    
    result = db.fetch_one(query, (agent_id,)) or {}
    
    # Дополнительный запрос для детализации по рейтингам
    ratings_query = """
        SELECT f.rating, COUNT(*) as count
        FROM agent_simulation_feedback f
        JOIN agents_simulations s ON f.simulation_id = s.id
        WHERE s.agent_id = %s
        GROUP BY f.rating
    """
    
    ratings = db.fetch_all(ratings_query, (agent_id,))
    rating_distribution = {row.get('rating', 0): row.get('count', 0) for row in ratings}
    
    return {
        "total_feedback": result.get("total_feedback", 0),
        "average_rating": float(result.get("average_rating", 0)) if result.get("average_rating") else 0.0,
        "positive_feedback": result.get("positive_feedback", 0),
        "negative_feedback": result.get("negative_feedback", 0),
        "min_rating": result.get("min_rating"),
        "max_rating": result.get("max_rating"),
        "rating_distribution": rating_distribution
    }


def get_recent_feedback(hours: int = 24) -> List[Dict[str, Any]]:
    """Получить недавнюю обратную связь за указанное количество часов"""
    query = """
        SELECT f.*, s.agent_id, s.conversation_id, u.first_name as user_name
        FROM agent_simulation_feedback f
        JOIN agents_simulations s ON f.simulation_id = s.id
        JOIN users u ON f.user_id = u.id
        WHERE f.created_at >= DATE_SUB(NOW(), INTERVAL %s HOUR)
        ORDER BY f.created_at DESC
    """
    return db.fetch_all(query, (hours,))


def get_feedback_with_comments() -> List[Dict[str, Any]]:
    """Получить обратную связь с текстовыми комментариями"""
    query = """
        SELECT f.*, s.agent_id, u.first_name as user_name
        FROM agent_simulation_feedback f
        JOIN agents_simulations s ON f.simulation_id = s.id
        JOIN users u ON f.user_id = u.id
        WHERE f.feedback_text IS NOT NULL AND f.feedback_text != ''
        ORDER BY f.created_at DESC
    """
    return db.fetch_all(query)


def get_feedback_stats() -> Dict[str, Any]:
    """Получить общую статистику по обратной связи для агентов"""
    query = """
        SELECT 
            COUNT(*) as total_feedback,
            AVG(rating) as average_rating,
            SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END) as positive_feedback,
            SUM(CASE WHEN rating <= 2 THEN 1 ELSE 0 END) as negative_feedback,
            MIN(created_at) as first_feedback_date,
            MAX(created_at) as last_feedback_date
        FROM agent_simulation_feedback
    """
    
    result = db.fetch_one(query) or {}
    
    # Дополнительный запрос для статистики по последним 24 часам
    recent_query = """
        SELECT COUNT(*) as recent_count, AVG(rating) as recent_avg_rating
        FROM agent_simulation_feedback
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
    """
    recent = db.fetch_one(recent_query) or {}
    
    # Дополнительный запрос для получения топовых агентов по отзывам
    top_agents_query = """
        SELECT 
            s.agent_id, 
            COUNT(f.id) as feedback_count, 
            AVG(f.rating) as avg_rating
        FROM agent_simulation_feedback f
        JOIN agents_simulations s ON f.simulation_id = s.id
        GROUP BY s.agent_id
        ORDER BY avg_rating DESC, feedback_count DESC
        LIMIT 5
    """
    top_agents = db.fetch_all(top_agents_query)
    
    return {
        "total_feedback": result.get("total_feedback", 0),
        "average_rating": float(result.get("average_rating", 0)) if result.get("average_rating") else 0.0,
        "positive_feedback": result.get("positive_feedback", 0),
        "negative_feedback": result.get("negative_feedback", 0),
        "first_feedback_date": result.get("first_feedback_date"),
        "last_feedback_date": result.get("last_feedback_date"),
        "last_24h": {
            "feedback_count": recent.get("recent_count", 0),
            "average_rating": float(recent.get("recent_avg_rating", 0)) if recent.get("recent_avg_rating") else 0.0
        },
        "top_agents": [
            {"agent_id": agent.get("agent_id"), "feedback_count": agent.get("feedback_count"), "avg_rating": agent.get("avg_rating")} 
            for agent in top_agents
        ]
    }