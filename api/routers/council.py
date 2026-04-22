from fastapi import APIRouter, Depends
from agents.council.council import AetherionCouncil
from api.dependencies import get_current_user

router = APIRouter()

@router.get("/stats")
async def get_council_stats(user: dict = Depends(get_current_user)):
    council = AetherionCouncil()
    stats = council.telemetry.get_stats()
    return stats

@router.get("/judges")
async def get_judges(user: dict = Depends(get_current_user)):
    council = AetherionCouncil()
    return {"judges": council.judges}
