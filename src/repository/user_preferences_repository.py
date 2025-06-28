from typing import Optional, Dict, Any, List
from datetime import datetime
import json
from src.database.my_connector import db
from src.database.models import UserPreferences


def get_all_preferences() -> List[Dict[str, Any]]:
    """Получить все записи о предпочтениях пользователей"""
    query = "SELECT * FROM user_preferences"
    return db.fetch_all(query)


def get_preference_by_id(preference_id: int) -> Optional[Dict[str, Any]]:
    """Получить запись о предпочтениях по ID"""
    query = "SELECT * FROM user_preferences WHERE id = %s"
    return db.fetch_one(query, (preference_id,))


def get_preference_by_user_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Получить предпочтения пользователя по ID пользователя"""
    query = "SELECT * FROM user_preferences WHERE user_id = %s"
    return db.fetch_one(query, (user_id,))


def create_preference(preference: UserPreferences) -> int:
    """Создать новую запись о предпочтениях пользователя"""
    preferred_genders = json.dumps(preference.PreferredGenders) if preference.PreferredGenders else None
    other_preferences = json.dumps(preference.OtherPreferences) if preference.OtherPreferences else None

    query = """
        INSERT INTO user_preferences 
        (user_id, age_min, age_max, preferred_genders, preferred_distance, other_preferences)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (
        preference.UserID,
        preference.AgeMin,
        preference.AgeMax,
        preferred_genders,
        preference.PreferredDistance,
        other_preferences
    )
    cursor = db.execute_query(query, params)
    return cursor.lastrowid


def update_preference(preference_id: int, updates: Dict[str, Any]) -> None:
    """Обновить запись о предпочтениях"""
    set_clauses = []
    params = []

    # Особая обработка для JSON полей
    if 'preferred_genders' in updates and updates['preferred_genders'] is not None:
        set_clauses.append("preferred_genders = %s")
        params.append(json.dumps(updates['preferred_genders']))
        updates.pop('preferred_genders')
    
    if 'other_preferences' in updates and updates['other_preferences'] is not None:
        set_clauses.append("other_preferences = %s")
        params.append(json.dumps(updates['other_preferences']))
        updates.pop('other_preferences')

    # Обработка остальных полей
    field_mapping = {
        "age_min": "AgeMin",
        "age_max": "AgeMax",
        "preferred_distance": "PreferredDistance"
    }

    for db_field, value in updates.items():
        if db_field in field_mapping and value is not None:
            set_clauses.append(f"{db_field} = %s")
            params.append(value)

    if not set_clauses:
        return

    # Автоматическое обновление поля updated_at
    set_clauses.append("updated_at = NOW()")
    
    params.append(preference_id)
    query = f"UPDATE user_preferences SET {', '.join(set_clauses)} WHERE id = %s"
    db.execute_query(query, params)


def update_user_preference(user_id: int, updates: Dict[str, Any]) -> None:
    """Обновить предпочтения по ID пользователя"""
    preference = get_preference_by_user_id(user_id)
    
    if preference:
        update_preference(preference['id'], updates)
    else:
        # Если предпочтений еще нет, создадим новую запись
        new_preference = UserPreferences(
            UserID=user_id,
            AgeMin=updates.get('age_min'),
            AgeMax=updates.get('age_max'),
            PreferredGenders=updates.get('preferred_genders'),
            PreferredDistance=updates.get('preferred_distance'),
            OtherPreferences=updates.get('other_preferences')
        )
        create_preference(new_preference)


def delete_preference(preference_id: int) -> None:
    """Удалить запись о предпочтениях"""
    query = "DELETE FROM user_preferences WHERE id = %s"
    db.execute_query(query, (preference_id,))


def delete_user_preferences(user_id: int) -> None:
    """Удалить предпочтения пользователя по ID пользователя"""
    query = "DELETE FROM user_preferences WHERE user_id = %s"
    db.execute_query(query, (user_id,))


def get_users_by_preferences(age: int, gender: str, distance: int = None, interests: List[str] = None) -> List[Dict[str, Any]]:
    """Найти пользователей с указанными предпочтениями (для системы рекомендаций)"""
    query_parts = [
        "SELECT u.* FROM users u",
        "INNER JOIN user_preferences p ON u.id = p.user_id",
        "WHERE p.age_min <= %s AND p.age_max >= %s",
        "AND JSON_CONTAINS(p.preferred_genders, %s)"
    ]
    params = [age, age, json.dumps(gender)]
    
    if distance is not None:
        query_parts.append("AND p.preferred_distance >= %s")
        params.append(distance)
    
    if interests and len(interests) > 0:
        interests_condition = []
        for interest in interests:
            interests_condition.append("JSON_CONTAINS(p.other_preferences->'$.interests', %s)")
            params.append(json.dumps(interest))
        
        query_parts.append(f"AND ({' OR '.join(interests_condition)})")
    
    query = " ".join(query_parts)
    return db.fetch_all(query, tuple(params))


def get_common_preferences(user_id1: int, user_id2: int) -> Dict[str, Any]:
    """Получить общие предпочтения между двумя пользователями (для алгоритма совместимости)"""
    query = """
        SELECT 
            p1.other_preferences->'$.interests' AS user1_interests,
            p2.other_preferences->'$.interests' AS user2_interests
        FROM 
            user_preferences p1,
            user_preferences p2
        WHERE 
            p1.user_id = %s AND p2.user_id = %s
    """
    result = db.fetch_one(query, (user_id1, user_id2))
    
    if not result:
        return {"common_interests": []}
    
    user1_interests = json.loads(result['user1_interests']) if result['user1_interests'] else []
    user2_interests = json.loads(result['user2_interests']) if result['user2_interests'] else []
    
    common_interests = list(set(user1_interests) & set(user2_interests))
    
    return {
        "common_interests": common_interests,
        "interest_match_percent": round(len(common_interests) * 100 / max(len(user1_interests), len(user2_interests), 1))
    }