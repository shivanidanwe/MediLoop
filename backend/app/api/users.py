from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
def users_root():
    return {"message": "Users API route placeholder"}
