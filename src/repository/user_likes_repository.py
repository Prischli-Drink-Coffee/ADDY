from typing import Optional, Dict, Any, List
from datetime import datetime
from src.database.my_connector import db
from src.database.models import UserLikes


def get_all_likes() -> List[Dict[str, Any]]:
    """Получить все лайки между пользователями"""
    query = "SELECT * FROM user_likes"
    return db.fetch_all(query)


def get_like_by_id(like_id: int) -> Optional[Dict[str, Any]]:
    """Получить лайк по ID"""
    query = "SELECT * FROM user_likes WHERE id = %s"
    return db.fetch_one(query, (like_id,))


def check_like_exists(from_user_id: int, to_user_id: int) -> bool:
    """Проверить, существует ли лайк от одного пользователя к другому"""
    query = "SELECT id FROM user_likes WHERE from_user_id = %s AND to_user_id = %s"
    result = db.fetch_one(query, (from_user_id, to_user_id))
    return result is not None


def create_like(like: UserLikes) -> int:
    """Создать новый лайк"""
    # Проверяем, не существует ли уже такой лайк
    if check_like_exists(like.FromUserID, like.ToUserID):
        # Лайк уже существует
        return 0
    
    query = """
        INSERT INTO user_likes (from_user_id, to_user_id)
        VALUES (%s, %s)
    """
    params = (
        like.FromUserID,
        like.ToUserID
    )
    cursor = db.execute_query(query, params)
    return cursor.lastrowid


def delete_like(like_id: int) -> None:
    """Удалить лайк по ID"""
    query = "DELETE FROM user_likes WHERE id = %s"
    db.execute_query(query, (like_id,))


def delete_user_like(from_user_id: int, to_user_id: int) -> None:
    """Удалить лайк от одного пользователя к другому"""
    query = "DELETE FROM user_likes WHERE from_user_id = %s AND to_user_id = %s"
    db.execute_query(query, (from_user_id, to_user_id))


def get_likes_from_user(user_id: int) -> List[Dict[str, Any]]:
    """Получить все лайки, поставленные пользователем"""
    query = """
        SELECT l.*, u.first_name, u.email
        FROM user_likes l
        INNER JOIN users u ON l.to_user_id = u.id
        WHERE l.from_user_id = %s
        ORDER BY l.created_at DESC
    """
    return db.fetch_all(query, (user_id,))


def get_likes_to_user(user_id: int) -> List[Dict[str, Any]]:
    """Получить все лайки, полученные пользователем"""
    query = """
        SELECT l.*, u.first_name, u.email
        FROM user_likes l
        INNER JOIN users u ON l.from_user_id = u.id
        WHERE l.to_user_id = %s
        ORDER BY l.created_at DESC
    """
    return db.fetch_all(query, (user_id,))


def check_mutual_like(user1_id: int, user2_id: int) -> bool:
    """Проверить наличие взаимных лайков между двумя пользователями"""
    query = """
        SELECT COUNT(*) as count
        FROM user_likes l1
        JOIN user_likes l2 ON l1.from_user_id = l2.to_user_id AND l1.to_user_id = l2.from_user_id
        WHERE (l1.from_user_id = %s AND l1.to_user_id = %s)
    """
    result = db.fetch_one(query, (user1_id, user2_id))
    return result["count"] > 0 if result else False


def get_mutual_likes(user_id: int) -> List[Dict[str, Any]]:
    """Получить список пользователей с взаимными лайками"""
    query = """
        SELECT u.id, u.first_name, u.email, u.last_activity, 
               MAX(l1.created_at) as like_created_at
        FROM users u
        JOIN user_likes l1 ON l1.to_user_id = u.id AND l1.from_user_id = %s
        JOIN user_likes l2 ON l2.from_user_id = u.id AND l2.to_user_id = %s
        GROUP BY u.id
        ORDER BY like_created_at DESC
    """
    return db.fetch_all(query, (user_id, user_id))


def get_potential_matches(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Получить список потенциальных совпадений для пользователя 
    (те, кто поставил лайк пользователю, но он им ещё нет)
    """
    query = """
        SELECT u.id, u.first_name, u.email, u.last_activity, l.created_at as like_created_at
        FROM users u
        JOIN user_likes l ON l.from_user_id = u.id AND l.to_user_id = %s
        LEFT JOIN user_likes l2 ON l2.from_user_id = %s AND l2.to_user_id = u.id
        WHERE l2.id IS NULL
        ORDER BY l.created_at DESC
        LIMIT %s
    """
    return db.fetch_all(query, (user_id, user_id, limit))


def count_likes_from_user(user_id: int) -> int:
    """Подсчитать количество лайков, поставленных пользователем"""
    query = "SELECT COUNT(*) as count FROM user_likes WHERE from_user_id = %s"
    result = db.fetch_one(query, (user_id,))
    return result["count"] if result else 0


def count_likes_to_user(user_id: int) -> int:
    """Подсчитать количество лайков, полученных пользователем"""
    query = "SELECT COUNT(*) as count FROM user_likes WHERE to_user_id = %s"
    result = db.fetch_one(query, (user_id,))
    return result["count"] if result else 0


def get_recent_likes(hours: int = 24) -> List[Dict[str, Any]]:
    """Получить список недавних лайков за указанное количество часов"""
    query = """
        SELECT l.*, u1.first_name as from_user_name, u2.first_name as to_user_name
        FROM user_likes l
        JOIN users u1 ON l.from_user_id = u1.id
        JOIN users u2 ON l.to_user_id = u2.id
        WHERE l.created_at >= DATE_SUB(NOW(), INTERVAL %s HOUR)
        ORDER BY l.created_at DESC
    """
    return db.fetch_all(query, (hours,))