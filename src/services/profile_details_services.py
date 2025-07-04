from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import HTTPException, status
from src.repository import profile_details_repository
from src.database.models import ProfileDetails
from src.utils.custom_logging import get_logger

log = get_logger(__name__)


class ProfileNotFoundError(HTTPException):
    def __init__(self, profile_id: int = None, user_id: int = None):
        detail = f'Profile {f"with ID {profile_id}" if profile_id else f"for user {user_id}"} not found'
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class ProfileValidationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


def get_all_profiles() -> List[ProfileDetails]:
    """Получить все профили пользователей"""
    profiles_data = profile_details_repository.get_all_profiles()
    return [_convert_db_profile(profile) for profile in profiles_data]


def get_profile_by_id(profile_id: int) -> ProfileDetails:
    """Получить профиль по ID"""
    profile_data = profile_details_repository.get_profile_by_id(profile_id)
    if not profile_data:
        raise ProfileNotFoundError(profile_id=profile_id)
    return _convert_db_profile(profile_data)


def get_profile_by_user_id(user_id: int) -> ProfileDetails:
    """Получить профиль по ID пользователя"""
    profile_data = profile_details_repository.get_profile_by_user_id(user_id)
    if not profile_data:
        raise ProfileNotFoundError(user_id=user_id)
    return _convert_db_profile(profile_data)


def create_profile(user_id: int, profile_data: Dict[str, Any]) -> ProfileDetails:
    """Создать новый профиль пользователя"""
    # Проверяем, не существует ли уже профиль для этого пользователя
    try:
        existing = get_profile_by_user_id(user_id)
        raise ProfileValidationError(f"Profile already exists for user {user_id} (ID: {existing.id})")
    except ProfileNotFoundError:
        pass
    
    # Валидация данных
    age = profile_data.get('age')
    if age is not None and not (18 <= age <= 120):
        raise ProfileValidationError("Age must be between 18 and 120")
    
    # Создаем объект ProfileDetails
    profile = ProfileDetails(
        user_id=user_id,
        age=profile_data.get('age'),
        gender=profile_data.get('gender'),
        interests=profile_data.get('interests'),
        bio=profile_data.get('bio'),
        profile_photo_url=profile_data.get('profile_photo_url'),
        location=profile_data.get('location'),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    profile_id = profile_details_repository.create_profile(profile)
    return get_profile_by_id(profile_id)


def update_profile(profile_id: int, updates: Dict[str, Any]) -> ProfileDetails:
    """Обновить профиль пользователя по ID профиля"""
    existing = get_profile_by_id(profile_id)
    
    # Валидация обновлений
    if 'Age' in updates and updates['Age'] is not None:
        if not (18 <= updates['Age'] <= 120):
            raise ProfileValidationError("Age must be between 18 and 120")
    
    update_data = {
        'age': updates.get('Age'),
        'gender': updates.get('Gender'),
        'interests': updates.get('Interests'),
        'bio': updates.get('Bio'),
        'profile_photo_url': updates.get('ProfilePhotoUrl'),
        'location': updates.get('Location')
    }
    
    # Удаляем None значения
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    if update_data:
        profile_details_repository.update_profile(profile_id, update_data)
    
    return get_profile_by_id(profile_id)


def update_user_profile(user_id: int, updates: Dict[str, Any]) -> ProfileDetails:
    """Обновить профиль по ID пользователя"""
    try:
        profile = get_profile_by_user_id(user_id)
        return update_profile(profile.ID, updates)
    except ProfileNotFoundError:
        # Если профиля нет - создаем новый
        return create_profile(user_id, updates)


def delete_profile(profile_id: int) -> Dict[str, str]:
    """Удалить профиль по ID"""
    get_profile_by_id(profile_id)  # Проверяем существование
    profile_details_repository.delete_profile(profile_id)
    return {"message": f"Profile {profile_id} deleted successfully"}


def delete_user_profile(user_id: int) -> Dict[str, str]:
    """Удалить профиль по ID пользователя"""
    profile = get_profile_by_user_id(user_id)
    return delete_profile(profile.ID)


def get_profiles_by_age_range(min_age: int, max_age: int) -> List[ProfileDetails]:
    """Получить профили в заданном возрастном диапазоне"""
    if min_age < 18 or max_age > 120:
        raise ProfileValidationError("Age range must be between 18 and 120")
    
    profiles_data = profile_details_repository.get_profiles_by_age_range(min_age, max_age)
    return [_convert_db_profile(profile) for profile in profiles_data]


def get_profiles_by_gender(gender: str) -> List[ProfileDetails]:
    """Получить профили по полу"""
    profiles_data = profile_details_repository.get_profiles_by_gender(gender)
    return [_convert_db_profile(profile) for profile in profiles_data]


def get_profiles_by_location(location: str) -> List[ProfileDetails]:
    """Получить профили по местоположению"""
    profiles_data = profile_details_repository.get_profiles_by_location(location)
    return [_convert_db_profile(profile) for profile in profiles_data]


def search_profiles_by_interests(interests: List[str]) -> List[ProfileDetails]:
    """Поиск профилей по интересам"""
    profiles_data = profile_details_repository.search_profiles_by_interests(interests)
    return [_convert_db_profile(profile) for profile in profiles_data]


def get_profiles_with_photo() -> List[ProfileDetails]:
    """Получить профили с фотографиями"""
    profiles_data = profile_details_repository.get_profiles_with_photo()
    return [_convert_db_profile(profile) for profile in profiles_data]


def get_incomplete_profiles() -> List[ProfileDetails]:
    """Получить неполные профили (без важных данных)"""
    profiles_data = profile_details_repository.get_incomplete_profiles()
    return [_convert_db_profile(profile) for profile in profiles_data]


def get_profile_completion_stats() -> Dict[str, Any]:
    """Получить статистику заполнения профилей"""
    return profile_details_repository.get_profile_completion_stats()


def get_profile_recommendations(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Получить рекомендации профилей для пользователя"""
    try:
        user_profile = get_profile_by_user_id(user_id)
        from src.services import user_preferences_services
        preferences = user_preferences_services.get_preferences_by_user(user_id)
        
        # Формируем параметры поиска на основе предпочтений
        search_params = {
            'min_age': preferences.AgeMin or 18,
            'max_age': preferences.AgeMax or 100,
            'gender': preferences.PreferredGenders[0] if preferences.PreferredGenders else None,
            'interests': user_profile.Interests.split(', ') if user_profile.Interests else []
        }
        
        # Исключаем текущего пользователя
        exclude_user = user_id
        
        return profile_details_repository.find_compatible_profiles(
            **search_params,
            exclude_user=exclude_user,
            limit=limit
        )
    except Exception as e:
        log.error(f"Error generating profile recommendations: {str(e)}")
        return []


def _convert_db_profile(profile_data: Dict[str, Any]) -> ProfileDetails:
    """Конвертировать данные из БД в Pydantic модель"""
    return ProfileDetails(
        id=profile_data.get('id'),
        user_id=profile_data.get('user_id'),
        age=profile_data.get('age'),
        gender=profile_data.get('gender'),
        interests=profile_data.get('interests'),
        bio=profile_data.get('bio'),
        profile_photo_url=profile_data.get('profile_photo_url'),
        location=profile_data.get('location'),
        created_at=profile_data.get('created_at'),
        updated_at=profile_data.get('updated_at')
    )