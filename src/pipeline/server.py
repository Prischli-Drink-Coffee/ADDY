import os
import asyncio
import json
from fastapi import (FastAPI, HTTPException, Depends, Request, File, UploadFile,
                     status, Form, Query, Response, Body)
from typing import Dict, List, Any, Optional
from fastapi.openapi.models import Tag as OpenApiTag
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse, FileResponse
from src.utils.custom_logging import get_logger
from src.utils.env import Env
from datetime import datetime
from src.services.cookie_services import session_manager
import asyncio
from contextlib import asynccontextmanager

from src.database.models import (
    Users,
    UserSessions,
    MatchStatusEnum,
    MessageTypeEnum,
    LearningStatusEnum,
    SimulationStatusEnum,
    DataTypeEnum,
    ProfileDetails,
    UserLikes,
    UserAgents,
    UserPreferences,
    UserConversationFeedback,
    Matches,
    ChatConversations,
    ChatMessages,
    AgentLearningData,
    AgentSimulations,
    AgentSimulationMessages,
    AgentSimulationFeedback
)
from src.services import (
    cookie_services,
    user_services,
    user_sessions_services,
    agent_learning_data_services,
    agent_simulation_feedback_services,
    agent_simulation_messages_services,
    agents_simulations_services,
    user_agents_services,
    user_preferences_services,
    user_likes_services,
    user_conversation_feedback_services,
    chat_conversations_services,
    chat_messages_services,
    matches_services,
    profile_details_services
)

env = Env()
log = get_logger(__name__)

app = FastAPI()

app_server = FastAPI(title="DatingApp Server API",
                     version="1.0.0",
                     description="Dating application with AI agent simulations")

app.mount("/server", app_server)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define API tags
ServerCookieTag = OpenApiTag(name="Cookie", description="Session management operations")
ServerUserTag = OpenApiTag(name="User", description="User management operations")
ServerSessionTag = OpenApiTag(name="Session", description="User session operations")
ServerProfileTag = OpenApiTag(name="Profile", description="User profile operations")
ServerMatchTag = OpenApiTag(name="Match", description="Match operations")
ServerChatTag = OpenApiTag(name="Chat", description="Chat operations")
ServerAgentTag = OpenApiTag(name="Agent", description="AI agent operations")
ServerSimulationTag = OpenApiTag(name="Simulation", description="Agent simulation operations")
ServerFeedbackTag = OpenApiTag(name="Feedback", description="Feedback operations")
ServerPreferenceTag = OpenApiTag(name="Preference", description="User preference operations")

app_server.openapi_tags = [
    ServerCookieTag.model_dump(),
    ServerUserTag.model_dump(),
    ServerSessionTag.model_dump(),
    ServerProfileTag.model_dump(),
    ServerMatchTag.model_dump(),
    ServerChatTag.model_dump(),
    ServerAgentTag.model_dump(),
    ServerSimulationTag.model_dump(),
    ServerFeedbackTag.model_dump(),
    ServerPreferenceTag.model_dump(),
]


# ------------------------------------------
# Agent Learning Data Endpoints
# ------------------------------------------


@app_server.post("/agent-learning-data/", 
                 response_model=AgentLearningData, 
                 tags=["Agent Learning Data"],
                 status_code=status.HTTP_201_CREATED)
async def create_new_learning_data(learning_data: Dict[str, Any] = Body(...)):
    """Create new agent learning data entry"""
    return agent_learning_data_services.create_learning_data(learning_data)

@app_server.get("/agent-learning-data/", 
                response_model=List[AgentLearningData], 
                tags=["Agent Learning Data"])
async def get_all_learning_data():
    """Get all agent learning data entries"""
    return agent_learning_data_services.get_all_learning_data()

@app_server.get("/agent-learning-data/{data_id}", 
                response_model=AgentLearningData, 
                tags=["Agent Learning Data"])
async def get_learning_data_by_id(data_id: int):
    """Get specific learning data by its ID"""
    return agent_learning_data_services.get_learning_data_by_id(data_id)

@app_server.get("/agents/{agent_id}/learning-data", 
                response_model=List[AgentLearningData], 
                tags=["Agent Learning Data"])
async def get_learning_data_for_agent(agent_id: int):
    """Get all learning data for a specific agent"""
    return agent_learning_data_services.get_learning_data_by_agent(agent_id)

@app_server.get("/agent-learning-data/type/{data_type}", 
                response_model=List[AgentLearningData], 
                tags=["Agent Learning Data"])
async def get_learning_data_by_type(data_type: str):
    """Get learning data of specific type"""
    return agent_learning_data_services.get_learning_data_by_type(data_type)

@app_server.put("/agent-learning-data/{data_id}", 
                response_model=AgentLearningData, 
                tags=["Agent Learning Data"])
async def update_existing_learning_data(data_id: int, updates: Dict[str, Any] = Body(...)):
    """Update existing learning data entry"""
    return agent_learning_data_services.update_learning_data(data_id, updates)

@app_server.patch("/agent-learning-data/{data_id}/mark-processed", 
                  response_model=AgentLearningData, 
                  tags=["Agent Learning Data"])
async def mark_data_as_processed(data_id: int, processed_metadata: Dict[str, Any] = Body(None)):
    """Mark learning data as processed and update metadata"""
    return agent_learning_data_services.mark_as_processed(data_id, processed_metadata)

@app_server.delete("/agent-learning-data/{data_id}", 
                   status_code=status.HTTP_204_NO_CONTENT,
                   tags=["Agent Learning Data"])
async def delete_learning_data_entry(data_id: int):
    """Delete a learning data entry"""
    agent_learning_data_services.delete_learning_data(data_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app_server.delete("/agents/{agent_id}/learning-data", 
                   response_model=Dict[str, str],
                   tags=["Agent Learning Data"])
async def delete_all_agent_learning_data(agent_id: int):
    """Delete all learning data for a specific agent"""
    return agent_learning_data_services.delete_agent_learning_data(agent_id)

@app_server.get("/agent-learning-data/unprocessed", 
                response_model=List[AgentLearningData], 
                tags=["Agent Learning Data"])
async def get_unprocessed_learning_data():
    """Get all unprocessed learning data"""
    return agent_learning_data_services.get_unprocessed_learning_data()

@app_server.get("/agent-learning-data/source/{source}", 
                response_model=List[AgentLearningData], 
                tags=["Agent Learning Data"])
async def get_learning_data_from_source(source: str):
    """Get learning data from specific source"""
    return agent_learning_data_services.get_learning_data_from_source(source)

@app_server.get("/agent-learning-data/recent", 
                response_model=List[AgentLearningData], 
                tags=["Agent Learning Data"])
async def get_recent_learning_data(hours: int = Query(24, gt=0)):
    """Get recent learning data entries within specified hours"""
    return agent_learning_data_services.get_recent_learning_data(hours)

@app_server.get("/agent-learning-data/metadata", 
                response_model=List[AgentLearningData], 
                tags=["Agent Learning Data"])
async def get_learning_data_by_metadata(
    key: str = Query(..., description="Metadata key to search for"),
    value: Optional[str] = Query(None, description="Optional value to filter by")
):
    """Get learning data containing specific metadata key"""
    return agent_learning_data_services.get_learning_data_by_metadata_key(key, value)

@app_server.get("/agents/{agent_id}/learning-data/stats", 
                response_model=Dict[str, Any], 
                tags=["Agent Learning Data"])
async def get_agent_learning_stats(agent_id: int):
    """Count learning data statistics for specific agent"""
    return agent_learning_data_services.count_learning_data_by_agent(agent_id)

@app_server.get("/agent-learning-data/stats", 
                response_model=Dict[str, Any], 
                tags=["Agent Learning Data"])
async def get_learning_data_statistics():
    """Get overall learning data statistics"""
    return agent_learning_data_services.get_learning_data_stats()

# ------------------------------------------
# Agent Simulation Feedback Endpoints
# ------------------------------------------

@app_server.post("/agent-simulation-feedback/", 
                 response_model=AgentSimulationFeedback, 
                 tags=["Agent Simulation Feedback"],
                 status_code=status.HTTP_201_CREATED)
async def create_simulation_feedback(feedback_data: Dict[str, Any] = Body(...)):
    """Create new feedback for an agent simulation"""
    return agent_simulation_feedback_services.create_feedback(feedback_data)

@app_server.get("/agent-simulation-feedback/", 
                response_model=List[AgentSimulationFeedback], 
                tags=["Agent Simulation Feedback"])
async def get_all_feedback():
    """Get all agent simulation feedback entries"""
    return agent_simulation_feedback_services.get_all_feedback()

@app_server.get("/agent-simulation-feedback/{feedback_id}", 
                response_model=AgentSimulationFeedback, 
                tags=["Agent Simulation Feedback"])
async def get_feedback_by_id(feedback_id: int):
    """Get specific feedback entry by its ID"""
    return agent_simulation_feedback_services.get_feedback_by_id(feedback_id)

@app_server.get("/simulations/{simulation_id}/feedback", 
                response_model=List[AgentSimulationFeedback], 
                tags=["Agent Simulation Feedback"])
async def get_feedback_for_simulation(simulation_id: int):
    """Get all feedback for a specific simulation"""
    return agent_simulation_feedback_services.get_feedback_by_simulation(simulation_id)

@app_server.get("/users/{user_id}/simulation-feedback", 
                response_model=List[AgentSimulationFeedback], 
                tags=["Agent Simulation Feedback"])
async def get_user_feedback(user_id: int):
    """Get all feedback submitted by a specific user"""
    return agent_simulation_feedback_services.get_feedback_by_user(user_id)

@app_server.get("/agents/{agent_id}/simulation-feedback", 
                response_model=List[AgentSimulationFeedback], 
                tags=["Agent Simulation Feedback"])
async def get_agent_feedback(agent_id: int):
    """Get all feedback for simulations of a specific agent"""
    return agent_simulation_feedback_services.get_feedback_by_agent(agent_id)

@app_server.put("/agent-simulation-feedback/{feedback_id}", 
                response_model=AgentSimulationFeedback, 
                tags=["Agent Simulation Feedback"])
async def update_feedback_entry(feedback_id: int, updates: Dict[str, Any] = Body(...)):
    """Update existing feedback entry"""
    return agent_simulation_feedback_services.update_feedback(feedback_id, updates)

@app_server.delete("/agent-simulation-feedback/{feedback_id}", 
                   status_code=status.HTTP_204_NO_CONTENT,
                   tags=["Agent Simulation Feedback"])
async def delete_feedback_entry(feedback_id: int):
    """Delete a feedback entry"""
    agent_simulation_feedback_services.delete_feedback(feedback_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app_server.delete("/simulations/{simulation_id}/feedback", 
                   response_model=Dict[str, str],
                   tags=["Agent Simulation Feedback"])
async def delete_all_simulation_feedback(simulation_id: int):
    """Delete all feedback for a specific simulation"""
    return agent_simulation_feedback_services.delete_simulation_feedback(simulation_id)

@app_server.get("/simulations/{simulation_id}/feedback/average-rating", 
                response_model=Dict[str, float], 
                tags=["Agent Simulation Feedback"])
async def get_simulation_average_rating(simulation_id: int):
    """Get average rating for a specific simulation"""
    return agent_simulation_feedback_services.get_average_rating_by_simulation(simulation_id)

@app_server.get("/agents/{agent_id}/feedback/average-rating", 
                response_model=Dict[str, float], 
                tags=["Agent Simulation Feedback"])
async def get_agent_average_rating(agent_id: int):
    """Get average rating across all simulations for a specific agent"""
    return agent_simulation_feedback_services.get_average_rating_by_agent(agent_id)

@app_server.get("/agents/{agent_id}/feedback/stats", 
                response_model=Dict[str, Any], 
                tags=["Agent Simulation Feedback"])
async def get_agent_feedback_statistics(agent_id: int):
    """Get detailed feedback statistics for an agent"""
    return agent_simulation_feedback_services.get_agent_feedback_stats(agent_id)

@app_server.get("/agent-simulation-feedback/recent", 
                response_model=List[AgentSimulationFeedback], 
                tags=["Agent Simulation Feedback"])
async def get_recent_feedback(hours: int = Query(24, gt=0)):
    """Get recent feedback entries within specified hours"""
    return agent_simulation_feedback_services.get_recent_feedback(hours)

@app_server.get("/agent-simulation-feedback/with-comments", 
                response_model=List[AgentSimulationFeedback], 
                tags=["Agent Simulation Feedback"])
async def get_feedback_with_comments():
    """Get all feedback entries that include text comments"""
    return agent_simulation_feedback_services.get_feedback_with_comments()

@app_server.get("/agent-simulation-feedback/stats", 
                response_model=Dict[str, Any], 
                tags=["Agent Simulation Feedback"])
async def get_overall_feedback_statistics():
    """Get overall feedback statistics"""
    return agent_simulation_feedback_services.get_feedback_stats()

# ------------------------------------------
# Agent Simulation Messages Endpoints
# ------------------------------------------

@app_server.post("/agent-simulation-messages/", 
                 response_model=AgentSimulationMessages, 
                 tags=["Simulation"],
                 status_code=status.HTTP_201_CREATED)
async def create_simulation_message(
    simulation_id: int = Form(...),
    message_content: str = Form(...),
    role: str = Form(...),
    message_type: str = Form(...),
    metadata: Optional[str] = Form(None)
):
    """Создать новое сообщение симуляции"""
    metadata_dict = None
    if metadata:
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат метаданных JSON"
            )
    
    return agent_simulation_messages_services.create_simulation_message(
        simulation_id=simulation_id,
        message_content=message_content,
        role=role,
        message_type=message_type,
        metadata=metadata_dict
    )

@app_server.get("/agent-simulation-messages/", 
                response_model=List[AgentSimulationMessages], 
                tags=["Simulation"])
async def get_all_simulation_messages():
    """Получить все сообщения симуляций агентов"""
    return agent_simulation_messages_services.get_all_simulation_messages()

@app_server.get("/agent-simulation-messages/{message_id}", 
                response_model=AgentSimulationMessages, 
                tags=["Simulation"])
async def get_simulation_message_by_id(message_id: int):
    """Получить сообщение симуляции по ID"""
    return agent_simulation_messages_services.get_message_by_id(message_id)

@app_server.get("/simulations/{simulation_id}/messages", 
                response_model=List[AgentSimulationMessages], 
                tags=["Simulation"])
async def get_messages_by_simulation(simulation_id: int):
    """Получить все сообщения конкретной симуляции"""
    return agent_simulation_messages_services.get_messages_by_simulation(simulation_id)

@app_server.get("/simulations/{simulation_id}/conversation", 
                response_model=List[Dict[str, Any]], 
                tags=["Simulation"])
async def get_simulation_conversation(simulation_id: int):
    """Получить все сообщения симуляции, отформатированные как диалог"""
    return agent_simulation_messages_services.get_conversation_from_simulation(simulation_id)

@app_server.get("/simulations/{simulation_id}/messages/role/{role}", 
                response_model=List[AgentSimulationMessages], 
                tags=["Simulation"])
async def get_messages_by_role(simulation_id: int, role: str):
    """Получить сообщения симуляции по конкретной роли"""
    return agent_simulation_messages_services.get_messages_by_role(simulation_id, role)

@app_server.get("/simulations/{simulation_id}/messages/type/{message_type}", 
                response_model=List[AgentSimulationMessages], 
                tags=["Simulation"])
async def get_messages_by_type(simulation_id: int, message_type: str):
    """Получить сообщения симуляции по типу сообщения"""
    return agent_simulation_messages_services.get_messages_by_type(simulation_id, message_type)

@app_server.get("/simulations/{simulation_id}/messages/last", 
                response_model=Optional[AgentSimulationMessages], 
                tags=["Simulation"])
async def get_last_simulation_message(simulation_id: int):
    """Получить последнее сообщение в симуляции"""
    return agent_simulation_messages_services.get_last_message(simulation_id)

@app_server.put("/agent-simulation-messages/{message_id}", 
                response_model=AgentSimulationMessages, 
                tags=["Simulation"])
async def update_simulation_message(
    message_id: int, 
    updates: Dict[str, Any] = Body(...)
):
    """Обновить сообщение симуляции"""
    return agent_simulation_messages_services.update_message(message_id, updates)

@app_server.delete("/agent-simulation-messages/{message_id}", 
                   response_model=Dict[str, str],
                   tags=["Simulation"])
async def delete_simulation_message(message_id: int):
    """Удалить сообщение симуляции"""
    return agent_simulation_messages_services.delete_message(message_id)

@app_server.delete("/simulations/{simulation_id}/messages", 
                   response_model=Dict[str, int],
                   tags=["Simulation"])
async def delete_simulation_messages(simulation_id: int):
    """Удалить все сообщения конкретной симуляции"""
    return agent_simulation_messages_services.delete_simulation_messages(simulation_id)

@app_server.post("/simulations/{simulation_id}/messages/add", 
                 response_model=AgentSimulationMessages, 
                 tags=["Simulation"],
                 status_code=status.HTTP_201_CREATED)
async def add_message_to_simulation(
    simulation_id: int,
    role: str = Form(...),
    content: str = Form(...),
    message_type: str = Form("text"),
    metadata: Optional[str] = Form(None)
):
    """Добавить новое сообщение в симуляцию с автоматической валидацией"""
    metadata_dict = None
    if metadata:
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат метаданных JSON"
            )
    
    return agent_simulation_messages_services.add_message_to_simulation(
        simulation_id=simulation_id,
        role=role,
        content=content,
        message_type=message_type,
        metadata=metadata_dict
    )

@app_server.get("/simulations/{simulation_id}/messages/count", 
                response_model=Dict[str, int], 
                tags=["Simulation"])
async def count_simulation_messages(simulation_id: int):
    """Подсчитать количество сообщений в симуляции по ролям"""
    return agent_simulation_messages_services.count_messages_by_simulation(simulation_id)

@app_server.get("/simulations/{simulation_id}/messages/stats", 
                response_model=Dict[str, int], 
                tags=["Simulation"])
async def get_simulation_message_stats(simulation_id: int):
    """Подсчитать количество сообщений в симуляции по типам"""
    return agent_simulation_messages_services.get_message_stats_by_type(simulation_id)

@app_server.get("/agent-simulation-messages/search", 
                response_model=List[AgentSimulationMessages], 
                tags=["Simulation"])
async def search_simulation_messages(search_term: str = Query(..., min_length=3)):
    """Поиск сообщений симуляции по содержимому"""
    return agent_simulation_messages_services.search_simulation_messages(search_term)

@app_server.get("/agent-simulation-messages/recent", 
                response_model=List[AgentSimulationMessages], 
                tags=["Simulation"])
async def get_recent_simulation_messages(hours: int = Query(24, gt=0)):
    """Получить недавние сообщения симуляций за указанное количество часов"""
    return agent_simulation_messages_services.get_recent_simulation_messages(hours)

@app_server.get("/agent-simulation-messages/metadata/{key}", 
                response_model=List[AgentSimulationMessages], 
                tags=["Simulation"])
async def get_messages_with_metadata_key(key: str):
    """Получить сообщения, содержащие определенный ключ в метаданных"""
    return agent_simulation_messages_services.get_messages_with_metadata_key(key)

# ------------------------------------------
# Agents Simulations Endpoints
# ------------------------------------------

@app_server.post("/agent-simulations/", 
                 response_model=AgentSimulations, 
                 tags=["Simulation"],
                 status_code=status.HTTP_201_CREATED)
async def create_agent_simulation(
    agent_id: int = Form(...),
    conversation_id: int = Form(...),
    simulation_data: Optional[str] = Form(None)
):
    """Создать новую симуляцию агента"""
    simulation_data_dict = None
    if simulation_data:
        try:
            simulation_data_dict = json.loads(simulation_data)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат данных симуляции JSON"
            )
    
    return agents_simulations_services.create_simulation(
        agent_id=agent_id,
        conversation_id=conversation_id,
        simulation_data=simulation_data_dict
    )

@app_server.post("/agent-simulations/run", 
                 response_model=AgentSimulations, 
                 tags=["Simulation"],
                 status_code=status.HTTP_201_CREATED)
async def run_agent_simulation(
    agent_id: int = Form(...),
    conversation_id: int = Form(...),
    simulation_data: Optional[str] = Form(None)
):
    """Запустить новую симуляцию агента и автоматически начать ее"""
    simulation_data_dict = None
    if simulation_data:
        try:
            simulation_data_dict = json.loads(simulation_data)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат данных симуляции JSON"
            )
    
    return agents_simulations_services.run_agent_simulation(
        agent_id=agent_id,
        conversation_id=conversation_id,
        simulation_data=simulation_data_dict
    )

@app_server.get("/agent-simulations/", 
                response_model=List[AgentSimulations], 
                tags=["Simulation"])
async def get_all_agent_simulations():
    """Получить все симуляции агентов"""
    return agents_simulations_services.get_all_simulations()

@app_server.get("/agent-simulations/{simulation_id}", 
                response_model=AgentSimulations, 
                tags=["Simulation"])
async def get_agent_simulation_by_id(simulation_id: int):
    """Получить симуляцию по ID"""
    return agents_simulations_services.get_simulation_by_id(simulation_id)

@app_server.get("/agents/{agent_id}/simulations", 
                response_model=List[AgentSimulations], 
                tags=["Simulation"])
async def get_simulations_by_agent(agent_id: int):
    """Получить все симуляции конкретного агента"""
    return agents_simulations_services.get_simulations_by_agent(agent_id)

@app_server.get("/conversations/{conversation_id}/simulations", 
                response_model=List[AgentSimulations], 
                tags=["Simulation"])
async def get_simulations_by_conversation(conversation_id: int):
    """Получить все симуляции для конкретной беседы"""
    return agents_simulations_services.get_simulations_by_conversation(conversation_id)

@app_server.get("/agent-simulations/active", 
                response_model=List[AgentSimulations], 
                tags=["Simulation"])
async def get_active_agent_simulations():
    """Получить все активные симуляции агентов"""
    return agents_simulations_services.get_active_simulations()

@app_server.get("/agent-simulations/completed", 
                response_model=List[AgentSimulations], 
                tags=["Simulation"])
async def get_completed_agent_simulations(limit: int = Query(100, gt=0, le=1000)):
    """Получить завершенные симуляции агентов"""
    return agents_simulations_services.get_completed_simulations(limit)

@app_server.get("/agent-simulations/failed", 
                response_model=List[AgentSimulations], 
                tags=["Simulation"])
async def get_failed_agent_simulations(limit: int = Query(100, gt=0, le=1000)):
    """Получить неудачные симуляции агентов"""
    return agents_simulations_services.get_failed_simulations(limit)

@app_server.get("/agent-simulations/recent", 
                response_model=List[AgentSimulations], 
                tags=["Simulation"])
async def get_recent_agent_simulations(hours: int = Query(24, gt=0, le=168)):
    """Получить недавние симуляции за указанное количество часов"""
    return agents_simulations_services.get_recent_simulations(hours)

@app_server.put("/agent-simulations/{simulation_id}", 
                response_model=AgentSimulations, 
                tags=["Simulation"])
async def update_agent_simulation(
    simulation_id: int, 
    updates: Dict[str, Any] = Body(...)
):
    """Обновить симуляцию агента"""
    return agents_simulations_services.update_simulation(simulation_id, updates)

@app_server.patch("/agent-simulations/{simulation_id}/start", 
                  response_model=AgentSimulations, 
                  tags=["Simulation"])
async def start_agent_simulation(simulation_id: int):
    """Начать симуляцию (изменить статус на 'in_progress')"""
    return agents_simulations_services.start_simulation(simulation_id)

@app_server.patch("/agent-simulations/{simulation_id}/complete", 
                  response_model=AgentSimulations, 
                  tags=["Simulation"])
async def complete_agent_simulation(
    simulation_id: int,
    simulation_data: Optional[str] = Form(None)
):
    """Завершить симуляцию успешно"""
    simulation_data_dict = None
    if simulation_data:
        try:
            simulation_data_dict = json.loads(simulation_data)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат данных симуляции JSON"
            )
    
    return agents_simulations_services.complete_simulation(simulation_id, simulation_data_dict)

@app_server.patch("/agent-simulations/{simulation_id}/fail", 
                  response_model=AgentSimulations, 
                  tags=["Simulation"])
async def fail_agent_simulation(
    simulation_id: int,
    error_message: str = Form(...),
    error_details: Optional[str] = Form(None)
):
    """Завершить симуляцию с ошибкой"""
    error_details_dict = None
    if error_details:
        try:
            error_details_dict = json.loads(error_details)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат деталей ошибки JSON"
            )
    
    return agents_simulations_services.fail_simulation(
        simulation_id=simulation_id,
        error_message=error_message,
        error_details=error_details_dict
    )

@app_server.delete("/agent-simulations/{simulation_id}", 
                   response_model=Dict[str, str],
                   tags=["Simulation"])
async def delete_agent_simulation(simulation_id: int):
    """Удалить симуляцию"""
    return agents_simulations_services.delete_simulation(simulation_id)

@app_server.get("/agent-simulations/stats", 
                response_model=Dict[str, Any], 
                tags=["Simulation"])
async def get_agent_simulation_stats():
    """Получить статистику по симуляциям агентов"""
    return agents_simulations_services.get_simulation_stats()

@app_server.get("/agent-simulations/top-agents", 
                response_model=List[Dict[str, Any]], 
                tags=["Simulation"])
async def get_top_agent_simulations(limit: int = Query(10, gt=0, le=100)):
    """Получить топ агентов по количеству успешных симуляций"""
    return agents_simulations_services.get_top_agent_simulations(limit)

# ------------------------------------------
# Chat Conversations Endpoints
# ------------------------------------------

@app_server.post("/chat-conversations/", 
                 response_model=ChatConversations, 
                 tags=["Chat"],
                 status_code=status.HTTP_201_CREATED)
async def create_chat_conversation(match_id: int = Form(...)):
    """Создать новую беседу для матча"""
    return chat_conversations_services.create_conversation(match_id)

@app_server.post("/chat-conversations/get-or-create", 
                 response_model=ChatConversations, 
                 tags=["Chat"])
async def get_or_create_chat_conversation(match_id: int = Form(...)):
    """Получить или создать беседу для матча"""
    return chat_conversations_services.get_or_create_conversation(match_id)

@app_server.get("/chat-conversations/", 
                response_model=List[ChatConversations], 
                tags=["Chat"])
async def get_all_chat_conversations():
    """Получить все беседы"""
    return chat_conversations_services.get_all_conversations()

@app_server.get("/chat-conversations/{conversation_id}", 
                response_model=ChatConversations, 
                tags=["Chat"])
async def get_chat_conversation_by_id(conversation_id: int):
    """Получить беседу по ID"""
    return chat_conversations_services.get_conversation_by_id(conversation_id)

@app_server.get("/matches/{match_id}/conversation", 
                response_model=ChatConversations, 
                tags=["Chat"])
async def get_conversation_by_match(match_id: int):
    """Получить беседу по ID матча"""
    return chat_conversations_services.get_conversation_by_match_id(match_id)

@app_server.get("/users/{user_id}/conversations", 
                response_model=List[Dict[str, Any]], 
                tags=["Chat"])
async def get_user_chat_conversations(user_id: int):
    """Получить все беседы пользователя с дополнительной информацией"""
    return chat_conversations_services.get_user_conversations(user_id)

@app_server.get("/users/{user1_id}/conversations/with/{user2_id}", 
                response_model=Optional[ChatConversations], 
                tags=["Chat"])
async def get_conversation_between_users(user1_id: int, user2_id: int):
    """Получить беседу между двумя пользователями (если существует)"""
    return chat_conversations_services.get_conversation_between_users(user1_id, user2_id)

@app_server.get("/chat-conversations/{conversation_id}/with-messages", 
                response_model=Dict[str, Any], 
                tags=["Chat"])
async def get_conversation_with_messages(
    conversation_id: int, 
    limit: int = Query(50, gt=0, le=500)
):
    """Получить беседу вместе с ее сообщениями"""
    return chat_conversations_services.get_conversation_with_messages(conversation_id, limit)

@app_server.get("/chat-conversations/active", 
                response_model=List[Dict[str, Any]], 
                tags=["Chat"])
async def get_active_chat_conversations():
    """Получить все активные беседы (в которых есть сообщения)"""
    return chat_conversations_services.get_active_conversations()

@app_server.get("/chat-conversations/empty", 
                response_model=List[Dict[str, Any]], 
                tags=["Chat"])
async def get_empty_chat_conversations():
    """Получить все пустые беседы (без сообщений)"""
    return chat_conversations_services.get_empty_conversations()

@app_server.get("/chat-conversations/recent", 
                response_model=List[Dict[str, Any]], 
                tags=["Chat"])
async def get_conversations_with_recent_activity(hours: int = Query(24, gt=0, le=168)):
    """Получить беседы с активностью за последние часы"""
    return chat_conversations_services.get_conversations_with_recent_activity(hours)

@app_server.put("/chat-conversations/{conversation_id}", 
                response_model=ChatConversations, 
                tags=["Chat"])
async def update_chat_conversation(
    conversation_id: int, 
    updates: Dict[str, Any] = Body(...)
):
    """Обновить беседу"""
    return chat_conversations_services.update_conversation(conversation_id, updates)

@app_server.patch("/chat-conversations/{conversation_id}/update-last-message-time", 
                  response_model=ChatConversations, 
                  tags=["Chat"])
async def update_last_message_time(conversation_id: int):
    """Обновить время последнего сообщения в беседе (прямо сейчас)"""
    return chat_conversations_services.update_last_message_time(conversation_id)

@app_server.delete("/chat-conversations/{conversation_id}", 
                   response_model=Dict[str, str],
                   tags=["Chat"])
async def delete_chat_conversation(conversation_id: int):
    """Удалить беседу по ID"""
    return chat_conversations_services.delete_conversation(conversation_id)

@app_server.get("/chat-conversations/statistics", 
                response_model=Dict[str, Any], 
                tags=["Chat"])
async def get_chat_conversation_statistics():
    """Получить статистику по беседам"""
    return chat_conversations_services.get_conversation_statistics()

# ------------------------------------------
# Chat Messages Endpoints
# ------------------------------------------

@app_server.post("/chat-messages/", 
                 response_model=ChatMessages, 
                 tags=["Chat"],
                 status_code=status.HTTP_201_CREATED)
async def create_chat_message(
    conversation_id: int = Form(...),
    sender_id: int = Form(...),
    message_text: str = Form(...),
    message_type: str = Form("USER")
):
    """Создать новое сообщение"""
    try:
        message_type_enum = MessageTypeEnum(message_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неверный тип сообщения. Должен быть одним из: {[e.value for e in MessageTypeEnum]}"
        )
    
    return chat_messages_services.create_message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        message_text=message_text,
        message_type=message_type_enum
    )

@app_server.get("/chat-messages/", 
                response_model=List[ChatMessages], 
                tags=["Chat"])
async def get_all_chat_messages():
    """Получить все сообщения"""
    return chat_messages_services.get_all_messages()

@app_server.get("/chat-messages/{message_id}", 
                response_model=ChatMessages, 
                tags=["Chat"])
async def get_chat_message_by_id(message_id: int):
    """Получить сообщение по ID"""
    return chat_messages_services.get_message_by_id(message_id)

@app_server.get("/conversations/{conversation_id}/messages", 
                response_model=List[ChatMessages], 
                tags=["Chat"])
async def get_conversation_messages(
    conversation_id: int,
    limit: int = Query(50, gt=0, le=500),
    offset: int = Query(0, ge=0)
):
    """Получить сообщения из конкретной беседы с пагинацией"""
    return chat_messages_services.get_messages_by_conversation(
        conversation_id=conversation_id,
        limit=limit,
        offset=offset
    )

@app_server.get("/conversations/{conversation_id}/messages/last", 
                response_model=Optional[ChatMessages], 
                tags=["Chat"])
async def get_last_conversation_message(conversation_id: int):
    """Получить последнее сообщение в беседе"""
    return chat_messages_services.get_last_message_in_conversation(conversation_id)

@app_server.get("/conversations/{conversation_id}/messages/agent-simulation", 
                response_model=List[ChatMessages], 
                tags=["Chat"])
async def get_agent_simulation_messages(conversation_id: int):
    """Получить сообщения агентов в конкретной беседе"""
    return chat_messages_services.get_agent_simulation_messages(conversation_id)

@app_server.get("/users/{user_id}/messages", 
                response_model=List[ChatMessages], 
                tags=["Chat"])
async def get_user_chat_messages(
    user_id: int,
    limit: int = Query(50, gt=0, le=500),
    offset: int = Query(0, ge=0)
):
    """Получить все сообщения, отправленные пользователем"""
    return chat_messages_services.get_user_messages(
        user_id=user_id,
        limit=limit,
        offset=offset
    )

@app_server.get("/users/{user_id}/unread-messages", 
                response_model=Dict[str, Any], 
                tags=["Chat"])
async def get_user_unread_messages_count(user_id: int):
    """Подсчитать непрочитанные сообщения для пользователя по всем беседам и для каждой беседы"""
    return chat_messages_services.count_unread_messages(user_id)

@app_server.get("/chat-messages/recent", 
                response_model=List[ChatMessages], 
                tags=["Chat"])
async def get_recent_chat_messages(hours: int = Query(24, gt=0, le=168)):
    """Получить сообщения за последние часы"""
    return chat_messages_services.get_recent_messages(hours)

@app_server.get("/chat-messages/search", 
                response_model=List[ChatMessages], 
                tags=["Chat"])
async def search_chat_messages(
    search_term: str = Query(..., min_length=3),
    conversation_id: Optional[int] = Query(None)
):
    """Поиск сообщений по тексту"""
    return chat_messages_services.search_messages(
        search_term=search_term,
        conversation_id=conversation_id
    )

@app_server.put("/chat-messages/{message_id}", 
                response_model=ChatMessages, 
                tags=["Chat"])
async def update_chat_message(
    message_id: int, 
    updates: Dict[str, Any] = Body(...)
):
    """Обновить сообщение"""
    return chat_messages_services.update_message(message_id, updates)

@app_server.patch("/conversations/{conversation_id}/messages/mark-read", 
                  response_model=Dict[str, int],
                  tags=["Chat"])
async def mark_conversation_messages_as_read(
    conversation_id: int,
    user_id: int = Form(...)
):
    """Отметить все непрочитанные сообщения в беседе как прочитанные для указанного пользователя"""
    return chat_messages_services.mark_messages_as_read(conversation_id, user_id)

@app_server.delete("/chat-messages/{message_id}", 
                   response_model=Dict[str, str],
                   tags=["Chat"])
async def delete_chat_message(message_id: int):
    """Удалить сообщение по ID"""
    return chat_messages_services.delete_message(message_id)

@app_server.get("/conversations/{conversation_id}/statistics", 
                response_model=Dict[str, Any], 
                tags=["Chat"])
async def get_conversation_message_statistics(conversation_id: int):
    """Получить статистику сообщений для беседы"""
    return chat_messages_services.get_conversation_statistics(conversation_id)

# ------------------------------------------
# Cookie Endpoints
# ------------------------------------------

# ------------------------------------------
# Cookie Endpoints
# ------------------------------------------

@app_server.post("/auth/session", 
                 response_model=Dict[str, Any], 
                 tags=["Cookie"],
                 status_code=status.HTTP_200_OK)
async def create_or_get_user_session(request: Request, response: Response):
    """Создать или получить пользовательскую сессию"""
    try:
        session_data = session_manager.create_or_get_user_session(request, response)
        return {
            "success": True,
            "data": session_data,
            "message": "Сессия успешно создана или обновлена"
        }
    except Exception as e:
        log.error(f"Ошибка при создании/получении сессии: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось создать или получить сессию"
        )

@app_server.get("/auth/current-user", 
                response_model=Dict[str, Any], 
                tags=["Cookie"])
async def get_current_user_info(request: Request):
    """Получить информацию о текущем пользователе из сессии"""
    try:
        user_data = session_manager.get_current_user_from_request(request)
        user = user_services.get_user_by_id(user_data["user_id"])
        
        return {
            "success": True,
            "data": {
                "user_id": user_data["user_id"],
                "session_id": user_data["session_id"],
                "fingerprint_hash": user_data["fingerprint_hash"],
                "user_info": {
                    "id": user.ID,
                    "is_active": user.IsActive,
                    "total_sessions": user.TotalSessions,
                    "last_active": user.LastActive.isoformat() if user.LastActive else None,
                    "created_at": user.CreatedAt.isoformat()
                }
            },
            "message": "Информация о пользователе получена"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        log.error(f"Ошибка при получении информации о пользователе: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось получить информацию о пользователе"
        )

@app_server.post("/auth/logout", 
                 response_model=Dict[str, str], 
                 tags=["Cookie"])
async def logout_user(request: Request, response: Response):
    """Выйти из системы (деактивировать сессию и очистить куки)"""
    try:
        result = session_manager.logout_user(request, response)
        return {
            "success": True,
            "message": result["message"]
        }
    except Exception as e:
        log.error(f"Ошибка при выходе из системы: {str(e)}")
        # Всегда очищаем куки, даже если произошла ошибка
        session_manager._jwt_manager.clear_cookie(response)
        return {
            "success": True,
            "message": "Сессия очищена"
        }

@app_server.get("/auth/session/validate", 
                response_model=Dict[str, Any], 
                tags=["Cookie"])
async def validate_current_session(request: Request):
    """Проверить валидность текущей сессии"""
    try:
        user_data = session_manager.get_current_user_from_request(request)
        session = user_sessions_services.get_session_by_id(user_data["session_id"])
        
        if not session or not session.IsActive:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Сессия недействительна или неактивна"
            )
        
        return {
            "success": True,
            "data": {
                "is_valid": True,
                "user_id": user_data["user_id"],
                "session_id": user_data["session_id"],
                "session_expires_at": session.ExpiresAt.isoformat() if session.ExpiresAt else None,
                "session_created_at": session.CreatedAt.isoformat()
            },
            "message": "Сессия действительна"
        }
    except HTTPException as e:
        return {
            "success": False,
            "data": {
                "is_valid": False
            },
            "message": e.detail
        }
    except Exception as e:
        log.error(f"Ошибка при валидации сессии: {str(e)}")
        return {
            "success": False,
            "data": {
                "is_valid": False
            },
            "message": "Ошибка при проверке сессии"
        }

@app_server.post("/auth/session/refresh", 
                 response_model=Dict[str, Any], 
                 tags=["Cookie"])
async def refresh_user_session(request: Request, response: Response):
    """Обновить токен пользовательской сессии"""
    try:
        current_user = session_manager.get_current_user_from_request(request)
        
        # Получаем текущий токен
        current_token = session_manager._jwt_manager.get_token_from_request(request)
        if not current_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен сессии не найден"
            )
        
        # Обновляем токен
        new_token = session_manager._jwt_manager.refresh_token(current_token, request)
        session_manager._jwt_manager.set_cookie(response, new_token)
        
        # Обновляем активность пользователя
        user_services.update_user_activity(current_user["user_id"])
        
        return {
            "success": True,
            "data": {
                "user_id": current_user["user_id"],
                "session_id": current_user["session_id"],
                "token_refreshed": True
            },
            "message": "Токен сессии успешно обновлен"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        log.error(f"Ошибка при обновлении токена: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось обновить токен сессии"
        )

@app_server.get("/auth/session/info", 
                response_model=Dict[str, Any], 
                tags=["Cookie"])
async def get_session_info(request: Request):
    """Получить подробную информацию о текущей сессии"""
    try:
        user_data = session_manager.get_current_user_from_request(request)
        session = user_sessions_services.get_session_by_id(user_data["session_id"])
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сессия не найдена"
            )
        
        return {
            "success": True,
            "data": {
                "session_id": session.ID,
                "user_id": session.UserID,
                "fingerprint_hash": session.FingerprintHash,
                "ip_address": session.IPAddress,
                "user_agent": session.UserAgent,
                "is_active": session.IsActive,
                "created_at": session.CreatedAt.isoformat(),
                "expires_at": session.ExpiresAt.isoformat() if session.ExpiresAt else None,
                "last_activity": session.LastActivity.isoformat() if session.LastActivity else None
            },
            "message": "Информация о сессии получена"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        log.error(f"Ошибка при получении информации о сессии: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось получить информацию о сессии"
        )

@app_server.delete("/auth/sessions/all", 
                   response_model=Dict[str, Any], 
                   tags=["Cookie"])
async def logout_all_user_sessions(request: Request, response: Response):
    """Завершить все сессии пользователя (кроме текущей)"""
    try:
        current_user = session_manager.get_current_user_from_request(request)
        
        # Деактивируем все сессии пользователя кроме текущей
        deactivated_count = user_sessions_services.deactivate_all_user_sessions_except_current(
            user_id=current_user["user_id"],
            current_session_id=current_user["session_id"]
        )
        
        return {
            "success": True,
            "data": {
                "deactivated_sessions_count": deactivated_count,
                "current_session_preserved": True
            },
            "message": f"Деактивировано {deactivated_count} сессий"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        log.error(f"Ошибка при завершении всех сессий: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось завершить все сессии"
        )

@app_server.get("/auth/fingerprint", 
                response_model=Dict[str, Any], 
                tags=["Cookie"])
async def get_browser_fingerprint(request: Request):
    """Получить отпечаток браузера для текущего запроса"""
    try:
        fingerprint_hash = session_manager._fingerprint_collector.generate_fingerprint_hash(request)
        fingerprint_data = session_manager._fingerprint_collector.collect_fingerprint_data(request)
        
        return {
            "success": True,
            "data": {
                "fingerprint_hash": fingerprint_hash,
                "fingerprint_components": fingerprint_data
            },
            "message": "Отпечаток браузера сгенерирован"
        }
    except Exception as e:
        log.error(f"Ошибка при генерации отпечатка браузера: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось сгенерировать отпечаток браузера"
        )
    
# ------------------------------------------
# Matches Endpoints
# ------------------------------------------

@app_server.post("/matches/", 
                 response_model=Matches, 
                 tags=["Match"],
                 status_code=status.HTTP_201_CREATED)
async def create_new_match(
    user1_id: int = Form(...),
    user2_id: int = Form(...)
):
    """Создать новый матч между пользователями"""
    return matches_services.create_match(user1_id, user2_id)

@app_server.post("/matches/from-likes", 
                 response_model=Optional[Matches], 
                 tags=["Match"],
                 status_code=status.HTTP_201_CREATED)
async def create_match_from_mutual_likes(
    from_user_id: int = Form(...),
    to_user_id: int = Form(...)
):
    """Создать матч между пользователями, если есть взаимные лайки"""
    match = matches_services.create_match_from_likes(from_user_id, to_user_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нет взаимных лайков между пользователями"
        )
    return match

@app_server.get("/matches/", 
                response_model=List[Matches], 
                tags=["Match"])
async def get_all_matches():
    """Получить все совпадения (матчи)"""
    return matches_services.get_all_matches()

@app_server.get("/matches/{match_id}", 
                response_model=Matches, 
                tags=["Match"])
async def get_match_by_id(match_id: int):
    """Получить матч по ID"""
    return matches_services.get_match_by_id(match_id)

@app_server.get("/matches/check/{user1_id}/{user2_id}", 
                response_model=Optional[Matches], 
                tags=["Match"])
async def check_match_between_users(user1_id: int, user2_id: int):
    """Проверить существование матча между двумя пользователями"""
    return matches_services.check_match_exists(user1_id, user2_id)

@app_server.get("/users/{user_id}/matches", 
                response_model=List[Dict[str, Any]], 
                tags=["Match"])
async def get_user_matches(
    user_id: int,
    status: Optional[str] = Query(None, description="Фильтр по статусу: ACTIVE, PAUSED, ENDED")
):
    """Получить все матчи пользователя с возможностью фильтрации по статусу"""
    match_status = None
    if status:
        try:
            match_status = MatchStatusEnum(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неверный статус. Должен быть одним из: {[e.value for e in MatchStatusEnum]}"
            )
    
    return matches_services.get_user_matches(user_id, match_status)

@app_server.get("/users/{user_id}/matches/active", 
                response_model=List[Dict[str, Any]], 
                tags=["Match"])
async def get_user_active_matches(user_id: int):
    """Получить активные матчи пользователя"""
    return matches_services.get_active_matches(user_id)

@app_server.get("/users/{user_id}/matches/paused", 
                response_model=List[Dict[str, Any]], 
                tags=["Match"])
async def get_user_paused_matches(user_id: int):
    """Получить приостановленные матчи пользователя"""
    return matches_services.get_paused_matches(user_id)

@app_server.get("/users/{user_id}/matches/ended", 
                response_model=List[Dict[str, Any]], 
                tags=["Match"])
async def get_user_ended_matches(user_id: int):
    """Получить завершенные матчи пользователя"""
    return matches_services.get_ended_matches(user_id)

@app_server.get("/users/{user_id}/matches/stats", 
                response_model=Dict[str, Any], 
                tags=["Match"])
async def get_user_match_statistics(user_id: int):
    """Получить статистику матчей для конкретного пользователя"""
    return matches_services.get_user_match_stats(user_id)

@app_server.get("/matches/recent", 
                response_model=List[Dict[str, Any]], 
                tags=["Match"])
async def get_recent_matches(hours: int = Query(24, gt=0, le=168)):
    """Получить недавние матчи за указанное количество часов"""
    return matches_services.get_recent_matches(hours)

@app_server.get("/matches/with-conversations", 
                response_model=List[Dict[str, Any]], 
                tags=["Match"])
async def get_matches_with_conversations():
    """Получить матчи, которые имеют активные беседы"""
    return matches_services.get_matches_with_conversations()

@app_server.get("/matches/without-conversations", 
                response_model=List[Dict[str, Any]], 
                tags=["Match"])
async def get_matches_without_conversations():
    """Получить матчи, которые не имеют активных бесед"""
    return matches_services.get_matches_without_conversations()

@app_server.get("/matches/statistics", 
                response_model=Dict[str, int], 
                tags=["Match"])
async def get_matches_statistics():
    """Получить статистику по количеству матчей в разных статусах"""
    return matches_services.get_matches_count()

@app_server.put("/matches/{match_id}", 
                response_model=Matches, 
                tags=["Match"])
async def update_match_data(
    match_id: int, 
    updates: Dict[str, Any] = Body(...)
):
    """Обновить данные матча"""
    return matches_services.update_match(match_id, updates)

@app_server.patch("/matches/{match_id}/status", 
                  response_model=Matches, 
                  tags=["Match"])
async def update_match_status(
    match_id: int,
    new_status: str = Form(...)
):
    """Обновить статус матча"""
    try:
        status_enum = MatchStatusEnum(new_status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неверный статус. Должен быть одним из: {[e.value for e in MatchStatusEnum]}"
        )
    
    return matches_services.update_match_status(match_id, status_enum)

@app_server.patch("/matches/{match_id}/pause", 
                  response_model=Matches, 
                  tags=["Match"])
async def pause_match(match_id: int):
    """Приостановить матч"""
    return matches_services.update_match_status(match_id, MatchStatusEnum.PAUSED)

@app_server.patch("/matches/{match_id}/resume", 
                  response_model=Matches, 
                  tags=["Match"])
async def resume_match(match_id: int):
    """Возобновить приостановленный матч"""
    return matches_services.update_match_status(match_id, MatchStatusEnum.ACTIVE)

@app_server.patch("/matches/{match_id}/end", 
                  response_model=Matches, 
                  tags=["Match"])
async def end_match(match_id: int):
    """Завершить матч"""
    return matches_services.update_match_status(match_id, MatchStatusEnum.ENDED)

@app_server.delete("/matches/{match_id}", 
                   response_model=Dict[str, str],
                   tags=["Match"])
async def delete_match(match_id: int):
    """Удалить матч по ID"""
    return matches_services.delete_match(match_id)

@app_server.post("/matches/cleanup-inactive", 
                 response_model=Dict[str, Any], 
                 tags=["Match"])
async def cleanup_inactive_matches(
    days_inactive: int = Form(30, gt=0, le=365)
):
    """Автоматически завершить неактивные матчи (без сообщений в течение N дней)"""
    result = matches_services.end_inactive_matches(days_inactive)
    return {
        "success": True,
        "data": result,
        "message": f"Проверено {result['total_checked']} матчей, завершено {result['ended_matches']}"
    }

# ------------------------------------------
# Profile Details Endpoints
# ------------------------------------------

@app_server.post("/profiles/", 
                 response_model=ProfileDetails, 
                 tags=["Profile"],
                 status_code=status.HTTP_201_CREATED)
async def create_user_profile(
    user_id: int = Form(...),
    age: Optional[int] = Form(None),
    gender: Optional[str] = Form(None),
    interests: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    profile_photo_url: Optional[str] = Form(None),
    location: Optional[str] = Form(None)
):
    """Создать новый профиль пользователя"""
    profile_data = {
        'Age': age,
        'Gender': gender,
        'Interests': interests,
        'Bio': bio,
        'ProfilePhotoUrl': profile_photo_url,
        'Location': location
    }
    
    return profile_details_services.create_profile(user_id, profile_data)

@app_server.get("/profiles/", 
                response_model=List[ProfileDetails], 
                tags=["Profile"])
async def get_all_user_profiles():
    """Получить все профили пользователей"""
    return profile_details_services.get_all_profiles()

@app_server.get("/profiles/{profile_id}", 
                response_model=ProfileDetails, 
                tags=["Profile"])
async def get_profile_by_id(profile_id: int):
    """Получить профиль по ID"""
    return profile_details_services.get_profile_by_id(profile_id)

@app_server.get("/users/{user_id}/profile", 
                response_model=ProfileDetails, 
                tags=["Profile"])
async def get_user_profile(user_id: int):
    """Получить профиль по ID пользователя"""
    return profile_details_services.get_profile_by_user_id(user_id)

@app_server.get("/users/{user_id}/profile/recommendations", 
                response_model=List[Dict[str, Any]], 
                tags=["Profile"])
async def get_profile_recommendations_for_user(
    user_id: int,
    limit: int = Query(10, gt=0, le=50)
):
    """Получить рекомендации профилей для пользователя"""
    return profile_details_services.get_profile_recommendations(user_id, limit)

@app_server.get("/profiles/search/age-range", 
                response_model=List[ProfileDetails], 
                tags=["Profile"])
async def get_profiles_by_age_range(
    min_age: int = Query(..., ge=18, le=120),
    max_age: int = Query(..., ge=18, le=120)
):
    """Получить профили в заданном возрастном диапазоне"""
    if min_age > max_age:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Минимальный возраст не может быть больше максимального"
        )
    
    return profile_details_services.get_profiles_by_age_range(min_age, max_age)

@app_server.get("/profiles/search/gender/{gender}", 
                response_model=List[ProfileDetails], 
                tags=["Profile"])
async def get_profiles_by_gender(gender: str):
    """Получить профили по полу"""
    return profile_details_services.get_profiles_by_gender(gender)

@app_server.get("/profiles/search/location/{location}", 
                response_model=List[ProfileDetails], 
                tags=["Profile"])
async def get_profiles_by_location(location: str):
    """Получить профили по местоположению"""
    return profile_details_services.get_profiles_by_location(location)

@app_server.get("/profiles/search/interests", 
                response_model=List[ProfileDetails], 
                tags=["Profile"])
async def search_profiles_by_interests(
    interests: str = Query(..., description="Интересы через запятую (например: спорт,музыка,кино)")
):
    """Поиск профилей по интересам"""
    interests_list = [interest.strip() for interest in interests.split(',') if interest.strip()]
    if not interests_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать хотя бы один интерес"
        )
    
    return profile_details_services.search_profiles_by_interests(interests_list)

@app_server.get("/profiles/with-photos", 
                response_model=List[ProfileDetails], 
                tags=["Profile"])
async def get_profiles_with_photos():
    """Получить профили с фотографиями"""
    return profile_details_services.get_profiles_with_photo()

@app_server.get("/profiles/incomplete", 
                response_model=List[ProfileDetails], 
                tags=["Profile"])
async def get_incomplete_profiles():
    """Получить неполные профили (без важных данных)"""
    return profile_details_services.get_incomplete_profiles()

@app_server.get("/profiles/statistics/completion", 
                response_model=Dict[str, Any], 
                tags=["Profile"])
async def get_profile_completion_statistics():
    """Получить статистику заполнения профилей"""
    return profile_details_services.get_profile_completion_stats()

@app_server.put("/profiles/{profile_id}", 
                response_model=ProfileDetails, 
                tags=["Profile"])
async def update_profile_by_id(
    profile_id: int,
    updates: Dict[str, Any] = Body(...)
):
    """Обновить профиль пользователя по ID профиля"""
    return profile_details_services.update_profile(profile_id, updates)

@app_server.put("/users/{user_id}/profile", 
                response_model=ProfileDetails, 
                tags=["Profile"])
async def update_or_create_user_profile(
    user_id: int,
    age: Optional[int] = Form(None),
    gender: Optional[str] = Form(None),
    interests: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    profile_photo_url: Optional[str] = Form(None),
    location: Optional[str] = Form(None)
):
    """Обновить профиль по ID пользователя (или создать новый, если не существует)"""
    updates = {}
    
    if age is not None:
        updates['Age'] = age
    if gender is not None:
        updates['Gender'] = gender
    if interests is not None:
        updates['Interests'] = interests
    if bio is not None:
        updates['Bio'] = bio
    if profile_photo_url is not None:
        updates['ProfilePhotoUrl'] = profile_photo_url
    if location is not None:
        updates['Location'] = location
    
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать хотя бы одно поле для обновления"
        )
    
    return profile_details_services.update_user_profile(user_id, updates)

@app_server.patch("/profiles/{profile_id}/photo", 
                  response_model=ProfileDetails, 
                  tags=["Profile"])
async def update_profile_photo(
    profile_id: int,
    profile_photo_url: str = Form(...)
):
    """Обновить фотографию профиля"""
    return profile_details_services.update_profile(profile_id, {'ProfilePhotoUrl': profile_photo_url})

@app_server.patch("/profiles/{profile_id}/bio", 
                  response_model=ProfileDetails, 
                  tags=["Profile"])
async def update_profile_bio(
    profile_id: int,
    bio: str = Form(...)
):
    """Обновить описание профиля"""
    return profile_details_services.update_profile(profile_id, {'Bio': bio})

@app_server.patch("/profiles/{profile_id}/interests", 
                  response_model=ProfileDetails, 
                  tags=["Profile"])
async def update_profile_interests(
    profile_id: int,
    interests: str = Form(..., description="Интересы через запятую")
):
    """Обновить интересы профиля"""
    return profile_details_services.update_profile(profile_id, {'Interests': interests})

@app_server.patch("/profiles/{profile_id}/location", 
                  response_model=ProfileDetails, 
                  tags=["Profile"])
async def update_profile_location(
    profile_id: int,
    location: str = Form(...)
):
    """Обновить местоположение профиля"""
    return profile_details_services.update_profile(profile_id, {'Location': location})

@app_server.delete("/profiles/{profile_id}", 
                   response_model=Dict[str, str],
                   tags=["Profile"])
async def delete_profile_by_id(profile_id: int):
    """Удалить профиль по ID"""
    return profile_details_services.delete_profile(profile_id)

@app_server.delete("/users/{user_id}/profile", 
                   response_model=Dict[str, str],
                   tags=["Profile"])
async def delete_user_profile(user_id: int):
    """Удалить профиль по ID пользователя"""
    return profile_details_services.delete_user_profile(user_id)

# ------------------------------------------
# User Agents Endpoints
# ------------------------------------------

@app_server.post("/user-agents/", 
                 response_model=UserAgents, 
                 tags=["Agent"],
                 status_code=status.HTTP_201_CREATED)
async def create_user_agent(
    user_id: int = Form(...),
    personality_data: str = Form(..., description="JSON строка с данными о личности агента")
):
    """Создать нового агента для пользователя"""
    try:
        personality_dict = json.loads(personality_data)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат данных личности JSON"
        )
    
    return user_agents_services.create_agent(user_id, personality_dict)

@app_server.get("/user-agents/", 
                response_model=List[UserAgents], 
                tags=["Agent"])
async def get_all_user_agents():
    """Получить всех агентов пользователей"""
    return user_agents_services.get_all_agents()

@app_server.get("/user-agents/{agent_id}", 
                response_model=UserAgents, 
                tags=["Agent"])
async def get_user_agent_by_id(agent_id: int):
    """Получить агента по ID"""
    return user_agents_services.get_agent_by_id(agent_id)

@app_server.get("/users/{user_id}/agent", 
                response_model=UserAgents, 
                tags=["Agent"])
async def get_agent_by_user_id(user_id: int):
    """Получить агента по ID пользователя"""
    return user_agents_services.get_agent_by_user_id(user_id)

@app_server.get("/user-agents/status/ready", 
                response_model=List[UserAgents], 
                tags=["Agent"])
async def get_ready_user_agents():
    """Получить всех агентов со статусом 'готов'"""
    return user_agents_services.get_ready_agents()

@app_server.get("/user-agents/status/learning", 
                response_model=List[UserAgents], 
                tags=["Agent"])
async def get_learning_user_agents():
    """Получить всех агентов со статусом 'обучается'"""
    return user_agents_services.get_learning_agents()

@app_server.get("/user-agents/requiring-update", 
                response_model=List[UserAgents], 
                tags=["Agent"])
async def get_agents_requiring_update(
    days_threshold: int = Query(7, gt=0, le=365, description="Количество дней с последнего обновления")
):
    """Получить агентов, требующих обновления (не обновлялись более N дней)"""
    return user_agents_services.get_agents_requiring_update(days_threshold)

@app_server.get("/user-agents/{agent_id}/similar", 
                response_model=List[Dict[str, Any]], 
                tags=["Agent"])
async def find_similar_agents(
    agent_id: int,
    threshold: float = Query(0.5, ge=0.0, le=1.0, description="Порог схожести (0.0 - 1.0)"),
    limit: int = Query(10, gt=0, le=50, description="Максимальное количество результатов")
):
    """Найти агентов с похожими характеристиками личности"""
    return user_agents_services.find_similar_agents(agent_id, threshold, limit)

@app_server.get("/user-agents/statistics", 
                response_model=Dict[str, Any], 
                tags=["Agent"])
async def get_user_agents_statistics():
    """Получить статистику по агентам"""
    return user_agents_services.get_agents_stats()

@app_server.put("/user-agents/{agent_id}", 
                response_model=UserAgents, 
                tags=["Agent"])
async def update_user_agent(
    agent_id: int,
    updates: Dict[str, Any] = Body(...)
):
    """Обновить данные агента"""
    return user_agents_services.update_agent(agent_id, updates)

@app_server.patch("/user-agents/{agent_id}/status", 
                  response_model=UserAgents, 
                  tags=["Agent"])
async def update_agent_status(
    agent_id: int,
    status: str = Form(..., description="Новый статус обучения")
):
    """Обновить статус обучения агента"""
    try:
        status_enum = LearningStatusEnum(status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неверный статус обучения. Должен быть одним из: {[e.value for e in LearningStatusEnum]}"
        )
    
    return user_agents_services.update_agent_status(agent_id, status_enum)

@app_server.patch("/user-agents/{agent_id}/personality", 
                  response_model=UserAgents, 
                  tags=["Agent"])
async def update_agent_personality(
    agent_id: int,
    personality_data: str = Form(..., description="JSON строка с обновленными данными о личности")
):
    """Обновить данные о личности агента"""
    try:
        personality_dict = json.loads(personality_data)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат данных личности JSON"
        )
    
    return user_agents_services.update_agent_personality(agent_id, personality_dict)

@app_server.post("/user-agents/{agent_id}/train", 
                 response_model=UserAgents, 
                 tags=["Agent"])
async def train_user_agent(
    agent_id: int,
    training_data: str = Form(..., description="JSON строка с тренировочными данными")
):
    """Обучить агента на новых данных"""
    try:
        training_dict = json.loads(training_data)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат тренировочных данных JSON"
        )
    
    return user_agents_services.train_agent(agent_id, training_dict)

@app_server.post("/user-agents/{agent_id}/reset-learning", 
                 response_model=UserAgents, 
                 tags=["Agent"])
async def reset_agent_learning(agent_id: int):
    """Сбросить обучение агента к базовому состоянию"""
    return user_agents_services.reset_agent_learning(agent_id)

@app_server.patch("/user-agents/{agent_id}/mark-ready", 
                  response_model=UserAgents, 
                  tags=["Agent"])
async def mark_agent_as_ready(agent_id: int):
    """Отметить агента как готового к работе"""
    return user_agents_services.update_agent_status(agent_id, LearningStatusEnum.READY)

@app_server.patch("/user-agents/{agent_id}/mark-learning", 
                  response_model=UserAgents, 
                  tags=["Agent"])
async def mark_agent_as_learning(agent_id: int):
    """Отметить агента как обучающегося"""
    return user_agents_services.update_agent_status(agent_id, LearningStatusEnum.LEARNING)

@app_server.delete("/user-agents/{agent_id}", 
                   response_model=Dict[str, str],
                   tags=["Agent"])
async def delete_user_agent_by_id(agent_id: int):
    """Удалить агента по ID"""
    return user_agents_services.delete_agent(agent_id)

@app_server.delete("/users/{user_id}/agent", 
                   response_model=Dict[str, str],
                   tags=["Agent"])
async def delete_agent_by_user_id(user_id: int):
    """Удалить агента по ID пользователя"""
    return user_agents_services.delete_user_agent(user_id)

# ------------------------------------------
# User Conversation Feedback Endpoints
# ------------------------------------------

@app_server.post("/conversation-feedback/", 
                 response_model=UserConversationFeedback, 
                 tags=["Feedback"],
                 status_code=status.HTTP_201_CREATED)
async def create_conversation_feedback(
    user_id: int = Form(...),
    conversation_id: int = Form(...),
    rating: int = Form(..., ge=1, le=5, description="Оценка от 1 до 5"),
    feedback_text: Optional[str] = Form(None, description="Текст отзыва")
):
    """Создать новую запись обратной связи о беседе"""
    feedback = UserConversationFeedback(
        UserID=user_id,
        ConversationID=conversation_id,
        Rating=rating,
        FeedbackText=feedback_text,
        CreatedAt=datetime.now()
    )
    
    return user_conversation_feedback_services.create_feedback(feedback)

@app_server.post("/conversation-feedback/upsert", 
                 response_model=UserConversationFeedback, 
                 tags=["Feedback"])
async def upsert_conversation_feedback(
    user_id: int = Form(...),
    conversation_id: int = Form(...),
    rating: int = Form(..., ge=1, le=5, description="Оценка от 1 до 5"),
    feedback_text: str = Form(..., description="Текст отзыва")
):
    """Создать или обновить отзыв о беседе (если уже существует - обновит)"""
    return user_conversation_feedback_services.upsert_feedback(
        user_id=user_id,
        conversation_id=conversation_id,
        rating=rating,
        feedback_text=feedback_text
    )

@app_server.get("/conversation-feedback/", 
                response_model=List[UserConversationFeedback], 
                tags=["Feedback"])
async def get_all_conversation_feedback():
    """Получить все записи обратной связи о беседах"""
    return user_conversation_feedback_services.get_all_feedback()

@app_server.get("/conversation-feedback/{feedback_id}", 
                response_model=UserConversationFeedback, 
                tags=["Feedback"])
async def get_conversation_feedback_by_id(feedback_id: int):
    """Получить запись обратной связи по ID"""
    return user_conversation_feedback_services.get_feedback_by_id(feedback_id)

@app_server.get("/users/{user_id}/conversations/{conversation_id}/feedback", 
                response_model=Optional[UserConversationFeedback], 
                tags=["Feedback"])
async def get_user_conversation_feedback(user_id: int, conversation_id: int):
    """Получить обратную связь конкретного пользователя о конкретной беседе"""
    return user_conversation_feedback_services.get_feedback_by_user_conversation(user_id, conversation_id)

@app_server.get("/conversations/{conversation_id}/feedback", 
                response_model=List[UserConversationFeedback], 
                tags=["Feedback"])
async def get_conversation_all_feedback(conversation_id: int):
    """Получить все отзывы о конкретной беседе"""
    return user_conversation_feedback_services.get_conversation_feedback(conversation_id)

@app_server.get("/conversations/{conversation_id}/rating/average", 
                response_model=Dict[str, float], 
                tags=["Feedback"])
async def get_conversation_average_rating(conversation_id: int):
    """Получить среднюю оценку беседы"""
    average_rating = user_conversation_feedback_services.get_average_conversation_rating(conversation_id)
    return {
        "conversation_id": conversation_id,
        "average_rating": average_rating
    }

@app_server.get("/users/{user_id}/feedback", 
                response_model=List[UserConversationFeedback], 
                tags=["Feedback"])
async def get_user_all_feedback(user_id: int):
    """Получить все отзывы, оставленные пользователем"""
    return user_conversation_feedback_services.get_user_feedback(user_id)

@app_server.get("/users/{user_id}/rating/average", 
                response_model=Dict[str, float], 
                tags=["Feedback"])
async def get_user_average_rating(user_id: int):
    """Получить среднюю оценку бесед пользователя"""
    average_rating = user_conversation_feedback_services.get_user_average_rating(user_id)
    return {
        "user_id": user_id,
        "average_rating": average_rating
    }

@app_server.get("/conversation-feedback/top-rated", 
                response_model=List[Dict[str, Any]], 
                tags=["Feedback"])
async def get_top_rated_conversations(limit: int = Query(10, gt=0, le=100)):
    """Получить беседы с самыми высокими оценками"""
    return user_conversation_feedback_services.get_conversations_with_highest_ratings(limit)

@app_server.get("/conversation-feedback/statistics", 
                response_model=Dict[str, Any], 
                tags=["Feedback"])
async def get_conversation_feedback_statistics():
    """Получить статистику по обратной связи"""
    return user_conversation_feedback_services.get_feedback_statistics()

@app_server.put("/conversation-feedback/{feedback_id}", 
                response_model=UserConversationFeedback, 
                tags=["Feedback"])
async def update_conversation_feedback(
    feedback_id: int,
    updates: Dict[str, Any] = Body(...)
):
    """Обновить запись обратной связи"""
    return user_conversation_feedback_services.update_feedback(feedback_id, updates)

@app_server.patch("/conversation-feedback/{feedback_id}/rating", 
                  response_model=UserConversationFeedback, 
                  tags=["Feedback"])
async def update_feedback_rating(
    feedback_id: int,
    rating: int = Form(..., ge=1, le=5, description="Новая оценка от 1 до 5")
):
    """Обновить оценку в отзыве"""
    return user_conversation_feedback_services.update_feedback(feedback_id, {"Rating": rating})

@app_server.patch("/conversation-feedback/{feedback_id}/text", 
                  response_model=UserConversationFeedback, 
                  tags=["Feedback"])
async def update_feedback_text(
    feedback_id: int,
    feedback_text: str = Form(..., description="Новый текст отзыва")
):
    """Обновить текст отзыва"""
    return user_conversation_feedback_services.update_feedback(feedback_id, {"FeedbackText": feedback_text})

@app_server.delete("/conversation-feedback/{feedback_id}", 
                   response_model=Dict[str, str],
                   tags=["Feedback"])
async def delete_conversation_feedback(feedback_id: int):
    """Удалить запись обратной связи"""
    return user_conversation_feedback_services.delete_feedback(feedback_id)

# ------------------------------------------
# User Likes Endpoints
# ------------------------------------------

@app_server.post("/user-likes/", 
                 response_model=UserLikes, 
                 tags=["Preference"],
                 status_code=status.HTTP_201_CREATED)
async def create_user_like(
    from_user_id: int = Form(..., description="ID пользователя, который ставит лайк"),
    to_user_id: int = Form(..., description="ID пользователя, которому ставят лайк")
):
    """Создать новый лайк от одного пользователя к другому"""
    return user_likes_services.create_like(from_user_id, to_user_id)

@app_server.post("/user-likes/with-match-check", 
                 response_model=Dict[str, Any], 
                 tags=["Preference"],
                 status_code=status.HTTP_201_CREATED)
async def create_like_and_check_match(
    from_user_id: int = Form(..., description="ID пользователя, который ставит лайк"),
    to_user_id: int = Form(..., description="ID пользователя, которому ставят лайк")
):
    """Создать лайк и проверить возможность создания матча при взаимных лайках"""
    like = user_likes_services.create_like(from_user_id, to_user_id)
    match = user_likes_services.check_and_create_match(from_user_id, to_user_id)
    
    return {
        "like": like.dict(),
        "match_created": match is not None,
        "match": match.dict() if match else None,
        "message": "Матч создан!" if match else "Лайк поставлен, ждем взаимности"
    }

@app_server.get("/user-likes/", 
                response_model=List[UserLikes], 
                tags=["Preference"])
async def get_all_user_likes():
    """Получить все лайки между пользователями"""
    return user_likes_services.get_all_likes()

@app_server.get("/user-likes/{like_id}", 
                response_model=UserLikes, 
                tags=["Preference"])
async def get_user_like_by_id(like_id: int):
    """Получить лайк по ID"""
    return user_likes_services.get_like_by_id(like_id)

@app_server.get("/user-likes/check/{from_user_id}/{to_user_id}", 
                response_model=Dict[str, bool], 
                tags=["Preference"])
async def check_like_exists(from_user_id: int, to_user_id: int):
    """Проверить, существует ли лайк от одного пользователя к другому"""
    exists = user_likes_services.check_like_exists(from_user_id, to_user_id)
    return {
        "like_exists": exists,
        "from_user_id": from_user_id,
        "to_user_id": to_user_id
    }

@app_server.get("/user-likes/mutual/{user1_id}/{user2_id}", 
                response_model=Dict[str, bool], 
                tags=["Preference"])
async def check_mutual_likes(user1_id: int, user2_id: int):
    """Проверить наличие взаимных лайков между двумя пользователями"""
    mutual = user_likes_services.check_mutual_like(user1_id, user2_id)
    return {
        "mutual_likes": mutual,
        "user1_id": user1_id,
        "user2_id": user2_id
    }

@app_server.get("/users/{user_id}/likes/sent", 
                response_model=List[UserLikes], 
                tags=["Preference"])
async def get_likes_sent_by_user(user_id: int):
    """Получить все лайки, поставленные пользователем"""
    return user_likes_services.get_likes_from_user(user_id)

@app_server.get("/users/{user_id}/likes/received", 
                response_model=List[UserLikes], 
                tags=["Preference"])
async def get_likes_received_by_user(user_id: int):
    """Получить все лайки, полученные пользователем"""
    return user_likes_services.get_likes_to_user(user_id)

@app_server.get("/users/{user_id}/likes/mutual", 
                response_model=List[Dict[str, Any]], 
                tags=["Preference"])
async def get_user_mutual_likes(user_id: int):
    """Получить список пользователей с взаимными лайками"""
    return user_likes_services.get_mutual_likes(user_id)

@app_server.get("/users/{user_id}/likes/potential-matches", 
                response_model=List[Dict[str, Any]], 
                tags=["Preference"])
async def get_user_potential_matches(
    user_id: int,
    limit: int = Query(20, gt=0, le=100, description="Максимальное количество результатов")
):
    """Получить список потенциальных совпадений для пользователя"""
    return user_likes_services.get_potential_matches(user_id, limit)

@app_server.get("/users/{user_id}/likes/statistics", 
                response_model=Dict[str, Any], 
                tags=["Preference"])
async def get_user_likes_statistics(user_id: int):
    """Получить статистику лайков пользователя"""
    return user_likes_services.get_user_likes_stats(user_id)

@app_server.get("/users/{user_id}/likes/count/sent", 
                response_model=Dict[str, int], 
                tags=["Preference"])
async def count_likes_sent_by_user(user_id: int):
    """Подсчитать количество лайков, поставленных пользователем"""
    count = user_likes_services.count_likes_from_user(user_id)
    return {
        "user_id": user_id,
        "likes_sent": count
    }

@app_server.get("/users/{user_id}/likes/count/received", 
                response_model=Dict[str, int], 
                tags=["Preference"])
async def count_likes_received_by_user(user_id: int):
    """Подсчитать количество лайков, полученных пользователем"""
    count = user_likes_services.count_likes_to_user(user_id)
    return {
        "user_id": user_id,
        "likes_received": count
    }

@app_server.get("/user-likes/recent", 
                response_model=List[UserLikes], 
                tags=["Preference"])
async def get_recent_user_likes(
    hours: int = Query(24, gt=0, le=168, description="Количество часов для поиска недавних лайков")
):
    """Получить список недавних лайков за указанное количество часов"""
    return user_likes_services.get_recent_likes(hours)

@app_server.delete("/user-likes/{like_id}", 
                   response_model=Dict[str, str],
                   tags=["Preference"])
async def delete_user_like_by_id(like_id: int):
    """Удалить лайк по ID"""
    return user_likes_services.delete_like(like_id)

@app_server.delete("/user-likes/{from_user_id}/{to_user_id}", 
                   response_model=Dict[str, str],
                   tags=["Preference"])
async def delete_like_between_users(from_user_id: int, to_user_id: int):
    """Удалить лайк от одного пользователя к другому"""
    return user_likes_services.delete_user_like(from_user_id, to_user_id)

# ------------------------------------------
# User Preferences Endpoints
# ------------------------------------------

@app_server.post("/user-preferences/", 
                 response_model=UserPreferences, 
                 tags=["User Preferences"],
                 status_code=status.HTTP_201_CREATED)
async def create_user_preferences(
    user_id: int = Form(..., description="ID пользователя"),
    age_min: Optional[int] = Form(None, ge=18, le=100, description="Минимальный возраст"),
    age_max: Optional[int] = Form(None, ge=18, le=100, description="Максимальный возраст"),
    preferred_genders: Optional[str] = Form(None, description="Предпочитаемые полы через запятую"),
    preferred_distance: Optional[int] = Form(None, ge=0, description="Предпочитаемое расстояние в км"),
    other_preferences: Optional[str] = Form(None, description="Другие предпочтения")
):
    """Создать предпочтения пользователя"""
    # Преобразуем строку полов в список
    genders_list = None
    if preferred_genders:
        genders_list = [gender.strip() for gender in preferred_genders.split(',')]
    
    preferences = UserPreferences(
        user_id=user_id,
        age_min=age_min,
        age_max=age_max,
        preferred_genders=genders_list,  # Передаем как список
        preferred_distance=preferred_distance,
        other_preferences=other_preferences,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    return user_preferences_services.create_preferences(user_id, preferences)

@app_server.get("/user-preferences/{preference_id}", 
                response_model=UserPreferences, 
                tags=["Preference"])
async def get_preferences_by_id(preference_id: int):
    """Получить предпочтения по ID записи"""
    return user_preferences_services.get_preferences_by_id(preference_id)

@app_server.get("/users/{user_id}/preferences", 
                response_model=UserPreferences, 
                tags=["Preference"])
async def get_user_preferences(user_id: int):
    """Получить предпочтения пользователя по ID пользователя"""
    return user_preferences_services.get_preferences_by_user(user_id)

@app_server.get("/users/{user_id}/compatible-users", 
                response_model=List[Dict[str, Any]], 
                tags=["Preference"])
async def find_compatible_users_for_user(
    user_id: int,
    max_distance: int = Query(50, ge=1, le=1000, description="Максимальное расстояние поиска в км")
):
    """Найти совместимых пользователей на основе предпочтений"""
    return user_preferences_services.find_compatible_users(user_id, max_distance)

@app_server.get("/users/{user_id1}/common-preferences/{user_id2}", 
                response_model=Dict[str, Any], 
                tags=["Preference"])
async def get_common_preferences_between_users(user_id1: int, user_id2: int):
    """Получить общие предпочтения между двумя пользователями"""
    return user_preferences_services.get_common_preferences(user_id1, user_id2)

@app_server.put("/users/{user_id}/preferences", 
                response_model=UserPreferences, 
                tags=["Preference"])
async def update_user_preferences(
    user_id: int,
    age_min: Optional[int] = Form(None, ge=18, le=100, description="Минимальный возраст"),
    age_max: Optional[int] = Form(None, ge=18, le=100, description="Максимальный возраст"),
    preferred_genders: Optional[str] = Form(None, description="Предпочитаемые полы через запятую"),
    preferred_distance: Optional[int] = Form(None, ge=0, description="Предпочитаемое расстояние в км"),
    other_preferences: Optional[str] = Form(None, description="Другие предпочтения в формате JSON")
):
    """Обновить предпочтения пользователя (создает новые, если не существуют)"""
    updates = {}
    
    if age_min is not None:
        updates['AgeMin'] = age_min
    if age_max is not None:
        updates['AgeMax'] = age_max
    if preferred_genders is not None:
        updates['PreferredGenders'] = [gender.strip() for gender in preferred_genders.split(',') if gender.strip()]
    if preferred_distance is not None:
        updates['PreferredDistance'] = preferred_distance
    if other_preferences is not None:
        try:
            updates['OtherPreferences'] = json.loads(other_preferences)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат JSON для других предпочтений"
            )
    
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать хотя бы одно поле для обновления"
        )
    
    return user_preferences_services.update_preferences(user_id, updates)

@app_server.patch("/users/{user_id}/preferences/age-range", 
                  response_model=UserPreferences, 
                  tags=["Preference"])
async def update_age_preferences(
    user_id: int,
    age_min: int = Form(..., ge=18, le=100, description="Минимальный возраст"),
    age_max: int = Form(..., ge=18, le=100, description="Максимальный возраст")
):
    """Обновить возрастные предпочтения пользователя"""
    if age_min > age_max:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Минимальный возраст не может быть больше максимального"
        )
    
    return user_preferences_services.update_preferences(user_id, {
        'AgeMin': age_min,
        'AgeMax': age_max
    })

@app_server.patch("/users/{user_id}/preferences/genders", 
                  response_model=UserPreferences, 
                  tags=["Preference"])
async def update_gender_preferences(
    user_id: int,
    preferred_genders: str = Form(..., description="Предпочитаемые полы через запятую")
):
    """Обновить предпочтения по полу"""
    genders_list = [gender.strip() for gender in preferred_genders.split(',') if gender.strip()]
    if not genders_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать хотя бы один предпочитаемый пол"
        )
    
    return user_preferences_services.update_preferences(user_id, {
        'PreferredGenders': genders_list
    })

@app_server.patch("/users/{user_id}/preferences/distance", 
                  response_model=UserPreferences, 
                  tags=["Preference"])
async def update_distance_preferences(
    user_id: int,
    preferred_distance: int = Form(..., ge=0, description="Предпочитаемое расстояние в км")
):
    """Обновить предпочтения по расстоянию"""
    return user_preferences_services.update_preferences(user_id, {
        'PreferredDistance': preferred_distance
    })

@app_server.patch("/users/{user_id}/preferences/other", 
                  response_model=UserPreferences, 
                  tags=["Preference"])
async def update_other_preferences(
    user_id: int,
    other_preferences: str = Form(..., description="Другие предпочтения в формате JSON")
):
    """Обновить другие предпочтения пользователя"""
    try:
        preferences_dict = json.loads(other_preferences)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат JSON для других предпочтений"
        )
    
    return user_preferences_services.update_preferences(user_id, {
        'OtherPreferences': preferences_dict
    })

@app_server.delete("/users/{user_id}/preferences", 
                   response_model=Dict[str, str],
                   tags=["Preference"])
async def delete_user_preferences(user_id: int):
    """Удалить предпочтения пользователя"""
    return user_preferences_services.delete_preferences(user_id)

# ------------------------------------------
# User Endpoints
# ------------------------------------------

@app_server.post("/users/", 
                 response_model=Users, 
                 tags=["User"],
                 status_code=status.HTTP_201_CREATED)
async def create_new_user(
    email: str = Form(..., description="Email пользователя"),
    password: str = Form(..., min_length=6, description="Пароль (минимум 6 символов)"),
    first_name: str = Form(..., min_length=1, description="Имя пользователя")
):
    """Создать нового пользователя"""
    return user_services.create_user(email, password, first_name)

@app_server.post("/users/authenticate", 
                 response_model=Optional[Users], 
                 tags=["User"])
async def authenticate_user(
    email: str = Form(..., description="Email пользователя"),
    password: str = Form(..., description="Пароль пользователя")
):
    """Аутентификация пользователя по email и паролю"""
    user = user_services.authenticate_user(email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )
    return user

@app_server.get("/users/", 
                response_model=List[Users], 
                tags=["User"])
async def get_all_users():
    """Получить всех пользователей"""
    return user_services.get_all_users()

@app_server.get("/users/{user_id}", 
                response_model=Users, 
                tags=["User"])
async def get_user_by_id(user_id: int):
    """Получить пользователя по ID"""
    return user_services.get_user_by_id(user_id)

@app_server.get("/users/email/{email}", 
                response_model=Optional[Users], 
                tags=["User"])
async def get_user_by_email(email: str):
    """Получить пользователя по email"""
    user = user_services.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с email {email} не найден"
        )
    return user

@app_server.get("/users/activity/period", 
                response_model=List[Users], 
                tags=["User"])
async def get_users_by_activity_period(
    start_date: str = Query(..., description="Начальная дата в формате YYYY-MM-DD HH:MM:SS"),
    end_date: str = Query(..., description="Конечная дата в формате YYYY-MM-DD HH:MM:SS")
):
    """Получить пользователей по периоду активности"""
    try:
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат даты. Используйте YYYY-MM-DD HH:MM:SS"
        )
    
    if start_datetime >= end_datetime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Начальная дата должна быть раньше конечной"
        )
    
    return user_services.get_users_by_activity_period(start_datetime, end_datetime)

@app_server.get("/users/statistics/active-count", 
                response_model=Dict[str, int], 
                tags=["User"])
async def get_active_users_count():
    """Получить количество активных пользователей"""
    count = user_services.get_active_users_count()
    return {
        "active_users_count": count,
        "timestamp": datetime.now().isoformat()
    }

@app_server.put("/users/{user_id}", 
                response_model=Users, 
                tags=["User"])
async def update_user_data(
    user_id: int,
    updates: Dict[str, Any] = Body(...)
):
    """Обновить данные пользователя"""
    return user_services.update_user(user_id, updates)

@app_server.patch("/users/{user_id}/email", 
                  response_model=Users, 
                  tags=["User"])
async def update_user_email(
    user_id: int,
    email: str = Form(..., description="Новый email пользователя")
):
    """Обновить email пользователя"""
    # Проверяем, что email не занят другим пользователем
    existing_user = user_services.get_user_by_email(email)
    if existing_user and existing_user.ID != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    return user_services.update_user(user_id, {"email": email})

@app_server.patch("/users/{user_id}/password", 
                  response_model=Users, 
                  tags=["User"])
async def update_user_password(
    user_id: int,
    password: str = Form(..., min_length=6, description="Новый пароль (минимум 6 символов)")
):
    """Обновить пароль пользователя"""
    return user_services.update_user(user_id, {"password": password})

@app_server.patch("/users/{user_id}/name", 
                  response_model=Users, 
                  tags=["User"])
async def update_user_name(
    user_id: int,
    first_name: str = Form(..., min_length=1, description="Новое имя пользователя")
):
    """Обновить имя пользователя"""
    return user_services.update_user(user_id, {"first_name": first_name})

@app_server.patch("/users/{user_id}/activity", 
                  response_model=Users, 
                  tags=["User"])
async def update_user_activity(user_id: int):
    """Обновить время последней активности пользователя (текущее время)"""
    return user_services.update_user_activity(user_id)

@app_server.delete("/users/{user_id}", 
                   response_model=Dict[str, str],
                   tags=["User"])
async def delete_user_account(user_id: int):
    """Удалить аккаунт пользователя"""
    return user_services.delete_user(user_id)

@app_server.get("/users/check/email-exists/{email}", 
                response_model=Dict[str, bool], 
                tags=["User"])
async def check_email_exists(email: str):
    """Проверить, существует ли пользователь с указанным email"""
    user = user_services.get_user_by_email(email)
    return {
        "email": email,
        "exists": user is not None
    }

# ------------------------------------------
# User Sessions Endpoints
# ------------------------------------------

@app_server.post("/user-sessions/", 
                 response_model=UserSessions, 
                 tags=["Session"],
                 status_code=status.HTTP_201_CREATED)
async def create_user_session(
    user_id: int = Form(..., description="ID пользователя"),
    fingerprint_hash: str = Form(..., description="Хэш отпечатка браузера"),
    jwt_token_hash: str = Form(..., description="Хэш JWT токена"),
    expires_at: str = Form(..., description="Время истечения в формате YYYY-MM-DD HH:MM:SS"),
    ip_address: Optional[str] = Form(None, description="IP-адрес пользователя")
):
    """Создать новую пользовательскую сессию"""
    try:
        expires_datetime = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат времени истечения. Используйте YYYY-MM-DD HH:MM:SS"
        )
    
    if expires_datetime <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Время истечения должно быть в будущем"
        )
    
    return user_sessions_services.create_session(
        user_id=user_id,
        fingerprint_hash=fingerprint_hash,
        jwt_token_hash=jwt_token_hash,
        expires_at=expires_datetime,
        ip_address=ip_address
    )

@app_server.get("/user-sessions/", 
                response_model=List[UserSessions], 
                tags=["Session"])
async def get_all_user_sessions():
    """Получить все пользовательские сессии"""
    return user_sessions_services.get_all_sessions()

@app_server.get("/user-sessions/{session_id}", 
                response_model=UserSessions, 
                tags=["Session"])
async def get_user_session_by_id(session_id: int):
    """Получить сессию по ID"""
    return user_sessions_services.get_session_by_id(session_id)

@app_server.get("/user-sessions/token/{token_hash}", 
                response_model=Optional[UserSessions], 
                tags=["Session"])
async def get_session_by_token_hash(token_hash: str):
    """Получить сессию по хэшу токена"""
    session = user_sessions_services.get_session_by_token_hash(token_hash)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сессия с указанным токеном не найдена"
        )
    return session

@app_server.get("/users/{user_id}/sessions", 
                response_model=List[UserSessions], 
                tags=["Session"])
async def get_all_user_sessions_by_user_id(user_id: int):
    """Получить все сессии пользователя"""
    return user_sessions_services.get_sessions_by_user(user_id)

@app_server.get("/users/{user_id}/sessions/active", 
                response_model=List[UserSessions], 
                tags=["Session"])
async def get_active_user_sessions(user_id: int):
    """Получить активные сессии пользователя"""
    return user_sessions_services.get_active_sessions_by_user(user_id)

@app_server.get("/user-sessions/ip/{ip_address}", 
                response_model=List[UserSessions], 
                tags=["Session"])
async def get_sessions_by_ip_address(ip_address: str):
    """Получить сессии по IP-адресу"""
    return user_sessions_services.get_sessions_by_ip(ip_address)

@app_server.get("/user-sessions/validate/{token_hash}", 
                response_model=Dict[str, Any], 
                tags=["Session"])
async def validate_user_session(token_hash: str):
    """Проверить валидность сессии по токену"""
    is_valid = user_sessions_services.validate_session(token_hash)
    return {
        "token_hash": token_hash,
        "is_valid": is_valid,
        "checked_at": datetime.now().isoformat()
    }

@app_server.put("/user-sessions/{session_id}", 
                response_model=UserSessions, 
                tags=["Session"])
async def update_user_session(
    session_id: int,
    updates: Dict[str, Any] = Body(...)
):
    """Обновить данные сессии"""
    return user_sessions_services.update_session(session_id, updates)

@app_server.patch("/user-sessions/{session_id}/extend", 
                  response_model=UserSessions, 
                  tags=["Session"])
async def extend_user_session(
    session_id: int,
    days: int = Form(30, gt=0, le=365, description="Количество дней для продления")
):
    """Продлить срок действия сессии"""
    return user_sessions_services.extend_session(session_id, days)

@app_server.patch("/user-sessions/{session_id}/deactivate", 
                  response_model=UserSessions, 
                  tags=["Session"])
async def deactivate_user_session(session_id: int):
    """Деактивировать конкретную сессию"""
    return user_sessions_services.deactivate_session(session_id)

@app_server.patch("/users/{user_id}/sessions/deactivate-all", 
                  response_model=Dict[str, int], 
                  tags=["Session"])
async def deactivate_all_user_sessions(user_id: int):
    """Деактивировать все сессии пользователя"""
    return user_sessions_services.deactivate_user_sessions(user_id)

@app_server.delete("/user-sessions/{session_id}", 
                   response_model=Dict[str, str],
                   tags=["Session"])
async def delete_user_session(session_id: int):
    """Удалить сессию по ID"""
    return user_sessions_services.delete_session(session_id)

@app_server.post("/user-sessions/cleanup-expired", 
                 response_model=Dict[str, int], 
                 tags=["Session"])
async def cleanup_expired_user_sessions():
    """Очистить истекшие сессии"""
    return user_sessions_services.cleanup_expired_sessions()





# ------------------------------------------
# Server Startup
# ------------------------------------------

def run_server():
    import uvicorn
    import yaml
    from src import path_to_logging
    
    uvicorn_log_config = path_to_logging()
    reload = env.__getattr__("DEBUG") == "TRUE"
    
    uvicorn.run(
        "src.pipeline.server:app", 
        host=env.__getattr__("SERVER_HOST"), 
        port=int(env.__getattr__("SERVER_PORT")),
        log_config=uvicorn_log_config, 
        reload=reload
    )

if __name__ == "__main__":
    log.info("Starting server")
    run_server()