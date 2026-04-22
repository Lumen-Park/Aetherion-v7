"""
OAuth2 / OIDC Routes – Standalone provider endpoints.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from core.oauth import OAuthManager

router = APIRouter(prefix="/oauth", tags=["OAuth"])

class OAuthCallbackRequest(BaseModel):
    code: str
    state: str = None

@router.get("/login/{provider}")
async def login(provider: str, state: str = None):
    """Initiate OAuth2 flow for a provider."""
    oauth = OAuthManager()
    try:
        url = oauth.get_authorization_url(provider, state=state)
        return {"url": url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/callback/{provider}")
async def callback(provider: str, code: str, state: str = None):
    """OAuth2 callback endpoint – exchanges code for token."""
    oauth = OAuthManager()
    try:
        token = oauth.exchange_code_for_token(provider, code, state)
        access_token = token.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received")
        # Return the token in a format that can be used by the frontend
        return {
            "access_token": f"oauth2:{provider}:{access_token}",
            "token_type": "bearer",
            "provider": provider,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth error: {str(e)}")

@router.get("/providers")
async def list_providers():
    """List configured OAuth providers."""
    oauth = OAuthManager()
    return {"providers": list(oauth.providers.keys())}
