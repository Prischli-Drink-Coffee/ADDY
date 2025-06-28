from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import HTTPException, status
from src.repository import chat_messages_repository
from src.database.models import ChatMessages, MessageTypeEnum
from src.utils.custom_logging import get_logger

log = get_logger(__name__)


class MessageNotFoundError(HTTPException):
    def __init__(self, message_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Message with ID {message_id} not found'
        )


class MessageValidationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


def get_all_messages() -> List[ChatMessages]:
    """Получить все сообщения"""
    messages_data = chat_messages_repository.get_all_messages()
    return [_convert_db_message(msg) for msg in messages_data]


def get_message_by_id(message_id: int) -> ChatMessages:
    """Получить сообщение по ID"""
    message_data = chat_messages_repository.get_message_by_id(message_id)
    if not message_data:
        raise MessageNotFoundError(message_id)
    return _convert_db_message(message_data)


def get_messages_by_conversation(
    conversation_id: int, 
    limit: int = 50, 
    offset: int = 0
) -> List[ChatMessages]:
    """Получить сообщения из конкретной беседы с пагинацией"""
    messages_data = chat_messages_repository.get_messages_by_conversation(
        conversation_id, limit, offset
    )
    return [_convert_db_message(msg) for msg in messages_data]


def create_message(
    conversation_id: int,
    sender_id: int,
    message_text: str,
    message_type: MessageTypeEnum = MessageTypeEnum.USER
) -> ChatMessages:
    """Создать новое сообщение"""
    if not message_text or len(message_text.strip()) == 0:
        raise MessageValidationError("Message text cannot be empty")
    
    if len(message_text) > 2000:
        raise MessageValidationError("Message is too long (max 2000 characters)")
    
    message = ChatMessages(
        ConversationID=conversation_id,
        SenderID=sender_id,
        MessageText=message_text,
        IsRead=False,
        MessageType=message_type,
        CreatedAt=datetime.now()
    )
    
    message_id = chat_messages_repository.create_message(message)
    return get_message_by_id(message_id)


def update_message(message_id: int, updates: Dict[str, Any]) -> ChatMessages:
    """Обновить сообщение"""
    existing = get_message_by_id(message_id)
    
    update_data = {}
    
    if 'MessageText' in updates:
        if not updates['MessageText'] or len(updates['MessageText'].strip()) == 0:
            raise MessageValidationError("Message text cannot be empty")
        if len(updates['MessageText']) > 2000:
            raise MessageValidationError("Message is too long (max 2000 characters)")
        update_data['message_text'] = updates['MessageText']
    
    if 'IsRead' in updates:
        update_data['is_read'] = updates['IsRead']
    
    if 'MessageType' in updates:
        if updates['MessageType'] not in MessageTypeEnum.__members__.values():
            raise MessageValidationError(
                f"Invalid message type. Must be one of: {list(MessageTypeEnum.__members__.values())}"
            )
        update_data['message_type'] = updates['MessageType']
    
    if not update_data:
        raise MessageValidationError("No valid fields to update")
    
    chat_messages_repository.update_message(message_id, update_data)
    return get_message_by_id(message_id)


def delete_message(message_id: int) -> Dict[str, str]:
    """Удалить сообщение по ID"""
    get_message_by_id(message_id)  # Проверяем существование
    chat_messages_repository.delete_message(message_id)
    return {"message": f"Message {message_id} deleted successfully"}


def mark_messages_as_read(conversation_id: int, user_id: int) -> Dict[str, int]:
    """
    Отметить все непрочитанные сообщения в беседе как прочитанные
    для указанного пользователя (исключая его собственные сообщения)
    """
    updated_count = chat_messages_repository.mark_messages_as_read(conversation_id, user_id)
    return {"updated_count": updated_count}


def count_unread_messages(user_id: int) -> Dict[str, Any]:
    """
    Подсчитать непрочитанные сообщения для пользователя 
    по всем беседам и для каждой беседы
    """
    return chat_messages_repository.count_unread_messages(user_id)


def get_agent_simulation_messages(conversation_id: int) -> List[ChatMessages]:
    """Получить сообщения агентов в конкретной беседе"""
    messages_data = chat_messages_repository.get_agent_simulation_messages(conversation_id)
    return [_convert_db_message(msg) for msg in messages_data]


def get_user_messages(user_id: int, limit: int = 50, offset: int = 0) -> List[ChatMessages]:
    """Получить все сообщения, отправленные пользователем"""
    messages_data = chat_messages_repository.get_user_messages(user_id, limit, offset)
    return [_convert_db_message(msg) for msg in messages_data]


def get_conversation_statistics(conversation_id: int) -> Dict[str, Any]:
    """Получить статистику сообщений для беседы"""
    return chat_messages_repository.get_conversation_statistics(conversation_id)


def get_recent_messages(hours: int = 24) -> List[ChatMessages]:
    """Получить сообщения за последние часы"""
    messages_data = chat_messages_repository.get_recent_messages(hours)
    return [_convert_db_message(msg) for msg in messages_data]


def search_messages(search_term: str, conversation_id: int = None) -> List[ChatMessages]:
    """Поиск сообщений по тексту"""
    if not search_term or len(search_term.strip()) < 3:
        raise MessageValidationError("Search term must be at least 3 characters long")
    
    messages_data = chat_messages_repository.search_messages(search_term, conversation_id)
    return [_convert_db_message(msg) for msg in messages_data]


def get_last_message_in_conversation(conversation_id: int) -> Optional[ChatMessages]:
    """Получить последнее сообщение в беседе"""
    message_data = chat_messages_repository.get_last_message_in_conversation(conversation_id)
    return _convert_db_message(message_data) if message_data else None


def _convert_db_message(message_data: Dict[str, Any]) -> ChatMessages:
    """Конвертировать данные из БД в Pydantic модель"""
    return ChatMessages(
        ID=message_data['id'],
        ConversationID=message_data['conversation_id'],
        SenderID=message_data['sender_id'],
        MessageText=message_data['message_text'],
        IsRead=message_data['is_read'],
        MessageType=message_data['message_type'],
        CreatedAt=message_data['created_at']
    )