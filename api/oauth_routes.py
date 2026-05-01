from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

router = APIRouter(prefix="/oauth", tags=["OAuth"])


@router.get("/login/{provider}")
async def login(provider: str, state: str = None):
    from core.oauth import OAuthManager                 
    oauth = OAuthManager()
    try:
        url = oauth.get_authorization_url(provider, state=state)
        return {"url": url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/callback/{provider}")
async def callback(provider: str, code: str, state: str = None):
    from core.oauth import OAuthManager                 
    oauth = OAuthManager()
    try:
        token = oauth.exchange_code_for_token(provider, code, state)
        access_token = token.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received")
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
    from core.oauth import OAuthManager                 
    oauth = OAuthManager()
    return {"providers": list(oauth.providers.keys())}
