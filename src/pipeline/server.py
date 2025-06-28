import os
import asyncio
import json
from fastapi import (FastAPI, HTTPException, Depends, Request, File, UploadFile,
                     status, Form, Query, WebSocket, WebSocketDisconnect, Response)
from typing import Dict, List, Any, Optional
from enum import Enum
from fastapi.openapi.models import Tag as OpenApiTag
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from src.utils.custom_logging import get_logger
from src.utils.env import Env
from src import path_to_project
from datetime import datetime, timedelta
from decimal import Decimal
from src.services.cookie_services import session_manager
from pathlib import Path
import asyncio
import signal
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

# Helper function to get current user
def get_current_user(request: Request) -> Dict[str, Any]:
    return session_manager.get_current_user_from_request(request)

# ------------------------------------------
# Session Management Endpoints
# ------------------------------------------

@app_server.post("/auth/session/create", response_model=Dict[str, Any], tags=["Cookie"])
async def create_or_get_session(request: Request, response: Response):
    return session_manager.create_or_get_user_session(request, response)

@app_server.get("/auth/session/current", response_model=Dict[str, Any], tags=["Cookie"])
async def get_current_session(request: Request):
    return session_manager.get_current_user_from_request(request)

@app_server.post("/auth/session/logout", response_model=Dict[str, str], tags=["Cookie"])
async def logout_session(request: Request, response: Response):
    return session_manager.logout_user(request, response)

@app_server.get("/auth/session/validate", response_model=bool, tags=["Cookie"])
async def validate_session(request: Request):
    try:
        session_manager.get_current_user_from_request(request)
        return True
    except HTTPException:
        return False

@app_server.post("/auth/session/refresh", response_model=Dict[str, Any], tags=["Cookie"])
async def refresh_session(request: Request, response: Response):
    current_session = session_manager.get_current_user_from_request(request)
    return session_manager.create_or_get_user_session(request, response)

@app_server.get("/auth/session/info", response_model=Dict[str, Any], tags=["Cookie"])
async def get_session_info(request: Request):
    current_user = session_manager.get_current_user_from_request(request)
    session = user_sessions_services.get_session_by_id(current_user["session_id"])
    user = user_services.get_user_by_id(current_user["user_id"])
    
    return {
        "session_info": {
            "id": session.id,
            "created_at": session.CreatedAt,
            "expires_at": session.ExpiresAt,
            "ip_address": session.IPAddress,
            "user_agent": session.UserAgent,
            "is_active": session.IsActive
        },
        "user_info": {
            "id": user.ID,
            "email": user.Email,
            "first_name": user.FirstName,
            "last_activity": user.LastActivity
        }
    }

# ------------------------------------------
# User Management Endpoints
# ------------------------------------------

@app_server.get("/users/", response_model=List[Users], tags=["User"])
async def get_all_users():
    return user_services.get_all_users()

@app_server.get("/users/{user_id}", response_model=Users, tags=["User"])
async def get_user_by_id(user_id: int):
    return user_services.get_user_by_id(user_id)

@app_server.post("/users/", response_model=Users, tags=["User"])
async def create_user(
    email: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(...)
):
    return user_services.create_user(email, password, first_name)

@app_server.patch("/users/{user_id}", response_model=Users, tags=["User"])
async def update_user(
    user_id: int, 
    email: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    first_name: Optional[str] = Form(None)
):
    updates = {}
    if email: updates["email"] = email
    if password: updates["password"] = password
    if first_name: updates["first_name"] = first_name
    
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    return user_services.update_user(user_id, updates)

@app_server.patch("/users/{user_id}/activity", response_model=Users, tags=["User"])
async def update_user_activity(user_id: int):
    return user_services.update_user_activity(user_id)

@app_server.delete("/users/{user_id}", response_model=Dict[str, str], tags=["User"])
async def delete_user(user_id: int):
    return user_services.delete_user(user_id)

@app_server.post("/users/authenticate", response_model=Users, tags=["User"])
async def authenticate_user(email: str = Form(...), password: str = Form(...)):
    user = user_services.authenticate_user(email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return user

@app_server.get("/users/active/count", response_model=int, tags=["User"])
async def get_active_users_count():
    return user_services.get_active_users_count()

# ------------------------------------------
# Profile Management Endpoints
# ------------------------------------------

@app_server.get("/profiles/{user_id}", response_model=ProfileDetails, tags=["Profile"])
async def get_profile_by_user_id(user_id: int):
    return profile_details_services.get_profile_by_user_id(user_id)

@app_server.post("/profiles/", response_model=ProfileDetails, tags=["Profile"])
async def create_profile(
    user_id: int = Form(...),
    age: Optional[int] = Form(None),
    gender: Optional[str] = Form(None),
    interests: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    location: Optional[str] = Form(None)
):
    profile_data = {
        "user_id": user_id,
        "age": age,
        "gender": gender,
        "interests": interests,
        "bio": bio,
        "location": location
    }
    return profile_details_services.create_profile(profile_data)

@app_server.patch("/profiles/{profile_id}", response_model=ProfileDetails, tags=["Profile"])
async def update_profile(
    profile_id: int,
    age: Optional[int] = Form(None),
    gender: Optional[str] = Form(None),
    interests: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    location: Optional[str] = Form(None)
):
    updates = {}
    if age: updates["age"] = age
    if gender: updates["gender"] = gender
    if interests: updates["interests"] = interests
    if bio: updates["bio"] = bio
    if location: updates["location"] = location
    
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    return profile_details_services.update_profile(profile_id, updates)

# ------------------------------------------
# Match Management Endpoints
# ------------------------------------------

@app_server.post("/matches/", response_model=Matches, tags=["Match"])
async def create_match(
    user1_id: int = Form(...),
    user2_id: int = Form(...),
    status: MatchStatusEnum = Form(MatchStatusEnum.active)
):
    return matches_services.create_match(user1_id, user2_id, status)

@app_server.get("/matches/{match_id}", response_model=Matches, tags=["Match"])
async def get_match_by_id(match_id: int):
    return matches_services.get_match_by_id(match_id)

@app_server.patch("/matches/{match_id}", response_model=Matches, tags=["Match"])
async def update_match_status(
    match_id: int, 
    status: MatchStatusEnum = Form(...)
):
    return matches_services.update_match_status(match_id, status)

@app_server.get("/users/{user_id}/matches", response_model=List[Matches], tags=["Match"])
async def get_user_matches(user_id: int):
    return matches_services.get_matches_by_user(user_id)

# ------------------------------------------
# Chat Management Endpoints
# ------------------------------------------

@app_server.post("/conversations/", response_model=ChatConversations, tags=["Chat"])
async def create_conversation(match_id: int = Form(...)):
    return chat_conversations_services.create_conversation(match_id)

@app_server.get("/conversations/{conversation_id}", response_model=ChatConversations, tags=["Chat"])
async def get_conversation_by_id(conversation_id: int):
    return chat_conversations_services.get_conversation_by_id(conversation_id)

@app_server.get("/conversations/match/{match_id}", response_model=ChatConversations, tags=["Chat"])
async def get_conversation_by_match_id(match_id: int):
    return chat_conversations_services.get_conversation_by_match_id(match_id)

@app_server.post("/messages/", response_model=ChatMessages, tags=["Chat"])
async def create_message(
    conversation_id: int = Form(...),
    sender_id: int = Form(...),
    message_text: str = Form(...),
    message_type: MessageTypeEnum = Form(MessageTypeEnum.user)
):
    return chat_messages_services.create_message(
        conversation_id, sender_id, message_text, message_type
    )

@app_server.get("/conversations/{conversation_id}/messages", response_model=List[ChatMessages], tags=["Chat"])
async def get_conversation_messages(conversation_id: int):
    return chat_messages_services.get_messages_by_conversation(conversation_id)

# ------------------------------------------
# Agent Management Endpoints
# ------------------------------------------

@app_server.post("/agents/", response_model=UserAgents, tags=["Agent"])
async def create_agent(
    user_id: int = Form(...),
    personality_data: str = Form(...),
    status: LearningStatusEnum = Form(LearningStatusEnum.learning)
):
    # Parse JSON personality data
    try:
        personality_json = json.loads(personality_data)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON for personality data"
        )
    
    return user_agents_services.create_agent(user_id, personality_json, status)

@app_server.get("/agents/{agent_id}", response_model=UserAgents, tags=["Agent"])
async def get_agent_by_id(agent_id: int):
    return user_agents_services.get_agent_by_id(agent_id)

@app_server.get("/users/{user_id}/agents", response_model=List[UserAgents], tags=["Agent"])
async def get_user_agents(user_id: int):
    return user_agents_services.get_agents_by_user(user_id)

@app_server.patch("/agents/{agent_id}", response_model=UserAgents, tags=["Agent"])
async def update_agent(
    agent_id: int,
    personality_data: Optional[str] = Form(None),
    status: Optional[LearningStatusEnum] = Form(None)
):
    updates = {}
    if personality_data:
        try:
            updates["personality_data"] = json.loads(personality_data)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON for personality data"
            )
    if status: updates["status"] = status
    
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    return user_agents_services.update_agent(agent_id, updates)

# ------------------------------------------
# Simulation Management Endpoints
# ------------------------------------------

@app_server.post("/simulations/", response_model=AgentSimulations, tags=["Simulation"])
async def create_simulation(
    agent1_id: int = Form(...),
    agent2_id: int = Form(...),
    conversation_id: int = Form(...),
    status: SimulationStatusEnum = Form(SimulationStatusEnum.pending)
):
    return agents_simulations_services.create_simulation(
        agent1_id, agent2_id, conversation_id, status
    )

@app_server.get("/simulations/{simulation_id}", response_model=AgentSimulations, tags=["Simulation"])
async def get_simulation_by_id(simulation_id: int):
    return agents_simulations_services.get_simulation_by_id(simulation_id)

@app_server.post("/simulations/{simulation_id}/messages", response_model=AgentSimulationMessages, tags=["Simulation"])
async def create_simulation_message(
    simulation_id: int = Form(...),
    sender_agent_id: int = Form(...),
    message_text: str = Form(...)
):
    return agent_simulation_messages_services.create_simulation_message(
        simulation_id, sender_agent_id, message_text
    )

@app_server.get("/simulations/{simulation_id}/messages", response_model=List[AgentSimulationMessages], tags=["Simulation"])
async def get_simulation_messages(simulation_id: int):
    return agent_simulation_messages_services.get_messages_by_simulation(simulation_id)

@app_server.patch("/simulations/{simulation_id}/complete", response_model=AgentSimulations, tags=["Simulation"])
async def complete_simulation(
    simulation_id: int,
    compatibility_score: float = Form(...),
    summary: str = Form(...)
):
    return agents_simulations_services.complete_simulation(
        simulation_id, compatibility_score, summary
    )

# ------------------------------------------
# Feedback Management Endpoints
# ------------------------------------------

@app_server.post("/feedback/simulation/", response_model=AgentSimulationFeedback, tags=["Feedback"])
async def create_simulation_feedback(
    simulation_id: int = Form(...),
    user_id: int = Form(...),
    accuracy_rating: int = Form(...),
    usefulness_rating: int = Form(...),
    feedback_text: Optional[str] = Form(None)
):
    return agent_simulation_feedback_services.create_feedback({
        "simulation_id": simulation_id,
        "user_id": user_id,
        "accuracy_rating": accuracy_rating,
        "usefulness_rating": usefulness_rating,
        "feedback_text": feedback_text
    })

@app_server.post("/feedback/conversation/", response_model=UserConversationFeedback, tags=["Feedback"])
async def create_conversation_feedback(
    conversation_id: int = Form(...),
    user_id: int = Form(...),
    rating: int = Form(...),
    feedback_text: Optional[str] = Form(None)
):
    return user_conversation_feedback_services.create_feedback({
        "conversation_id": conversation_id,
        "user_id": user_id,
        "rating": rating,
        "feedback_text": feedback_text
    })

# ------------------------------------------
# Preference Management Endpoints
# ------------------------------------------

@app_server.post("/preferences/", response_model=UserPreferences, tags=["Preference"])
async def create_preferences(
    user_id: int = Form(...),
    age_min: Optional[int] = Form(None),
    age_max: Optional[int] = Form(None),
    preferred_genders: Optional[str] = Form(None),
    preferred_distance: Optional[int] = Form(None),
    other_preferences: Optional[str] = Form(None)
):
    # Parse JSON preferences
    try:
        genders_json = json.loads(preferred_genders) if preferred_genders else None
        other_json = json.loads(other_preferences) if other_preferences else None
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON for preferences"
        )
    
    return user_preferences_services.create_preferences(
        user_id, age_min, age_max, genders_json, preferred_distance, other_json
    )

@app_server.get("/preferences/{user_id}", response_model=UserPreferences, tags=["Preference"])
async def get_preferences_by_user(user_id: int):
    return user_preferences_services.get_preferences_by_user(user_id)

@app_server.patch("/preferences/{preference_id}", response_model=UserPreferences, tags=["Preference"])
async def update_preferences(
    preference_id: int,
    age_min: Optional[int] = Form(None),
    age_max: Optional[int] = Form(None),
    preferred_genders: Optional[str] = Form(None),
    preferred_distance: Optional[int] = Form(None),
    other_preferences: Optional[str] = Form(None)
):
    updates = {}
    if age_min: updates["age_min"] = age_min
    if age_max: updates["age_max"] = age_max
    if preferred_genders:
        try:
            updates["preferred_genders"] = json.loads(preferred_genders)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON for preferred genders"
            )
    if preferred_distance: updates["preferred_distance"] = preferred_distance
    if other_preferences:
        try:
            updates["other_preferences"] = json.loads(other_preferences)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON for other preferences"
            )
    
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    return user_preferences_services.update_preferences(preference_id, updates)

# ------------------------------------------
# Like Management Endpoints
# ------------------------------------------

@app_server.post("/likes/", response_model=UserLikes, tags=["Match"])
async def create_like(
    from_user_id: int = Form(...),
    to_user_id: int = Form(...)
):
    return user_likes_services.create_like(from_user_id, to_user_id)

@app_server.get("/users/{user_id}/likes/received", response_model=List[UserLikes], tags=["Match"])
async def get_received_likes(user_id: int):
    return user_likes_services.get_likes_by_to_user(user_id)

@app_server.get("/users/{user_id}/likes/sent", response_model=List[UserLikes], tags=["Match"])
async def get_sent_likes(user_id: int):
    return user_likes_services.get_likes_by_from_user(user_id)

# ------------------------------------------
# Agent Learning Data Endpoints
# ------------------------------------------

@app_server.post("/agent-learning-data/", response_model=AgentLearningData, tags=["Agent"])
async def create_learning_data(
    agent_id: int = Form(...),
    data_type: DataTypeEnum = Form(...),
    data_content: str = Form(...)
):
    try:
        content_json = json.loads(data_content)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON for data content"
        )
    
    return agent_learning_data_services.create_learning_data({
        "agent_id": agent_id,
        "data_type": data_type,
        "data_content": content_json
    })

@app_server.get("/agents/{agent_id}/learning-data", response_model=List[AgentLearningData], tags=["Agent"])
async def get_agent_learning_data(agent_id: int):
    return agent_learning_data_services.get_learning_data_by_agent(agent_id)

# ------------------------------------------
# Websocket for Real-time Chat
# ------------------------------------------

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

manager = ConnectionManager()

@app_server.websocket("/chat/{conversation_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: int, user_id: int):
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Save message to database
            message = chat_messages_services.create_message(
                conversation_id, user_id, data, MessageTypeEnum.user
            )
            
            # Notify other participant
            conversation = chat_conversations_services.get_conversation_by_id(conversation_id)
            match = matches_services.get_match_by_id(conversation.MatchID)
            other_user_id = match.User1ID if user_id == match.User2ID else match.User2ID
            
            await manager.send_personal_message(
                json.dumps({
                    "sender_id": user_id,
                    "message": data,
                    "timestamp": datetime.now().isoformat()
                }), 
                other_user_id
            )
    except WebSocketDisconnect:
        manager.disconnect(user_id)

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
        host=env.__getattr__("HOST"), 
        port=int(env.__getattr__("SERVER_PORT")),
        log_config=uvicorn_log_config, 
        reload=reload
    )

if __name__ == "__main__":
    log.info("Starting server")
    run_server()