from typing import Optional, Dict, Any, List
from datetime import datetime
from src.repository import user_repository
from src.database.models import Users
from fastapi import HTTPException, status
from src.utils.exam_services import check_if_exists
from src.utils.custom_logging import get_logger

log = get_logger(__name__)


class UserNotFoundError(HTTPException):
    def __init__(self, user_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User {user_id} not found'
        )


def get_all_users() -> List[Users]:
    """Получить всех пользователей"""
    users_data = user_repository.get_all_users()
    return [Users(**user) for user in users_data]


def get_user_by_id(user_id: int) -> Users:
    """Получить пользователя по ID"""
    user_data = user_repository.get_user_by_id(user_id)
    if not user_data:
        raise UserNotFoundError(user_id)
    return Users(**user_data)


def get_user_by_email(email: str) -> Optional[Users]:
    """Получить пользователя по email"""
    user_data = user_repository.get_user_by_email(email)
    return Users(**user_data) if user_data else None


def create_user(email: str, password: str, first_name: str) -> Users:
    """Создать нового пользователя"""
    if user_repository.get_user_by_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User with this email already exists'
        )

    user = Users(
        Email=email,
        Password=password,
        FirstName=first_name,
        LastActivity=datetime.now(),
        CreatedAt=datetime.now()
    )

    user_id = user_repository.create_user(user)
    return get_user_by_id(user_id)


def update_user(user_id: int, updates: Dict[str, Any]) -> Users:
    """Обновить данные пользователя"""
    existing_user = get_user_by_id(user_id)
    
    # Подготовка данных для обновления
    update_data = {}
    if 'email' in updates and updates['email'] is not None:
        update_data['email'] = updates['email']
    if 'password' in updates and updates['password'] is not None:
        update_data['password'] = updates['password']
    if 'first_name' in updates and updates['first_name'] is not None:
        update_data['first_name'] = updates['first_name']
    if 'last_activity' in updates and updates['last_activity'] is not None:
        update_data['last_activity'] = updates['last_activity']

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields to update"
        )

    user_repository.update_user(user_id, update_data)
    return get_user_by_id(user_id)


def update_user_activity(user_id: int) -> Users:
    """Обновить время последней активности пользователя"""
    user_repository.update_user_activity(user_id, datetime.now())
    return get_user_by_id(user_id)


def delete_user(user_id: int) -> Dict[str, str]:
    """Удалить пользователя"""
    get_user_by_id(user_id)
    user_repository.delete_user(user_id)
    return {"message": "User deleted successfully"}


def authenticate_user(email: str, password: str) -> Optional[Users]:
    """Аутентификация пользователя"""
    user_data = user_repository.get_user_by_email(email)
    if not user_data:
        return None
    
    user = Users(**user_data)
    if user.Password != password:  # На практике должно быть сравнение хэшей
        return None
    return user


def get_users_by_activity_period(start_date: datetime, end_date: datetime) -> List[Users]:
    """Получить пользователей по периоду активности"""
    users_data = user_repository.get_users_by_activity_period(start_date, end_date)
    return [Users(**user) for user in users_data]


def get_active_users_count() -> int:
    """Получить количество активных пользователей"""
    return user_repository.get_active_users_count()