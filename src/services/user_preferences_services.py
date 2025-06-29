from typing import Optional, Dict, Any, List
from datetime import datetime
import json
from fastapi import HTTPException, status
from src.repository import user_preferences_repository
from src.database.models import UserPreferences
from src.utils.custom_logging import get_logger

log = get_logger(__name__)


class PreferencesNotFoundError(HTTPException):
    def __init__(self, user_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Preferences for user {user_id} not found'
        )


class PreferencesValidationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


def get_preferences_by_id(preference_id: int) -> UserPreferences:
    """Получить предпочтения по ID записи"""
    pref_data = user_preferences_repository.get_preference_by_id(preference_id)
    if not pref_data:
        raise PreferencesNotFoundError(preference_id)
    return _convert_db_preferences(pref_data)


def get_preferences_by_user(user_id: int) -> UserPreferences:
    """Получить предпочтения пользователя по ID пользователя"""
    pref_data = user_preferences_repository.get_preference_by_user_id(user_id)
    if not pref_data:
        raise PreferencesNotFoundError(user_id)
    return _convert_db_preferences(pref_data)


def create_preferences(user_id: int, preferences: UserPreferences) -> UserPreferences:
    """Создать новые предпочтения для пользователя"""
    # Проверяем, что пользователь существует и у него еще нет предпочтений
    try:
        existing = get_preferences_by_user(user_id)
        raise PreferencesValidationError(
            f"User {user_id} already has preferences (ID: {existing.id})"
        )
    except PreferencesNotFoundError:
        pass
    
    # Валидация данных
    if preferences.age_min and preferences.age_max and preferences.age_min > preferences.age_max:
        raise PreferencesValidationError(
            "Minimum age cannot be greater than maximum age"
        )
    
    if preferences.preferred_distance and preferences.preferred_distance < 0:
        raise PreferencesValidationError(
            "Preferred distance cannot be negative"
        )
    
    # Создаем запись в БД
    pref_id = user_preferences_repository.create_preference(preferences)
    return get_preferences_by_id(pref_id)


def update_preferences(user_id: int, updates: Dict[str, Any]) -> UserPreferences:
    """Обновить предпочтения пользователя"""
    # Получаем текущие предпочтения
    try:
        current_pref = get_preferences_by_user(user_id)
    except PreferencesNotFoundError:
        # Если предпочтений нет - создаем новые
        new_pref = UserPreferences(
            user_id=user_id,  # исправлено: строчные буквы
            age_min=updates.get('AgeMin'),
            age_max=updates.get('AgeMax'),
            preferred_genders=updates.get('PreferredGenders'),
            preferred_distance=updates.get('PreferredDistance'),
            other_preferences=updates.get('OtherPreferences')
        )
        return create_preferences(user_id, new_pref)
    
    # Валидация обновлений
    if 'AgeMin' in updates and 'AgeMax' in updates:
        if updates['AgeMin'] > updates['AgeMax']:
            raise PreferencesValidationError(
                "Minimum age cannot be greater than maximum age"
            )
    elif 'AgeMin' in updates:
        if updates['AgeMin'] > current_pref.age_max:  # исправлено: строчные буквы
            raise PreferencesValidationError(
                "Minimum age cannot be greater than current maximum age"
            )
    elif 'AgeMax' in updates:
        if updates['AgeMax'] < current_pref.age_min:  # исправлено: строчные буквы
            raise PreferencesValidationError(
                "Maximum age cannot be less than current minimum age"
            )
    
    if 'PreferredDistance' in updates and updates['PreferredDistance'] < 0:
        raise PreferencesValidationError(
            "Preferred distance cannot be negative"
        )
    
    # Применяем обновления
    update_data = {
        'age_min': updates.get('AgeMin'),
        'age_max': updates.get('AgeMax'),
        'preferred_genders': updates.get('PreferredGenders'),
        'preferred_distance': updates.get('PreferredDistance'),
        'other_preferences': updates.get('OtherPreferences')
    }
    
    # Удаляем None значения
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    if update_data:
        user_preferences_repository.update_preference(current_pref.id, update_data)  # исправлено: строчные буквы
    
    return get_preferences_by_user(user_id)


def delete_preferences(user_id: int) -> Dict[str, str]:
    """Удалить предпочтения пользователя"""
    try:
        pref = get_preferences_by_user(user_id)
        user_preferences_repository.delete_preference(pref.ID)
        return {"message": f"Preferences for user {user_id} deleted successfully"}
    except PreferencesNotFoundError:
        return {"message": f"No preferences found for user {user_id}"}


def find_compatible_users(user_id: int, max_distance: int = 50) -> List[Dict[str, Any]]:
    """
    Найти совместимых пользователей на основе предпочтений
    Возвращает список словарей с информацией о совместимости
    """
    try:
        user_pref = get_preferences_by_user(user_id)
    except PreferencesNotFoundError:
        raise PreferencesValidationError(
            "User preferences must be set to find compatible matches"
        )
    
    # Получаем профиль пользователя для определения его характеристик
    # (предполагаем, что есть соответствующий сервис)
    from src.services import profile_services
    try:
        profile = profile_services.get_profile_by_user(user_id)
    except Exception:
        raise PreferencesValidationError(
            "User profile must be completed to find compatible matches"
        )
    
    # Формируем параметры для поиска
    search_params = {
        'age': profile.Age,
        'gender': profile.Gender,
        'distance': max_distance
    }
    
    if user_pref.OtherPreferences and 'interests' in user_pref.OtherPreferences:
        search_params['interests'] = user_pref.OtherPreferences['interests']
    
    # Ищем пользователей с подходящими предпочтениями
    compatible_users = user_preferences_repository.get_users_by_preferences(**search_params)
    
    # Фильтруем тех, кто уже был лайкнут или в матчах
    from src.services import user_likes_services, matches_services
    liked_users = {like.ToUserID for like in user_likes_services.get_user_likes(user_id)}
    matches = matches_services.get_user_matches(user_id)
    matched_users = {match.user1_id if match.user2_id == user_id else match.user2_id for match in matches}
    
    result = []
    for user in compatible_users:
        if user['id'] in liked_users or user['id'] in matched_users:
            continue
        
        # Рассчитываем процент совпадения интересов
        common = get_common_preferences(user_id, user['id'])
        result.append({
            'user_id': user['id'],
            'match_percentage': common['interest_match_percent'],
            'common_interests': common['common_interests'],
            'profile_data': {
                'age': user.get('age'),
                'gender': user.get('gender'),
                'location': user.get('location')
            }
        })
    
    # Сортируем по проценту совпадения
    return sorted(result, key=lambda x: x['match_percentage'], reverse=True)


def get_common_preferences(user_id1: int, user_id2: int) -> Dict[str, Any]:
    """Получить общие предпочтения между двумя пользователями"""
    pref1 = get_preferences_by_user(user_id1)
    pref2 = get_preferences_by_user(user_id2)
    
    common_interests = []
    if pref1.OtherPreferences and pref2.OtherPreferences:
        interests1 = pref1.OtherPreferences.get('interests', [])
        interests2 = pref2.OtherPreferences.get('interests', [])
        common_interests = list(set(interests1) & set(interests2))
    
    total_interests = max(
        len(pref1.OtherPreferences.get('interests', [])) if pref1.OtherPreferences else 0,
        len(pref2.OtherPreferences.get('interests', [])) if pref2.OtherPreferences else 0,
        1  # Чтобы избежать деления на 0
    )
    
    return {
        'common_interests': common_interests,
        'interest_match_percent': round(len(common_interests) * 100 / total_interests)
    }


def _convert_db_preferences(pref_data: Dict[str, Any]) -> UserPreferences:
    """Конвертировать данные из БД в Pydantic модель"""
    return UserPreferences(
        ID=pref_data['id'],
        UserID=pref_data['user_id'],
        AgeMin=pref_data['age_min'],
        AgeMax=pref_data['age_max'],
        PreferredGenders=json.loads(pref_data['preferred_genders']) if pref_data['preferred_genders'] else None,
        PreferredDistance=pref_data['preferred_distance'],
        OtherPreferences=json.loads(pref_data['other_preferences']) if pref_data['other_preferences'] else None,
        CreatedAt=pref_data['created_at'],
        UpdatedAt=pref_data['updated_at']
    )