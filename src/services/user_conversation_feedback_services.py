from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import HTTPException, status
from src.repository import user_conversation_feedback_repository
from src.database.models import UserConversationFeedback
from src.utils.custom_logging import get_logger

log = get_logger(__name__)


class FeedbackNotFoundError(HTTPException):
    def __init__(self, feedback_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Feedback with ID {feedback_id} not found'
        )


class FeedbackValidationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


class DuplicateFeedbackError(HTTPException):
    def __init__(self, user_id: int, conversation_id: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'User {user_id} already left feedback for conversation {conversation_id}'
        )


def get_all_feedback() -> List[UserConversationFeedback]:
    """Получить все записи обратной связи о беседах"""
    feedback_data = user_conversation_feedback_repository.get_all_feedback()
    return [_convert_db_feedback(fb) for fb in feedback_data]


def get_feedback_by_id(feedback_id: int) -> UserConversationFeedback:
    """Получить запись обратной связи по ID"""
    feedback_data = user_conversation_feedback_repository.get_feedback_by_id(feedback_id)
    if not feedback_data:
        raise FeedbackNotFoundError(feedback_id)
    return _convert_db_feedback(feedback_data)


def get_feedback_by_user_conversation(user_id: int, conversation_id: int) -> Optional[UserConversationFeedback]:
    """Получить обратную связь конкретного пользователя о конкретной беседе"""
    feedback_data = user_conversation_feedback_repository.get_feedback_by_user_conversation(user_id, conversation_id)
    return _convert_db_feedback(feedback_data) if feedback_data else None


def create_feedback(feedback: UserConversationFeedback) -> UserConversationFeedback:
    """Создать новую запись обратной связи"""
    # Проверка валидности оценки
    if feedback.Rating is not None and (feedback.Rating < 1 or feedback.Rating > 5):
        raise FeedbackValidationError("Rating must be between 1 and 5")
    
    # Проверка существования отзыва
    existing = get_feedback_by_user_conversation(feedback.UserID, feedback.ConversationID)
    if existing:
        raise DuplicateFeedbackError(feedback.UserID, feedback.ConversationID)
    
    feedback_id = user_conversation_feedback_repository.create_feedback(feedback)
    return get_feedback_by_id(feedback_id)


def update_feedback(feedback_id: int, updates: Dict[str, Any]) -> UserConversationFeedback:
    """Обновить запись обратной связи"""
    existing = get_feedback_by_id(feedback_id)
    
    # Валидация обновлений
    if 'Rating' in updates and updates['Rating'] is not None:
        if updates['Rating'] < 1 or updates['Rating'] > 5:
            raise FeedbackValidationError("Rating must be between 1 and 5")
    
    update_data = {
        'rating': updates.get('Rating'),
        'feedback_text': updates.get('FeedbackText')
    }
    
    # Удаляем None значения
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    if update_data:
        user_conversation_feedback_repository.update_feedback(feedback_id, update_data)
    
    return get_feedback_by_id(feedback_id)


def delete_feedback(feedback_id: int) -> Dict[str, str]:
    """Удалить запись обратной связи"""
    get_feedback_by_id(feedback_id)  # Проверяем существование
    user_conversation_feedback_repository.delete_feedback(feedback_id)
    return {"message": f"Feedback {feedback_id} deleted successfully"}


def get_conversation_feedback(conversation_id: int) -> List[UserConversationFeedback]:
    """Получить все отзывы о конкретной беседе"""
    feedback_data = user_conversation_feedback_repository.get_conversation_feedback(conversation_id)
    return [_convert_db_feedback(fb) for fb in feedback_data]


def get_user_feedback(user_id: int) -> List[UserConversationFeedback]:
    """Получить все отзывы, оставленные пользователем"""
    feedback_data = user_conversation_feedback_repository.get_user_feedback(user_id)
    return [_convert_db_feedback(fb) for fb in feedback_data]


def get_average_conversation_rating(conversation_id: int) -> float:
    """Получить среднюю оценку беседы"""
    return user_conversation_feedback_repository.get_average_conversation_rating(conversation_id)


def get_user_average_rating(user_id: int) -> float:
    """Получить среднюю оценку бесед пользователя"""
    return user_conversation_feedback_repository.get_user_average_rating(user_id)


def get_conversations_with_highest_ratings(limit: int = 10) -> List[Dict[str, Any]]:
    """Получить беседы с самыми высокими оценками"""
    return user_conversation_feedback_repository.get_conversations_with_highest_ratings(limit)


def get_feedback_statistics() -> Dict[str, Any]:
    """Получить статистику по обратной связи"""
    return user_conversation_feedback_repository.get_feedback_statistics()


def upsert_feedback(user_id: int, conversation_id: int, rating: int, feedback_text: str) -> UserConversationFeedback:
    """
    Создать или обновить отзыв о беседе.
    Если отзыв уже существует - обновит его, иначе создаст новый.
    """
    existing = get_feedback_by_user_conversation(user_id, conversation_id)
    
    if existing:
        return update_feedback(existing.ID, {
            'Rating': rating,
            'FeedbackText': feedback_text
        })
    else:
        new_feedback = UserConversationFeedback(
            UserID=user_id,
            ConversationID=conversation_id,
            Rating=rating,
            FeedbackText=feedback_text,
            CreatedAt=datetime.now()
        )
        return create_feedback(new_feedback)


def _convert_db_feedback(feedback_data: Dict[str, Any]) -> UserConversationFeedback:
    """Конвертировать данные из БД в Pydantic модель"""
    return UserConversationFeedback(
        ID=feedback_data['id'],
        UserID=feedback_data['user_id'],
        ConversationID=feedback_data['conversation_id'],
        Rating=feedback_data['rating'],
        FeedbackText=feedback_data['feedback_text'],
        CreatedAt=feedback_data['created_at']
    )