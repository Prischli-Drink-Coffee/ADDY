from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import HTTPException, status
from src.repository import user_likes_repository
from src.database.models import UserLikes
from src.utils.custom_logging import get_logger

log = get_logger(__name__)


class LikeNotFoundError(HTTPException):
    def __init__(self, like_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Like with ID {like_id} not found'
        )


class LikeAlreadyExistsError(HTTPException):
    def __init__(self, from_user_id: int, to_user_id: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Like from user {from_user_id} to user {to_user_id} already exists'
        )


class LikeValidationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


def get_all_likes() -> List[UserLikes]:
    """Получить все лайки между пользователями"""
    likes_data = user_likes_repository.get_all_likes()
    return [_convert_db_like(like) for like in likes_data]


def get_like_by_id(like_id: int) -> UserLikes:
    """Получить лайк по ID"""
    like_data = user_likes_repository.get_like_by_id(like_id)
    if not like_data:
        raise LikeNotFoundError(like_id)
    return _convert_db_like(like_data)


def check_like_exists(from_user_id: int, to_user_id: int) -> bool:
    """Проверить, существует ли лайк от одного пользователя к другому"""
    return user_likes_repository.check_like_exists(from_user_id, to_user_id)


def create_like(from_user_id: int, to_user_id: int) -> UserLikes:
    """Создать новый лайк"""
    if from_user_id == to_user_id:
        raise LikeValidationError("User cannot like themselves")
    
    if check_like_exists(from_user_id, to_user_id):
        raise LikeAlreadyExistsError(from_user_id, to_user_id)
    
    like = UserLikes(
        FromUserID=from_user_id,
        ToUserID=to_user_id,
        CreatedAt=datetime.now()
    )
    
    like_id = user_likes_repository.create_like(like)
    return get_like_by_id(like_id)


def delete_like(like_id: int) -> Dict[str, str]:
    """Удалить лайк по ID"""
    get_like_by_id(like_id)  # Проверяем существование
    user_likes_repository.delete_like(like_id)
    return {"message": f"Like {like_id} deleted successfully"}


def delete_user_like(from_user_id: int, to_user_id: int) -> Dict[str, str]:
    """Удалить лайк от одного пользователя к другому"""
    if not check_like_exists(from_user_id, to_user_id):
        raise LikeNotFoundError(0)
    
    user_likes_repository.delete_user_like(from_user_id, to_user_id)
    return {"message": f"Like from user {from_user_id} to user {to_user_id} deleted successfully"}


def get_likes_from_user(user_id: int) -> List[UserLikes]:
    """Получить все лайки, поставленные пользователем"""
    likes_data = user_likes_repository.get_likes_from_user(user_id)
    return [_convert_db_like(like) for like in likes_data]


def get_likes_to_user(user_id: int) -> List[UserLikes]:
    """Получить все лайки, полученные пользователем"""
    likes_data = user_likes_repository.get_likes_to_user(user_id)
    return [_convert_db_like(like) for like in likes_data]


def check_mutual_like(user1_id: int, user2_id: int) -> bool:
    """Проверить наличие взаимных лайков между двумя пользователями"""
    return user_likes_repository.check_mutual_like(user1_id, user2_id)


def get_mutual_likes(user_id: int) -> List[Dict[str, Any]]:
    """Получить список пользователей с взаимными лайками"""
    return user_likes_repository.get_mutual_likes(user_id)


def get_potential_matches(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Получить список потенциальных совпадений для пользователя 
    (те, кто поставил лайк пользователю, но он им ещё нет)
    """
    return user_likes_repository.get_potential_matches(user_id, limit)


def count_likes_from_user(user_id: int) -> int:
    """Подсчитать количество лайков, поставленных пользователем"""
    return user_likes_repository.count_likes_from_user(user_id)


def count_likes_to_user(user_id: int) -> int:
    """Подсчитать количество лайков, полученных пользователем"""
    return user_likes_repository.count_likes_to_user(user_id)


def get_recent_likes(hours: int = 24) -> List[UserLikes]:
    """Получить список недавних лайков за указанное количество часов"""
    likes_data = user_likes_repository.get_recent_likes(hours)
    return [_convert_db_like(like) for like in likes_data]


def check_and_create_match(from_user_id: int, to_user_id: int) -> Optional[Dict[str, Any]]:
    """
    Проверить взаимные лайки и создать матч при наличии
    Возвращает информацию о созданном матче или None
    """
    if check_mutual_like(from_user_id, to_user_id):
        from src.services import matches_services
        try:
            match = matches_services.create_match(from_user_id, to_user_id)
            return match
        except Exception as e:
            log.error(f"Error creating match: {str(e)}")
            return None
    return None


def get_user_likes_stats(user_id: int) -> Dict[str, Any]:
    """Получить статистику лайков пользователя"""
    return {
        "likes_sent": count_likes_from_user(user_id),
        "likes_received": count_likes_to_user(user_id),
        "mutual_likes": len(get_mutual_likes(user_id)),
        "potential_matches": len(get_potential_matches(user_id))
    }


def _convert_db_like(like_data: Dict[str, Any]) -> UserLikes:
    """Конвертировать данные из БД в Pydantic модель"""
    return UserLikes(
        id=like_data['id'],
        from_user_id=like_data['from_user_id'],
        to_user_id=like_data['to_user_id'],
        created_at=like_data['created_at']
    )