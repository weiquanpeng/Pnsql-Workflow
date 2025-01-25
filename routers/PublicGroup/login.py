from fastapi import APIRouter

router = APIRouter()


@router.get("/login")
async def login():
    return {"message": "This is a login route"}


@router.get("/logout")
async def logout():
    return {"message": "This is a logout route"}
