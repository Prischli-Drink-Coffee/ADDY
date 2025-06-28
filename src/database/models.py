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
    ID: Optional[int] = Field(None, 
                             alias="id")
    Email: StrictStr = Field(..., 
                            alias="email", 
                            examples=["user@example.com"])
    Password: StrictStr = Field(..., 
                               alias="password", 
                               examples=["hashed_password_string"])
    FirstName: StrictStr = Field(..., 
                                alias="first_name", 
                                examples=["Александр"])
    LastActivity: datetime = Field(..., 
                                  alias="last_activity", 
                                  examples=[f"{datetime.now()}"])
    CreatedAt: Optional[datetime] = Field(None, 
                                        alias="created_at", 
                                        examples=[f"{datetime.now()}"])


class UserSessions(BaseModel):
    """
    Модель сессий пользователей
    """
    ID: Optional[int] = Field(None, 
                             alias="id")
    UserID: StrictInt = Field(..., 
                             alias="user_id", 
                             examples=[1])
    FingerprintHash: StrictStr = Field(..., 
                                      alias="fingerprint_hash", 
                                      examples=["a1b2c3d4e5f6789012345678901234567890abcdef"])
    JwtTokenHash: StrictStr = Field(..., 
                                   alias="jwt_token_hash", 
                                   examples=["a1b2c3d4e5f6789012345678901234567890abcdef"])
    ExpiresAt: datetime = Field(..., 
                               alias="expires_at", 
                               examples=[f"{datetime.now()}"])
    IPAddress: Optional[StrictStr] = Field(None, 
                                          alias="ip_address", 
                                          examples=["192.168.1.1"])
    IsActive: StrictBool = Field(default=True, 
                                alias="is_active", 
                                examples=[True])
    CreatedAt: Optional[datetime] = Field(None, 
                                        alias="created_at", 
                                        examples=[f"{datetime.now()}"])


class ProfileDetails(BaseModel):
    """
    Модель деталей профиля пользователя
    """
    ID: Optional[int] = Field(None, 
                             alias="id")
    UserID: StrictInt = Field(..., 
                             alias="user_id", 
                             examples=[1])
    Age: Optional[StrictInt] = Field(None, 
                                    alias="age", 
                                    examples=[25])
    Gender: Optional[StrictStr] = Field(None, 
                                       alias="gender", 
                                       examples=["мужской"])
    Interests: Optional[StrictStr] = Field(None, 
                                         alias="interests", 
                                         examples=["музыка, спорт, путешествия"])
    Bio: Optional[StrictStr] = Field(None, 
                                    alias="bio", 
                                    examples=["Увлекаюсь горными походами и фотографией"])
    ProfilePhotoUrl: Optional[StrictStr] = Field(None, 
                                               alias="profile_photo_url", 
                                               examples=["https://example.com/photos/user1.jpg"])
    Location: Optional[StrictStr] = Field(None, 
                                         alias="location", 
                                         examples=["Москва"])
    CreatedAt: Optional[datetime] = Field(None, 
                                        alias="created_at", 
                                        examples=[f"{datetime.now()}"])
    UpdatedAt: Optional[datetime] = Field(None, 
                                        alias="updated_at", 
                                        examples=[f"{datetime.now()}"])


class UserLikes(BaseModel):
    """
    Модель лайков между пользователями
    """
    ID: Optional[int] = Field(None, 
                             alias="id")
    FromUserID: StrictInt = Field(..., 
                                 alias="from_user_id", 
                                 examples=[1])
    ToUserID: StrictInt = Field(..., 
                               alias="to_user_id", 
                               examples=[2])
    CreatedAt: Optional[datetime] = Field(None, 
                                        alias="created_at", 
                                        examples=[f"{datetime.now()}"])


class Matches(BaseModel):
    """
    Модель совпадений (взаимных лайков) между пользователями
    """
    ID: Optional[int] = Field(None, 
                             alias="id")
    User1ID: StrictInt = Field(..., 
                              alias="user1_id", 
                              examples=[1])
    User2ID: StrictInt = Field(..., 
                              alias="user2_id", 
                              examples=[2])
    MatchStatus: MatchStatusEnum = Field(default=MatchStatusEnum.ACTIVE, 
                                       alias="match_status", 
                                       examples=["active"])
    CreatedAt: Optional[datetime] = Field(None, 
                                        alias="created_at", 
                                        examples=[f"{datetime.now()}"])
    UpdatedAt: Optional[datetime] = Field(None, 
                                        alias="updated_at", 
                                        examples=[f"{datetime.now()}"])


class ChatConversations(BaseModel):
    """
    Модель чат-диалогов
    """
    ID: Optional[int] = Field(None, 
                             alias="id")
    MatchID: StrictInt = Field(..., 
                              alias="match_id", 
                              examples=[1])
    LastMessageAt: Optional[datetime] = Field(None, 
                                            alias="last_message_at", 
                                            examples=[f"{datetime.now()}"])
    CreatedAt: Optional[datetime] = Field(None, 
                                        alias="created_at", 
                                        examples=[f"{datetime.now()}"])


class ChatMessages(BaseModel):
    """
    Модель сообщений в чате
    """
    ID: Optional[int] = Field(None, 
                             alias="id")
    ConversationID: StrictInt = Field(..., 
                                     alias="conversation_id", 
                                     examples=[1])
    SenderID: StrictInt = Field(..., 
                               alias="sender_id", 
                               examples=[1])
    MessageText: StrictStr = Field(..., 
                                  alias="message_text", 
                                  examples=["Привет! Как дела?"])
    IsRead: StrictBool = Field(default=False, 
                              alias="is_read", 
                              examples=[False])
    MessageType: MessageTypeEnum = Field(default=MessageTypeEnum.USER, 
                                       alias="message_type", 
                                       examples=["user"])
    CreatedAt: Optional[datetime] = Field(None, 
                                        alias="created_at", 
                                        examples=[f"{datetime.now()}"])


class UserAgents(BaseModel):
    """
    Модель агентов пользователей
    """
    ID: Optional[int] = Field(None, 
                             alias="id")
    UserID: StrictInt = Field(..., 
                             alias="user_id", 
                             examples=[1])
    PersonalityData: Dict[str, Any] = Field(..., 
                                         alias="personality_data", 
                                         examples=[{"communication_style": "friendly", "response_patterns": ["often asks questions", "uses emojis"]}])
    LearningStatus: LearningStatusEnum = Field(default=LearningStatusEnum.LEARNING, 
                                             alias="learning_status", 
                                             examples=["learning"])
    LastUpdatedAt: datetime = Field(..., 
                                   alias="last_updated_at", 
                                   examples=[f"{datetime.now()}"])
    CreatedAt: Optional[datetime] = Field(None, 
                                        alias="created_at", 
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