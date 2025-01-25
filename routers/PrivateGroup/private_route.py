from fastapi import APIRouter

router = APIRouter()

@router.get("/private")
async def private_route():
    return {"message": "This is a private route"}