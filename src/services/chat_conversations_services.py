from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import HTTPException, status
from src.repository import chat_conversations_repository
from src.database.models import ChatConversations
from src.utils.custom_logging import get_logger

log = get_logger(__name__)


class ConversationNotFoundError(HTTPException):
    def __init__(self, conversation_id: int = None, match_id: int = None):
        detail = f'Conversation {f"with ID {conversation_id}" if conversation_id else f"for match {match_id}"} not found'
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class ConversationValidationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


def get_all_conversations() -> List[ChatConversations]:
    """Получить все беседы"""
    conversations_data = chat_conversations_repository.get_all_conversations()
    return [_convert_db_conversation(conv) for conv in conversations_data]


def get_conversation_by_id(conversation_id: int) -> ChatConversations:
    """Получить беседу по ID"""
    conversation_data = chat_conversations_repository.get_conversation_by_id(conversation_id)
    if not conversation_data:
        raise ConversationNotFoundError(conversation_id=conversation_id)
    return _convert_db_conversation(conversation_data)


def get_conversation_by_match_id(match_id: int) -> ChatConversations:
    """Получить беседу по ID матча"""
    conversation_data = chat_conversations_repository.get_conversation_by_match_id(match_id)
    if not conversation_data:
        raise ConversationNotFoundError(match_id=match_id)
    return _convert_db_conversation(conversation_data)


def create_conversation(match_id: int) -> ChatConversations:
    """Создать новую беседу для матча"""
    # Проверяем, не существует ли уже беседа для этого матча
    try:
        existing = get_conversation_by_match_id(match_id)
        raise ConversationValidationError(f"Conversation already exists for match {match_id} (ID: {existing.ID})")
    except ConversationNotFoundError:
        pass
    
    conversation = ChatConversations(
        MatchID=match_id,
        LastMessageAt=datetime.now(),
        CreatedAt=datetime.now()
    )
    
    conversation_id = chat_conversations_repository.create_conversation(conversation)
    return get_conversation_by_id(conversation_id)


def update_conversation(conversation_id: int, updates: Dict[str, Any]) -> ChatConversations:
    """Обновить беседу"""
    existing = get_conversation_by_id(conversation_id)
    
    update_data = {
        'last_message_at': updates.get('LastMessageAt')
    }
    
    # Удаляем None значения
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    if not update_data:
        raise ConversationValidationError("No valid fields to update")
    
    chat_conversations_repository.update_conversation(conversation_id, update_data)
    return get_conversation_by_id(conversation_id)


def update_last_message_time(conversation_id: int) -> ChatConversations:
    """Обновить время последнего сообщения в беседе (прямо сейчас)"""
    return update_conversation(conversation_id, {'LastMessageAt': datetime.now()})


def delete_conversation(conversation_id: int) -> Dict[str, str]:
    """Удалить беседу по ID"""
    get_conversation_by_id(conversation_id)  # Проверяем существование
    chat_conversations_repository.delete_conversation(conversation_id)
    return {"message": f"Conversation {conversation_id} deleted successfully"}


def get_user_conversations(user_id: int) -> List[Dict[str, Any]]:
    """Получить все беседы пользователя с дополнительной информацией"""
    return chat_conversations_repository.get_user_conversations(user_id)


def get_active_conversations() -> List[Dict[str, Any]]:
    """Получить все активные беседы (в которых есть сообщения)"""
    return chat_conversations_repository.get_active_conversations()


def get_empty_conversations() -> List[Dict[str, Any]]:
    """Получить все пустые беседы (без сообщений)"""
    return chat_conversations_repository.get_empty_conversations()


def get_conversations_with_recent_activity(hours: int = 24) -> List[Dict[str, Any]]:
    """Получить беседы с активностью за последние часы"""
    return chat_conversations_repository.get_conversations_with_recent_activity(hours)


def get_conversation_with_messages(conversation_id: int, limit: int = 50) -> Dict[str, Any]:
    """Получить беседу вместе с ее сообщениями"""
    conversation = get_conversation_by_id(conversation_id)
    from src.services import chat_messages_services
    messages = chat_messages_services.get_messages_by_conversation(conversation_id, limit)
    
    return {
        **conversation.dict(),
        "messages": [msg.dict() for msg in messages]
    }


def get_conversation_statistics() -> Dict[str, Any]:
    """Получить статистику по беседам"""
    return chat_conversations_repository.get_conversation_statistics()


def get_or_create_conversation(match_id: int) -> ChatConversations:
    """Получить или создать беседу для матча"""
    try:
        return get_conversation_by_match_id(match_id)
    except ConversationNotFoundError:
        return create_conversation(match_id)


def get_conversation_between_users(user1_id: int, user2_id: int) -> Optional[ChatConversations]:
    """Получить беседу между двумя пользователями (если существует)"""
    from src.services import matches_services
    
    try:
        match = matches_services.check_match_exists(user1_id, user2_id)
        if not match:
            return None
        return get_conversation_by_match_id(match.ID)
    except Exception:
        return None


def _convert_db_conversation(conversation_data: Dict[str, Any]) -> ChatConversations:
    """Конвертировать данные из БД в Pydantic модель"""
    return ChatConversations(
        ID=conversation_data['id'],
        MatchID=conversation_data['match_id'],
        LastMessageAt=conversation_data['last_message_at'],
        CreatedAt=conversation_data['created_at']
    )