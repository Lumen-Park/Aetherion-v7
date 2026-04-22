from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.auth import AuthManager

security = HTTPBearer(auto_error=False)

def get_auth_manager() -> AuthManager:
    return AuthManager()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    auth_manager: AuthManager = Depends(get_auth_manager),
):
    if not credentials:
        if auth_manager.auth_enabled:
            raise HTTPException(status_code=401, detail="Missing authorization header")
        return {"role": "admin", "auth_disabled": True}
    
    token = credentials.credentials
    auth_info = auth_manager.authenticate(token)
    if not auth_info:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return auth_info

def require_role(required_role: str):
    def role_checker(user=Depends(get_current_user)):
        auth_manager = AuthManager()
        if not auth_manager.authorize(user, required_role):
            raise HTTPException(status_code=403, detail=f"Requires {required_role} role")
        return user
    return role_checker
