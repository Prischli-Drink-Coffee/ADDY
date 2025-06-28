from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from src.repository import user_sessions_repository
from src.database.models import UserSessions
from src.utils.custom_logging import get_logger

log = get_logger(__name__)


class SessionNotFoundError(HTTPException):
    def __init__(self, session_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Session {session_id} not found'
        )


class SessionValidationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


def get_all_sessions() -> List[UserSessions]:
    """Получить все сессии"""
    sessions_data = user_sessions_repository.get_all_sessions()
    return [UserSessions(**session) for session in sessions_data]


def get_session_by_id(session_id: int) -> UserSessions:
    """Получить сессию по ID"""
    session_data = user_sessions_repository.get_session_by_id(session_id)
    if not session_data:
        raise SessionNotFoundError(session_id)
    return UserSessions(**session_data)


def get_session_by_token_hash(token_hash: str) -> Optional[UserSessions]:
    """Получить сессию по хэшу токена"""
    session_data = user_sessions_repository.get_session_by_token_hash(token_hash)
    return UserSessions(**session_data) if session_data else None


def get_active_sessions_by_user(user_id: int) -> List[UserSessions]:
    """Получить активные сессии пользователя"""
    sessions_data = user_sessions_repository.get_active_sessions_by_user(user_id)
    return [UserSessions(**session) for session in sessions_data]


def get_sessions_by_user(user_id: int) -> List[UserSessions]:
    """Получить все сессии пользователя"""
    sessions_data = user_sessions_repository.get_sessions_by_user(user_id)
    return [UserSessions(**session) for session in sessions_data]


def create_session(
    user_id: int,
    fingerprint_hash: str,
    jwt_token_hash: str,
    expires_at: datetime,
    ip_address: Optional[str] = None
) -> UserSessions:
    """Создать новую сессию"""
    if user_sessions_repository.get_session_by_token_hash(jwt_token_hash):
        raise SessionValidationError('Session with this token hash already exists')

    session = UserSessions(
        UserID=user_id,
        FingerprintHash=fingerprint_hash,
        JwtTokenHash=jwt_token_hash,
        ExpiresAt=expires_at,
        IPAddress=ip_address,
        IsActive=True,
        CreatedAt=datetime.now()
    )

    session_id = user_sessions_repository.create_session(session)
    return get_session_by_id(session_id)


def update_session(session_id: int, updates: Dict[str, Any]) -> UserSessions:
    """Обновить данные сессии"""
    existing_session = get_session_by_id(session_id)
    
    # Подготовка данных для обновления
    update_data = {}
    if 'jwt_token_hash' in updates and updates['jwt_token_hash'] is not None:
        update_data['jwt_token_hash'] = updates['jwt_token_hash']
    if 'fingerprint_hash' in updates and updates['fingerprint_hash'] is not None:
        update_data['fingerprint_hash'] = updates['fingerprint_hash']
    if 'expires_at' in updates and updates['expires_at'] is not None:
        update_data['expires_at'] = updates['expires_at']
    if 'ip_address' in updates and updates['ip_address'] is not None:
        update_data['ip_address'] = updates['ip_address']
    if 'is_active' in updates and updates['is_active'] is not None:
        update_data['is_active'] = updates['is_active']

    if not update_data:
        raise SessionValidationError("No valid fields to update")

    user_sessions_repository.update_session(session_id, update_data)
    return get_session_by_id(session_id)


def deactivate_session(session_id: int) -> UserSessions:
    """Деактивировать сессию"""
    return update_session(session_id, {"is_active": False})


def deactivate_user_sessions(user_id: int) -> Dict[str, int]:
    """Деактивировать все сессии пользователя"""
    user_sessions_repository.deactivate_user_sessions(user_id)
    active_sessions = user_sessions_repository.count_active_sessions_by_user(user_id)
    return {"remaining_active_sessions": active_sessions}


def delete_session(session_id: int) -> Dict[str, str]:
    """Удалить сессию"""
    get_session_by_id(session_id)
    user_sessions_repository.delete_session(session_id)
    return {"message": "Session deleted successfully"}


def cleanup_expired_sessions() -> Dict[str, int]:
    """Очистить истекшие сессии"""
    deleted_count = user_sessions_repository.delete_expired_sessions()
    return {"deleted_count": deleted_count}


def validate_session(token_hash: str) -> bool:
    """Проверить валидность сессии"""
    session_data = user_sessions_repository.get_session_by_token_hash(token_hash)
    if not session_data:
        return False
    
    session = UserSessions(**session_data)
    return session.IsActive and session.ExpiresAt > datetime.now()


def extend_session(session_id: int, days: int = 30) -> UserSessions:
    """Продлить срок действия сессии"""
    new_expires_at = datetime.now() + timedelta(days=days)
    return update_session(session_id, {"expires_at": new_expires_at})


def get_sessions_by_ip(ip_address: str) -> List[UserSessions]:
    """Получить сессии по IP-адресу"""
    sessions_data = user_sessions_repository.get_sessions_by_ip(ip_address)
    return [UserSessions(**session) for session in sessions_data]