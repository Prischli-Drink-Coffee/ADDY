from pydantic import BaseModel, Field, StrictStr, StrictInt, StrictBool, StrictFloat
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal


class MatchStatusEnum(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"


class MessageTypeEnum(str, Enum):
    USER = "user"
    AGENT_SIMULATION = "agent_simulation"


class LearningStatusEnum(str, Enum):
    LEARNING = "learning"
    READY = "ready"
    UPDATING = "updating"


class SimulationStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class DataTypeEnum(str, Enum):
    MESSAGE_HISTORY = "message_history"
    PROFILE_INTERACTION = "profile_interaction"
    PREFERENCES = "preferences"


class Users(BaseModel):
    """
    Модель пользователей приложения знакомств
    """
    id: Optional[int] = Field(None, 
                             examples=[1])
    email: StrictStr = Field(..., 
                            examples=["user@example.com"])
    password: StrictStr = Field(..., 
                               examples=["hashed_password_string"])
    first_name: StrictStr = Field(..., 
                                 examples=["Александр"])
    last_activity: datetime = Field(..., 
                                   examples=[f"{datetime.now()}"])
    created_at: Optional[datetime] = Field(None, 
                                         examples=[f"{datetime.now()}"])


class UserSessions(BaseModel):
    """
    Модель сессий пользователей
    """
    id: Optional[int] = Field(None, 
                             examples=[1])
    user_id: StrictInt = Field(..., 
                              examples=[1])
    fingerprint_hash: StrictStr = Field(..., 
                                       examples=["a1b2c3d4e5f6789012345678901234567890abcdef"])
    jwt_token_hash: StrictStr = Field(..., 
                                     examples=["a1b2c3d4e5f6789012345678901234567890abcdef"])
    expires_at: datetime = Field(..., 
                                examples=[f"{datetime.now()}"])
    ip_address: Optional[StrictStr] = Field(None, 
                                           examples=["192.168.1.1"])
    is_active: StrictInt = Field(default=1, 
                                examples=[1])
    created_at: Optional[datetime] = Field(None, 
                                         examples=[f"{datetime.now()}"])


class ProfileDetails(BaseModel):
    """
    Модель деталей профиля пользователя
    """
    id: Optional[int] = Field(None, 
                             examples=[1])
    user_id: StrictInt = Field(..., 
                              examples=[1])
    age: Optional[StrictInt] = Field(None, 
                                   examples=[25])
    gender: Optional[StrictStr] = Field(None, 
                                      examples=["мужской"])
    interests: Optional[StrictStr] = Field(None, 
                                         examples=["музыка, спорт, путешествия"])
    bio: Optional[StrictStr] = Field(None, 
                                   examples=["Увлекаюсь горными походами и фотографией"])
    profile_photo_url: Optional[StrictStr] = Field(None, 
                                                 examples=["https://example.com/photos/user1.jpg"])
    location: Optional[StrictStr] = Field(None, 
                                        examples=["Москва"])
    created_at: Optional[datetime] = Field(None, 
                                         examples=[f"{datetime.now()}"])
    updated_at: Optional[datetime] = Field(None, 
                                         examples=[f"{datetime.now()}"])


class UserLikes(BaseModel):
    """
    Модель лайков между пользователями
    """
    id: Optional[int] = Field(None, 
                             examples=[1])
    from_user_id: StrictInt = Field(..., 
                                   examples=[1])
    to_user_id: StrictInt = Field(..., 
                                 examples=[2])
    created_at: Optional[datetime] = Field(None, 
                                         examples=[f"{datetime.now()}"])


class Matches(BaseModel):
    """
    Модель совпадений (взаимных лайков) между пользователями
    """
    id: Optional[int] = Field(None, 
                             examples=[1])
    user1_id: StrictInt = Field(..., 
                               examples=[1])
    user2_id: StrictInt = Field(..., 
                               examples=[2])
    match_status: MatchStatusEnum = Field(default=MatchStatusEnum.ACTIVE, 
                                        examples=["active"])
    created_at: Optional[datetime] = Field(None, 
                                         examples=[f"{datetime.now()}"])
    updated_at: Optional[datetime] = Field(None, 
                                         examples=[f"{datetime.now()}"])


class ChatConversations(BaseModel):
    """
    Модель чат-диалогов
    """
    id: Optional[int] = Field(None, 
                             examples=[1])
    match_id: StrictInt = Field(..., 
                               examples=[1])
    last_message_at: Optional[datetime] = Field(None, 
                                               examples=[f"{datetime.now()}"])
    created_at: Optional[datetime] = Field(None, 
                                         examples=[f"{datetime.now()}"])


class ChatMessages(BaseModel):
    """
    Модель сообщений в чате
    """
    id: Optional[int] = Field(None, 
                             examples=[1])
    conversation_id: StrictInt = Field(..., 
                                      examples=[1])
    sender_id: StrictInt = Field(..., 
                                examples=[1])
    message_text: StrictStr = Field(..., 
                                   examples=["Привет! Как дела?"])
    is_read: StrictBool = Field(default=False, 
                               examples=[False])
    message_type: MessageTypeEnum = Field(default=MessageTypeEnum.USER, 
                                         examples=["user"])
    created_at: Optional[datetime] = Field(None, 
                                         examples=[f"{datetime.now()}"])


class UserAgents(BaseModel):
    """
    Модель агентов пользователей
    """
    id: Optional[int] = Field(None, 
                             examples=[1])
    user_id: StrictInt = Field(..., 
                              examples=[1])
    personality_data: Dict[str, Any] = Field(..., 
                                           examples=[{"communication_style": "friendly", "response_patterns": ["often asks questions", "uses emojis"]}])
    learning_status: LearningStatusEnum = Field(default=LearningStatusEnum.LEARNING, 
                                              examples=["learning"])
    last_updated_at: datetime = Field(..., 
                                     examples=[f"{datetime.now()}"])
    created_at: Optional[datetime] = Field(None, 
                                          examples=[f"{datetime.now()}"])


class AgentLearningData(BaseModel):
    """
    Модель данных для обучения агентов
    """
    id: Optional[int] = Field(None, 
                             examples=[1])
    agent_id: StrictInt = Field(..., 
                               examples=[1])
    data_type: DataTypeEnum = Field(..., 
                                   examples=["message_history"])
    data_content: Dict[str, Any] = Field(..., 
                                        examples=[{"messages": [{"text": "Привет!", "timestamp": "2025-06-27T22:15:30"}]}])
    created_at: Optional[datetime] = Field(None, 
                                         examples=[f"{datetime.now()}"])


class AgentSimulations(BaseModel):
    """
    Модель симуляций общения между агентами
    """
    id: Optional[int] = Field(None, 
                             examples=[1])
    conversation_id: StrictInt = Field(..., 
                                      examples=[1])
    agent1_id: StrictInt = Field(..., 
                                examples=[1])
    agent2_id: StrictInt = Field(..., 
                                examples=[2])
    simulation_status: SimulationStatusEnum = Field(default=SimulationStatusEnum.PENDING, 
                                                   examples=["pending"])
    compatibility_score: Optional[Decimal] = Field(None, 
                                                  examples=[0.85])
    simulation_summary: Optional[StrictStr] = Field(None, 
                                                   examples=["Агенты показали высокую совместимость. Взаимный интерес к теме путешествий."])
    started_at: Optional[datetime] = Field(None, 
                                         examples=[f"{datetime.now()}"])
    completed_at: Optional[datetime] = Field(None, 
                                           examples=[f"{datetime.now()}"])
    created_at: Optional[datetime] = Field(None, 
                                         examples=[f"{datetime.now()}"])


class AgentSimulationMessages(BaseModel):
    """
    Модель сообщений в симуляции общения агентов
    """
    id: Optional[int] = Field(None, 
                             examples=[1])
    simulation_id: StrictInt = Field(..., 
                                    examples=[1])
    sender_agent_id: StrictInt = Field(..., 
                                      examples=[1])
    message_text: StrictStr = Field(..., 
                                   examples=["Привет! Я заметил, что тебе тоже нравится туризм. Какие места ты уже посетил?"])
    sentiment_score: Optional[Decimal] = Field(None, 
                                              examples=[0.75])
    created_at: Optional[datetime] = Field(None, 
                                         examples=[f"{datetime.now()}"])


class UserPreferences(BaseModel):
    """
    Модель предпочтений пользователей для поиска
    """
    id: Optional[int] = Field(None, 
                             examples=[1])
    user_id: StrictInt = Field(..., 
                              examples=[1])
    age_min: Optional[StrictInt] = Field(None, 
                                        examples=[20])
    age_max: Optional[StrictInt] = Field(None, 
                                        examples=[35])
    preferred_genders: Optional[List[str]] = Field(None, 
                                                  examples=[["женский"]])
    preferred_distance: Optional[StrictInt] = Field(None, 
                                                   examples=[50])
    other_preferences: Optional[Dict[str, Any]] = Field(None, 
                                                       examples=[{"interests": ["музыка", "путешествия"], "non_smokers": True}])
    created_at: Optional[datetime] = Field(None, 
                                         examples=[f"{datetime.now()}"])
    updated_at: Optional[datetime] = Field(None, 
                                         examples=[f"{datetime.now()}"])


class UserConversationFeedback(BaseModel):
    """
    Модель обратной связи по реальным беседам
    """
    id: Optional[int] = Field(None, 
                             examples=[1])
    user_id: StrictInt = Field(..., 
                              examples=[1])
    conversation_id: StrictInt = Field(..., 
                                      examples=[1])
    rating: Optional[StrictInt] = Field(None, 
                                       examples=[4])
    feedback_text: Optional[StrictStr] = Field(None, 
                                              examples=["Приятное общение, много общих интересов"])
    created_at: Optional[datetime] = Field(None, 
                                         examples=[f"{datetime.now()}"])


class AgentSimulationFeedback(BaseModel):
    """
    Модель обратной связи по симуляции агентов
    """
    id: Optional[int] = Field(None, 
                             examples=[1])
    simulation_id: StrictInt = Field(..., 
                                    examples=[1])
    user_id: StrictInt = Field(..., 
                              examples=[1])
    accuracy_rating: Optional[StrictInt] = Field(None, 
                                                examples=[5])
    usefulness_rating: Optional[StrictInt] = Field(None, 
                                                  examples=[4])
    feedback_text: Optional[StrictStr] = Field(None, 
                                              examples=["Агент отлично воспроизвел мой стиль общения"])
    created_at: Optional[datetime] = Field(None, 
                                         examples=[f"{datetime.now()}"])