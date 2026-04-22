from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from core.auth import AuthManager
from core.oauth import OAuthManager

router = APIRouter()

class LoginRequest(BaseModel):
    provider: Optional[str] = None
    code: Optional[str] = None
    api_key: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user: dict

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    auth = AuthManager()
    
    # OAuth2 callback
    if request.provider and request.code:
        oauth = OAuthManager()
        token = oauth.exchange_code_for_token(request.provider, request.code)
        access_token = token.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received")
        user_info = oauth.get_user_info(request.provider, access_token)
        # Issue a JWT for subsequent requests
        jwt_token = AuthManager.generate_jwt(
            user_info.get("email", "unknown"), "operator", auth.jwt_secret
        )
        return TokenResponse(
            access_token=jwt_token,
            role="operator",
            user=user_info
        )
    
    # API Key login
    if request.api_key:
        auth_info = auth.verify_api_key(request.api_key)
        if not auth_info:
            raise HTTPException(status_code=401, detail="Invalid API key")
        jwt_token = AuthManager.generate_jwt(
            "api_key_user", auth_info["role"], auth.jwt_secret
        )
        return TokenResponse(
            access_token=jwt_token,
            role=auth_info["role"],
            user={"role": auth_info["role"]}
        )
    
    raise HTTPException(status_code=400, detail="Missing provider/code or api_key")

@router.get("/providers")
async def list_providers():
    oauth = OAuthManager()
    return {"providers": list(oauth.providers.keys())}

@router.get("/login/{provider}")
async def login_redirect(provider: str):
    oauth = OAuthManager()
    url = oauth.get_authorization_url(provider)
    return {"url": url}
