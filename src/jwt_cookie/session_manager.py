import hashlib
from fastapi import Request, HTTPException, status, Response
import jwt
from dataclasses import dataclass
from src.jwt_cookie.settings import Settings
from src.utils.custom_logging import get_logger
from src.services import user_sessions_services, user_services
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

log = get_logger(__name__)


@dataclass(frozen=True)
class TokenPayload:
    user_id: int
    fingerprint_hash: str
    session_id: int
    token_type: str = "user_session"

    def to_jwt_dict(self, expiration_delta: timedelta) -> Dict[str, Any]:
        now = datetime.utcnow()
        return {
            "user_id": self.user_id,
            "fingerprint_hash": self.fingerprint_hash,
            "session_id": self.session_id,
            "token_type": self.token_type,
            "exp": int((now + expiration_delta).timestamp()),
            "iat": int(now.timestamp())
        }


class FingerprintCollector:
    @staticmethod
    def generate_fingerprint_hash(request: Request) -> str:
        headers = [
            request.headers.get("user-agent", ""),
            request.headers.get("accept-language", ""),
            request.headers.get("accept-encoding", "")
        ]
        fingerprint_data = "|".join(headers)
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()


class JWTCookieManager:
    def __init__(self) -> None:
        self._cookie_name: str = "session_token"
        self._cookie_max_age: int = 30 * 24 * 60 * 60  # 30 days
        self._settings = Settings()

    def create_user_token(self, user_id: int, fingerprint_hash: str, session_id: int) -> str:
        payload = TokenPayload(
            user_id=user_id,
            fingerprint_hash=fingerprint_hash,
            session_id=session_id
        )
        
        jwt_payload = payload.to_jwt_dict(timedelta(seconds=self._cookie_max_age))
        token = jwt.encode(
            payload=jwt_payload,
            key=self._settings.auth_jwt.private_key_content,
            algorithm=self._settings.algorithm
        )
        
        # Save token hash to database
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        user_sessions_services.update_session(
            session_id, 
            {"jwt_token_hash": token_hash}
        )
        
        return token

    def decode_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                jwt=token,
                key=self._settings.auth_jwt.public_key_content,
                algorithms=[self._settings.algorithm]
            )
            
            # Verify session in database
            session = user_sessions_services.get_session_by_id(payload["session_id"])
            if not session or not session.IsActive:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session revoked or inactive"
                )
                
            # Verify token hash matches
            current_token_hash = hashlib.sha256(token.encode()).hexdigest()
            if session.JwtTokenHash != current_token_hash:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token does not match session"
                )
                
            return payload
            
        except jwt.ExpiredSignatureError:
            log.warning("JWT token expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token expired"
            )
        except jwt.InvalidTokenError as e:
            log.warning(f"Invalid JWT token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid token"
            )

    def validate_payload_structure(self, payload: Dict[str, Any]) -> bool:
        required_fields = {"user_id", "fingerprint_hash", "session_id", "token_type"}
        return required_fields.issubset(payload.keys())

    def extract_user_data(self, payload: Dict[str, Any]) -> Dict[str, int]:
        if not self.validate_payload_structure(payload):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload structure"
            )
        
        # Update user's last activity
        user_services.update_user_activity(int(payload["user_id"]))
        
        return {
            "user_id": int(payload["user_id"]),
            "session_id": int(payload["session_id"])
        }

    def verify_fingerprint(self, payload: Dict[str, Any], request: Request) -> bool:
        token_fingerprint = payload.get("fingerprint_hash")
        current_fingerprint = FingerprintCollector.generate_fingerprint_hash(request)
        return token_fingerprint == current_fingerprint

    def set_cookie(self, response: Response, token: str) -> None:
        response.set_cookie(
            key=self._cookie_name,
            value=token,
            max_age=self._cookie_max_age,
            httponly=True,
            secure=True,
            samesite="lax"
        )

    def get_token_from_request(self, request: Request) -> Optional[str]:
        return request.cookies.get(self._cookie_name)

    def clear_cookie(self, response: Response) -> None:
        response.delete_cookie(
            key=self._cookie_name,
            httponly=True,
            secure=True,
            samesite="lax"
        )

    def refresh_token(self, old_token: str, request: Request) -> str:
        payload = self.decode_token(old_token)
        
        if not self.verify_fingerprint(payload, request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Device fingerprint mismatch"
            )
        
        user_data = self.extract_user_data(payload)
        return self.create_user_token(
            user_data["user_id"],
            payload["fingerprint_hash"],
            user_data["session_id"]
        )