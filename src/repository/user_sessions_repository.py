from typing import Optional, Dict, Any, List
from datetime import datetime
from src.database.my_connector import db
from src.database.models import UserSessions


def get_all_sessions() -> List[Dict[str, Any]]:
    query = "SELECT * FROM user_sessions"
    return db.fetch_all(query)

def get_session_by_id(session_id: int) -> Optional[Dict[str, Any]]:
    query = "SELECT * FROM user_sessions WHERE id = %s"
    return db.fetch_one(query, (session_id,))

def get_session_by_token_hash(token_hash: str) -> Optional[Dict[str, Any]]:
    query = "SELECT * FROM user_sessions WHERE jwt_token_hash = %s"
    return db.fetch_one(query, (token_hash,))

def get_active_sessions_by_user(user_id: int) -> List[Dict[str, Any]]:
    query = "SELECT * FROM user_sessions WHERE user_id = %s AND is_active = TRUE AND expires_at > NOW()"
    return db.fetch_all(query, (user_id,))

def get_sessions_by_user(user_id: int) -> List[Dict[str, Any]]:
    query = "SELECT * FROM user_sessions WHERE user_id = %s ORDER BY created_at DESC"
    return db.fetch_all(query, (user_id,))

def get_sessions_by_fingerprint(fingerprint_hash: str) -> List[Dict[str, Any]]:
    """Получить сессии по отпечатку браузера"""
    query = """
        SELECT * FROM user_sessions 
        WHERE fingerprint_hash = %s 
        AND is_active = 1 
        ORDER BY created_at DESC
    """
    return db.fetch_all(query, (fingerprint_hash,))

def create_session(session: UserSessions) -> int:
    query = """
        INSERT INTO user_sessions (user_id, jwt_token_hash, fingerprint_hash, expires_at, ip_address, is_active)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (
        session.UserID,
        session.JwtTokenHash,
        session.FingerprintHash,  # Новое поле
        session.ExpiresAt,
        session.IPAddress,
        session.IsActive
    )
    cursor = db.execute_query(query, params)
    return cursor.lastrowid

def update_session(session_id: int, updates: Dict[str, Any]) -> None:
    set_clauses = []
    params = []

    field_mapping = {
        "jwt_token_hash": "JwtTokenHash",
        "fingerprint_hash": "FingerprintHash",  # Новое поле
        "expires_at": "ExpiresAt",
        "ip_address": "IPAddress",
        "is_active": "IsActive"
    }

    for db_field, value in updates.items():
        if db_field in field_mapping and value is not None:
            set_clauses.append(f"{db_field} = %s")
            params.append(value)

    if not set_clauses:
        return

    params.append(session_id)
    query = f"UPDATE user_sessions SET {', '.join(set_clauses)} WHERE id = %s"
    db.execute_query(query, params)

def deactivate_session(session_id: int) -> None:
    query = "UPDATE user_sessions SET is_active = 0 WHERE id = %s"
    db.execute_query(query, (session_id,))

def deactivate_user_sessions(user_id: int) -> None:
    query = "UPDATE user_sessions SET is_active = 0 WHERE user_id = %s"
    db.execute_query(query, (user_id,))

def delete_session(session_id: int) -> None:
    query = "DELETE FROM user_sessions WHERE id = %s"
    db.execute_query(query, (session_id,))

def delete_expired_sessions() -> int:
    query = "DELETE FROM user_sessions WHERE expires_at < NOW()"
    cursor = db.execute_query(query)
    return cursor.rowcount

def get_sessions_by_ip(ip_address: str) -> List[Dict[str, Any]]:
    query = "SELECT * FROM user_sessions WHERE ip_address = %s ORDER BY created_at DESC"
    return db.fetch_all(query, (ip_address,))

def count_active_sessions_by_user(user_id: int) -> int:
    query = "SELECT COUNT(*) as count FROM user_sessions WHERE user_id = %s AND is_active = 1 AND expires_at > NOW()"
    result = db.fetch_one(query, (user_id,))
    return result["count"] if result else 0