from fastapi import APIRouter
from app.schemas.responses import SuccessResponse

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    return SuccessResponse(
        data={"status": "working"},
        message="API is working"
    ) 