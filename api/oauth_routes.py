from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from core.oauth import OAuthManager

router = APIRouter(prefix="/oauth", tags=["authentication"])

@router.get("/login/{provider}")
async def login(provider: str, request: Request):
    oauth = OAuthManager()
    try:
        state = request.query_params.get("state")
        url = oauth.get_authorization_url(provider, state=state)
        return RedirectResponse(url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/callback/{provider}")
async def callback(provider: str, code: str, state: str = None):
    oauth = OAuthManager()
    try:
        token = oauth.exchange_code_for_token(provider, code, state)
        access_token = token.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received")

        # Return the token to the client (or set a cookie)
        # In production, issue a JWT for the user.
        return {"access_token": f"oauth2:{provider}:{access_token}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
