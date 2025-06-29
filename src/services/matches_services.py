from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import HTTPException, status
from src.repository import matches_repository
from src.database.models import Matches, MatchStatusEnum
from src.utils.custom_logging import get_logger

log = get_logger(__name__)


class MatchNotFoundError(HTTPException):
    def __init__(self, match_id: int = None, user_ids: tuple = None):
        detail = f'Match {f"with ID {match_id}" if match_id else f"between users {user_ids}"} not found'
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class MatchValidationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


def get_all_matches() -> List[Matches]:
    """Получить все совпадения (матчи)"""
    matches_data = matches_repository.get_all_matches()
    return [_convert_db_match(match) for match in matches_data]


def get_match_by_id(match_id: int) -> Matches:
    """Получить матч по ID"""
    match_data = matches_repository.get_match_by_id(match_id)
    if not match_data:
        raise MatchNotFoundError(match_id=match_id)
    return _convert_db_match(match_data)


def check_match_exists(user1_id: int, user2_id: int) -> Optional[Matches]:
    """Проверить существование матча между двумя пользователями"""
    match_data = matches_repository.check_match_exists(user1_id, user2_id)
    return _convert_db_match(match_data) if match_data else None


def create_match(user1_id: int, user2_id: int) -> Matches:
    """Создать новый матч между пользователями"""
    if user1_id == user2_id:
        raise MatchValidationError("Users cannot match with themselves")
    
    # Проверяем, существует ли уже матч между этими пользователями
    existing = check_match_exists(user1_id, user2_id)
    if existing:
        if existing.MatchStatus != MatchStatusEnum.ACTIVE:
            return update_match_status(existing.ID, MatchStatusEnum.ACTIVE)
        raise MatchValidationError(f"Match already exists between users {user1_id} and {user2_id}")
    
    match = Matches(
        User1ID=user1_id,
        User2ID=user2_id,
        MatchStatus=MatchStatusEnum.ACTIVE,
        CreatedAt=datetime.now(),
        UpdatedAt=datetime.now()
    )
    
    match_id = matches_repository.create_match(match)
    return get_match_by_id(match_id)


def update_match(match_id: int, updates: Dict[str, Any]) -> Matches:
    """Обновить данные матча"""
    existing = get_match_by_id(match_id)
    
    # Валидация обновлений
    if 'MatchStatus' in updates:
        if updates['MatchStatus'] not in MatchStatusEnum.__members__.values():
            raise MatchValidationError(f"Invalid status. Must be one of: {list(MatchStatusEnum.__members__.values())}")
    
    update_data = {
        'match_status': updates.get('MatchStatus')
    }
    
    # Удаляем None значения
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    if update_data:
        matches_repository.update_match(match_id, update_data)
    
    return get_match_by_id(match_id)


def update_match_status(match_id: int, status: MatchStatusEnum) -> Matches:
    """Обновить статус матча"""
    return update_match(match_id, {'MatchStatus': status})


def delete_match(match_id: int) -> Dict[str, str]:
    """Удалить матч по ID"""
    get_match_by_id(match_id)  # Проверяем существование
    matches_repository.delete_match(match_id)
    return {"message": f"Match {match_id} deleted successfully"}


def get_user_matches(user_id: int, status: MatchStatusEnum = None) -> List[Dict[str, Any]]:
    """Получить все матчи пользователя с возможностью фильтрации по статусу"""
    return matches_repository.get_user_matches(user_id, status)


def get_active_matches(user_id: int) -> List[Dict[str, Any]]:
    """Получить активные матчи пользователя"""
    return get_user_matches(user_id, MatchStatusEnum.ACTIVE)


def get_paused_matches(user_id: int) -> List[Dict[str, Any]]:
    """Получить приостановленные матчи пользователя"""
    return get_user_matches(user_id, MatchStatusEnum.PAUSED)


def get_ended_matches(user_id: int) -> List[Dict[str, Any]]:
    """Получить завершенные матчи пользователя"""
    return get_user_matches(user_id, MatchStatusEnum.ENDED)


def create_match_from_likes(from_user_id: int, to_user_id: int) -> Optional[Matches]:
    """
    Создать матч между пользователями, если есть взаимные лайки.
    Возвращает объект матча или None, если нет взаимных лайков.
    """
    from src.services import user_likes_services
    
    if not user_likes_services.check_mutual_like(from_user_id, to_user_id):
        return None
    
    try:
        return create_match(from_user_id, to_user_id)
    except MatchValidationError as e:
        log.warning(f"Match creation skipped: {str(e)}")
        return check_match_exists(from_user_id, to_user_id)


def get_recent_matches(hours: int = 24) -> List[Dict[str, Any]]:
    """Получить недавние матчи за указанное количество часов"""
    return matches_repository.get_recent_matches(hours)


def get_matches_with_conversations() -> List[Dict[str, Any]]:
    """Получить матчи, которые имеют активные беседы"""
    return matches_repository.get_matches_with_conversations()


def get_matches_without_conversations() -> List[Dict[str, Any]]:
    """Получить матчи, которые не имеют активных бесед"""
    return matches_repository.get_matches_without_conversations()


def get_matches_count() -> Dict[str, int]:
    """Получить статистику по количеству матчей в разных статусах"""
    return matches_repository.get_matches_count()


def get_user_match_stats(user_id: int) -> Dict[str, Any]:
    """Получить статистику матчей для конкретного пользователя"""
    return matches_repository.get_user_match_stats(user_id)


def end_inactive_matches(days_inactive: int = 30) -> Dict[str, Any]:
    """
    Автоматически завершает неактивные матчи (без сообщений в течение N дней)
    Возвращает статистику по завершенным матчам
    """
    inactive_matches = matches_repository.find_inactive_matches(days_inactive)
    ended_count = 0
    
    for match in inactive_matches:
        try:
            update_match_status(match['id'], MatchStatusEnum.ENDED)
            ended_count += 1
        except Exception as e:
            log.error(f"Failed to end match {match['id']}: {str(e)}")
    
    return {
        "total_checked": len(inactive_matches),
        "ended_matches": ended_count
    }


def _convert_db_match(match_data: Dict[str, Any]) -> Matches:
    """Конвертировать данные из БД в Pydantic модель"""
    return Matches(
        ID=match_data['id'],
        User1ID=match_data['user1_id'],
        User2ID=match_data['user2_id'],
        MatchStatus=match_data['match_status'],
        CreatedAt=match_data['created_at'],
        UpdatedAt=match_data['updated_at']
    )