from fastapi import APIRouter, Depends
from agents.colleges.all_colleges import list_all_agents, AGENT_REGISTRY
from api.dependencies import get_current_user

router = APIRouter()

@router.get("/")
async def get_agents(user: dict = Depends(get_current_user)):
    agents = []
    for name in list_all_agents():
        cls = AGENT_REGISTRY.get(name)
        agents.append({
            "name": name,
            "college": cls.college if cls else "Unknown",
            "expertise": cls.expertise if cls else "General",
        })
    return {"agents": agents}

@router.get("/colleges")
async def get_colleges(user: dict = Depends(get_current_user)):
    from agents.colleges.all_colleges import COLLEGE_MAPPING
    return {"colleges": COLLEGE_MAPPING}
