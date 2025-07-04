from typing import Optional, Dict, Any, List
from datetime import datetime
from src.database.my_connector import db
from src.database.models import ProfileDetails


def get_all_profiles() -> List[Dict[str, Any]]:
    """Получить все профили пользователей"""
    query = "SELECT * FROM profile_details"
    return db.fetch_all(query)


def get_profile_by_id(profile_id: int) -> Optional[Dict[str, Any]]:
    """Получить профиль по ID"""
    query = "SELECT * FROM profile_details WHERE id = %s"
    return db.fetch_one(query, (profile_id,))


def get_profile_by_user_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Получить профиль по ID пользователя"""
    query = "SELECT * FROM profile_details WHERE user_id = %s"
    return db.fetch_one(query, (user_id,))


def create_profile(profile: ProfileDetails) -> int:
    """Создать новый профиль пользователя"""
    # Проверяем, существует ли уже профиль для этого пользователя
    existing = get_profile_by_user_id(profile.user_id)
    if existing:
        # Профиль уже существует, возвращаем его ID
        return existing['id']
    
    query = """
        INSERT INTO profile_details 
        (user_id, age, gender, interests, bio, profile_photo_url, location)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        profile.user_id,
        profile.age,
        profile.gender,
        profile.interests,
        profile.bio,
        profile.profile_photo_url,
        profile.location
    )
    cursor = db.execute_query(query, params)
    return cursor.lastrowid


def update_profile(profile_id: int, updates: Dict[str, Any]) -> None:
    """Обновить профиль пользователя по ID профиля"""
    set_clauses = []
    params = []

    field_mapping = {
        "age": "Age",
        "gender": "Gender",
        "interests": "Interests",
        "bio": "Bio",
        "profile_photo_url": "ProfilePhotoUrl",
        "location": "Location"
    }

    for db_field, value in updates.items():
        if db_field in field_mapping and value is not None:
            set_clauses.append(f"{db_field} = %s")
            params.append(value)

    if not set_clauses:
        return

    # Автоматическое обновление поля updated_at
    set_clauses.append("updated_at = NOW()")
    
    params.append(profile_id)
    query = f"UPDATE profile_details SET {', '.join(set_clauses)} WHERE id = %s"
    db.execute_query(query, params)


def update_user_profile(user_id: int, updates: Dict[str, Any]) -> None:
    """Обновить профиль по ID пользователя"""
    profile = get_profile_by_user_id(user_id)
    
    if profile:
        update_profile(profile['id'], updates)
    else:
        # Если профиля еще нет, создаем новый
        new_profile = ProfileDetails(
            UserID=user_id,
            Age=updates.get('age'),
            Gender=updates.get('gender'),
            Interests=updates.get('interests'),
            Bio=updates.get('bio'),
            ProfilePhotoUrl=updates.get('profile_photo_url'),
            Location=updates.get('location')
        )
        create_profile(new_profile)


def delete_profile(profile_id: int) -> None:
    """Удалить профиль по ID"""
    query = "DELETE FROM profile_details WHERE id = %s"
    db.execute_query(query, (profile_id,))


def delete_user_profile(user_id: int) -> None:
    """Удалить профиль по ID пользователя"""
    query = "DELETE FROM profile_details WHERE user_id = %s"
    db.execute_query(query, (user_id,))


def get_profiles_by_age_range(min_age: int, max_age: int) -> List[Dict[str, Any]]:
    """Получить профили в заданном возрастном диапазоне"""
    query = """
        SELECT p.*, u.first_name, u.email, u.last_activity
        FROM profile_details p
        JOIN users u ON p.user_id = u.id
        WHERE p.age BETWEEN %s AND %s
        ORDER BY u.last_activity DESC
    """
    return db.fetch_all(query, (min_age, max_age))


def get_profiles_by_gender(gender: str) -> List[Dict[str, Any]]:
    """Получить профили по полу"""
    query = """
        SELECT p.*, u.first_name, u.email, u.last_activity
        FROM profile_details p
        JOIN users u ON p.user_id = u.id
        WHERE p.gender = %s
        ORDER BY u.last_activity DESC
    """
    return db.fetch_all(query, (gender,))


def get_profiles_by_location(location: str) -> List[Dict[str, Any]]:
    """Получить профили по местоположению"""
    query = """
        SELECT p.*, u.first_name, u.email, u.last_activity
        FROM profile_details p
        JOIN users u ON p.user_id = u.id
        WHERE p.location LIKE %s
        ORDER BY u.last_activity DESC
    """
    return db.fetch_all(query, (f"%{location}%",))


def search_profiles_by_interests(interests: List[str]) -> List[Dict[str, Any]]:
    """Поиск профилей по интересам"""
    conditions = []
    params = []
    
    for interest in interests:
        conditions.append("p.interests LIKE %s")
        params.append(f"%{interest}%")
    
    query = f"""
        SELECT p.*, u.first_name, u.email, u.last_activity
        FROM profile_details p
        JOIN users u ON p.user_id = u.id
        WHERE {' OR '.join(conditions)}
        ORDER BY u.last_activity DESC
    """
    return db.fetch_all(query, tuple(params))


def get_profiles_with_photo() -> List[Dict[str, Any]]:
    """Получить профили с фотографиями"""
    query = """
        SELECT p.*, u.first_name, u.email, u.last_activity
        FROM profile_details p
        JOIN users u ON p.user_id = u.id
        WHERE p.profile_photo_url IS NOT NULL AND p.profile_photo_url != ''
        ORDER BY u.last_activity DESC
    """
    return db.fetch_all(query)


def get_incomplete_profiles() -> List[Dict[str, Any]]:
    """Получить неполные профили (без важных данных)"""
    query = """
        SELECT p.*, u.first_name, u.email, u.last_activity
        FROM profile_details p
        JOIN users u ON p.user_id = u.id
        WHERE p.age IS NULL 
           OR p.gender IS NULL 
           OR p.bio IS NULL 
           OR p.location IS NULL
           OR p.profile_photo_url IS NULL
        ORDER BY u.last_activity DESC
    """
    return db.fetch_all(query)


def get_profile_completion_stats() -> Dict[str, Any]:
    """Получить статистику заполнения профилей"""
    query = """
        SELECT 
            COUNT(*) as total_profiles,
            SUM(CASE WHEN age IS NOT NULL THEN 1 ELSE 0 END) as age_count,
            SUM(CASE WHEN gender IS NOT NULL THEN 1 ELSE 0 END) as gender_count,
            SUM(CASE WHEN interests IS NOT NULL THEN 1 ELSE 0 END) as interests_count,
            SUM(CASE WHEN bio IS NOT NULL THEN 1 ELSE 0 END) as bio_count,
            SUM(CASE WHEN profile_photo_url IS NOT NULL THEN 1 ELSE 0 END) as photo_count,
            SUM(CASE WHEN location IS NOT NULL THEN 1 ELSE 0 END) as location_count
        FROM profile_details
    """
    
    result = db.fetch_one(query) or {}
    total = result.get("total_profiles", 0)
    
    if total == 0:
        return {
            "total_profiles": 0,
            "completion_percentages": {
                "age": 0,
                "gender": 0,
                "interests": 0,
                "bio": 0,
                "photo": 0,
                "location": 0,
                "overall": 0
            }
        }
    
    return {
        "total_profiles": total,
        "completion_percentages": {
            "age": round(result.get("age_count", 0) * 100 / total, 1),
            "gender": round(result.get("gender_count", 0) * 100 / total, 1),
            "interests": round(result.get("interests_count", 0) * 100 / total, 1),
            "bio": round(result.get("bio_count", 0) * 100 / total, 1),
            "photo": round(result.get("photo_count", 0) * 100 / total, 1),
            "location": round(result.get("location_count", 0) * 100 / total, 1),
            "overall": round(
                (result.get("age_count", 0) + result.get("gender_count", 0) + 
                 result.get("interests_count", 0) + result.get("bio_count", 0) + 
                 result.get("photo_count", 0) + result.get("location_count", 0)) * 100 / (total * 6), 1)
        }
    }