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
    ID: Optional[int] = Field(None, 
                             alias="id")
    AgentID: StrictInt = Field(..., 
                              alias="agent_id", 
                              examples=[1])
    DataType: DataTypeEnum = Field(..., 
                                  alias="data_type", 
                                  examples=["message_history"])
    DataContent: Dict[str, Any] = Field(..., 
                                     alias="data_content", 
                                     examples=[{"messages": [{"text": "Привет!", "timestamp": "2025-06-27T22:15:30"}]}])
    CreatedAt: Optional[datetime] = Field(None, 
                                        alias="created_at", 
                                        examples=[f"{datetime.now()}"])


class AgentSimulations(BaseModel):
    """
    Модель симуляций общения между агентами
    """
    ID: Optional[int] = Field(None, 
                             alias="id")
    ConversationID: StrictInt = Field(..., 
                                     alias="conversation_id", 
                                     examples=[1])
    Agent1ID: StrictInt = Field(..., 
                               alias="agent1_id", 
                               examples=[1])
    Agent2ID: StrictInt = Field(..., 
                               alias="agent2_id", 
                               examples=[2])
    SimulationStatus: SimulationStatusEnum = Field(default=SimulationStatusEnum.PENDING, 
                                                 alias="simulation_status", 
                                                 examples=["pending"])
    CompatibilityScore: Optional[Decimal] = Field(None, 
                                                alias="compatibility_score", 
                                                examples=[0.85])
    SimulationSummary: Optional[StrictStr] = Field(None, 
                                                 alias="simulation_summary", 
                                                 examples=["Агенты показали высокую совместимость. Взаимный интерес к теме путешествий."])
    StartedAt: Optional[datetime] = Field(None, 
                                        alias="started_at", 
                                        examples=[f"{datetime.now()}"])
    CompletedAt: Optional[datetime] = Field(None, 
                                          alias="completed_at", 
                                          examples=[f"{datetime.now()}"])
    CreatedAt: Optional[datetime] = Field(None, 
                                        alias="created_at", 
                                        examples=[f"{datetime.now()}"])


class AgentSimulationMessages(BaseModel):
    """
    Модель сообщений в симуляции общения агентов
    """
    ID: Optional[int] = Field(None, 
                             alias="id")
    SimulationID: StrictInt = Field(..., 
                                   alias="simulation_id", 
                                   examples=[1])
    SenderAgentID: StrictInt = Field(..., 
                                    alias="sender_agent_id", 
                                    examples=[1])
    MessageText: StrictStr = Field(..., 
                                  alias="message_text", 
                                  examples=["Привет! Я заметил, что тебе тоже нравится туризм. Какие места ты уже посетил?"])
    SentimentScore: Optional[Decimal] = Field(None, 
                                            alias="sentiment_score", 
                                            examples=[0.75])
    CreatedAt: Optional[datetime] = Field(None, 
                                        alias="created_at", 
                                        examples=[f"{datetime.now()}"])


class UserPreferences(BaseModel):
    """
    Модель предпочтений пользователей для поиска
    """
    ID: Optional[int] = Field(None, 
                             alias="id")
    UserID: StrictInt = Field(..., 
                             alias="user_id", 
                             examples=[1])
    AgeMin: Optional[StrictInt] = Field(None, 
                                      alias="age_min", 
                                      examples=[20])
    AgeMax: Optional[StrictInt] = Field(None, 
                                      alias="age_max", 
                                      examples=[35])
    PreferredGenders: Optional[List[str]] = Field(None, 
                                               alias="preferred_genders", 
                                               examples=[["женский"]])
    PreferredDistance: Optional[StrictInt] = Field(None, 
                                                 alias="preferred_distance", 
                                                 examples=[50])
    OtherPreferences: Optional[Dict[str, Any]] = Field(None, 
                                                    alias="other_preferences", 
                                                    examples=[{"interests": ["музыка", "путешествия"], "non_smokers": True}])
    CreatedAt: Optional[datetime] = Field(None, 
                                        alias="created_at", 
                                        examples=[f"{datetime.now()}"])
    UpdatedAt: Optional[datetime] = Field(None, 
                                        alias="updated_at", 
                                        examples=[f"{datetime.now()}"])


class UserConversationFeedback(BaseModel):
    """
    Модель обратной связи по реальным беседам
    """
    ID: Optional[int] = Field(None, 
                             alias="id")
    UserID: StrictInt = Field(..., 
                             alias="user_id", 
                             examples=[1])
    ConversationID: StrictInt = Field(..., 
                                     alias="conversation_id", 
                                     examples=[1])
    Rating: Optional[StrictInt] = Field(None, 
                                      alias="rating", 
                                      examples=[4])
    FeedbackText: Optional[StrictStr] = Field(None, 
                                            alias="feedback_text", 
                                            examples=["Приятное общение, много общих интересов"])
    CreatedAt: Optional[datetime] = Field(None, 
                                        alias="created_at", 
                                        examples=[f"{datetime.now()}"])


class AgentSimulationFeedback(BaseModel):
    """
    Модель обратной связи по симуляции агентов
    """
    ID: Optional[int] = Field(None, 
                             alias="id")
    SimulationID: StrictInt = Field(..., 
                                   alias="simulation_id", 
                                   examples=[1])
    UserID: StrictInt = Field(..., 
                             alias="user_id", 
                             examples=[1])
    AccuracyRating: Optional[StrictInt] = Field(None, 
                                              alias="accuracy_rating", 
                                              examples=[5])
    UsefulnessRating: Optional[StrictInt] = Field(None, 
                                                alias="usefulness_rating", 
                                                examples=[4])
    FeedbackText: Optional[StrictStr] = Field(None, 
                                            alias="feedback_text", 
                                            examples=["Агент отлично воспроизвел мой стиль общения"])
    CreatedAt: Optional[datetime] = Field(None, 
                                        alias="created_at", 
                                        examples=[f"{datetime.now()}"])