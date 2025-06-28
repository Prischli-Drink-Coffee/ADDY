from typing import Optional, Dict, Any
from datetime import datetime
from src.database.my_connector import db
from src.database.models import Users


def get_all_users() -> list[Dict[str, Any]]:
    query = "SELECT * FROM users"
    return db.fetch_all(query)

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    query = "SELECT * FROM users WHERE id = %s"
    return db.fetch_one(query, (user_id,))

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    query = "SELECT * FROM users WHERE email = %s"
    return db.fetch_one(query, (email,))

def create_user(user: Users) -> int:
    query = """
        INSERT INTO users (email, password, first_name, last_activity)
        VALUES (%s, %s, %s, %s)
    """
    params = (
        user.Email,
        user.Password,
        user.FirstName,
        user.LastActivity
    )
    cursor = db.execute_query(query, params)
    return cursor.lastrowid

def update_user(user_id: int, updates: Dict[str, Any]) -> None:
    set_clauses = []
    params = []

    field_mapping = {
        "email": "Email",
        "password": "Password",
        "first_name": "FirstName",
        "last_activity": "LastActivity"
    }

    for db_field, value in updates.items():
        if db_field in field_mapping and value is not None:
            set_clauses.append(f"{db_field} = %s")
            params.append(value)

    if not set_clauses:
        return

    params.append(user_id)
    query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = %s"
    db.execute_query(query, params)

def update_user_activity(user_id: int, last_activity: datetime) -> None:
    query = "UPDATE users SET last_activity = %s WHERE id = %s"
    db.execute_query(query, (last_activity, user_id))

def delete_user(user_id: int) -> None:
    query = "DELETE FROM users WHERE id = %s"
    db.execute_query(query, (user_id,))

def get_users_by_activity_period(start_date: datetime, end_date: datetime) -> list[Dict[str, Any]]:
    query = "SELECT * FROM users WHERE last_activity BETWEEN %s AND %s ORDER BY last_activity DESC"
    return db.fetch_all(query, (start_date, end_date))

def get_active_users_count() -> int:
    query = "SELECT COUNT(*) as count FROM users WHERE last_activity >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
    result = db.fetch_one(query)
    return result["count"] if result else 0